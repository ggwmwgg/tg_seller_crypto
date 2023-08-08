import math
import random
import string

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from data.config import admins
from keyboards.inline import m_m_inline
from states.main import Main

from utils.db_api.models import Country, Product, DeliveryMethod, Category, Stock, User, Order, Image
from utils.wallet import get_ltc_price_async


async def add_backslashes(text: str) -> str:
    """
    Adds backslashes to a string.

    :param text: The string to add backslashes to.
    :return: The string with backslashes.
    """
    text = text.replace('.', '\.')
    text = text.replace('(', '\(')
    text = text.replace(')', '\)')
    text = text.replace('-', '\-')
    text = text.replace('!', '\!')
    text = text.replace('+', '\+')
    text = text.replace('=', '\=')
    text = text.replace('#', '\#')
    text = text.replace('|', '\|')
    return text


async def add_backslash(num: float) -> str:
    """
    Adds a backslash to a number before the decimal point.

    :param num: The number to add a backslash to, as a float.
    :return: The number with a backslash, as a string.
    """
    num_str = str(num)
    decimal_index = num_str.find('.')
    if decimal_index != -1:
        return num_str[:decimal_index] + '\\' + num_str[decimal_index:]
    else:
        return num_str


async def create_m_m_text(user: User, text: str) -> str:
    """
    Creates a text for the main menu.

    :param user: The user to create the text for.
    :param text: The text to add to the main menu.
    :return: The text for the main menu.
    """
    balance = await get_ltc_price_async(user.balance)
    balance = math.ceil(balance * 1000) / 1000
    balance = await add_backslash(balance)
    full = await add_backslashes(user.full_name)
    text_before = (f"Hello, *{full}*\!\n\n"
                   f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                   f"Your ID: {user.tg_id}\n"
                   f"Balance: *${user.balance}*  \(\~{balance} LTC\)\n")
    if user.coupon > 0:
        text_mid = f"Coupon: ${user.coupon}\n"
    else:
        text_mid = ""

    text_after = f"Orders: {user.orders_no}\n\n" \
                 f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n" \
                 f"{text}"
    return text_before + text_mid + text_after


async def add_percentage(num: int, percentage: float) -> float:
    """
    Adds a percentage to a number.

    :param num: A number to add a percentage to.
    :param percentage: The percentage to add.
    :return: The number with the percentage added.
    """
    return num + (num * percentage)


async def open_image_async(path: str) -> bytes:
    """
    Opens an image from the images folder.

    :param path: The path to the image.
    :return: The image as bytes.
    """
    with open(f"utils/images/{path}", 'rb') as file:
        return file.read()


async def save_image_async(path: str, image: bytes) -> None:
    """
    Saves an image to the images folder.

    :param path: The path to save the image to.
    :param image: The image to save.
    :return: None
    """
    with open(f"utils/images/{path}", 'wb') as file:
        file.write(image)


async def check_image_name(name: str) -> bool:
    """
    Checks if the image name is valid.

    :param name: The name of the image.
    :return: True if the name is valid, False otherwise.
    """
    if name.endswith('.jpg') or name.endswith('.png'):
        return True
    else:
        return False


async def generate_random_string() -> str:
    """
    Generates a random string.

    :return: The random string.
    """
    str_new = ''.join(random.choice(string.ascii_letters) for i in range(18))
    return str_new + ".jpg"


async def send_to_mm(query: types.CallbackQuery, user: User, state: FSMContext, txt: str):
    """
    Sends the user to the main menu.

    :param query: Received callback query.
    :param user: The user to send to the main menu.
    :param state: The state of the user.
    :param txt: The text to add to the main menu.
    :return: None
    """
    keyboard = await m_m_inline()
    text = await create_m_m_text(user, f"{txt}_Where to go?_")

    await query.message.edit_caption(
        caption=text,
        parse_mode=types.ParseMode.MARKDOWN_V2,
        reply_markup=keyboard
    )
    await state.reset_data()
    await Main.main.set()


