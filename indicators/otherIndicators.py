from . import trend
import math


def getRow(candles, index):
    red = isRed(candles[index])
    count = 1
    for i in range(index + 1, len(candles)):
        if red and isRed(candles[i]):
            count += 1

        if not red and not isRed(candles[i]):
            count += 1

        if red and not isRed(candles[i]):
            break

        if not red and isRed(candles[i]):
            break
    return count



def getRows(candles):
    index = 0
    redRows = list()
    greenRows = list()

    while(index < len(candles)):
        numRows = getRow(candles, index)
        if isRed(candles[index]):
            redRows.append(numRows)

        else:
            greenRows.append(numRows)

        index += numRows

    return (redRows, greenRows)



def avgCansInRow(candles):
    rows = getRows(candles)
    avgRed = sum(rows[0]) / len(rows[0])
    avgGreen = sum(rows[1]) / len(rows[1])
    return (avgRed, avgGreen)



def getRowSlopes(candles):
    index = 0
    redSlopes = list()
    greenSlopes = list()

    while(index < len(candles)):
        numRows = getRow(candles, index)
        diff = candles[index + numRows - 1][2] - candles[index][1]
        slope = diff / numRows
        if isRed(candles[index]):
            redSlopes.append(slope)

        else:
            greenSlopes.append(slope)

        index += numRows

    return (redSlopes, greenSlopes)



def avgRowSlopes(candles):
    slopes = getRowSlopes(candles)
    avgRed = sum(slopes[0]) / len(slopes[0])
    avgGreen = sum(slopes[1]) / len(slopes[1])
    return (avgRed, avgGreen)



def avgGain14(candles):
    gain = 0
    for candle in candles:
        if not isRed(candle):
            gain += candle[2] - candle[1]

    return gain / 14



def avgLoss14(candles):
    loss = 0
    for candle in candles:
        if isRed(candle):
           loss += candle[1] - candle[2]

    return loss / 14



def getRSI(candles):
    RSI = list()

    tGain = 0
    tLoss = 0
    for i in range(14):
        if isRed(candles[i]):
            tLoss += candles[i][1] - candles[i][2]

        else:
            tGain += candles[i][2] - candles[i][1]

    firstRS = tGain / tLoss

    RSI.append(100 - 100 / (1 + firstRS))

    pGain = tGain
    pLoss = tLoss
    pAGain = tGain / 14
    pALoss = tLoss / 14
    for i in range(14, len(candles)):
        if isRed(candles[i]):
                SRS = pAGain * 13 / (pALoss * 13 + candles[i][1] - candles[i][2])
                RSI.append(100 - 100 / (1 + SRS))

        else:
                SRS = (pAGain * 13 + candles[i][2] - candles[i][1]) / (pALoss * 13)
                RSI.append(100 - 100 / (1 + SRS))

        pAGain = avgGain14(candles[:i])
        pALoss = avgLoss14(candles[:i])

    return RSI



def getMovingSTD(candles, period):
    if len(candles) < period:
        raise ValueError('Not enough candles for the specified period')

    STD = list()
    for i in range(period - 1):
        STD.append(None)

    SMA = trend.getSMA(candles, period)
    for i in range(period - 1, len(candles)):
        totalSq = 0
        for j in range(period - 1, -1, -1):
            totalSq += (candles[i - j][4] - SMA[i]) ** 2
        STD.append(math.sqrt(totalSq / period))

    return STD



def getMovingGeoSTD(candles, period):
    if len(candles) < period:
        raise ValueError('Not enough candles for the specified period')

    STD = list()
    for i in range(period - 1):
        STD.append(None)

    SMA = trend.getGeoSMA(candles, period)
    for i in range(period - 1, len(candles)):
        totalSq = 0
        for j in range(period - 1, -1, -1):
            totalSq += math.log(candles[i - j][4] / SMA[i]) ** 2
        stdPoint = math.exp(math.sqrt(totalSq / period))
        STD.append(stdPoint)

    return STD