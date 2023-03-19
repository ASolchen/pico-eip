import os
if hasattr(os, "uname") and os.uname()[0]=='rp2':
    from eip_server.etherneip_socket_server import EIP_PICO_server
    print("Starting server...")
    eip = EIP_PICO_server()
else:
    from eip_server.etherneip_socket_server import EIP_server
    print("Starting server...")
    eip = EIP_server()


