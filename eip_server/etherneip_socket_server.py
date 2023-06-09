import socket
import struct, time
import threading


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.daemon = True

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()



class EIP_Header():
    def __init__(self, data=None) -> None:
        self.cmd = None
        self.len = None
        self.session = None
        self.stat = None
        self.sender_context = None
        self.options = None
        if data:
            self.decode(data)
    
    def decode(self, data):
        #unpacks data from the socket
        self.cmd = struct.unpack('H', data[:2])[0]
        self.len = struct.unpack('H', data[2:4])[0]
        self.session = struct.unpack('I', data[4:8])[0]
        self.stat = struct.unpack('I', data[8:12])[0]
        self.sender_context = struct.unpack('Q', data[12:20])[0]
        self.options = struct.unpack('I', data[20:24])[0]

    def encode(self) -> bytes:
        #packs this object up to send to socket
        data = struct.pack('H',self.cmd) + \
                struct.pack('H',self.len) + \
                struct.pack('I',self.session) + \
                struct.pack('I',self.stat) + \
                struct.pack('Q',self.sender_context) + \
                struct.pack('I',self.options)
        return data


class CIP_ConnectionManager(): #72 bytes to parse
    def __init__(self, data) -> None:
        self.sequence = 1
        self.interface_handle = struct.unpack('I', data[:4])[0]     #00000000 Interface Handle: CIP (0x00000000)
        self.timeout = struct.unpack('H', data[4:6])[0]             #0000     Timeout: 0
        self.count = struct.unpack('H', data[6:8])[0]               #0200     Item Count: 2
        self.type_id_0 = struct.unpack('H', data[8:10])[0]          #0000     Type ID: Null Address Item (0x0000)
        self.type_id_0_len = struct.unpack('H', data[10:12])[0]     #0000     Length: 0 
        self.type_id_1 = struct.unpack('H', data[12:14])[0]         #b200     Type ID: Unconnected Data Item (0x00b2)
        self.type_id_1_len = struct.unpack('H', data[14:16])[0]     #4800     Length: 72
        self.service = struct.unpack('B', data[16:17])[0]           #54       Service: Forward Open (Request)
        self.path_len = struct.unpack('B', data[17:18])[0]          #02       Request Path Size: 2 words
        self.path_segment = struct.unpack('H', data[18:20])[0]      #2006     Path Segment: 0x20 (8-Bit Class Segment)
        self.path_instance = struct.unpack('H', data[20:22])[0]     #2401     Path Segment: 0x24 (8-Bit Instance Segment)
        self.tick_time = struct.unpack('B', data[22:23])[0]         #05       Priority and Tick Time 0<<4 || 5
        self.timeout_ticks = struct.unpack('B', data[23:24])[0]     #9a       Time-out ticks: 154
        self.o_to_t_id = struct.unpack('I', data[24:28])[0]         #00000000 O->T Network Connection ID: 0x00000000
        self.t_to_o_id = struct.unpack('I', data[28:32])[0]         #013d3300 T->O Network Connection ID: 0x00333d01
        self.conx_serial = struct.unpack('H', data[32:34])[0]       #0100     Connection Serial Number: 0x0001
        self.vid = struct.unpack('H', data[34:36])[0]               #0100     Originator Vendor ID: Rockwell Automation/Allen-Bradley (0x0001)
        self.o_serial = struct.unpack('I', data[36:40])[0]          #05d41dc0 Originator Serial Number: 0xc01dd405
        self.timeout_mult = struct.unpack('I', data[40:44])[0]      #00000000 Connection Timeout Multiplier: *4 (0) + (3-byte padding)
        self.o_to_t_rpi = struct.unpack('I', data[44:48])[0]        #30750000 O->T RPI: 30.000ms
        self.o_to_t_params = struct.unpack('H', data[48:50])[0]     #2648     O->T Network Connection Parameters: 0x4826
        self.t_to_o_rpi = struct.unpack('I', data[50:54])[0]        #30750000 T->O RPI: 30.000ms
        self.t_to_o_params = struct.unpack('H', data[54:56])[0]     #2248     T->O Network Connection Parameters: 0x4822
        self.trans_trig = struct.unpack('B', data[56:57])[0]        #81       Transport Type/Trigger: 0x81, Direction: Server, Trigger: Cyclic, Class: 1
        self.conx_path_len = struct.unpack('B', data[57:58])[0]     #0f       Connection Path Size: 15 words
        self.conx_path_seg_info = struct.unpack('B'*30, data[58:88])#340401000c00e9fd8203200424972c962c64800500000000000000000000  Connection Path: [Key], Assembly, Instance: 0x97, Connection Point: 0x96, Connection Point: 0x64, [Data]
        self.app_reply_len = None
        self.reserved = None
        self.type_id = None
        self.type_id_2 = struct.unpack('H', data[16:18])[0]

    
    def cm_encode(self)->bytes:
        data = struct.pack('I', self.interface_handle)      #00000000 Interface Handle: CIP (0x00000000)
        data += struct.pack('H', self.timeout)              #0000 Timeout: 0
        data += struct.pack('H', 3)                         #0300 Item Count: 3
        data += struct.pack('H', self.type_id_0)            #0000 type Id (Null Address Item)
        data += struct.pack('H', self.type_id_0_len)        #0000 item length (0 bytes)
        data += struct.pack('H', self.type_id_1)            #b200 type id (Unconnected Data Item)
        data += struct.pack('H', 30)                        #1e00 item length (30)
        data += struct.pack('B', 0xd4)                      #d4 Service (Forward Open + response) flag
        data += struct.pack('BBB',0,0,0)                    #000000 #padding
        data += struct.pack('I', 0x023d0013)                 #13003d02 #O->T Network Connection ID: 0x023d0013
        data += struct.pack('I', self.t_to_o_id)             #013d3300 #T->O Network Connection ID: 0x00333d01
        data += struct.pack('H', self.conx_serial)          #0100 #Connection Serial Number: 0x0001
        data += struct.pack('H', self.vid)                  #0100 Originator Vendor ID: Rockwell Automation/Allen-Bradley (0x0001)
        data += struct.pack('I', self.o_serial)              # 05d41dc0 Originator Serial Number: 0xc01dd405
        data += struct.pack('I', self.o_to_t_rpi)            # 30750000 O->T API: 30.000ms
        data += struct.pack('I', self.t_to_o_rpi)            # 30750000 T->O API: 30.000ms
        data += struct.pack('B', 0x00)                      # 00 Application Reply Size: 0 words
        data += struct.pack('B', 0x00)                      # 00 Reserved: 0x00
        data += struct.pack('H', 0x8000)                    # 0080 Type ID: Socket Address Info O->T (0x8000)
        data += struct.pack('H', 16)                        # 1000 Length: 16
        data += struct.pack('H', 0x0200)                    # 0002 sin_family: 2
        data += struct.pack('H', 0xae08)                    # 08ae sin_port: 2222
        data += struct.pack('I', 0x00000000)                # 00000000 sin_addr: 0.0.0.0
        data += struct.pack('Q', 0x0000000000000000)        # 0000000000000000 sin_zero: 0000000000000000
        return data

    def cip_io_encode(self):
        data = struct.pack('H', 2)                 #0200 Item Count: 2
        data += struct.pack('H', 0x8002)           #0280 Type ID: Sequenced Address Item (0x8002)
        data += struct.pack('H', 8)                #08 Length: 8
        data += struct.pack('I', self.t_to_o_id)   #013d3300 Connection ID: 0x00333d01
        data += struct.pack('I', self.sequence)    #01000000 Encapsulation Sequence Number: 1-2^16
        data += struct.pack('H', 0x00b1)           #b100 Type ID: Connected Data Item (0x00b1)
        data += struct.pack('H', 34)               #2200 Length: 34
        data += struct.pack('H', self.sequence)    #2200 CIP Sequence Count: 1-2^16
        data += struct.pack('B'*32, *[0x00 for i in range(32)])    #Data!!
        #increment sequence number
        self.sequence = (self.sequence + 1) % 2**16
        return data
    

