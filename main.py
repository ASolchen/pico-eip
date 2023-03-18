import os
from eip_server.etherneip_socket_server import EIP_server

if hasattr(os, "uname") and os.uname()[0]=='rp2':
    import eip_server.pico_network
eip = EIP_server()


