import time

import network
import ntptime
from machine import RTC

import config
from max7219 import buildMatrix, displaySend

# set the wlan in station mode and turn-on
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# create a RTC instance
rtc = RTC()


def connect_wifi():
    if not wlan.isconnected():
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        print("Waiting for connection")
        while not wlan.isconnected():
            time.sleep(1)
    wlan_config = wlan.ifconfig()
    print(wlan_config)


def getUTCTime():
    timenow = rtc.datetime()
    try:
        ntptime.settime()
        newtime = rtc.datetime()
        if timenow != newtime:
            print("Time updated")
        else:
            print("Time correct")
        timeCurrent = True
    except Exception as e:
        print("Could not update time", e)
        timeCurrent = False
    return timeCurrent


# connect_wifi()
matrix = buildMatrix(0, 0, [2, 13, 2, 11, 4, 13, 6, 13, 2, 13, 3])
displaySend(matrix)


def main():
    currentTime = ()
    # check if connected to wifi, if not connect
    connect_wifi()
    getUTCTime()
    currentTime = updateCurrentTime(currentTime)
    print(currentTime)
    while True:
        if rtc.datetime()[0:7] != currentTime:
            currentTime = rtc.datetime()[0:7]
            print(currentTime)
            hour, minute, second = (
                str(currentTime[4]),
                str(currentTime[5]),
                str(currentTime[6]),
            )
            print(hour + ":" + minute + "." + second)


def updateCurrentTime(currentTime):
    if rtc.datetime()[0:7] != currentTime:
        return rtc.datetime()[0:7]


if __name__ == "__main__":
    main()
