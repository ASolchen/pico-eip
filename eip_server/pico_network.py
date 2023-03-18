import socket
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("ACCESS POINT","PASSWORD")
sta_if = network.WLAN(network.STA_IF)
