import trading as t
import math
import time
from .tools import getNested, getGCD

class Section:
	buffers = None
	iterateKey = None
	startTime = None
	endTime = None
	candles = None
	_extraCandles = None


	def __init__(self, buffers, iterateKey, startTime=0, endTime=-1):
		self.buffers = buffers
		self.iterateKey = iterateKey
		self.startTime = startTime
		self.endTime = endTime
		self._getCandles()
		self._getExtraCandles()



	def _getCandles(self):
		iterWidth = t.Chart.widthToSec(self.iterateKey[1])
		endTime = self.endTime
		if endTime == -1:
			endTime = time.time()
		endTime = math.floor(endTime / iterWidth) * iterWidth

		candles = {}
		for pair in self.buffers:
			candles[pair] = {}
			for width in self.buffers[pair]:
				widthSec = t.Chart.widthToSec(width)
				start = self.startTime - self.buffers[pair][width] * widthSec
				start = math.floor(start / widthSec) * widthSec
				chart = t.Chart(pair, width, startTime=start, endTime=endTime)
				candles[pair][width] = chart.candles

		self.candles = self._fixCandles(candles)



	def _fixCandles(self, candles):
		maxTime = self._getMaxTime(candles)
		for pair in candles:
			for width in candles[pair]:
				if maxTime == None:
					candles[pair][width] = []
				else:
					widthSec = t.Chart.widthToSec(width)
					back = self.buffers[pair][width]
					backTime = maxTime - back * widthSec
					backTime = math.floor(backTime / widthSec) * widthSec
					firstTime = candles[pair][width][0][0]
					offset = int((backTime - firstTime) / widthSec)
					candles[pair][width] = candles[pair][width][offset:]
				
		return candles



	def _getMaxTime(self, section):
		maxTime = None
		for pair in section:
			for width in section[pair]:
				index = self.buffers[pair][width]
				if index >= len(section[pair][width]):
					return None
				time = section[pair][width][index][0]
				if maxTime == None or time > maxTime:
					maxTime = time
		return maxTime



	def _getExtraCandles(self):
		iterWidth = t.Chart.widthToSec(self.iterateKey[1])
		startIndex = getNested(self.buffers, self.iterateKey)

		self._extraCandles = {}
		iterCandles = getNested(self.candles, self.iterateKey)
		startTime = iterCandles[startIndex][0]
		endTime = iterCandles[-1][0] + iterWidth

		for pair in self.candles:
			widths = [iterWidth]
			for width in self.candles[pair]:
				widths.append(t.Chart.widthToSec(width))
			width = t.Chart.secToWidth(getGCD(widths))

			if width in self.candles[pair]:
				self._extraCandles[pair] = None
			else:
				chart = t.Chart(pair, width, startTime, endTime)
				self._extraCandles[pair] = chart.candles



	def getLastCandle(self, pair, width, endTime):
		smallSec = None
		candles = None
		if self._extraCandles[pair] == None:
			widths = list(self.candles[pair].keys())
			for i in range(len(widths)):
				widths[i] = [widths[i], t.Chart.widthToSec(widths[i])]
			widths.sort(key=lambda x:x[1])
			candles = self.candles[pair][widths[0][0]]
			smallSec = widths[0][1]

		else:
			candles = self._extraCandles[pair]
			smallSec = candles[1][0] - candles[0][0]

		widthSec = t.Chart.widthToSec(width)
		endIndex = math.floor((endTime - candles[0][0]) / smallSec)
		startTime = math.floor(endTime / widthSec) * widthSec
		if startTime == endTime:
			startTime -= widthSec
		num = int((endTime - startTime) / smallSec)
		candles = candles[endIndex - num:endIndex]

		if len(candles) > 0:
			timeSec = candles[0][0]
			o = candles[0][1]
			h = candles[0][2]
			l = candles[0][3]
			c = candles[-1][4]
			v = candles[0][5]
			for i in range(1, len(candles)):
				if candles[i][2] > h:
					h = candles[i][2]
				if candles[i][3] < l:
					l = candles[i][3]
				v += candles[i][5]

			return [timeSec, o, h, l, c, v]

		return None
		
