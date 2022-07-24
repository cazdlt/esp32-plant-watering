import network
import upip
import webrepl

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


def install_requirements():
    upip.debug = False
    packages = []
    print("Installing dependencies:", packages)
    upip.install(packages)
    print("Finished installing dependencies")


connect(config.WLAN_SSID, config.WLAN_PASSWORD)
install_requirements()
webrepl.start()
