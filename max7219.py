from machine import SPI, Pin
from micropython import const
from time import sleep

_noOp = const(0)
_decodemode = const(9)
_intensity = const(10)
_scanlimit = const(11)
_shutdown = const(12)
_displayTest = const(15)
_numberOfMatrix = const(4)
_matrixColumns = const(8)
_matrixRows = const(8)


spi = SPI(0, sck=Pin(2), baudrate=10000000, mosi=Pin(3))
cs = Pin(5, Pin.OUT)

# Character set
digits = [
    ["1111", "1001", "1001", "1001", "1001", "1001", "1111"],  # 0 4x7
    ["0001", "0001", "0001", "0001", "0001", "0001", "0001"],  # 1
    ["1111", "0001", "0001", "1111", "1000", "1000", "1111"],  # 2
    ["1111", "0001", "0001", "1111", "0001", "0001", "1111"],  # 3
    ["1001", "1001", "1001", "1111", "0001", "0001", "0001"],  # 4
    ["1111", "1000", "1000", "1111", "0001", "0001", "1111"],  # 5
    ["1111", "1000", "1000", "1111", "1001", "1001", "1111"],  # 6
    ["1111", "0001", "0001", "0001", "0001", "0001", "0001"],  # 7
    ["1111", "1001", "1001", "1111", "1001", "1001", "1111"],  # 8
    ["1111", "1001", "1001", "1111", "0001", "0001", "0001"],  # 9
    ["0000", "0000", "0000", "0000", "0000", "0000", "0000"],  # space (10)
    ["000", "010", "010", "000", "010", "010", "000"],  # comma (11)
    ["000", "000", "000", "000", "000", "000", "010"],  # period (12)
    ["0", "0", "0", "0", "0", "0", "0"],  # separator (13)
    ["000", "000", "111", "101", "101", "101", "111"],  # 0 3x5 (14)
    ["000", "000", "001", "001", "001", "001", "001"],  # 1 (15)
    ["000", "000", "111", "001", "111", "100", "111"],  # 2 (16)
    ["000", "000", "111", "001", "111", "001", "111"],  # 3 (17)
    ["000", "000", "101", "101", "111", "001", "001"],  # 4 (18)
    ["000", "000", "111", "100", "111", "001", "111"],  # 5 (19)
    ["000", "000", "111", "100", "111", "101", "111"],  # 6 (20)
    ["000", "000", "111", "001", "001", "001", "001"],  # 7 (21)
    ["000", "000", "111", "101", "111", "101", "111"],  # 8 (22)
    ["000", "000", "111", "101", "111", "001", "001"],  # 9 (23)
]


def extractBytes(data):
    bytesList = []
    for i in range(len(data) // 8):
        bits = data[((i * 8)) : ((1 + i) * 8)]
        bytesList.append(int(bits, 2))
    return bytesList


def buildMatrix(xPos, yPos, digitNumber):
    matrixData = []
    # fill the number of blank rows required from yPos
    for y in range(yPos):
        matrixData.append("0" * (_numberOfMatrix * _matrixColumns))

    # build the matrix row by row starting at 0 + yPosm
    for row in range(_matrixRows - 1):
        rowData = ""
        # populate with leading zeros depending on xPos
        rowData = rowData + ("0" * xPos)
        for c in digitNumber:
            rowData = rowData + digits[c][row]
        # check the row is full with digits, if not add trailing zeros
        while len(rowData) < _numberOfMatrix * _matrixColumns:
            rowData = rowData + "0"
        while len(rowData) > _numberOfMatrix * _matrixColumns:
            rowData = rowData[:-1]
        matrixData.append(rowData)

    # fill any missing rows with zeros
    if len(matrixData) < _matrixRows:
        matrixData.append("0" * (_numberOfMatrix * _matrixColumns))

    # cut of the last rows if larger than the matrix size
    while len(matrixData) > _matrixRows:
        matrixData.pop()
    return matrixData


def displaySend(matrix):
    # data has to be sent a row at a time with
    # a cs(0) in advance and a cs(1) post
    for row in range(len(matrix)):
        bytestoSend = extractBytes(matrix[row])
        cs(0)
        for b in bytestoSend:
            spi.write(bytearray([row + 1, b]))
        cs(1)


def displayCommand(command, data):
    cs(0)
    for m in range(_numberOfMatrix):
        spi.write(bytearray([command, data]))
    cs(1)


def displayInit():
    for command, data in (
        (_shutdown, 0),
        # (_displayTest, 1),
        (_scanlimit, 7),
        (_decodemode, 0),
        # (_shutdown, 0),
        # (_displayTest, 0),
    ):
        displayCommand(command, data)


def displayClear():
    for column in range(8):
        cs(0)
        for m in range(_numberOfMatrix):
            spi.write(bytearray([1 + column, 0]))
        cs(1)


displayInit()
displayCommand(_shutdown, 0)
displayCommand(_intensity, 5)
displayCommand(_displayTest, 1)
sleep(2)
displayCommand(_displayTest, 0)
displayClear()

displayCommand(_shutdown, 1)
