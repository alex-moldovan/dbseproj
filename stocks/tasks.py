# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from stocks.models import Trade, Market, Alert, Company
from django.db.models import Avg, StdDev, Count, Min, Max
from datetime import date, timedelta, datetime
from django.db import connection

import socket
import csv
import codecs
import time

FF_PRC_AVG_FACT = 5
FF_PRC_DEV_FACT = 20
FF_SZE_AVG_FACT = 5
FF_SZE_DEV_FACT = 20
FF_BID_AVG_FACT = 5
FF_BID_DEV_FACT = 20
FF_ASK_AVG_FACT = 5
FF_ASK_DEV_FACT = 20
VS_FACT = 2
PD_DAY_LIM = 50
PD_FLC_UB = 1.5
PD_FLC_LB = 0.7

@shared_task
def importCSV(path):
	with connection.cursor() as cursor:
		cursor.execute("LOAD DATA LOCAL INFILE %s INTO TABLE stocks_trade FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 LINES (trade_time,buyer,seller,price,size,currency,symbol,sector,bid,ask) SET id = NULL, checked = False;", [path])

	tr = Trade.objects.filter(checked = 0)
	time = tr[0].trade_time

	if Trade.objects.filter(checked = 0).count() > 500000:
		updatemarketimport()

	for trade in tr:
		trade.checked = True
		detectAnomalies(trade.id)
		trade.save()

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
					detectAnomalies.delay(q.id, None)

	#target.close()
	sock.close()

def validateTime(trade_time):
	try:
		tt = datetime.strptime(trade_time, "%Y-%m-%d %H:%M:%S.%f")
	except ValueError:
		return False
	return True

@shared_task
def detectAnomalies(tradeid, stats = None):
	tr = Trade.objects.get(id=tradeid)
	detectFatFinger(tr, stats)

def sendAlert(tr, problem, market = None):
	q = Alert(trade=tr, market=market, occur_date=tr.trade_time, symbol=tr.symbol, sector=tr.sector, anomaly=problem, resolved=False)
	print("new alert")
	q.save()

@shared_task
def updatecompanies():
	symbols = Trade.objects.values('symbol').distinct()
	for s in symbols:
		trade = Trade.objects.filter(symbol=s['symbol'])[0]
		company = Company(symbol=trade.symbol, sector=trade.sector)
		company.save()
	#Delete invalid objects
	Company.objects.filter(sector="").delete()

def updatemarketimport():
	# Get all symbols
	symbols = Trade.objects.values('symbol').distinct()
	for s in symbols:
		comp = Company.objects.get(symbol=s['symbol'])

		tl = Trade.objects.filter(symbol=s['symbol'], checked=0).values_list('id', flat=True).order_by('-id')
		tll = list(tl)

		newtrade = Trade.objects.filter(symbol=s['symbol'], checked=0).order_by('-id')[0]

		pa = Trade.objects.filter(pk__in = tll, symbol=s['symbol']).aggregate(Avg('price'))
		ps = Trade.objects.filter(pk__in = tll, symbol=s['symbol']).aggregate(StdDev('price'))
		sa = Trade.objects.filter(pk__in = tll, symbol=s['symbol']).aggregate(Avg('size'))
		ss = Trade.objects.filter(pk__in = tll, symbol=s['symbol']).aggregate(StdDev('size'))

		stats = Trade.objects.raw("SELECT 1 as id, slope, (vls.meanY - vls.slope*vls.meanX) as intercept FROM (SELECT ((sl.n*sl.sumXY - sl.sumX*sl.sumY) / (sl.n*sl.sumXX - sl.sumX*sl.sumX)) AS slope, sl.meanY as meanY, sl.meanX as meanX FROM (SELECT COUNT(y) as n, AVG(x) as meanX, SUM(x) as sumX, SUM(x*x) as sumXX, AVG(y) as meanY, SUM(y) as sumY, SUM(y*y) as sumYY, SUM(x*y) as sumXY FROM (SELECT UNIX_TIMESTAMP(trade_time) x, price y FROM stocks_trade WHERE symbol=%s AND checked=0 ORDER BY x DESC LIMIT 100000) AS vl) AS sl) AS vls;", [s['symbol']]);
		for stat in stats:
			slope = stat.slope
			intercept = stat.intercept

		q = Market(update_date=newtrade.trade_time, symbol=s['symbol'], sector=comp.sector, price_avg=pa['price__avg'], price_stddev=ps['price__stddev'], size_avg=sa['size__avg'], size_stddev=ss['size__stddev'], price_slope=slope, price_intercept=intercept)
		q.save()


