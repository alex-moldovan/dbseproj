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
			hist = datetime.strptime(request.POST['hist'], "%m/%d/%y")
		else:
			hist = datetime.date.today() + datetime.timedelta(days=1)
			# datetime.strptime(request.POST['hist'], "%m/%d/%y")

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
	}

	return render(request, 'stocks/index.html', context)

def stock(request, sectorName, symbolName):
	if request.POST and request.FILES:
		return read_file(request)
	else:
		latest_stock_list = Trade.objects.filter(symbol=symbolName).order_by('-trade_time')[:100000]
		#latest_stock_list = latest_stock_list.filter(symbol=symbolName)
		#latest_stock_list = latest_stock_list.order_by('-trade_time')[:10000]

		#chart = simple(request, latest_stock_list)
		chart = candle(request, latest_stock_list)

		latest_stock_list = Trade.objects.filter(symbol=symbolName).order_by('-trade_time')[:1000]

		context = {
			'stockName' : symbolName,
			'sectorName' : sectorName,
			'latest_stock_list': latest_stock_list,
			'chart': chart,
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
		alerts_list = Alert.objects.filter(resolved=False)
		prev_false = Alert.objects.filter(resolved=True, false_alarm=True)
		prev_serious = Alert.objects.filter(resolved=True, false_alarm=False)

	context = {
		'alertsList' : alerts_list,
		'prevFalse' : prev_false,
		'prevSerious' : prev_serious,
	}

	return render(request, 'stocks/index.html', context)
