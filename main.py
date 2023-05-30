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


def main():
    currentTime = ()
    # check if connected to wifi, if not connect
    connect_wifi()
    getUTCTime()
    currentTime = updateCurrentTime(currentTime)
    while True:
        if rtc.datetime()[0:7] != currentTime:
            currentTime = rtc.datetime()[0:7]
            formattedTime = formatTimeforMatrix(currentTime[4:7])
            matrix = buildMatrix(
                0,
                0,
                formattedTime,
            )
            displaySend(matrix)


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


def formatTimeforMatrix(currentTime):
    # print(currentTime)
    formattedTime = []
    returnedTime = []
    # convert all digits to strings
    for t in currentTime:
        formattedTime.append(str(t))

    # build a list of individual ints
    # split the hours
    if len(formattedTime[0]) < 2:
        returnedTime.append(0)

    [returnedTime.append(int(i)) for i in str(formattedTime[0])]

    # split the minutes
    if len(formattedTime[1]) < 2:
        returnedTime.append(0)
    [returnedTime.append(int(i)) for i in str(formattedTime[1])]

    # split the seconds
    if len(formattedTime[2]) < 2:
        returnedTime.append(0)
    [returnedTime.append(int(i)) for i in str(formattedTime[2])]

    # format to the required characters
    requiredCharacters = [
        returnedTime[0],
        13,
        returnedTime[1],
        11,
        returnedTime[2],
        13,
        returnedTime[3],
        13,
        13,
        # shift the seconds to the 3x5 character set
        returnedTime[4] + 14,
        13,
        returnedTime[5] + 14,
    ]

    return requiredCharacters


def updateCurrentTime(currentTime):
    if rtc.datetime()[0:7] != currentTime:
        return rtc.datetime()[0:7]


if __name__ == "__main__":
    main()
