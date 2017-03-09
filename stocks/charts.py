# file charts.py
from django.shortcuts import render
def simple(request, data):
    import random
    import django
    import datetime

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    import base64
    import io
    import matplotlib.pyplot as plt

    data=data[:1000]

    fig=Figure(figsize=(10,5))
    ax=fig.add_subplot(111)
    x=[]
    y=[]
    for row in data:
        x.append(row.trade_time)
        y.append(row.price)
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    #response=django.http.HttpResponse(content_type='image/png')
    #canvas.print_png(response)
    sio = io.BytesIO()
    fig.savefig(sio, format="png")
    return base64.encodebytes(sio.getvalue()).decode()

def candle(request, data):
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter, WeekdayLocator,\
        DayLocator, MONDAY
    from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc, candlestick2_ohlc
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    import base64
    import io
    from datetime import timedelta

    data = data.all().reverse()

    mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
    alldays = DayLocator()              # minor ticks on the days
    weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
    dayFormatter = DateFormatter('%d')      # e.g., 12


    if len(data) == 0:
        raise SystemExit

    #fig, ax = plt.subplots()
    #fig.subplots_adjust(bottom=0.2)
    fig=Figure(figsize=(10,5))
    ax=fig.add_subplot(111)
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)
    #ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    #ax.xaxis.set_minor_formatter(dayFormatter)

    #plot_day_summary(ax, quotes, ticksize=3)
    #candlestick_ohlc(ax, quotes, width=0.6)
    d = timedelta(minutes=45)

    startTime=""
    opens=()
    closes=()
    highs=()
    lows=()
    minPrice=0
    maxPrice=0

    for row in data:
        if startTime=="":
            startTime=row.trade_time
            opens+=(row.price,)
            minPrice=row.price
            maxPrice=row.price
        if minPrice > row.price:
            minPrice=row.price
        if maxPrice < row.price:
            maxPrice=row.price
        if row.trade_time > startTime + d:
            closes+=(row.price,)
            lows+=(minPrice,)
            highs+=(maxPrice,)
            startTime=""
    if startTime!="":
        closes+=(data.all().reverse()[0].price,)
        lows+=(minPrice,)
        highs+=(maxPrice,)

    #plot_day_summary(ax, quotes2, ticksize=3)
    #candlestick2_ohlc(ax, quotes2['opens'], quotes2['highs'], quotes2['lows'], quotes2['closes'], width=0.2, colorup='k', colordown='r', alpha=1.0)
    candlestick2_ohlc(ax, opens, highs, lows, closes, width=0.45)

    ax.xaxis_date()
    ax.autoscale_view()
    #fig.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    sio = io.BytesIO()
    fig.savefig(sio, format="png")
    #plt.show()
    return base64.encodebytes(sio.getvalue()).decode()
