import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 7501
#server address and port this listens
class UDPServer:
    def __init__(self, ip="127.0.0.1", port=7501, buffer_size=1024): #default values. this can be imported and changed
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.sock.bind((ip, port))
        print(f"UDP server initialized on {ip}:{port}")



    def listener(self):  # listens on the specified ip and port returns message and address

        while True:
            data, addr = self.sock.recvfrom(self.buffer_size)
            message = data.decode('utf-8')
            print(f"Received message: {message} from {addr}")
            return message, addr #returns a tuple of the message and address
        
    def change_address(self, new_ip): # functionality to change the ip address the server listens on
        self.ip = new_ip
        self.sock.bind((new_ip, self.port))
        print(f"Changed UDP server address to {new_ip}")









