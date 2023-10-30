import socket
import struct
import sys
import math

import argparse

CODE_RRQ = 1
CODE_WRQ = 2
CODE_DATA = 3
CODE_ACK = 4
CODE_ERR = 5

IP = "127.0.0.1:6969"

# Funció per enviar un paquet UDP a una adreça IP específica
def send_udp_packet(client_socket, data, ip=IP):
    # Divideix l'adreça IP en adreça i port
    parsed_ip = ip.split(":")
    # Envia les dades a l'adreça IP i port especificats
    client_socket.sendto(data, (parsed_ip[0], int(parsed_ip[1])))

# Funció per enviar una sol·licitud TFTP a un servidor
def send_request(client_socket, opcode, filename, mode='octet'):
    # Estructura de dades que representa la sol·licitud TFTP (opcode + nom del fitxer + mode)
    data = struct.pack('!H', opcode) + filename.encode('utf-8') + b'\0' + mode.encode('utf-8') + b'\0'
    # Crida a la funció send_udp_packet per enviar la sol·licitud amb les dades empaquetades
    send_udp_packet(client_socket, data)

# Funcions per enviar paquets
def send_read_request(client_socket, filename):
    send_request(client_socket, CODE_RRQ, filename)

def send_write_request(client_socket, filename):
    send_request(client_socket, CODE_WRQ, filename)

def send_data(client_socket, block_num, block_data):
    data = struct.pack('!H', CODE_DATA) + struct.pack('!H', block_num) + struct.pack(f"{len(block_data)}s", block_data.encode('utf-8'))
    print(f"sending data, num={block_num}")
    send_udp_packet(client_socket, data)

def send_ack(client_socket, block_num):
    data = struct.pack('!H', CODE_ACK) + struct.pack('!H', block_num)
    send_udp_packet(client_socket, data)


# Funció per parsear paquets rebuts
def parse_header(data_recv):
    opcode = struct.unpack('!H', data_recv[:2])[0]
    block_num = struct.unpack('!H', data_recv[2:4])[0]

    return opcode, block_num

def parse_data(data):
    return struct.unpack(f"{len(data)}s", data)[0].decode('utf-8')

# Funció per gestionar un paquet d'error rebut des del servidor TFTP
def handle_error_packet(packet):
    # Extreu el codi d'error del paquet (2 bytes)
    error_code = struct.unpack('!H', packet[2:4])[0]
    # Extreu el missatge d'error del paquet (a partir del cinquè byte, decodificat com a UTF-8)
    error_message = packet[4:].decode('utf-8')
    # Imprimeix el codi i el missatge d'error
    print(f'Error {error_code}: {error_message}')
    

# Descarrega un fitxer des d'un servidor TFTP
def download_file(filename):
    file_content = ""

    # Crea un socket UDP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1)

    # Envia una sol·licitud de lectura per obtenir permís per llegir el fitxer
    send_read_request(client_socket, filename) 
    curr_block = 1
    while True:
        # Espera la resposta del servidor (màxim 516 bytes)
        received_data, server_address = client_socket.recvfrom(516) 

        # Parseja la capçalera del paquet rebut per obtenir l'opcode i el número de bloc
        opcode, block_num = parse_header(received_data) 
        # Parseja les dades del paquet per obtenir el contingut del bloc
        file_block_data = parse_data(received_data[4:])
        print(f"block received #{block_num} {len(file_block_data)}")

        # Comprova si l'opcode és DATA i el número de bloc és el correcte
        if opcode == CODE_DATA and block_num == curr_block: 
            file_content += file_block_data
            # Envia una confirmació d'ACK amb el número de bloc rebut
            send_ack(client_socket, block_num)
            print(f"ACK #{block_num} sent")
            curr_block += 1
        elif opcode == CODE_ERR:
            # Gestiona el paquet d'error rebut del servidor
            handle_error_packet(received_data)

        # Comprova si la longitud del bloc rebut és menor que 512 (indicant l'últim bloc)
        if len(file_block_data) < 512:
            break

    # Desa el contingut del fitxer descarregat en un fitxer local amb el mateix nom 
    save_file(filename, file_content)
    print("File saved!")

# Escriu un fitxer a un servidor TFTP
def write_file(filename, file_content):
    # Calcula el nombre de segments de 512 bytes necessaris per emmagatzemar el contingut del fitxer 
    file_content_segments = math.ceil(len(file_content)/512) 
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(3)

    # Envia una sol·licitud d'escriptura per obtenir permís per escriure el fitxer
    send_write_request(client_socket, filename) 

    curr_block = 0
    # Variable per determinar si és el primer bloc que s'envia
    is_first = True
    while curr_block < file_content_segments:# Bucle fins que s'hagin enviat tots els segments del fitxer
        opcode, block_num, isfake = 0, 0, False
        try:
            # Espera la resposta del servidor (màxim 516 bytes)
            received_data, server_address = client_socket.recvfrom(516)
            opcode, block_num = parse_header(received_data)
        except:
            # En cas de que no es rebi l'ACK ni l'error, ens inventem l'ACK
            opcode, block_num = 4, curr_block
            isfake = True
        print(f"ack received {opcode} {block_num} {'*' if isfake else ''}")

        if opcode == CODE_ACK and block_num == curr_block:
            # Quan rebem el primer ACK, no sumem perque tenim que enviar el block = 0
            if not is_first:
                curr_block += 1
            else:
                is_first = False
            send_data(client_socket, curr_block, file_content[(curr_block)*512:(curr_block+1)*512])
        elif opcode == CODE_ERR:
            handle_error_packet(received_data)


def save_file(filename, data):
    with open(filename, 'wb') as file:
        file.write(data.encode('utf-8'))
    file.close()

def read_file(filename):
    content = ""
    with open(filename, 'r') as file:
        content = file.read() 
    file.close()
    return content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TFTP Client")
    
    parser.add_argument("operation", type=str, help="r=Read w=Write")
    parser.add_argument("filename", type=str, help="The name of the file to read/write")
    parser.add_argument("--port", "-p", help="Port the server is listening default: 6969")

    args = parser.parse_args()

    if args.port:
        IP = "127.0.0.1:" + port

    if args.operation == "r":
        download_file(args.filename)
    elif args.operation == "w":
        file_content = read_file(args.filename)
        write_file("c_" + args.filename, file_content)
    else:
        print("ERROR: operation must be r=Read or w=Write")
        print("")
        parser.print_help()
