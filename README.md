# pico-eip
##Use a Raspberry Pi Pico W as an EthernetIP remote IO device

This is very early in testing. The standard python version (windows/mac/linux) is working. It's a bit buggy but keeps trying. I also had the micropytohn version working, but needs some updating. Eventually, I'd like to use the Pico's 2nd core to handle the IO (UDP) connection.

Testing in a CompactLogix PLC.

This was developed by running the example app at [https://github.com/EIPStackGroup/OpENer](https://github.com/EIPStackGroup/OpENer), and using the .eds from their project - .EDS file is from [https://github.com/EIPStackGroup/OpENer/tree/master/data](https://github.com/EIPStackGroup/OpENer/tree/master/data).

Wireshark captures where gather from a session using the above app. This python version replicates that session and only provides the minimal services needed. This is to keep the footprint very small so it can run on a Pico W.