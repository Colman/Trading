from . import trend
from . import otherIndicators
import numpy as np
import math
import decimal


def getBollinger(candles, period=20, std=2):
    if len(candles) < period:
        raise ValueError('Not enough candles for the specified period')

    bollinger = list()
    for i in range(period - 1):
        entry = list()
        entry.append(None)
        entry.append(None)
        entry.append(None)
        bollinger.append(entry)

    SMA = trend.getSMA(candles, period)
    STD = otherIndicators.getMovingSTD(candles, period)
    for i in range(period - 1, len(candles)):
        entry = list()
        entry.append(SMA[i] - (STD[i] * std))
        entry.append(SMA[i])
        entry.append(SMA[i] + (STD[i] * std))
        bollinger.append(entry)

    return bollinger



def getBollingerPoints(candles, period=20, std=2):
    n = period
    z = std
    v = 0
    t = 0
    for i in range(len(candles) - n + 1, len(candles)):
        v += candles[i][4]
        t += candles[i][4] ** 2

    s = t + (t * (z**2)) + ((n**2) * t) - (n * t * (z**2)) - (2 * n * t)
    s += (v**2) + ((v**2) * (z**2)) - (n * (v**2))
    s *= n
    if s < 0:
        return [None, None]

    root = math.sqrt(s)

    num = (n * v) - v - (v * (z**2))
    den = (n**2) - (2 * n) + 1 + (z**2) - (n * (z**2))

    if den == 0:
        return [None, None]

    low = (num + z * root) / den
    high = (num - z * root) / den

    return [low, high]



def getGeoBollinger(candles, period=20, std=2):
    if len(candles) < period:
        raise ValueError('Not enough candles for the specified period')

    bollinger = list()
    for i in range(period - 1):
        entry = list()
        entry.append(None)
        entry.append(None)
        entry.append(None)
        bollinger.append(entry)

    SMA = trend.getGeoSMA(candles, period)
    STD = otherIndicators.getMovingGeoSTD(candles, period)
    for i in range(period - 1, len(candles)):
        entry = list()
        entry.append(SMA[i] - (STD[i] * std))
        entry.append(SMA[i])
        entry.append(SMA[i] + (STD[i] * std))
        bollinger.append(entry)

    return bollinger
    