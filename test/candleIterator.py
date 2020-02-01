from .tools import getNested
from trading import Chart
import math
import copy
import time

class CandleIterator:
	_section = None
	_startIndex = 0
	_endIndex = -1
	_index = 0
	_offsets = None
	_factors = None


	def __init__(self, section):
		self._section = section
		self._startIndex = getNested(section.buffers, section.iterateKey) - 1
		self._iterateWidth = Chart.widthToSec(section.iterateKey[1])
		self._endIndex = len(getNested(section.candles, section.iterateKey))
		self._index = self._startIndex
		self._getOffsets()



	def __iter__(self):
		return self


	def __next__(self):
		if self._index >= self._endIndex:
			raise StopIteration

		candles = self._section.candles
		newCandles = {}
		for pair in candles:
			newCandles[pair] = {}
			for width in candles[pair]:
				offset = self._offsets[pair][width]
				factor = self._factors[pair][width]
				index = math.floor((self._index + offset) / factor)
				buff = self._section.buffers[pair][width]
				temp = candles[pair][width][index - buff + 1: index]

				startTime = getNested(candles, self._section.iterateKey)[self._index][0]
				endTime = startTime + self._iterateWidth
				lastCandle = self._section.getLastCandle(pair, width, endTime)
				temp.append(lastCandle)
				newCandles[pair][width] = temp
	
		self._index += 1
		return newCandles



	def _getOffsets(self):
		candles = self._section.candles

		iterateWidth = Chart.widthToSec(self._section.iterateKey[1])
		iterate = getNested(candles, self._section.iterateKey)
		if len(iterate) == 0:
			return

		iterateTime = iterate[0][0]
		self._offsets = {}
		self._factors = {}
		for key in candles:
			self._offsets[key] = {}
			self._factors[key] = {}
			for width in candles[key]:
				otherTime = candles[key][width][0][0]
				factor = Chart.widthToSec(width) / iterateWidth
				self._factors[key][width] = factor
				self._offsets[key][width] = int((iterateTime - otherTime) / iterateWidth)