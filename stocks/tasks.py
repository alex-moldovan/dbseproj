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

#@periodic_task(run_every=(crontab(hour=0, minute=57, day_of_week="*")))
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
					#detectAnomalies.delay(q.id)

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
		# Make stats based on trades registered yesterday
		## TO-DO ADD OR / last 25k trades (or so) / whichever is greater of the 2 values.
		yesterday = datetime.today() - timedelta(days=1)
		pa = Trade.objects.filter(trade_time__gte = yesterday, symbol=s['symbol']).aggregate(Avg('price'))
		ps = Trade.objects.filter(trade_time__gte = yesterday, symbol=s['symbol']).aggregate(StdDev('price'))
		sa = Trade.objects.filter(trade_time__gte = yesterday, symbol=s['symbol']).aggregate(Avg('size'))
		ss = Trade.objects.filter(trade_time__gte = yesterday, symbol=s['symbol']).aggregate(StdDev('size'))

		stats = Trade.objects.raw("SELECT 1 as id, slope, (vls.meanY - vls.slope*vls.meanX) as intercept FROM (SELECT ((sl.n*sl.sumXY - sl.sumX*sl.sumY) / (sl.n*sl.sumXX - sl.sumX*sl.sumX)) AS slope, sl.meanY as meanY, sl.meanX as meanX FROM (SELECT COUNT(y) as n, AVG(x) as meanX, SUM(x) as sumX, SUM(x*x) as sumXX, AVG(y) as meanY, SUM(y) as sumY, SUM(y*y) as sumYY, SUM(x*y) as sumXY FROM (SELECT UNIX_TIMESTAMP(trade_time) x, price y FROM stocks_trade WHERE trade_time >= DATE_SUB(curdate(), INTERVAL 1 DAY) AND symbol=%s) AS vl) AS sl) AS vls;", [s['symbol']]);
		for stat in stats:
			slope = stat.slope
			intercept = stat.intercept

		q = Market(update_date=date.today(), symbol=s['symbol'], price_avg=pa['price__avg'], price_stddev=ps['price__stddev'], size_avg=sa['size__avg'], size_stddev=ss['size__stddev'], price_slope=slope, price_intercept=intercept)
		q.save()

def predictFuturePrice(date, symbol, timestamp):
	pass