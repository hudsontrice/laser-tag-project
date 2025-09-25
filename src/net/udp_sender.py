import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 7500
#client
#once game starts send 202 to hardware
#once the game ends send 221 to hardware THREE times
'''Need to set up 2 udp sockets for transmission of data to/from players
Use localhost (127.0.0.1) for network address
Use socket 7500 to broadcast, 7501 to receive (make sure to allow receive for any ip address)
Include functionality to be able to change network address
Format of transmission will be a single integer (equipment id of player who got hit)
Format of received data will be integer:integer (equipment id of player transmitting:equipment id of player hit)
After the game start count down timer finishes, the software will broadcast code 202
When the game ends, the software will broadcast code 221 three times
When data is received, software will broadcast equipment id of player that was hit
if player tags another player on their own team, broadcast their own equipment id as well of the equipment id of who they hit (two transmissions)
If code 53 is received, the red base has been scored. If the player is on the green team, they will receive 100 points and the base icon (from the instructor's github) will be added to the left of their codename.
if code 43 is received, the green base has been scored. If the player is on the red team, they will receive 100 points and the base icon (from the instructor's github) will be added to the left of their codename.'''


class UDPSender:
    def __init__(self, ip="127.0.0.1", port=7500):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        print(f"UDP sender initialized to transmit on {ip}:{port}")

    def send_message(self, message):
        try:
            self.sock.sendto(message.encode('utf-8'), (self.ip, self.port))
            print(f"Sent message: {message} to {self.ip}:{self.port}")
        except Exception as e:
            print(f"Error sending message: {e}")

    def change_address(self, new_ip): # added functionality to change the ip address the sender transmits can also change upon intialization
        self.ip = new_ip
        print(f"Changed UDP sender address to {new_ip}")


