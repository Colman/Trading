from . import requests
import datetime
import time
import math
import json
import os


class Chart:
	candles = list()
	_pair = ""
	_width = ""
	_startTime = 0
	_endTime = 0


	def __init__(self, pair, width, startTime=0, endTime=-1):
		self._pair = pair
		if Chart.widthToSec(width) < 900:
			raise ValueError("Width must be no smaller than 15m")
		self._width = width
		self._startTime = startTime
		if endTime == -1:
			self._endTime = time.time()
		else:
			self._endTime = endTime
		if self.checkUpdate():
			self._updateCandles()
		self._getCandles()
		


	def _getCandles(self):
		candlesFile = open(self._getCandlesPath(self._pair), "r")
		fileStr = candlesFile.read()
		candlesFile.close()

		if fileStr == None:
			return
		candles = json.loads(fileStr)
		if len(candles) == 0:
			return

		startIndex = math.ceil((self._startTime - candles[0][0]) / 900)
		endIndex = math.ceil((self._endTime - candles[0][0]) / 900)

		if startIndex < 0:
			startIndex = 0
		if endIndex >= len(candles):
			endIndex = len(candles)

		if startIndex >= endIndex:
			return []

		candles = candles[startIndex:endIndex]
		if len(candles) < 2:
			self.candles = candles
		else:
			self.candles = self._convertCandles(candles, Chart.widthToSec(self._width))



	def checkUpdate(self):
		fileStr = ""
		try:
			candlesFile = open(self._getCandlesPath(self._pair), "r")
			fileStr = candlesFile.read()
			candlesFile.close()
		except FileNotFoundError as e:
			pass

		if fileStr != "":
			candles = json.loads(fileStr)
			if len(candles) > 0 and self._endTime <= candles[-1][0]:
				return False

		return True



	def _updateCandles(self):
		fileStr = ""
		try:
			candlesFile = open(self._getCandlesPath(self._pair), "r")
			fileStr = candlesFile.read()
			candlesFile.close()
		except FileNotFoundError as e:
			pass

		candles = list()
		startTime = 0
		startPrice = 0
		if fileStr != "":
			candles = json.loads(fileStr)
			if len(candles) > 0:
				del candles[-1]
				if len(candles) > 0:
					startTime = candles[-1][0] + 900
					startPrice = candles[-1][4]
			
		while True:
			newCandles = self._fetchCandles(self._pair, startPrice, startTime)
			if len(newCandles) == 0:
				break
			candles += newCandles
			startTime = candles[-1][0] + 900
			startPrice = candles[-1][4]

		candlesFile = open(self._getCandlesPath(self._pair), "w")
		candlesFile.write(str(candles))
		candlesFile.close()
		


	def _fetchCandles(self, pair, startPrice=0, startTime=0):
		url = "/v2/candles/trade:15m:t" + pair.replace("-", "")
		url += "/hist?limit=1000&sort=1&start=" + str(startTime * 1000)

		req = requests.Requests()
		candles = req.request(url)
		if candles == None:
			return list()

		for i in range(len(candles)):
			candles[i] = [
				round(candles[i][0] / 1000),
				candles[i][1],
				candles[i][3],
				candles[i][4],
				candles[i][2],
				candles[i][5]
			]

		if startTime == 0:
			startTime = candles[0][0]
			startPrice = candles[0][1]

		endTime = 0
		if len(candles) > 0:
			endTime = candles[-1][0]
			
		return self._fillCandles(candles, startPrice, startTime, endTime + 900)



	def _fillCandles(self, candles, startPrice, startTime, endTime):
		lastTime = startTime - 900
		lastPrice = startPrice
		newCandles = list()
		for i in range(len(candles)):
			thisTime = candles[i][0]

			for j in range(lastTime + 900, thisTime, 900):
				newCandles.append([j, lastPrice, lastPrice, lastPrice, lastPrice, 0])
			newCandles.append(candles[i])
			lastTime = thisTime
			lastPrice = candles[i][4]

		for i in range(lastTime + 900, endTime, 900):
			newCandles.append([i, lastPrice, lastPrice, lastPrice, lastPrice, 0])

		return newCandles



	def _convertCandles(self, candles, newWidthSec):
		if len(candles) < 2:
			return None
		widthSec = candles[1][0] - candles[0][0]
		if newWidthSec < widthSec or newWidthSec % widthSec != 0:
			return None

		startTime = math.ceil(candles[0][0] / newWidthSec) * newWidthSec
		startIndex = int((startTime - candles[0][0]) / widthSec)
		step = int(newWidthSec / widthSec)
		newCandles = list()
		for i in range(startIndex, len(candles), step):
			high = candles[i][2]
			low = candles[i][3]
			close = 0
			volume = 0
			for j in range(step):
				if i + j >= len(candles):
					break
				if candles[i + j][2] > high:
					high = candles[i + j][2]
				if candles[i + j][3] < low:
					low = candles[i + j][3]
				close = candles[i + j][4]
				volume += candles[i + j][5]
			newCandle = [candles[i][0], candles[i][1], high, low, close, volume]
			newCandles.append(newCandle)

		return newCandles



	def _getCandlesPath(self, pair):
		relative = "candles/" + pair + ".json"
		return os.path.join(os.path.dirname(__file__), relative)



	@staticmethod
	def widthToSec(width):
		if width[-1] == "m":
			return int(width[:-1]) * 60
		elif width[-1] == "h":
			return int(width[:-1]) * 60 * 60
		elif width[-1] == "d":
			return int(width[:-1]) * 60 * 60 * 24
		else:
			return int(width[:-1]) * 60 * 60 * 24 * 7



	@staticmethod
	def secToWidth(sec):
		w = sec / (60 * 60 * 24 * 7)
		if int(w) == w:
			return str(int(w)) + "w"
		d = sec / (60 * 60 * 24)
		if int(d) == d:
			return str(int(d)) + "d"
		h = sec / (60 * 60)
		if int(h) == h:
			return str(int(h)) + "h"

		return str(int(sec / 60)) + "m"