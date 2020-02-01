def getSMA(candles, period, index=4):
	if len(candles) < period:
		raise ValueError('Not enough candles for the specified period')

	SMA = list()
	for i in range(period - 1):
		SMA.append(None)

	for i in range(period - 1, len(candles)):
		total = 0
		for j in range(period - 1, -1, -1):
			total += candles[i - j][index]
		SMA.append(total / period)

	return SMA



def getGeoSMA(candles, period, index=4):
	if len(candles) < period:
		raise ValueError('Not enough candles for the specified period')

	SMA = list()
	for i in range(period - 1):
		SMA.append(None)

	for i in range(period - 1, len(candles)):
		total = 1
		for j in range(period - 1, -1, -1):
			total *= candles[i - j][index]
		SMA.append(total ** (1 / period))

	return SMA



def getSlope(candles, width, back):
	if len(candles) < width + back:
		raise ValueError('Not enough points for width and back')

	SMA = getSMA(candles[-width - back:], width)
	slope = (SMA[-1] - SMA[-1 - back]) / SMA[-1 - back]

	return slope



def getGeoSlope(candles, width, back):
	if len(candles) < width + back:
		raise ValueError('Not enough points for width and back')

	SMA = getGeoSMA(candles[-width - back:], width)
	slope = (SMA[-1] - SMA[-1 - back]) / SMA[-1 - back]

	return slope



def getHA(candles):
	if len(candles) < 2:
		raise ValueError('Not enough candles')

	ha = list()
	#Calc first candle
	o = (candles[0][1] + candles[0][4]) / 2
	c = (candles[0][1] + candles[0][2] + candles[0][3] + candles[0][4]) / 4
	ha.append([candles[0][0], o, candles[0][2], candles[0][3], c, candles[0][5]])
	
	for i in range(1, len(candles)):
		candle = candles[i]
		prior = ha[-1]

		c = (candle[1] + candle[2] + candle[3] + candle[4]) / 4
		o = (prior[1] + prior[4]) / 2
		h = max(candle[2], o, c)
		l = min(candle[3], o, c)
		ha.append([candle[0], o, h, l, c, candle[5]])

	return ha