@shared_task
def updatemarket():
	# Get all symbols
	symbols = Trade.objects.values('symbol').distinct()
	for s in symbols:
		yesterday = datetime.today() - timedelta(days=1)
		comp = Company.objects.get(symbol=s['symbol'])

		tl = Trade.objects.filter(symbol=s['symbol']).values_list('id', flat=True).order_by('-id')[:50000]
		tll = list(tl)

		pa = Trade.objects.filter(pk__in = tll, symbol=s['symbol']).aggregate(Avg('price'))
		ps = Trade.objects.filter(pk__in = tll, symbol=s['symbol']).aggregate(StdDev('price'))
		sa = Trade.objects.filter(pk__in = tll, symbol=s['symbol']).aggregate(Avg('size'))
		ss = Trade.objects.filter(pk__in = tll, symbol=s['symbol']).aggregate(StdDev('size'))

		stats = Trade.objects.raw("SELECT 1 as id, slope, (vls.meanY - vls.slope*vls.meanX) as intercept FROM (SELECT ((sl.n*sl.sumXY - sl.sumX*sl.sumY) / (sl.n*sl.sumXX - sl.sumX*sl.sumX)) AS slope, sl.meanY as meanY, sl.meanX as meanX FROM (SELECT COUNT(y) as n, AVG(x) as meanX, SUM(x) as sumX, SUM(x*x) as sumXX, AVG(y) as meanY, SUM(y) as sumY, SUM(y*y) as sumYY, SUM(x*y) as sumXY FROM (SELECT UNIX_TIMESTAMP(trade_time) x, price y FROM stocks_trade WHERE symbol=%s ORDER BY x DESC LIMIT 100000) AS vl) AS sl) AS vls;", [s['symbol']]);
		for stat in stats:
			slope = stat.slope
			intercept = stat.intercept

		q = Market(update_date=datetime.now(), symbol=s['symbol'], sector=comp.sector, price_avg=pa['price__avg'], price_stddev=ps['price__stddev'], size_avg=sa['size__avg'], size_stddev=ss['size__stddev'], price_slope=slope, price_intercept=intercept)
		q.save()


def predictFuturePrice(date, symbol, timestamp):
	pass

