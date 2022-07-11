import network
import webrepl
import upip
import config


def connect(ssid, pwd):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print(f"Connecting to network {ssid}")
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            pass
    print("Connected.")
    print("network ifconfig:", sta_if.ifconfig())
    print("hostname:", sta_if.config("dhcp_hostname"))

#def install_requirements():
#    upip.install(module, str(target))

connect(config.WLAN_SSID, config.WLAN_PASSWORD)
webrepl.start()
