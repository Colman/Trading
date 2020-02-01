def parseTable(path):
	file = open(path, "r")
	rows = list()
	keys = list()
	index = 0
	for row in file:
		if index == 1:
			index += 1
			continue

		rowArr = row.split("|")
		for i in range(len(rowArr)):
			rowArr[i] = rowArr[i].strip()
			try:
				rowArr[i] = float(rowArr[i])
			except ValueError as e:
				pass
		del rowArr[-1]

		if index == 0:
			for i in range(len(rowArr)):
				rowArr[i] = rowArr[i].lower()
			keys = rowArr
		else:
			row = {}
			for i in range(len(rowArr)):
				row[keys[i]] = rowArr[i]
			rows.append(row)

		index += 1

	return rows



def formatTable(rows, sizes):
	lines = list()

	for row in rows:
		line = ""
		for i in range(len(row)):
			if i != 0:
				line += " "
			cell = str(row[i])
			if len(cell) > sizes[i]:
				cell = cell[:sizes[i]]
			line += cell
			for j in range(len(cell), sizes[i]):
				line += " "
			line += " |"
		lines.append(line)

	return lines