from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse
from django.db import connection
from django.conf import settings
from stocks.models import Trade, Alert, Market, Company
from stocks.charts import simple, candle
from stocks.tasks import importCSV
from django.http import HttpResponse
import datetime
import csv
import codecs
import time
import decimal
from datetime import timedelta
from django.core import serializers

# Create your views here.

def read_file(request):
	if request.POST and request.FILES:
		uploaded_file = request.FILES['csv_file']
		# File is temporarely uploaded

		# Write the file to disk in chunks
		fout = open("files/%s" % uploaded_file.name, 'wb')
		for chunk in uploaded_file.chunks():
			fout.write(chunk)
		fout.close()

		path = settings.PROJECT_ROOT + "/files/%s" % uploaded_file.name

		importCSV.delay(path);

	return redirect(reverse('index'))

def read_alerts(request):
	s = serializers.serialize("json", Alert.objects.filter(resolved=False))
	return HttpResponse(s)

def predict_future(request):
	if request.POST:
		symbol = request.POST['symbol']
		future = request.POST['date']
		if 'hist' in request.POST:
			hist = datetime.datetime.strptime(request.POST['hist'], "%d/%m/%Y")
		else:
			hist = datetime.datetime.now() + datetime.timedelta(days=1)

	market = Market.get_closest_to(hist, symbol);
	ftpc = time.mktime(datetime.datetime.strptime(future, "%d/%m/%Y").timetuple())

	y = market.price_slope * decimal.Decimal(ftpc) + market.price_intercept

	# s = serializers.serialize("json")
	return HttpResponse(y)

def index(request):
	if request.POST and request.FILES:
		return read_file(request)
	else:
		latest_stock_list = Company.objects.values_list('sector', flat=True).distinct()

	context = {
		'latest_stock_list': latest_stock_list,
		'index': True
	}

	return render(request, 'stocks/index.html', context)

def stock(request, sectorName, symbolName):
	if request.POST and request.FILES:
		return read_file(request)
	else:

		if 'hist' in request.POST:
			hist = datetime.datetime.strptime(request.POST['hist'], "%d/%m/%Y")
			hist_send = request.POST['hist']
		else:
			hist = datetime.datetime.now()
			hist_send = datetime.date.today().strftime("%d/%m/%Y")


		latest_stock_list = Trade.objects.filter(symbol=symbolName, trade_time__lte = hist + datetime.timedelta(days=1)).order_by('-trade_time')[:500000]
		#latest_stock_list = latest_stock_list.filter(symbol=symbolName, trade_time__lte = hist + datetime.timedelta(days=1))
		#latest_stock_list = latest_stock_list.order_by('-trade_time')[:10000]

		#chart = simple(request, latest_stock_list)
		chart = candle(request, latest_stock_list)

		latest_stock_list = Trade.objects.filter(symbol=symbolName, trade_time__lte = hist + datetime.timedelta(days=1)).order_by('-trade_time')[:1000]
		releated_alerts = Alert.objects.filter(symbol=symbolName).order_by('-id')
		count = Trade.objects.filter(symbol=symbolName, trade_time__lte = hist + datetime.timedelta(days=1)).count()

		mrk = Market.get_closest_to(hist + datetime.timedelta(days=1), symbolName);



		context = {
			'stockName' : symbolName,
			'sectorName' : sectorName,
			'latest_stock_list': latest_stock_list,
			'chart': chart,
			'releated_alerts': releated_alerts,
			'count': count,
			'price': mrk.price_avg,
			'volume': mrk.size_avg,
			'hist': hist_send,
		}

		return render(request, 'stocks/index.html', context)

def sector(request, sectorName):
	if request.POST and request.FILES:
		return read_file(request)
	else:
		latest_stock_list = Company.objects.filter(sector=sectorName).order_by().values_list('symbol', flat=True).distinct()
		#latest_stock_list = latest_stock_list.values_list('symbol', flat=True).distinct()

	context = {
		'stockName' : sectorName,
		'latest_stock_list': latest_stock_list,
	}

	return render(request, 'stocks/index.html', context)

def alerts(request):
	if request.POST and request.FILES:
		return read_file(request)
	else:
		alerts_list = Alert.objects.filter(resolved=0).order_by('-id')
		prev_false = Alert.objects.filter(resolved=1, false_alarm=1).order_by('-id')
		prev_serious = Alert.objects.filter(resolved=1, false_alarm=0).order_by('-id')

	context = {
		'alertsList' : alerts_list,
		'prevFalse' : prev_false,
		'prevSerious' : prev_serious,
	}

	return render(request, 'stocks/index.html', context)

def alert(request, alertId):
	if request.POST and request.FILES:
		return read_file(request)
	
	solution = "none"

	if request.POST:
		if 'solution' in request.POST:
			solution = request.POST['solution']

	alert = Alert.objects.get(id=alertId)

	if solution == "resolve":
		alert.resolved = 1
		alert.false_alarm = 0
	elif solution == "falsealarm":
		alert.resolved = 1
		alert.false_alarm = 1
	elif solution == "unresolve":
		alert.resolved = 0
	
	alert.save()


	if (alert.symbol):
		mrk = Market.get_closest_to(alert.occur_date + datetime.timedelta(days=1), alert.symbol);
	else :
		mrk = None
	context = {
		'alert' : alert,
		'trade' : alert.trade,
		'market' : mrk,
	}

	return render(request, 'stocks/index.html', context)