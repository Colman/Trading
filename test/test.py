import trading as t
from .tools import settingsRange
from .testCase import TestCase
from .result import Result
import time
import math
import copy
import datetime


class Test:
	_settings = None
	_buffers = None
	_getPosition = None
	_lev = None
	_testCase = None
	result = None


	def __init__(self, sectionTimes, settings, buffers, getPosition, lev=1, progress=False):
		self._settings = settings
		self._buffers = buffers
		self._getPosition = getPosition
		self._lev = lev
		self._testCase = TestCase(sectionTimes, buffers)

		if self._isFind():
			self.result = self._find(progress)
		else:
			self.result = self._testSettings(settings)



	def _isFind(self, settings=None):
		if settings == None:
			settings = self._settings
			
		for key in settings:
			if isinstance(settings[key], dict):
				if self._isFind(settings[key]):
					return True
			elif isinstance(settings[key], list):
				return True

		return False



	def _find(self, progress):
		maxProfit = 0
		maxSettings = {}
		first = True

		for settings in settingsRange(self._settings):
			timeSec = None
			if first and progress:
				timeSec = time.time()

			result = self._testSettings(settings)

			if result["profit"] > maxProfit:
				maxSettings = settings
				maxProfit = result["profit"]
				print(maxSettings)
				print(maxProfit)
				print("")

			if first and progress:
				timeSec = time.time() - timeSec
				iterator = settingsRange(self._settings)
				iterations = len(list(iterator))

				per = datetime.timedelta(seconds=timeSec)
				eta = datetime.timedelta(seconds=timeSec * iterations)
				print("Time Per => " + str(per))
				print("ETA => " + str(eta))
				first = False

		return {
			"settings": maxSettings,
			"profit": maxProfit
		}



	def _testSettings(self, settings):
		finalResult = {
			"trades": [],
			"profit": 1
		}

		for section in self._testCase.sections:
			result = Result(section, settings, self._getPosition, self._lev).result
			finalResult["trades"] += result["trades"]
			finalResult["profit"] *= result["profit"]

		return finalResult