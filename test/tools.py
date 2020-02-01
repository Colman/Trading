from itertools import product
import threading
import logging


def getMaxVal(entry):
    maxVal = entry
    if isinstance(entry, list):
        vals = range(*entry)
        if len(vals) > 0:
            maxVal = vals[-1]

    return maxVal



def getNested(d, keys):
    if len(keys) == 1:
        return d[keys[0]]
    return getNested(d[keys[0]], keys[1:])



def setNested(d, keys, value):
    if len(keys) == 1:
        d[keys[0]] = value
    setNested(d[keys[0]], keys[1:], value)



def frange(start, end, step=1):
	tmp = start
	if step < 0:
		while(tmp > end):
			yield tmp
			tmp += step
	else:
		while(tmp < end):
			yield tmp
			tmp += step



def settingsRange(settings):
	keys, values = zip(*settings.items())
	output = list()
	for value in values:
		if isinstance(value, list):
			isFloat = False
			for value2 in value:
				if isinstance(value2, float):
					isFloat = True
					break
			if isFloat:
				output.append(frange(*value))
			else:
				output.append(range(*value))

		elif isinstance(value, dict):
			output.append(settingsRange(value))

		else:
			output.append([value])

	for value in product(*output):
		yield dict(zip(keys, value))



def getGCD(values):
	if len(values) == 0:
		return None
	result = values[0]
	for x in values[1:]:
		if result < x:
			temp = result
			result = x
			x = temp
		while x != 0:
			temp = x
			x = result % x
			result = temp
	return result