import os
if hasattr(os, "uname") and os.uname()[0]=='rp2':
    
    print("starting PICO wifi")
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("SSID","Password")
    sta_if = network.WLAN(network.STA_IF)
    addr = socket.getaddrinfo('0.0.0.0', 44818)[0][-1]
    print(addr)
    HOST = sta_if.ifconfig()[0]
else:
    HOST = "192.168.10.10"
print(f'Hosting on {HOST}')
TCP_PORT = 44818
UDP_PORT = 2222 # on the server

class EIP_PICO_server():
    def __init__(self) -> None:
        while 1:
            time.sleep(5)
            self.tcp_conn = None
            self.tcp_addr = None
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.tcp_socket.settimeout(5.0)
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_socket.bind(socket.getaddrinfo('0.0.0.0', 44818)[0][-1])
            self.udp_socket.settimeout(None)
            self.update()
            self.tcp_socket.close()
            self.udp_socket.close()
            print("resetting all connections")
            time.sleep(5)

    def update(self):
        try:
            self.tcp_socket.listen(1)
            print("Listening on TCP...")
            self.tcp_conn, self.tcp_addr = self.tcp_socket.accept()
            data = self.tcp_conn.recv(1024)
            print(f"TCP data (List Services): {data}")
            #read the session and stucture
            #send back the tcp data needed
            print(data)
            eip_header = EIP_Header(data)
            if eip_header.cmd == 0x0004: #List Services
                cip_data = b"\x01\x00\x00\x01\x14\x00\x01\x00\x20\x01\x43\x6f\x6d\x6d\x75\x6e\x69\x63\x61\x74\x69\x6f\x6e\x73\x00\x00"
                eip_header.len = len(cip_data)
                print(eip_header.encode()+cip_data)
                self.tcp_conn.sendall(eip_header.encode()+cip_data)
                data = self.tcp_conn.recv(1024)
                eip_header = EIP_Header(data)
                if eip_header.cmd == 0x0065: #Register Session
                    print(f"TCP data (register session): {data}")
                    cip_data = b"\x01\x00\x00\x00"
                    eip_header.len = len(cip_data)
                    eip_header.session = 1
                    data = eip_header.encode() + cip_data
                    print(data)
                    self.tcp_conn.sendall(data)
                    ##################
                    data = self.tcp_conn.recv(1024)
                    eip_header = EIP_Header(data)
                    if eip_header.cmd == 0x006f: #Send RR Data
                        print(f"TCP data (Forward Open): {data}")
                        con_manager = CIP_ConnectionManager(data[24:], )
                        cip_data = con_manager.cm_encode()
                        eip_header.len = len(cip_data)
                        data = eip_header.encode()+cip_data
                        self.tcp_conn.sendall(data)
                        print("sent forward open reply")
                        self.udp_socket.bind((HOST, UDP_PORT))
                        self.udp_socket.settimeout(0.06)
                        print("UDP Listening")
                        rpi_t = time.ticks_ms()
                        udp_ok = True
                        udp_watchdog = rpi_t
                        while udp_ok:
                            if (time.ticks_diff(time.ticks_ms(), rpi_t) > 20):
                                rpi_t = time.ticks_ms()
                                print(f'Sequence: {con_manager.sequence}')
                                tx_data = con_manager.cip_io_encode()
                                print(f"UDP Tx data: {len(tx_data)} bytes")
                                self.udp_socket.sendto(tx_data, (self.tcp_addr[0], UDP_PORT))
                            try:
                                rx_data, addr = self.udp_socket.recvfrom(1024)
                                udp_watchdog = time.ticks_ms()
                                print(f"UDP Rx data: {len(rx_data)} bytes")
                            except Exception as e:
                                    print(f"Error in UDP {e}")
                            if (time.ticks_ms() - udp_watchdog > 5000):
                                udp_ok = False
                                print("UDP watchdog expired")
        except Exception as err:
            print(err)

                                
