import numpy as np
import trading as t
from .exchange import Exchange
from .candleIterator import CandleIterator
from .tools import getNested
import time


class Result:
	_section = None
	_settings = None
	_getPosition = None
	_lev = None
	_exchange = None
	_collateral = None
	result = None
	

	def __init__(self, section, settings, getPosition, lev=1):
		self._section = section
		self._settings = settings
		self._getPosition = getPosition
		self._lev = lev
		self._exchange = Exchange()
		self._collateral = self._exchange.START_SYMBOL
		self._getResult()



	def _getResult(self):
		trades = []
		for candles in CandleIterator(self._section):
			trades2 = self._getTrades(candles)
			trades += trades2

		position = self._exchange.position
		if position != None:
			pair = position["pair"]
			candles = self._section.candles[pair]
			width = list(candles.keys())[0]
			price = candles[width][-1][4]
			self._exchange.closePosition(price, None)

		
		self._changeCollateral(self._exchange.START_SYMBOL, self._section.candles)
		balance = self._exchange.getBalance(self._exchange.START_SYMBOL)
		profit = balance / self._exchange.START_AMOUNT

		self.result = {
			"trades": trades,
			"profit": profit
		}



	def _getTrades(self, candles):
		self._checkLiq(candles)

		newPosition = self._getPosition(candles, self._settings)
		if newPosition["isLong"] != None:
			oldPosition = self._exchange.position
			
			if self._lev == 1:
				newSymbol = newPosition["pair"].split("-")[1]
				if newPosition["isLong"]:
					newSymbol = newPosition["pair"].split("-")[0]
				
				if self._collateral != newSymbol:
					return self._changePosition(newPosition, candles)

			else:
				newIsLong = newPosition["isLong"]
				newPair = newPosition["pair"]
				if oldPosition == None:
					return self._changePosition(newPosition, candles)
						
				elif oldPosition["isLong"] != newIsLong or oldPosition["pair"] != newPair:
					return self._changePosition(newPosition, candles)

		return []



	def _checkLiq(self, candles):
		position = self._exchange.position
		if position != None:
			isLong = position["isLong"]
			pair = position["pair"]
			width = self._section.iterateKey[1]
			widthSec = t.Chart.widthToSec(width)
			endTime = getNested(candles, self._section.iterateKey)[-1][0] + widthSec
			candle = self._section.getLastCandle(pair, width, endTime)

			over = not isLong and candle[2] >= position["liqPrice"]
			under = isLong and candle[3] <= position["liqPrice"]
			if over or under:
				self._exchange.closePosition(position["liqPrice"], True)



	def _changePosition(self, position, candles):
		if self._exchange.position != None:
			closeCandles = candles[self._exchange.position["pair"]]
			width = list(closeCandles.keys())[0]
			closePrice = closeCandles[width][-1][4]
			self._exchange.closePosition(closePrice, True)


		iterate = getNested(candles, self._section.iterateKey)
		timeSec = iterate[-1][0] + t.Chart.widthToSec(self._section.iterateKey[1])
		trades = []

		colSymbol = None
		if self._lev == 1 and position["isLong"]:
			colSymbol = position["pair"].split("-")[0]
		else:
			colSymbol = position["pair"].split("-")[1]

		collateral = self._changeCollateral(colSymbol, candles)
		if collateral != None:
			trades.append([timeSec] + collateral)

		if self._lev != 1:
			posCandles = candles[position["pair"]]
			width = list(posCandles.keys())[0]
			price = posCandles[width][-1][4]
			action = None
			amount = None
			if position["isLong"]:
				amount = self._enter(position["pair"], price, self._lev)
				action = "Long"

			else:
				amount = self._exit(position["pair"], price, self._lev)
				action = "Short"

			trades.append([timeSec, action, position["pair"], amount, price])

		return trades



	def _changeCollateral(self, newSymbol, candles):
		if newSymbol != self._collateral:
			newPair = newSymbol + "-" + self._collateral
			
			if newPair in candles:
				width = list(candles[newPair].keys())[0]
				price = candles[newPair][width][-1][4]
				amount = self._enter(newPair, price)
				self._collateral = newSymbol
				return ["Buy", newPair, amount, price]

			else:
				newPair = self._collateral + "-" + newSymbol
				width = list(candles[newPair].keys())[0]
				price = candles[newPair][width][-1][4]
				amount = self._exit(newPair, price)
				self._collateral = newSymbol
				return ["Sell", newPair, amount, price]

		return None

			


	def _enter(self, pair, price, lev=1):
		amount = None
		balance = self._exchange.getBalance(pair.split("-")[1])
		if lev == 1:
			amount = balance * 0.9999 / price
			self._exchange.buy(pair, amount, price, True)
			self._collateral = pair.split("-")[0]
		else:
			amount = balance * 0.9999 * lev / price
			self._exchange.long(pair, amount, price, True)

		return amount



	def _exit(self, pair, price, lev=1):
		amount = None
		if lev == 1:
			symbol = pair.split("-")[0]
			amount = self._exchange.getBalance(symbol) * 0.9999
			self._exchange.sell(pair, amount, price, True)
			self._collateral = pair.split("-")[1]
		else:
			balance = self._exchange.getBalance(pair.split("-")[1])
			amount = balance * 0.9999 * (lev - 1) / price
			self._exchange.short(pair, amount, price, True)

		return amount