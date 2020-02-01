import datetime
import json
import base64
import hashlib
import hmac
import time
import requests
import os


class Requests:
	_BASE_URL = "https://api.bitfinex.com" #Base URL for all requests

	def __init__(self, private=None, public=None):
		self._private = private
		self._public = public
		


	def request(self, path):
		url = self._BASE_URL + path

		date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		logFile = open(self._getLogPath("log/requests.log"), "a")
		logFile.write(date + " - " + url + "\n\n")
		logFile.close()

		while True: 
			response = requests.request("GET", url)
			logFile = open(self._getLogPath("log/responses.log"), "a")
			logFile.write(date + " - " + response.text + "\n\n")
			logFile.close()
			if response.status_code == 200:
				return response.json()
			if response.status_code == 429:
				time.sleep(float(response.headers["Retry-After"]))
			else:
				return None
		


	def authRequest(self, path, body={}):
		url = self._BASE_URL + path

		date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		logFile = open(self._getLogPath("log/requests.log"), "a")
		logFile.write(date + " - " + url + " " + str(body) + "\n\n")
		logFile.close()

		body["nonce"] = self._nonce()
		headers = self._headers(body)
		if headers == None:
			return None

		while True:
			response = requests.post(url, headers=headers, data=body, verify=True)
			logFile = open(self._getLogPath("log/responses.log"), "a")
			logFile.write(date + " - " + response.text + "\n\n")
			logFile.close()
			if response.status_code == 200:
				return response.json()
			if response.status_code == 429:
				time.sleep(float(response.headers["Retry-After"]))
			else:
				return None



	def _nonce(self):
		return str(int(round(time.time() * 10000)))



	def _headers(self, body):
		if self._private == None or self._public == None:
			return None

		bodyBytes = json.dumps(body).encode(encoding='UTF-8')
		body64 = base64.standard_b64encode(bodyBytes)
		secbytes = self._private.encode(encoding='UTF-8')
		sig = hmac.new(secbytes, body64, hashlib.sha384).hexdigest()
		return {
			'X-BFX-APIKEY': self._public,
    		'X-BFX-PAYLOAD': body64,
    		'X-BFX-SIGNATURE': sig
		}



	def _getLogPath(self, relative):
		return os.path.join(os.path.dirname(__file__), relative)