import trading as t
from .section import Section

class TestCase:
	sectionTimes = None
	buffers = None
	getPosition = None
	iterateKey = None
	sections = None


	def __init__(self, sectionTimes, buffers):
		self.sectionTimes = sectionTimes
		self.buffers = buffers
		self._getIterateKey()
		self._getSections()



	def _getIterateKey(self):
		sortedWidths = self._getSortedWidths()
		iterateKey = None
		minWidth = None
		for pair in sortedWidths:
			thisWidth = sortedWidths[pair][0]
			if minWidth == None or thisWidth[1] < minWidth:
				iterateKey = [pair, thisWidth[0]]
				minWidth = thisWidth[1]

		self.iterateKey = iterateKey



	def _getSortedWidths(self):
		widths = {}
		for pair in self.buffers:
			widths2 = []
			for key in self.buffers[pair]:
				width = [key, t.Chart.widthToSec(key)]
				widths2.append(width)
			widths2.sort(key=lambda x: x[1])
			widths[pair] = widths2

		return widths



	def _getSections(self):
		self.sections = []
		for sectionTime in self.sectionTimes:
			section = Section(self.buffers, self.iterateKey, sectionTime[0], sectionTime[1])
			self.sections.append(section)