async def create_order_m_text(order: Order, status: str) -> str:
    """
    Creates a text for the order menu.
    :param order: Order to create the text for.
    :param status: Status of the order.
    :return: The text for the order menu.
    """
    order_type = "Digital" if order.type == 0 else "Preorder" if order.type == 1 else "Deposit"
    if order.type == 2:

        text_main = (f"*Order: \#{order.id}*\n\n"
                     f"Type: *{order_type}*\n"
                     f"Status: *{status}*\n"
                     f"Deposit amount: *${order.to_balance}*\n\n"
                     f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n")
    else:

        product = await order.product
        cat = await product.category
        d_method = await product.d_method
        country = await product.country
        d_type_name = (lambda t: {1: "Online", 2: "Express", 3: "Courier"}.get(t, "Preorder"))(product.d_type)
        text_main = (f"*Order: \#{order.id}*\n\n"
                     f"Type: *{order_type}*\n"
                     f"Status: *{status}*\n"
                     f"Product: *{cat.name} {await add_backslash(product.quantity)} \({d_type_name}\)*\n"
                     f"Country: *{country.name}*\n"
                     f"Delivery method: *{d_method.name}*\n\n"
                     f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n")
    return text_main


async def create_order_b_text(order: Order, user: User) -> str:
    """
    Creates a text for the order menu (in the end).

    :param order: Order to create the text for.
    :param user: User to create the text for.
    :return: The text for the order menu.
    """
    if order.withdrawn:
        adm_text = (f"User: *@{user.username}*\n"
                    f"Withdrawn: *Yes*\n"
                    f"TXID: *`{order.seed_old}`*\n\n")
    else:
        adm_text = (f"User: *@{user.username}*\n"
                    f"Witdrawn: *No*\n"
                    f"Wallet: *`{order.wallet_old}`*\n"
                    f"Seed: *{order.seed_old}*\n\n")
    return adm_text


async def send_product_images(dp, product_id: int, chat_id: int, txt: str = "", send_admins: bool = False):
    """
    Sends the product images to the user.
    :param dp: Dispatcher.
    :param product_id: Product id.
    :param chat_id: Chat id.
    :param txt: Text to send with the images.
    :param send_admins: Whether to send the images to the admins.
    :return: None
    """
    product = await Product.get(id=product_id).prefetch_related('images')
    media = types.MediaGroup()
    if txt == "":
        txt = product.description
    for i, image in enumerate(product.images):
        input_file = types.InputFile(f"utils/images/{image.url}")
        if i == 0:
            media.attach_photo(input_file, caption=txt, parse_mode=types.ParseMode.MARKDOWN_V2)
        else:
            media.attach_photo(input_file)
    if not send_admins:
        await dp.bot.send_media_group(chat_id, media)
    else:
        for admin in admins:
            try:
                await dp.bot.send_media_group(admin, media)
            except Exception as err:
                pass


async def get_showcase(types_s: bool = True, all_i: bool = True) -> str:
    """
    Gets the showcase text.
    :param types_s: Whether to show digital (True) or preorders (False).
    :param all_i: Whether to show all products (True) or only the ones with quantity (False).
    :return: The showcase text.
    """
    countries = await Country.filter(stocks__isnull=False, stocks__type=types_s).distinct().order_by("-name").values("id",
                                                                                                                  "name")
    txt = "*Showcase:*\n\n"
    for country in countries:
        txt = txt + f"_- {country['name']}:_\n"
        d_methods = await DeliveryMethod.filter(country__name=country["name"], stocks__type=types_s).distinct().values(
            "id", "name")
        for method in d_methods:
            txt = txt + f"_\n  - {method['name']}:_\n\n"
            categories = await Category.filter(
                stocks__country_id=country["id"],
                stocks__d_method_id=method["id"],
                stocks__type=types_s
            ).distinct().order_by("name").values("id", "name")
            for category in categories:
                stock_quantities = await Stock.filter(
                    product__category_id=category["id"],
                    country_id=country["id"],
                    d_method_id=method["id"],
                    type=types_s
                ).distinct().values("product_id", "quantity")

                stock_quantities_list = []
                for stock_quantity in stock_quantities:
                    if not all_i:
                        if stock_quantity["quantity"] not in stock_quantities_list:
                            price = await Product.get(id=stock_quantity["product_id"])
                            txt = txt + f"*    - {category['name']} {stock_quantity['quantity']} (${price.price})*\n"
                            stock_quantities_list.append(stock_quantity["quantity"])
                    else:
                        price = await Product.get(id=stock_quantity["product_id"])
                        txt = txt + f"*    - {category['name']} {stock_quantity['quantity']} (${price.price})*\n"

    txt = await add_backslashes(txt)
    return txt


async def user_profile_acp(user: User, txt: str = "_Choose an action:_") -> str:
    """
    Creates a text for the user profile menu.

    :param user: User to create the text for.
    :param txt: Text to send with the menu.
    :return: The text for the user profile menu.
    """
    text = (f"User: *_`@{user.username}`_*\n\n"
            f"ID: *_{user.id}_*\n"
            f"Username: *_{user.full_name}_*\n"
            f"Balance: *_${user.balance}_*\n"
            f"Coupons: *_${user.coupon}_*\n"
            f"Orders: *_{user.orders_no}_*\n"
            f"Spent: *_${user.spent}_*\n"
            f"Role: *_{user.role}_*\n"
            f"Banned: *_{user.banned}_*\n"
            f"Registration date: *_{user.created_at}_*\n\n"
            f"{txt}")
    text = await add_backslashes(text)
    return text


async def get_stocks(stocks_type: bool = True, text: str = "\n_Choose an action:_") -> str:
    """
    Gets the stocks text.
    :param stocks_type: Whether to show digital (True) or preorders (False).
    :param text: Text to send with the stocks.
    :return: The stocks text.
    """
    if stocks_type:
        txt = "*Available digital products:*\n\n"
    else:
        txt = "*Available products in preorders:*\n\n"
    stocks = await Stock.filter(
        type=stocks_type
    ).all()
    for stock in stocks:
        category = await stock.category
        country = await stock.country
        d_method = await stock.d_method
        product = await stock.product
        txt += f"*{stock.id}. {category.name} ({stock.quantity}) ${product.price} | {stock.d_type} | {country.name} | {d_method.name}*\n"
        if stocks_type:
            txt += f"    - {product.description}\n\n"
    txt += text
    txt = await add_backslashes(txt)
    return txt


async def cat_method_country() -> str:
    """
    Shows available Product types, categories, countries and delivery methods.
    :return: The text.
    """
    categories = await Category.all()
    countries = await Country.all()
    d_methods = await DeliveryMethod.all()
    txt = "*P\_Types:*\n\n*1. Online*\n *2. Express*\n*3. Courier*\n*4. Preorder*\n\n"
    txt += "*Categories:*\n\n"
    for category in categories:
        txt += f"*{category.id}. {category.name}*\n"
    txt += "\n*Countries:*\n\n"
    for country in countries:
        txt += f"*{country.id}. {country.name}*\n"
    txt += "\n*Delivery methods:*\n\n"
    for d_method in d_methods:
        txt += f"*{d_method.id}. {d_method.name}*\n"
    txt = await add_backslashes(txt)
    return txt


async def get_preorders_list() -> str:
    """
    Gets the preorders list.
    :return: The preorders list.
    """
    orders = await Order.filter(
        status="delivery",
        type=1
    ).all()
    txt = "*List of active preorders:*\n\n"
    for order in orders:
        product = await order.product
        category = await product.category
        country = await product.country
        d_method = await product.d_method
        txt += f"*{order.id}. {category.name} ({product.quantity}) | {product.d_type} | {country.name} | {d_method.name}*\n"
        txt = await add_backslashes(txt)
    txt += "\n_Choose an order id to send:_"
    return txt


async def create_product_stock(message: types.Message, type_s: bool = True) -> Product:
    """
    Creates a product and a stock.
    :param message: Message to get the product info from.
    :param type_s: Whether the product is digital (True) or preorder (False).
    :return: The created product.
    """
    if type_s:
        split = message.caption.split(",")
    else:
        split = message.text.split(",")
    d_type = split[0]
    quantity = split[1]
    category = await Category.get(id=int(split[2]))
    country = await Country.get(id=int(split[3]))
    delivery_method = await DeliveryMethod.get(id=int(split[4]))
    price = split[5]
    description = split[6]
    p = await Product.create(
        description=description,
        country=country,
        category=category,
        quantity=quantity,
        type=type_s,
        d_method=delivery_method,
        d_type=d_type,
        price=price
    )
    await Stock.update_or_create(product=p, country=country, type=type_s, category=category,
                                 d_method=delivery_method, d_type=d_type, quantity=quantity)
    return p


async def add_photo(message, dp) -> Image:
    """
    Adds a photo to the database.

    :param message: Message to get the photo from.
    :param dp: Dispatcher.
    :return: The created image db object.
    """
    photo = message.photo[-1].file_id
    photo_name = await generate_random_string()
    path = f"utils/images/{photo_name}"
    await dp.bot.download_file_by_id(photo, path)
    image = await Image.create(url=photo_name)
    return image

