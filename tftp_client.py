import socket

CODE_RRQ = 1
CODE_WRQ = 2
CODE_DATA = 3
CODE_ACK = 4
CODE_ERR = 5

def send_udp_packet(ip, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    parsed_ip = ip.split(":")
    client_socket.sendto(data, (parsed_ip[0], int(parsed_ip[1])))
    client_socket.close()

def send_request(ip, opcode, filename, mode='octet'):
    pass

# Funciones para enviar paquetes
def send_read_request(ip, filename):
    send_request(ip, 'rrq', filename)

def send_write_request(ip, filename):
    send_request(ip, 'wrq', filename)

def send_data(ip, block_num, data):
    pass

def send_ack(ip, block_num):
    pass

def send_error(ip, error_num, error_msg):
    pass



# Funcion para parsear paquetes recividos
def parse_packet(data_recv):
    opcode = 0 # Los dos primeros bytes
    block_num = -1 # Los 2 bytes siguientes
    data = "" # en caso de DATA, lo que quede hasta el final
    
    return opcode, block_num, data



def create_listen_socket(ip):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    parsed_ip = ip.split(":")
    server_socket.bind((parsed_ip[0], int(parsed_ip[1])))
    return server_socket

def download_file(ip, filename):
    file_content = ""

    listen_socket = create_listen_socket(ip) # creamos un socket para escuchar

    send_read_request(ip, filename) # enviamos el primer paquete para pedir permiso para leer un archivo
    while True:
        received_data, client_address = listen_socket.recvfrom() # esperamos respuesta del servidor

        opcode, block_num, data = parse_packet(received_data) # parseamos el paquete recivido

        if opcode == CODE_DATA: 
            file_content += data
            send_ack(ip, block_num)
        elif opcode == CODE_ERR:
            print("pues ha dao error")

        # sabemos que ha terminado cuando la data son < 512 bytes