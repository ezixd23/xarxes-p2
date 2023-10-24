import socket
import struct
import sys

CODE_RRQ = 1
CODE_WRQ = 2
CODE_DATA = 3
CODE_ACK = 4
CODE_ERR = 5

IP = "127.0.0.1:6969"

def send_udp_packet(client_socket, data, ip=IP):
    parsed_ip = ip.split(":")
    client_socket.sendto(data, (parsed_ip[0], int(parsed_ip[1])))

def send_request(client_socket, opcode, filename, mode='octet'):
    data = struct.pack('!H', opcode) + filename.encode('utf-8') + b'\0' + mode.encode('utf-8') + b'\0'
    send_udp_packet(client_socket, data)

# Funciones para enviar paquetes
def send_read_request(client_socket, filename):
    send_request(client_socket, CODE_RRQ, filename)

def send_write_request(client_socket, filename):
    send_request(client_socket, CODE_WRQ, filename)

def send_data(client_socket, block_num, data):
    pass

def send_ack(client_socket, block_num):
    data = struct.pack('!H', CODE_ACK) + struct.pack('!H', block_num)
    send_udp_packet(client_socket, data)


# Funcion para parsear paquetes recividos
def parse_header(data_recv):
    opcode = struct.unpack('!H', data_recv[:2])[0]
    block_num = struct.unpack('!H', data_recv[2:4])[0]

    return opcode, block_num

def parse_data(data):
    return struct.unpack(f"{len(data)}s", data)[0].decode('utf-8')

def handle_error_packet(packet):
    error_code = struct.unpack('!H', packet[2:4])[0]
    error_message = packet[4:].decode('utf-8')
    print(f'Error {error_code}: {error_message}')
    sys.exit(1)


def download_file(filename):
    file_content = ""

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1)

    send_read_request(client_socket, filename) # enviamos el primer paquete para pedir permiso para leer un archivo

    curr_block = 1
    while True:
        received_data, server_address = client_socket.recvfrom(516) # esperamos respuesta del servidor

        opcode, block_num = parse_header(received_data) # parseamos el paquete recivido
        file_block_data = parse_data(received_data[4:])
        print(f"block received {opcode} {block_num} {len(file_block_data)}")

        if opcode == CODE_DATA and block_num == curr_block: 
            file_content += file_block_data
            save_file("downloaded.txt", file_content)
            send_ack(client_socket, block_num)
            curr_block += 1
        elif opcode == CODE_ERR:
            handle_error_packet(received_data)

        if len(file_block_data) < 512:
            break

    print(file_content) # TODO: Guardar archivo


def save_file(filename, data):
    with open(filename, 'wb') as file:
        file.write(data.encode('utf-8'))
    file.close()

download_file("data.txt")