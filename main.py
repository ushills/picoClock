import time

import network
import ntptime
import urequests
from machine import RTC
from machine import WDT

import config
from max7219 import buildMatrix, displaySend, displayClear

# set the wlan in station mode and turn-on
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# create a RTC instance
rtc = RTC()

# import configuration variables
TZLOCATION = config.TZLOCATION
DISPLAYOFFTIME = config.DISPLAYOFFTIME
DISPLAYONTIME = config.DISPLAYONTIME


def main():
    currentTime = ()
    # check if connected to wifi, if not connect
    connect_wifi()
    getUTCTime()
    currentTime = updateCurrentTime(currentTime)
    tzoffset = getTimezoneOffset(TZLOCATION)
    # start a watchdog timer
    wdt = WDT(timeout=5000)
    while True:
        wdt.feed()
        if rtc.datetime()[0:7] != currentTime:
            # make any adjustment for timezones
            localtime = time.localtime(time.mktime(time.localtime()) + tzoffset)
            print(localtime)
            formattedTime = formatTimeforMatrix(localtime[3:6])
            matrix = buildMatrix(
                0,
                0,
                formattedTime,
            )
            if displayOnCheck(localtime):
                displaySend(matrix)
            else:
                displayClear()
            # update the currentTime again
            currentTime = rtc.datetime()[0:7]

            # if the hour marker is at 00 try to update
            # the RTC to NTP
            if rtc.datetime()[4] == 1:
                getUTCTime()
                tzoffset = getTimezoneOffset(TZLOCATION)


def connect_wifi():
    if not wlan.isconnected():
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        print("Waiting for connection")
        while not wlan.isconnected():
            time.sleep(1)
    wlan_config = wlan.ifconfig()
    print(wlan_config)


def displayOnCheck(localtime):
    # localtime format (2024, 8, 3, 16, 49, 28, 5, 216)
    if int(DISPLAYOFFTIME) > int(localtime[3]) > (int(DISPLAYONTIME)-1):
        # print ("Display On")
        return True
    # print("Display Off")
    return False    


def getTimezoneOffset(TZLOCATION):
    if TZLOCATION == "IP":
        tzinfo = urequests.get("https://worldtimeapi.org/api/ip")
    else:
        tzlocation = TZLOCATION
        tzinfo = urequests.get("http://worldtimeapi.org/api/timezone/" + tzlocation)
    if tzinfo.status_code == 200:
        timezone = tzinfo.json()["timezone"]
        dst = tzinfo.json()["dst"]
        print("Timezone location =", timezone)
        if dst is True:
            print("DST Active")
        tz_offset = tzinfo.json()["raw_offset"]
        dst_offset = tzinfo.json()["dst_offset"]
        return tz_offset + dst_offset
    else:
        print("Could not retreive timezone info reverting to UTC")
        return 0


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
