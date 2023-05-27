from machine import SPI, Pin
from micropython import const

_noOp = const(0)
_decodemode = const(9)
_intensity = const(10)
_scanlimit = const(11)
_shutdown = const(12)
_displayTest = const(15)
_numberOfMatrix = const(4)
_matrixColumns = const(8)
_matrixRows = const(8)


spi = SPI(0, sck=Pin(2), baudrate=8000000, mosi=Pin(3))
cs = Pin(5, Pin.OUT)

# Character set
digits = [
    ["1111", "1001", "1001", "1001", "1001", "1001", "1111"],  # 0
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
    ["0", "0", "0", "0", "0", "0", "0"],  # separator (12)
]


def extractBytes(data):
    bytesList = []
    for i in range(len(data) // 8):
        bits = data[((i * 8)) : ((1 + i) * 8)]
        print(bits)
        bytesList.append(int(bits, 2))
    return bytesList


def buildMatrix(xPos, yPos, digitNumber):
    matrixData = []
    # fill the number of blank rows required from yPos
    for y in range(yPos):
        matrixData.append("0" * (_numberOfMatrix * _matrixColumns))

    # build the matrix row by row starting at 0 + yPos
    for row in range(_matrixRows - 1 - yPos):
        rowData = ""
        for c in digitNumber:
            rowData = rowData + digits[c][row]
        # check the row is full with digits, if not add trailing zeros
        if len(rowData) != _numberOfMatrix * _matrixColumns:
            rowData = rowData + (
                "0" * ((_NumberOfMatrix * _matrixColumns) - len(rowData))
            )
        matrixData.append(rowData)

    # fill any missing rows with zeros
    if len(matrixData) != _matrixRows:
        matrixData.append("0" * ((_numberOfMatrix * _matrixColumns) - len(matrixData)))
    return matrixData


def displayCommand(command, data):
    cs(0)
    for m in range(_numberOfMatrix):
        spi.write(bytearray([command, data]))
    cs(1)


def displayInit():
    for command, data in (
        (_shutdown, 0),
        (_displayTest, 0),
        (_scanlimit, 7),
        (_decodemode, 0),
        (_shutdown, 0),
        (_displayTest, 0),
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
displayCommand(_intensity, 1)
displayClear()

displayCommand(_shutdown, 1)
