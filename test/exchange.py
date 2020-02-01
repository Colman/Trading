import datetime
import os


class Exchange:
	START_SYMBOL = "USD"
	START_AMOUNT = 100
	MAKER_FEE = 0.999
	TAKER_FEE = 0.997
	balances = None
	position = None


	def __init__(self, balances=None):
		if balances == None:
			self.balances = {self.START_SYMBOL: self.START_AMOUNT}
		else:
			self.balances = balances



	def setBalance(self, symbol, amount):
		self.balances[symbol] = amount



	def getBalance(self, symbol):
		if symbol in self.balances:
			return self.balances[symbol]
		
		return 0



	def buy(self, pair, amount, price, isTaker=False):
		if amount == 0 or price <= 0:
			return False

		symbol0 = pair.split("-")[0]
		symbol1 = pair.split("-")[1]

		balance = self.getBalance(symbol1)
		if balance < amount * price:
			return False
		self.setBalance(symbol1, balance - amount * price)


		balance = self.getBalance(symbol0)
		if isTaker:
			self.setBalance(symbol0, balance + amount * self.TAKER_FEE)
		else:
			self.setBalance(symbol0, balance + amount * self.MAKER_FEE)

		return True



	def sell(self, pair, amount, price, isTaker=False):
		if amount == 0 or price <= 0:
			return False

		symbol0 = pair.split("-")[0]
		symbol1 = pair.split("-")[1]

		balance = self.getBalance(symbol0)
		if balance < amount:
			return False
		self.setBalance(symbol0, balance - amount)


		balance = self.getBalance(symbol1)
		if isTaker:
			self.setBalance(symbol1, balance + amount * price * self.TAKER_FEE)
		else:
			self.setBalance(symbol1, balance + amount * price * self.MAKER_FEE)

		return True



	def long(self, pair, amount, price, isTaker=False):
		symbol = pair.split("-")[1]
		balance = self.getBalance(symbol)
		if balance == 0 or amount == 0:
			return False

		lev = amount * price / balance
		if lev > 3.3333:
			return False

		if isTaker:
			self.setBalance(symbol, balance - amount * price * (1 - self.TAKER_FEE))
		else:
			self.setBalance(symbol, balance - amount * price * (1 - self.MAKER_FEE))
			
		lev = amount * price / self.getBalance(symbol)
		liq = price * (0.15 - 1 / lev + 1)
		if isTaker:
			liq /= self.TAKER_FEE
		else:
			liq /= self.MAKER_FEE


		self.position = {
			"pair":pair,
			"isLong": True,
			"amount":amount,
			"price": price,
			"liqPrice": liq
		}

		return True



	def short(self, pair, amount, price, isTaker=False):
		symbol = pair.split("-")[1]
		balance = self.getBalance(symbol)
		if balance == 0 or amount == 0:
			return False

		lev = amount * price / balance
		if lev > 3.3333:
			return False

		if isTaker:
			self.setBalance(symbol, balance - amount * price * (1 - self.TAKER_FEE))
		else:
			self.setBalance(symbol, balance - amount * price * (1 - self.MAKER_FEE))
			
		lev = amount * price / self.getBalance(symbol) + 1
		liq = price / (0.15 - 1 / lev + 1)
		if isTaker:
			liq *= self.TAKER_FEE
		else:
			liq *= self.MAKER_FEE

		self.position = {
			"pair":pair,
			"isLong": False,
			"amount":amount,
			"price": price,
			"liqPrice": liq
		}

		return True



	def closePosition(self, price, isTaker=False):
		pos = self.position
		if pos != None:
			symbol = pos["pair"].split("-")[1]
			balance = self.getBalance(symbol)

			size = pos["amount"] * price
			if isTaker:
				size *= self.TAKER_FEE
			elif isTaker == False:
				size *= self.MAKER_FEE

			if pos["isLong"]:
				balance += size - pos["amount"] * pos["price"]

			else:
				balance += pos["amount"] * pos["price"] - size
			

			self.setBalance(symbol, balance)
			self.position = None