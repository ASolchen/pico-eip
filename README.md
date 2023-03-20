# pico-eip
## Use a Raspberry Pi Pico W as an EthernetIP remote IO device

This is very early in testing. The standard python version (windows/mac/linux) is working. It's a bit buggy but keeps trying. I also had the micropython version working, but needs some updating. Eventually, I'd like to use the Pico's 2nd core to handle the IO (UDP) connection.

Testing in a CompactLogix PLC.

This was developed by running the example app at [https://github.com/EIPStackGroup/OpENer](https://github.com/EIPStackGroup/OpENer), and using the .eds from their project - .EDS file is from [https://github.com/EIPStackGroup/OpENer/tree/master/data](https://github.com/EIPStackGroup/OpENer/tree/master/data).

Wireshark captures were gather from a session using the above app. This python version replicates that session and only provides the minimal services needed. This is to keep the footprint very small so it can run on a Pico W.

## To run on a PC:
Get the ip address on you PC that the PLC can connect to and in the eip_server/ethernetip_socket_server.py file change the HOST:
`HOST = "your.pc.ip.address"`

In the PLC software, register the eds file and create a device on the network interface. Set the device IP address to your PC's IP.
Run it:
```console
foo@bar:~/PICO-EIP$ python3 main.py
```

## Future Plans:
1. Get the PC version more stable. Once running, it will be stable until a sequence roll-over. The sequence is a 16-bit number so it rolls over at 2**16
2. Update Pico version to match the methods used in the pc one.
3. Change data format in eds and code. Right now it is 32 bytes in, 32 bytes out.
4. Add proper logging, not `print(f'doing stuff')`    
5. Use kwarg for HOST
6. Make a client-side version to allow using a PC as master. Possibly use real remote IO, as well.
