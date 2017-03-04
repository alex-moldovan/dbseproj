# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from stocks.models import Trade, Market, Sector, Alert
from django.db.models import Avg, StdDev, Count, Min, Max
from datetime import date, timedelta, datetime

import socket
import csv
import codecs
import time

@shared_task
def stocksfeed():

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(('cs261.dcs.warwick.ac.uk', 80))
	sock.settimeout(None)

	buffer = ""
	# Write the target to a file for testing purposes.
	#target = open("livetest.csv", 'w')
	while True:
		# Buffer size should be a small power of 2. 4096 should be enough.
		data = sock.recv(4096)
		if data:
			buffer = data.decode()
			buffer = buffer.splitlines()
			# target.write(buffer)
			reader = csv.reader(buffer)
			for row in reader:
				# Simple validation rule
				if len(row) == 10 and validateTime(row[0]):
					q = Trade(trade_time=row[0], buyer=row[1], seller=row[2], price=row[3], size=row[4], currency=row[5], symbol=row[6], sector=row[7], bid=row[8], ask=row[9], checked=1)
					q.save()

					# Send detectAnomalies to another worker (thread)
					detectAnomalies.delay(q.id)
		else:
			break
	#target.close()
	sock.close()

def validateTime(trade_time):
	try:
		tt = datetime.strptime(trade_time, "%Y-%m-%d %H:%M:%S.%f")
	except ValueError:
		return False
	return True

@shared_task
def detectAnomalies(tradeid):
	tr = Trade.objects.get(id=tradeid)
	detectFatFinger(tr)
	detectPumpDump(tr)

def detectFatFinger(tr):
	stats = Market.objects.filter(symbol=tr.symbol).latest('id')

	# Check price
	if float(tr.price) > (stats.price_avg * 5):
		sendAlert(tr,"fatfinger-price")

	# Check size
	if int(tr.size) > (stats.size_avg * 8):
		sendAlert(tr,"fatfinger-size")
	elif int(tr.size) > (stats.size_avg * 4):
		# For lower differences it can mean a volume spike
		sendAlert(tr,"volume-spike")

	# Check bid
	if float(tr.bid) > (stats.price_avg * 5):
		sendAlert(tr,"fatfinger-bid")

	# Check ask
	if float(tr.ask) > (stats.price_avg * 5):
		sendAlert(tr,"fatfinger-ask")

def detectPumpDump(tr):
	# Such operations can take a long time (lookup data for 100 days)
	# Take minimum buy bid (min_b) in last n days
	# If ask > ?1.5*min_b could be dumping.

	# This needs a more complex check

	min_b = Trade.objects.filter(buyer=tr.seller, symbol=tr.symbol, trade_time__gte = datetime.today() - timedelta(days=100)).earliest('bid')
	if float(tr.ask) > 1.5 * float(min_b.bid):
		sendAlert(tr,"pump-and-dump")

def sendAlert(tr, problem):
	q = Alert(trade=tr, anomaly=problem, resolved=0)
	print("new alert")
	q.save()

@shared_task
def updatemarket():
	# Get all symbols
	symbols = Trade.objects.values('symbol').distinct()
	for s in symbols:
		# Arbitrarely chosen 25000 - to check (assumption last 25k trades are enough for good approximations)
		pa = Trade.objects.filter(symbol=s['symbol']).order_by('-trade_time')[:25000].aggregate(Avg('price'))
		ps = Trade.objects.filter(symbol=s['symbol']).order_by('-trade_time')[:25000].aggregate(StdDev('price'))
		sa = Trade.objects.filter(symbol=s['symbol']).order_by('-trade_time')[:25000].aggregate(Avg('size'))
		ss = Trade.objects.filter(symbol=s['symbol']).order_by('-trade_time')[:25000].aggregate(StdDev('size'))
		q = Market(update_date=date.today(), symbol=s['symbol'], price_avg=pa['price__avg'], price_stddev=ps['price__stddev'], size_avg=sa['size__avg'], size_stddev=ss['size__stddev'])
		q.save()