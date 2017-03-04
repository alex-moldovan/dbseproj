from django.apps import AppConfig


class StocksConfig(AppConfig):
	name = 'stocks'
	verbose_name = "Stock Trades"
	def ready(self):
		from stocks.tasks import updatemarket, stocksfeed
		stocksfeed.delay()
		updatemarket.delay()