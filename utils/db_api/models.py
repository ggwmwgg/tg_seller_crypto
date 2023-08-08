from tortoise import Model, fields


class User(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.BigIntField()
    username = fields.CharField(max_length=50)
    full_name = fields.CharField(max_length=50)
    orders_no = fields.IntField(default=0)
    wallet = fields.CharField(max_length=128)
    seed = fields.TextField()
    balance = fields.IntField(default=0)
    spent = fields.FloatField(default=0.0)
    discount = fields.FloatField(default=0)
    coupon = fields.IntField(default=0)
    role = fields.CharField(max_length=50, default='user')
    banned = fields.BooleanField(default=False)
    false_orders = fields.IntField(default=0)
    used_coupons = fields.ManyToManyField('models.Coupons', related_name='users')
    active_order = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


    class Meta:
        table = "users"

    def __str__(self):
        return f'{self.id} | {self.tg_id} | {self.wallet} | {self.balance}'

    def __repr__(self):
        return self.__str__()


class Country(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)

    class Meta:
        table = "countries"

    def __str__(self):
        return f'{self.id} | {self.name}'

    def __repr__(self):
        return self.__str__()


class DeliveryMethod(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    country = fields.ForeignKeyField('models.Country', related_name='delivery_methods')
    class Meta:
        table = "delivery_methods"

    def __str__(self):
        return f'{self.id} | {self.name}'

    def __repr__(self):
        return self.__str__()


class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    description = fields.TextField()
    image = fields.ForeignKeyField('models.Image', related_name='categories')

    class Meta:
        table = "categories"

    def __str__(self):
        return f'{self.id} | {self.name}'

    def __repr__(self):
        return self.__str__()


class Image(Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=50)

    class Meta:
        table = "images"

    def __str__(self):
        return f'{self.id} | {self.url}'

    def __repr__(self):
        return self.__str__()


class Product(Model):
    id = fields.IntField(pk=True)
    images = fields.ManyToManyField(
        'models.Image',
        related_name='products',
        through='product_images',
        on_delete=fields.CASCADE
    )
    description = fields.TextField()
    country = fields.ForeignKeyField('models.Country', related_name='products')
    type = fields.BooleanField(default=True)  # True - digital, False - preorder
    category = fields.ForeignKeyField('models.Category', related_name='products')
    quantity = fields.FloatField()
    d_method = fields.ForeignKeyField('models.DeliveryMethod', related_name='products')
    d_type = fields.IntField(default=0)  # 1. Online 2. Express 3. Courier 4. Preorder
    price = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)


class Stock(Model):
    id = fields.IntField(pk=True)
    product = fields.ForeignKeyField('models.Product', related_name='stocks')
    country = fields.ForeignKeyField('models.Country', related_name='stocks')
    type = fields.BooleanField(default=True)  # True - digital, False - preorder
    category = fields.ForeignKeyField('models.Category', related_name='stocks')
    d_method = fields.ForeignKeyField('models.DeliveryMethod', related_name='stocks')
    d_type = fields.IntField(default=0)  # 1. Online 2. Express 3. Courier 4. Preorder
    quantity = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)


class Order(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='orders')
    product = fields.ForeignKeyField('models.Product', related_name='orders', null=True)
    type = fields.IntField(default=0)  # 0. Digital 1. Pre-order 2. Balance
    price = fields.FloatField()
    status = fields.CharField(max_length=50, default='none')
    withdrawn = fields.BooleanField(default=False)
    wallet_old = fields.CharField(max_length=256, null=True)
    seed_old = fields.TextField(null=True)
    message_id = fields.IntField(default=0)
    to_balance = fields.IntField(default=0.0)
    to_coupon = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)


class Coupons(Model):
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=50)
    amount = fields.IntField()
    usages_left = fields.IntField()
