import network
import time
import config

# set the wlan in station mode and turn-on
wlan = network.WLAN(network.STA_IF)
wlan.active(True)


def connect_wifi():
    if not wlan.isconnected():
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        print("Waiting for connection")
        while not wlan.isconnected():
            time.sleep(1)
    wlan_config = wlan.ifconfig()
    print(wlan_config)


connect_wifi()
