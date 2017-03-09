from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse
from django.db import connection
from django.conf import settings
from stocks.models import Trade
from stocks.charts import simple, candle
from stocks.tasks import importCSV
import csv
import codecs
import time

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

def index(request):
	if request.POST and request.FILES:
		return read_file(request)
	else:
		latest_stock_list = Trade.objects.values_list('sector', flat=True).distinct()

	context = {
		'latest_stock_list': latest_stock_list,
	}

	return render(request, 'stocks/index.html', context)

def stock(request, sectorName, symbolName):
	if request.POST and request.FILES:
		return read_file(request)
	else:
		latest_stock_list = Trade.objects.filter(symbol=symbolName).order_by('-trade_time')[:10000]
		#latest_stock_list = latest_stock_list.filter(symbol=symbolName)
		#latest_stock_list = latest_stock_list.order_by('-trade_time')[:10000]

		#chart = simple(request, latest_stock_list)
		chart = candle(request, latest_stock_list)

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
		latest_stock_list = Trade.objects.filter(sector=sectorName).order_by().values_list('symbol', flat=True).distinct()
		#latest_stock_list = latest_stock_list.values_list('symbol', flat=True).distinct()

	context = {
		'stockName' : sectorName,
		'latest_stock_list': latest_stock_list,
	}

	return render(request, 'stocks/index.html', context)
