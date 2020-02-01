import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import datetime
import pytz
import trading as t
from .tools import frange


class Plot:
	_trades = None
	_lev = None
	_symbol = None


	def __init__(self, trades, lev, symbol):
		self._trades = trades
		self._lev = lev
		self._symbol = symbol



	def _dateFormatter(self, x, y):
		return datetime.datetime.utcfromtimestamp(x).strftime("%Y-%m-%d")



	def show(self):
		times = list()
		balances = list()
		for trade in self._trades:
			symbols = trade[2].split("-")
			first = False
			if symbols[0] == self._symbol:
				first = True
			elif symbols[1] != self._symbol:
				times.append(trade[0])
				balances.append(0)
				continue


			if trade[1] == "Sell":
				if first:
					balances.append(trade[3])
				else:
					balances.append(trade[3] * trade[4])

			elif trade[1] == "Short":
				if first:
					balances.append(trade[3] / (self._lev - 1))
				else:
					balances.append(trade[3] * trade[4] / (self._lev - 1))

			elif trade[1] == "Long" or trade[1] == "Buy":
				if first:
					balances.append(trade[3] / self._lev)
				else:
					balances.append(trade[3] * trade[4] / self._lev)
			else:
				continue

			times.append(trade[0])
			
		'''
		candles = t.Chart("ETH-USD", "3d").candles

		bounds = [
			[1469145600, 1487721600],
			[1506038400, 1510617600],
			[1529712000, 1533686400]
		]
		maxSettings = []
		maxRight = 0
		for period in range(10, 80, 4):
			for cutoff in frange(0.5, 2.5, 0.1):
					STD = t.getMovingGeoSTD(candles, period)[period - 1:]

					right = 0
					for i in range(len(STD)):
						point = STD[i]
						index = i + period - 1
						time = candles[index][0]

						vol = point > cutoff
					
						contains = False
						for bound in bounds:
							if time > bound[0] and time < bound[1]:
								contains = True
								break

						if contains and not vol:
							right += 1
						elif not contains and vol:
							right += 1

					if right > maxRight:
						maxSettings = [period, cutoff]
						print(maxRight, maxSettings)
						maxRight = right

		print(maxSettings)


		period = maxSettings[0]
		cutoff = maxSettings[1]
		times2 = list()
		for i in range(period - 1, len(candles)):
			times2.append(candles[i][0])

		STD = t.getMovingGeoSTD(candles, period)[period - 1:]
		cutoffs = list()
		for point in STD:
			if point > cutoff:
				cutoffs.append(10000)
			else:
				cutoffs.append(1000)
		
		'''
		area = 0.07
		ax = plt.axes(yscale="log")
		plt.plot(times, balances)
		#plt.plot(times2, cutoffs)
		plt.title(self._symbol + " vs. Time")
		plt.xlabel("Time")
		plt.ylabel(self._symbol)
		ax.xaxis.set_major_formatter(tick.FuncFormatter(self._dateFormatter))
		plt.show()