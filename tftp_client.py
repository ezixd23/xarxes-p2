import socket

def send_udp_packet(ip, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    parsed_ip = ip.split(":")
    client_socket.sendto(data, (parsed_ip[0], int(parsed_ip[1])))
    client_socket.close()

def send_request(opcode, filename, mode):
    pass

def send_read_request(filename, mode):
    send_request('rrq', filename, mode)

def send_write_request(filename, mode):
    send_request('wrq', filename, mode)

def send_data(block_num, data):
    pass

def send_ack(block_num):
    pass

def send_error(error_num, error_msg):
    pass