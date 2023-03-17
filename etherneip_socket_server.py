#server
import socket

HOST = "192.168.20.21"
TCP_PORT = 44818
UDP_PORT = 2222 # on the server

class EIP_server():
	def __init__(self) -> None:
		self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.tcp_socket.settimeout(5)
		self.tcp_socket.bind((HOST, TCP_PORT))
		self.tcp_conn = None
		self.tcp_addr = None
		self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.udp_socket.settimeout(5)
		self.udp_conn = None
		self.state = 0
	
	def start(self):
		self.update()

	def update(self):
		self.tcp_socket.listen()
		print("Listening on TCP...")
		self.tcp_conn, self.tcp_addr = self.tcp_socket.accept()
		with self.tcp_conn as c:
			data = c.recv(1024)
			print(f"TCP data (List Services): {data!r}")
			#read the session and stucture
			#send back the tcp data needed
			print(data)
			if data[:4] == b'\x04\x00\x00\x00':
				eip_header = b"\x04\x00\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
				#send back EIP header unchanged and list the Services
				c.sendall(eip_header+b'\x01\x00\x00\x01\x14\x00\x01\x00 \x01Communications\x00\x00')
				##################
				data = c.recv(1024)
				#register session
				print(f"TCP data (register session): {data!r}")
				#read the session and stucture
				#send back the tcp data needed
				print(data)
				c.sendall(data)
				##################
				data = c.recv(1024)
				print(f"TCP data (Forward Open): {data!r}")
				data = data[:2]+b'\x42\x00' +data[4:24] # EIP header
				data += b"\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\xb2\x00\x1e\x00" \
							b"\xd4\x00\x00\x00\x13\x00\x3d\x02\x01\x3d\x33\x00\x01\x00\x01\x00" \
							b"\x05\xd4\x1d\xc0\x30\x75\x00\x00\x30\x75\x00\x00\x00\x00\x00\x80" \
							b"\x10\x00\x00\x02\x08\xae\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
							b"\x00\x00"
				print(len(data))
				c.sendall(data)
				fwd_opn = data
				print("sent forward open reply")
				self.udp_socket.bind((HOST, UDP_PORT))
				print("UDP Listening")
				#set TCP to non-blocking and check for Keep alive
				c.settimeout(0.02)
				while 1:
					udp_data, addr = self.udp_socket.recvfrom(1024)
					#print(f"UDP data: {udp_data!r}")
					print(udp_data[16:24])
					udp_data = b'data'
					self.udp_socket.sendto(udp_data, addr)
					tcp_data = None
					try:
						tcp_data = c.recv(1024)
					except TimeoutError:
						pass
					if tcp_data:
						c.sendall(fwd_opn)


eip = EIP_server()
eip.start()
print("Closing")

