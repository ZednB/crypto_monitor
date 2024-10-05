from tortoise import Model, fields


class CurrencyPair(Model):
    id = fields.IntField(pk=True)
    base_currency = fields.CharField(max_length=10)
    quote_currency = fields.CharField(max_length=10)

    def __str__(self):
        return f"{self.base_currency}/{self.quote_currency}"


class Price(Model):
    id = fields.IntField(pk=True)
    pair = fields.ForeignKeyField('models.CurrencyPair', related_name='prices')
    price = fields.DecimalField(max_digits=18, decimal_places=8)
    max_price = fields.DecimalField(max_digits=18, decimal_places=8, null=True)
    min_price = fields.DecimalField(max_digits=18, decimal_places=8, null=True)
    difference = fields.DecimalField(max_digits=10, decimal_places=6)
    date = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pair} - {self.price}"


class Holding(Model):
    id = fields.IntField(pk=True)
    pair = fields.ForeignKeyField('models.CurrencyPair', related_name='logs')
    total_amount = fields.DecimalField(max_digits=18, decimal_places=8)

    def __str__(self):
        return f"{self.pair} - {self.total_amount}"


class PriceChangeLog(Model):
    id = fields.IntField(pk=True)
    pair = fields.ForeignKeyField('models.CurrencyPair', related_name='price_logs')
    price = fields.DecimalField(max_digits=18, decimal_places=8)
    difference = fields.DecimalField(max_digits=10, decimal_places=6)
    date = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pair} - {self.difference} - {self.date}"
