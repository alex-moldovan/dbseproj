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
	sector = models.CharField(max_length=10)
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

	def get_closest_to(target, symbol):
		closest_greater_qs = Market.objects.filter(symbol=symbol, update_date__gte=target).order_by('update_date')
		closest_less_qs    = Market.objects.filter(symbol=symbol, update_date__lt=target).order_by('-update_date')

		try:
			try:
				closest_greater = closest_greater_qs[0]
			except IndexError:
				return closest_less_qs[0]

			try:
				closest_less = closest_less_qs[0]
			except IndexError:
				return closest_greater_qs[0]
		except IndexError:
			raise self.model.DoesNotExist("There is no closest object"
										  " because there are no objects.")

		if closest_greater.update_date - target > target - closest_less.update_date:
			return closest_less
		else:
			return closest_greater

	def __str__(self):
		return "id: %d, d: %s, s: %s, pa: %f, ps: %f, sa: %d, ss: %d" % (self.id, self.update_date, self.symbol, self.price_avg, self.price_stddev, self.size_avg, self.size_stddev)

class Alert(models.Model):
	trade = models.ForeignKey(
		'Trade',
		on_delete=models.CASCADE,
		null=True,
	)
	market = models.ForeignKey(
		'Market',
		on_delete=models.CASCADE,
		null=True,
	)
	occur_date = models.DateField(db_index=True)
	symbol = models.CharField(db_index=True, max_length=50, null=True)
	sector = models.CharField(db_index=True, max_length=50, null=True)
	anomaly = models.CharField(max_length=50)
	resolved = models.BooleanField(default=False)
	false_alarm = models.BooleanField(default=False)

class Sector(models.Model):
	name = models.CharField(db_index=True, max_length=100)
	day_size_avg = models.IntegerField(default=0)
	current_day_size = models.IntegerField(default = 0)
	days = models.IntegerField(default=0)

class Company(models.Model):
	symbol = models.CharField(max_length=10, primary_key=True)
	sector = models.CharField(max_length=50)