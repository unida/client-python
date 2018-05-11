import websocket
import requests
import json
import time
import zlib
from base64 import b64decode
from random import randint
from threading import Thread

class SocketConnectionClosed(Exception):
	pass

class Unida:
	def __init__(self, api_key):
		host = 'data.unida.io'

		self._rest_host = 'https://' + host
		self._ws_host = 'wss://' + host
		self._api_key = api_key
		self._subscribed = False

		self._message_queue = []

	def _post(self, path, payload):
		# payload['api_key'] = self._api_key

		r = requests.post(self._rest_host + path, data=json.dumps(payload), headers={
			'X-Api-Key': self._api_key
		})

		return json.loads(r.text)

	def _get(self, path):
		r = requests.get(self._rest_host + path, headers={
			'X-Api-Key': self._api_key
		})

		return json.loads(r.text)		

	def _stream_msg_handler(self, ws, msg):
		self._message_queue.append(json.loads(zlib.decompress(msg)))

	def _ws_handler(self, path):
		ws = websocket.WebSocketApp(self._ws_host + path, on_message=self._stream_msg_handler)
		ws.run_forever()

	def _keep_session(self, subscriptions):
		while True:
			try:
				sub = self._post('/realtime/create-session/', {
					'subscriptions': subscriptions,
					'format': 'avro'
				})
			except:
				time.sleep(1)
				continue

			path = '/realtime/{}/'.format(sub['session_id'])

			self._subscribed = True

			self._ws_handler(path)

			time.sleep(1)

	def subscribe(self, subscriptions):
		t = Thread(target=self._keep_session, args=(subscriptions, ))
		t.deamonize = True
		t.start()

		while not self._subscribed:
			time.sleep(0.1)

	def stream_receive(self, blocking=True):
		while True:
			if len(self._message_queue) == 0 and blocking:
				time.sleep(0.01)
			elif len(self._message_queue) == 0 and not blocking:
				return None
			else:
				return self._message_queue.pop(0)

	def current_book(self, exchange, symbol):
		return self._get('/current/{}/{}/{}/'.format(exchange, 'book', symbol.replace('/', '_')))

	def history(self, entity, exchange, symbol, since, to):
		if entity == 'book':
			entity = 'books'

		symbol = symbol.replace('/', '_')
		history = self._get('/history/{}/{}/{}/{}/{}/'.format(entity, exchange, symbol, since, to))

		if entity:
			for i in range(len(history)):
				history[i]['asks'] = zlib.decompress(b64decode(history[i]['asks']))
				history[i]['bids'] = zlib.decompress(b64decode(history[i]['bids']))

		return history