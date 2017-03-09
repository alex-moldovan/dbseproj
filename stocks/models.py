from django.db import models

# Create your models here.

class Trade(models.Model):
	trade_time = models.DateTimeField(db_index=True)
	buyer = models.EmailField()
	seller = models.EmailField()
	price = models.DecimalField(max_digits=7, decimal_places=2)
	size = models.IntegerField(default=0)
	currency = models.CharField(max_length=3)
	symbol = models.CharField(db_index=True, max_length=10)
	sector = models.CharField(db_index=True, max_length=50)
	bid = models.DecimalField(max_digits=7, decimal_places=2)
	ask = models.DecimalField(max_digits=7, decimal_places=2)
	checked = models.BooleanField()

	def __str__(self):
		return '%s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s' % (self.trade_time, self.buyer, self.seller, self.price, self.size, self.currency, self.symbol, self.sector, self.bid, self.ask, self.checked)

class Market(models.Model):
	update_date = models.DateField(db_index=True)
	symbol = models.CharField(db_index=True, max_length=10)
	price_avg = models.DecimalField(max_digits=7, decimal_places=2)
	price_stddev = models.DecimalField(max_digits=7, decimal_places=2)
	size_avg = models.IntegerField(default=0)
	size_stddev = models.IntegerField(default=0)
	price_slope = models.DecimalField(default=0, max_digits=10, decimal_places = 9)
	price_intercept = models.DecimalField(default=0, max_digits=10, decimal_places = 2)
	day_size_avg = models.IntegerField(default=0)
	current_day_size = models.IntegerField(default=0)
	tda_price_avg = models.DecimalField(default=0, max_digits=7, decimal_places=2)
	sda_price_avg = models.DecimalField(default=0, max_digits=7, decimal_places=2)
	fluctuation = models.DecimalField(default=0, max_digits=10, decimal_places=9)
	anomalous_high = models.BooleanField(default=False)
	pd_track_days = models.IntegerField(default=0)

	def __str__(self):
		return "id: %d, d: %s, s: %s, pa: %f, ps: %f, sa: %d, ss: %d" % (self.id, self.update_date, self.symbol, self.price_avg, self.price_stddev, self.size_avg, self.size_stddev)

class Alert(models.Model):
	trade = models.ForeignKey(
		'Trade',
		on_delete=models.CASCADE,
		null=True,
	)
	occur_date = models.DateField(db_index=True)
	symbol = models.CharField(db_index=True, max_length=50, null=True)
	sector = models.CharField(db_index=True, max_length=50, null=True)
	category = models.CharField(max_length=50)
	anomaly = models.CharField(max_length=50)
	resolved = models.BooleanField()