class EIP_server():
    
    def __init__(self) -> None:
        self.io_thread = None
        self.udp_socket = None
        self.udp_active = False
        while 1:
            if self.io_thread:
                self.io_thread.stop()
                self.io_thread.join()
                self.io_thread = None
            self.con_manager = None
            self.tcp_conn = None
            self.tcp_addr = None
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.settimeout(0.5)
            self.tcp_socket.bind((HOST, TCP_PORT))
            self.update()
            self.tcp_socket.close()
            print("resetting all connections")
            time.sleep(1)

    def update(self):
        try:
            self.tcp_socket.listen()
            print("Listening on TCP...")
            self.tcp_conn, self.tcp_addr = self.tcp_socket.accept()
            with self.tcp_conn as c:
                while 1:
                    self.handle_tcp(c)
        except Exception as err:
            print(err)

    def handle_tcp(self, connection):
        services = {0x0004: self.handle_list_services,
                    0x0065: self.handle_register_session,
                    0x006f: self.handle_send_rr,
                    }
        data = connection.recv(1024)
        eip_header = EIP_Header(data)
        try:
            res = services[eip_header.cmd](eip_header, data)
        except KeyError as e:
            print(f"Unknown EIP command: {eip_header.cmd}")
        print(f"Sending [{hex(eip_header.cmd)}]: {res}")
        connection.sendall(res)
        return res

    def handle_list_services(self, eip_header, data):
        cip_data = b"\x01\x00\x00\x01\x14\x00\x01\x00\x20\x01\x43\x6f\x6d\x6d\x75\x6e\x69\x63\x61\x74\x69\x6f\x6e\x73\x00\x00"
        print(f"TCP data (List Services): {data}")
        eip_header.len = len(cip_data)
        res = eip_header.encode()+cip_data
        print(res)
        return res

    def handle_register_session(self, eip_header, data):
        print(f"TCP data (register session): {data}")
        cip_data = b"\x01\x00\x00\x00"
        eip_header.len = len(cip_data)
        eip_header.session = 1
        res = eip_header.encode() + cip_data
        print(res)
        return res

    def handle_send_rr(self, eip_header,  data):
        print(f"TCP data (Forward Open): {data}")
        self.con_manager = CIP_ConnectionManager(data[24:], )
        #self.con_manager.sequence = 65000 # to test roll-over
        cip_data = self.con_manager.cm_encode()
        eip_header.len = len(cip_data)
        res = eip_header.encode()+cip_data
        self.start_io_thread()
        return res

    def start_io_thread(self):
        self.udp_active = False
        if self.io_thread:
            print(f"Killing thread {self.io_thread}")
            self.io_thread.stop()
            self.io_thread.join()
        self.io_thread = StoppableThread(target=self.handle_cip_io)
        print(f"Starting thread {self.io_thread}")
        self.io_thread.start()


    def handle_cip_io(self):
        if self.udp_socket: #clean up an old socket
            self.udp_socket.close()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((HOST, UDP_PORT))
        self.udp_socket.settimeout(0.06)
        print("UDP Listening")
        t = time.time()
        self.udp_active = True
        udp_watchdog = t
        while self.udp_active:
            debug = not (self.con_manager.sequence % 10)
            if ((time.time() - t) > 0.02):
                t = time.time()
                tx_data = self.con_manager.cip_io_encode()
                if debug:
                    print(f'Sequence: {self.con_manager.sequence}')
                    print(f"\tUDP Tx data: {len(tx_data)} bytes")
                self.udp_socket.sendto(tx_data, (self.tcp_addr[0], UDP_PORT))
            try:
                rx_data, addr = self.udp_socket.recvfrom(1024)
                udp_watchdog = time.time()
                if debug:
                    print(f"\tUDP Rx data: {len(rx_data)} bytes")
            except TimeoutError:
                    pass
            if (time.time() - udp_watchdog > 5.0):
                self.udp_active = False
                print("UDP watchdog expired")
        self.udp_socket.close()

if __name__ == "__main__":
    eip = EIP_server()
    print("Closing")

