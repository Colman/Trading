from . import requests
import datetime
import os
import time


class Exchange:
	_reqs = None


	def __init__(self, private, public):
		self._reqs = requests.Requests(private, public)



	def getBalances(self, symbols):
		balances = self._fetchBalances()
		newBalances = {}
		for symbol in symbols:
			if symbol not in balances.keys():
				newBalances[symbol] = {
					"exchange": [0.0, 0.0],
					"margin": [0.0, 0.0]
				}
			else:
				newBalances[symbol] = balances[symbol]

		return newBalances



	def _fetchBalances(self):
		'''
		Description:
			This function gets all balances from all wallets

		Args:
			pair - The pair to order
			amount - The amount to order
			isMargin - If the order is a margin order
			price - The price to order at. If 0 or not supplied, market price is used.

		Returns:
			The array of balances, None if error
		'''

		data = {
			"request": "/v1/balances"
		}
		balances = self._reqs.authRequest("/v1/balances", data)
		if balances == None:
			return balances

		newBalances = {}
		for i in range(len(balances)):
			t = balances[i]["type"]
			if t == "deposit":
				continue
			if t == "trading":
				t = "margin"

			symbol = balances[i]["currency"].upper()
			if symbol not in newBalances:
				newBalances[symbol] = {}
			amount = float(balances[i]["amount"])
			available = float(balances[i]["available"])
			newBalances[symbol][t] = [amount, available]

		for symbol in newBalances.keys():
			keys = ["exchange", "margin"]
			for key in keys:
				if key not in newBalances[symbol]:
					newBalances[symbol][key] = [0.0, 0.0]

		return newBalances



	def checkOrder(self, orderId):
		'''
		Description:
			This function checks the status of an order by its id

		Args:
			id - The id of the order to check

		Returns:
			[avg_price, remaining_amount] or None if the order doesn't exist
		'''


		data = {
			"request": "/v1/order/status",
  			"order_id": orderId
		}
		order = self._reqs.authRequest("/v1/order/status", data)
		if order == None:
			return None

		price = order["avg_execution_price"]
		amount = order["remaining_amount"]
		if price == None or amount == None:
			return None

		return [price, amount]



	def fetchPositions(self):
		data = {
			"request": "/v1/positions"
		}
		positions = self._reqs.authRequest("/v1/positions", data)
		if positions == None:
			return None

		newPositions = []
		for position in positions:
			symbol0 = position["symbol"][:3].upper()
			symbol1 = position["symbol"][3:].upper()
			pair = symbol0 + "-" + symbol1

			amount = float(position["amount"])
			posType = "long"
			if amount < 0:
				posType = "short"

			newPosition = {
				"id": position["id"],
				"pair":pair,
				"type": posType,
				"amount": abs(amount),
				"price": float(position["base"])
			}
			newPositions.append(newPosition)

		return newPositions



	def closePosition(self, posId):
		data = {
			"request": "/v1/position/close",
			"position_id": posId
		}
		res = self._reqs.authRequest("/v1/position/close", data)
		if res == None:
			return False

		for i in range(5):
			pos = self.fetchPositions()
			if pos == None:
				return False

			if len(pos) == 0:
				return True

			time.sleep(5)

		return False



	def buy(self, pair, amount, price=0):
		return self._placeOrder(pair, amount, False, price)



	def sell(self, pair, amount, price=0):
		return self._placeOrder(pair, -amount, False, price)



	def long(self, pair, amount, price=0):
		return self._placeOrder(pair, amount, True, price)



	def short(self, pair, amount, price=0):
		return self._placeOrder(pair, -amount, True, price)



	def _placeOrder(self, pair, amount, isMargin, price=0):
		'''
		Description:
			This function places an order at a given price. If the amount
			is > 0 it is a buy, if it's < 0 it's a sell. If the price
			is 0 or not given, the order will be a market order.

		Args:
			pair - The pair to order
			amount - The amount to order
			isMargin - If the order is a margin order
			price - The price to order at. If 0 or not supplied, market price is used.

		Returns:
			Order id if the order was placed, false otherwise.
		'''

		if amount == 0:
			return None

		data = {
			"request": "/v1/order/new",
			"symbol": pair.replace("-", ""),
			"amount": str(amount), 
			"price": "1",
			"side": "buy",
			"exchange": "bitfinex",
			"type": "market",
			"ocoorder": False,
			"buy_price_oco": 0.0,
			"sell_price_oco": 0.0
		}

		if amount < 0:
			data["amount"] = str(-amount)
			data["side"] = "sell"

		if isMargin and price > 0:
			data["type"] = "limit"
			data["price"] = str(price)

		if not isMargin:
			if price == 0:
				data["type"] = "exchange market"
			else:
				data["type"] = "exchange limit"
				data["price"] = str(price)
			

		order = self._reqs.authRequest("/v1/order/new", data)
		if order == None or order["order_id"] == None:
			return None

		return order["order_id"]