def detectFatFinger(tr, stats = None):
	stats = Market.objects.filter(symbol=tr.symbol).latest('id')
	price_dev = abs(tr.price - stats.price_avg)
	size_dev = abs(tr.size - stats.size_avg)
	bid_dev = abs(tr.bid - stats.price_avg)
	ask_dev = abs(tr.ask - stats.price_avg)

	# Check price deviation
	if float(price_dev) > (stats.price_stddev * FF_PRC_DEV_FACT) or float(price_dev) < (stats.price_stddev / FF_PRC_DEV_FACT):
		sendAlert(tr,"fatfinger-price-dev")

	# Check price
	if float(tr.price) > (stats.price_avg * FF_PRC_AVG_FACT) or float(tr.price) < (stats.price_avg / FF_PRC_AVG_FACT):
		sendAlert(tr,"fatfinger-price-avg")

	# Check size deviation
	if float(size_dev) > (stats.size_stddev * FF_SZE_DEV_FACT) or float(size_dev) < (stats.size_stddev / FF_SZE_DEV_FACT):
		sendAlert(tr,"fatfinger-size-dev")

	# Check size
	if int(tr.size) > (stats.size_avg * FF_SZE_AVG_FACT) or int(tr.size) < (stats.size_avg / FF_SZE_AVG_FACT):
		sendAlert(tr,"fatfinger-size-avg")

	# Check bid deviation
	if float(bid_dev) > (stats.price_stddev * FF_BID_DEV_FACT) or float(bid_dev) < (stats.price_stddev / FF_BID_DEV_FACT):
		sendAlert(tr,"fatfinger-bid-dev")

	# Check bid
	if float(tr.bid) > (stats.price_avg * FF_BID_AVG_FACT) or float(tr.bid) < (stats.price_avg / FF_BID_AVG_FACT):
		sendAlert(tr,"fatfinger-bid-avg")

	# Check ask deviation
	if float(ask_dev) > (stats.price_stddev * FF_ASK_DEV_FACT) or float(ask_dev) < (stats.price_stddev / FF_ASK_DEV_FACT):
		sendAlert(tr,"fatfinger-ask-dev")

	# Check ask
	if float(tr.ask) > (stats.price_avg * FF_ASK_AVG_FACT) or float(tr.ask) < (stats.price_avg / FF_ASK_AVG_FACT):
		sendAlert(tr,"fatfinger-ask-avg")


'''
	! For each market entry also store the average daily size and current day's
	  cumulative size, as volume spike analysis is done on stocks traded in a
	  day, not in an individual trade.

	This function should be called once every 4 hours or so, and it should
	check for each symbol if the cumulative size for that day so far is
	anomalous compared to the average daily size, e.g. it's 2x higher/lower.
'''

'''
	! For each market entry also store the average daily size and current day's
	  cumulative size, as volume spike analysis is done on stocks traded in a
	  day, not in an individual trade.

	This function should be called once every 4 hours or so, and it should
	check for each symbol if the cumulative size for that day so far is
	anomalous compared to the average daily size, e.g. it's 2x higher/lower.
'''
def detectVolumeSpike():
	market = Market.objects.all()
	sectors = Sector.objects.all()
	today = datetime.today()
	prev_time = today - timedelta(hours=4)

	for sector in sectors:
		new_size = Trade.objects.filter(trade_time__gte=prev_time, sector=sector['name']).aggregate(Avg('size'))
		sector.current_day_size += new_size

	for stock in market:
		new_size = Trade.objects.filter(trade_time__gte=prev_time, symbol=stock['symbol']).aggregate(Avg('size'))
		stock.current_day_size += new_size

	# check for volume spikes in the updated data
	for stock in market:
		if stock.day_size_avg == 0:
			continue

		# volume spikes can go both ways
		if stock.current_day_size > (stock.day_size_avg * VS_FACT) or stock.current_day_size < (stock.day_size_avg * VS_FACT):
			# pick a random trade with the respective symbol, as this is the
			# only relevant data for this anomaly type
			tr = Trade.objects.filter(symbol=stock.symbol)[0]
			sendAlert(tr,"volume-spike-stock")

	for sector in sectors:
		if sector.day_size_avg == 0:
			continue

		if sector.current_day_size > (sector.day_size_avg * VS_FACT) or sector.current_day_size < (sector.day_size_avg * VS_FACT):
			tr = Trade.objects.filter(sector=sector.name)[0]
			sendAlert(tr, "volume-spike-sector")

	# if it's midnight, update the averages and reset the daily stats
	if today.hour > 0 and today.hour < 1:
		for stock in market:
			stock.day_size_avg = (stock.day_size_avg * stock.days + stock.current_day_size) / float(stock.days + 1)
			stock.days += 1
			stock.current_day_size = 0
		for sector in sectors:
			sector.day_size_avg = (sector.day_size_avg * sector.days + sector.current_day_size) / float(sector.days + 1)
			sector.days += 1
			sector.current_day_size = 0

