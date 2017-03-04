from django.shortcuts import render
from django.utils import timezone
from django.db import connection
from django.conf import settings
from stocks.models import Trade
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

		with connection.cursor() as cursor:
			cursor.execute("LOAD DATA INFILE %s INTO TABLE stocks_trade FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 LINES (trade_time,buyer,seller,price,size,currency,symbol,sector,bid,ask) SET id = NULL, checked = False;", [path])
				
	return redirect(reverse('stocks:index'))

def index(request):
	if request.POST and request.FILES:
		return read_file(request)
	else:
		latest_stock_list = Trade.objects.order_by('symbol', 'sector', '-trade_time')[:1000]
		symbolPointer = ""
		sectorPointer = ""
		htmlString = ""
		for stock in latest_stock_list:
			if symbolPointer == stock.symbol:
				if sectorPointer == stock.sector:
					htmlString += "<li>" + stock.__str__() + "</li>"
				else:
					htmlString += "</ul></li><li>" + stock.sector + "<ul><li>" + stock.__str__() + "</li>"
			else:
				if symbolPointer == "":
					htmlString += "<ul class='treeview'><li>" + stock.symbol + "<ul><li>" + stock.sector + "<ul><li>" + stock.__str__() + "</li>"
				else:
					htmlString += "</ul></li></ul></li><li>" + stock.symbol + "<ul><li>" + stock.sector + "<ul><li>" + stock.__str__() + "</li>"

			symbolPointer = stock.symbol
			sectorPointer = stock.sector

		htmlString += "</ul></li></ul></li></ul>"

		context = {
			'latest_stock_list': latest_stock_list,
			'htmlString': htmlString,
		}

		return render(request, 'stocks/index.html', context)