'''
	! For each market entry store three more values:
	  - sda_price_avg - starting day's price average
	  - fluctuation - by what factor the average daily price has increased;
	    if 0, the average price on that day will be taken as the starting value
	  - anomalous_high - flag that tracks if the average daily price fluctuates
	    past a certain amount, e.g. it grows past 1.5x; if this flag is set to
	    True and the price goes down to 0.7x or so, then a pump and dump could
	    have occurred.
	  - pd_track_days - how many days the price fluctuation has been tracked
	    for; if it exceeds a certain amount, e.g. 50, reset the fluctuation and
		the flag, and consider that day's average as the new starting value.

	This function should be called once a day, preferably when the live feed
	goes down, so it can analyse the average prices for that day. Bids and asks
	should revolve around the market price, so only the price is taken into
	consideration here.
'''
def detectPumpDump():
	market = Market.objects.all()
	yesterday = datetime.today() - timedelta(days=1)

	for stock in market:
		# if needed, reset the values and restart the P & D analysis
		if stock.fluctuation == 0 or stock.pd_track_days > PD_DAY_LIM:
			anomalous_high = False
			pd_track_days = 0
		else:
			stock.fluctuation = price_avg / sda_price_avg
			# if the price gets too high, set the flag to True in order to
			# signal a P & D if it drops too much later on; also refresh
			# pd_track_days so as to not lose track of the possible dump
			if stock.fluctuation > PD_FLC_UB:
				anomalous_high = True
				pd_track_days = 0
			# if the price has dropped significantly after hitting an unusual
			# high, it is most likely a P & D, so send an alert
			elif stock.fluctuation < PD_FLC_LB and anomalous_high == True:
				# pick a random trade with the respective symbol, as this is the
				# only relevant data for this anomaly type
				tr = Trade.objects.filter(symbol=stock.symbol)[0]
				sendAlert(tr,"pump-and-dump")


'''
	Call this function with the name of a problem and -1 or 1, to adjust its
	corresponding factor.
	For example, if a false positive has been given for a fat finger price
	difference from the average, call adjustFactor("fatfinger-price-avg", 1)
	to increase the bounds, so that the system won't give as many false
	positives later on.
'''
def adjustFactor(error_type, adj_type):
	if error_type == 'fatfinger-price-avg':
		FF_PRC_AVG_FACT += FF_PRC_AVG_FACT * 0.1 * adj_type
	elif error_type == 'fatfinger-price-dev':
		FF_PRC_DEV_FACT += FF_PRC_DEV_FACT * 0.1 * adj_type
	elif error_type == 'fatfinger-size-avg':
		FF_SZE_AVG_FACT += FF_SZE_AVG_FACT * 0.1 * adj_type
	elif error_type == 'fatfinger-size-dev':
		FF_SZE_DEV_FACT += FF_SZE_DEV_FACT * 0.1 * adj_type
	elif error_type == 'fatfinger-bid-avg':
		FF_BID_AVG_FACT += FF_BID_AVG_FACT * 0.1 * adj_type
	elif error_type == 'fatfinger-bid-dev':
		FF_BID_DEV_FACT += FF_BID_DEV_FACT * 0.1 * adj_type
	elif error_type == 'fatfinger-ask-avg':
		FF_ASK_AVG_FACT += FF_ASK_AVG_FACT * 0.1 * adj_type
	elif error_type == 'fatfinger-ask-dev':
		FF_ASK_DEV_FACT += FF_ASK_DEV_FACT * 0.1 * adj_type
	elif error_type == 'volume-spike':
		VS_FACT += VS_FACT * 0.1 * adj_type
	elif error_type == 'pump-and-dump':
		PD_FLC_LB += PD_FLC_LB * 0.1 * adj_type
		PD_FLC_UB += PD_FLC_UB * 0.1 * adj_type
		PD_DAY_LIM += PD_DAY_LIM * 0.1 * adj_type
