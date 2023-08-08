import logging
from utils.db_api.models import Image, Category, Product, DeliveryMethod, Stock, Country


async def test_db_entries():
    logging.info("Adding test entries to DB")
    await Image.update_or_create(url="gtav.jpg")
    gta_v_logo = await Image.get(url="gtav.jpg")
    await Image.update_or_create(url="gtav_rockstar.jpg")
    gta_v_ingame_balance = await Image.get(url="gtav_rockstar.jpg")
    await Image.update_or_create(url="origin.png")
    origin_logo = await Image.get(url="origin.png")
    await Image.update_or_create(url="steam.jpg")
    steam_logo = await Image.get(url="steam.jpg")
    await Image.update_or_create(url="br2021_1.jpg")
    baby_roshan2021_1 = await Image.get(url="br2021_1.jpg")
    await Image.update_or_create(url="br2021_2.jpg")
    baby_roshan2021_2 = await Image.get(url="br2021_2.jpg")
    await Image.update_or_create(url="br_2022.jpg")
    baby_roshan2022 = await Image.get(url="br_2022.jpg")
    await Image.update_or_create(url="steam20_1_1.png")
    steam_20_1_1 = await Image.get(url="steam20_1_1.png")
    await Image.update_or_create(url="steam20_1_2.png")
    steam_20_1_2 = await Image.get(url="steam20_1_2.png")
    await Image.update_or_create(url="steam20_2_1.png")
    steam_20_2_1 = await Image.get(url="steam20_2_1.png")
    await Image.update_or_create(url="steam20_2_2.png")
    steam_20_2_2 = await Image.get(url="steam20_2_2.png")
    await Image.update_or_create(url="steam50_1_1.png")
    steam_50_1_1 = await Image.get(url="steam50_1_1.png")
    await Image.update_or_create(url="steam50_1_2.png")
    steam_50_1_2 = await Image.get(url="steam50_1_2.png")
    await Image.update_or_create(url="steam100_1_1.png")
    steam_100_1_1 = await Image.get(url="steam100_1_1.png")
    await Image.update_or_create(url="steam100_1_2.png")
    steam_100_1_2 = await Image.get(url="steam100_1_2.png")
    await Image.update_or_create(url="steam100_2_1.png")
    steam_100_2_1 = await Image.get(url="steam100_2_1.png")
    await Image.update_or_create(url="steam100_2_2.png")
    steam_100_2_2 = await Image.get(url="steam100_2_2.png")
    await Image.update_or_create(url="steam1000_1_1.png")
    steam_1000_1_1 = await Image.get(url="steam1000_1_1.png")
    await Image.update_or_create(url="steam1000_1_2.png")
    steam_1000_1_2 = await Image.get(url="steam1000_1_2.png")
    await Image.update_or_create(url="gtavjp_1.png")
    gta_v_jp_1 = await Image.get(url="gtavjp_1.png")
    await Image.update_or_create(url="gtavjp_2.png")
    gta_v_jp_2 = await Image.get(url="gtavjp_2.png")
    await Image.update_or_create(url="gtavus_1.png")
    gta_v_us_1 = await Image.get(url="gtavus_1.png")
    await Image.update_or_create(url="gtavus_2.png")
    gta_v_us_2 = await Image.get(url="gtavus_2.png")
    await Image.update_or_create(url="gtavru_1.png")
    gta_v_ru_1 = await Image.get(url="gtavru_1.png")
    await Image.update_or_create(url="gtavru_2.png")
    gta_v_ru_2 = await Image.get(url="gtavru_2.png")

    await Category.update_or_create(name="Steam", description="Steam", image=steam_logo)
    steam = await Category.get(name="Steam")
    await Category.update_or_create(name="Origin", description="Origin", image=origin_logo)
    origin = await Category.get(name="Origin")
    await Category.update_or_create(name="GTA V", description="GTA V", image=gta_v_logo)
    gta_v = await Category.get(name="GTA V")
    await Category.update_or_create(name="Baby Roshan 2021", description="Baby Roshan 2021", image=baby_roshan2021_1)
    baby_roshan_2021 = await Category.get(name="Baby Roshan 2021")
    await Category.update_or_create(name="Baby Roshan 2022", description="Baby Roshan 2022", image=baby_roshan2022)
    baby_roshan_2022 = await Category.get(name="Baby Roshan 2022")

    await Country.update_or_create(name="USA")
    usa = await Country.get(name="USA")
    await Country.update_or_create(name="Japan")
    japan = await Country.get(name="Japan")
    await Country.update_or_create(name="Russia")
    russia = await Country.get(name="Russia")
    await Country.update_or_create(name="China")
    china = await Country.get(name="China")

    await DeliveryMethod.update_or_create(name="Balance", country=usa)
    balance_usa = await DeliveryMethod.get(name="Balance", country=usa)
    await DeliveryMethod.update_or_create(name="Game Code", country=usa)
    game_code_usa = await DeliveryMethod.get(name="Game Code", country=usa)
    await DeliveryMethod.update_or_create(name="In-game Items", country=usa)
    in_game_items_usa = await DeliveryMethod.get(name="In-game Items", country=usa)
    await DeliveryMethod.update_or_create(name="In-game Balance", country=usa)
    in_game_balance_usa = await DeliveryMethod.get(name="In-game Balance", country=usa)
    await DeliveryMethod.update_or_create(name="Collectibles", country=usa)
    collectibles_usa = await DeliveryMethod.get(name="Collectibles", country=usa)

    await DeliveryMethod.update_or_create(name="Balance", country=japan)
    balance_japan = await DeliveryMethod.get(name="Balance", country=japan)
    await DeliveryMethod.update_or_create(name="Game Code", country=japan)
    game_code_japan = await DeliveryMethod.get(name="Game Code", country=japan)
    await DeliveryMethod.update_or_create(name="In-game Items", country=japan)
    in_game_items_japan = await DeliveryMethod.get(name="In-game Items", country=japan)
    await DeliveryMethod.update_or_create(name="In-game Balance", country=japan)
    in_game_balance_japan = await DeliveryMethod.get(name="In-game Balance", country=japan)
    await DeliveryMethod.update_or_create(name="Collectibles", country=japan)
    collectibles_japan = await DeliveryMethod.get(name="Collectibles", country=japan)

    await DeliveryMethod.update_or_create(name="Balance", country=russia)
    balance_ru = await DeliveryMethod.get(name="Balance", country=russia)
    await DeliveryMethod.update_or_create(name="Game Code", country=russia)
    game_code_ru = await DeliveryMethod.get(name="Game Code", country=russia)
    await DeliveryMethod.update_or_create(name="In-game Items", country=russia)
    in_game_items_ru = await DeliveryMethod.get(name="In-game Items", country=russia)
    await DeliveryMethod.update_or_create(name="In-game Balance", country=russia)
    in_game_balance_ru = await DeliveryMethod.get(name="In-game Balance", country=russia)
    await DeliveryMethod.update_or_create(name="Collectibles", country=russia)
    collectibles_ru = await DeliveryMethod.get(name="Collectibles", country=russia)

    await DeliveryMethod.update_or_create(name="Balance", country=china)
    balance_cn = await DeliveryMethod.get(name="Balance", country=china)
    await DeliveryMethod.update_or_create(name="Game Code", country=china)
    game_code_cn = await DeliveryMethod.get(name="Game Code", country=china)
    await DeliveryMethod.update_or_create(name="In-game Items", country=china)
    in_game_items_cn = await DeliveryMethod.get(name="In-game Items", country=china)
    await DeliveryMethod.update_or_create(name="In-game Balance", country=china)
    in_game_balance_cn = await DeliveryMethod.get(name="In-game Balance", country=china)
    await DeliveryMethod.update_or_create(name="Collectibles", country=china)
    collectibles_cn = await DeliveryMethod.get(name="Collectibles", country=china)

    # Steam digital 20$ USA code balance 1
    await Product.update_or_create(
        description="A9N2G-RNA7W-BRET0 ($20 Steam USA)",
        country=usa,
        category=steam,
        quantity=20,
        type=True,
        d_method=balance_usa,
        d_type=0,
        price=22
    )
    p = await Product.get(description="A9N2G-RNA7W-BRET0 ($20 Steam USA)")
    await p.images.add(steam_20_1_1, steam_20_1_2)
    await Stock.update_or_create(product=p, country=usa, type=True, category=steam,
                                 d_method=balance_usa, d_type=p.d_type, quantity=p.quantity)

    # Steam digital 20$ USA code balance 2
    await Product.update_or_create(
        description="A98JD-KLD7W-KIFWD ($20 Steam USA)",
        country=usa,
        category=steam,
        quantity=20,
        type=True,
        d_method=balance_usa,
        d_type=0,
        price=22
    )
    p = await Product.get(description="A98JD-KLD7W-KIFWD ($20 Steam USA)")
    await p.images.add(steam_20_2_1, steam_20_2_2)
    await Stock.update_or_create(product=p, country=usa, type=True, category=steam,
                                 d_method=balance_usa, d_type=p.d_type, quantity=p.quantity)

    # Steam digital 50$ USA code balance
    await Product.update_or_create(
        description="AK9J3-FRE7W-NMD0 ($50 Steam USA)",
        country=usa,
        category=steam,
        quantity=50,
        type=True,
        d_method=balance_usa,
        d_type=0,
        price=52
    )
    p = await Product.get(description="AK9J3-FRE7W-NMD0 ($50 Steam USA)")
    await p.images.add(steam_50_1_1, steam_50_1_2)
    await Stock.update_or_create(product=p, country=usa, type=True, category=steam,
                                 d_method=balance_usa, d_type=p.d_type, quantity=p.quantity)

    # Steam digital 1000Y Japan code balance
    await Product.update_or_create(
        description="A9N2G-RNA7W-BRET0 (1000Y Steam Japan)",
        country=japan,
        category=steam,
        quantity=1000,
        type=True,
        d_method=balance_japan,
        d_type=0,
        price=10
    )
    p = await Product.get(description="A9N2G-RNA7W-BRET0 (1000Y Steam Japan)")
    await p.images.add(steam_100_1_1, steam_100_1_2)
    await Stock.update_or_create(product=p, country=japan, type=True, category=steam,
                                 d_method=balance_japan, d_type=p.d_type, quantity=p.quantity)

    # Steam digital 1000Y Japan code balance
    await Product.update_or_create(
        description="J6F3D-O8HDF-GJED6 (1000Y Steam Japan)",
        country=japan,
        category=steam,
        quantity=1000,
        type=True,
        d_method=balance_japan,
        d_type=0,
        price=10
    )
    p = await Product.get(description="J6F3D-O8HDF-GJED6 (1000Y Steam Japan)")
    await p.images.add(steam_100_2_1, steam_100_2_2)
    await Stock.update_or_create(product=p, country=japan, type=True, category=steam,
                                 d_method=balance_japan, d_type=p.d_type, quantity=p.quantity)

    # Steam digital 10000Y Japan code balance
    await Product.update_or_create(
        description="DS23D-OJG9F-FDED6-KDF3A (10000Y Steam Japan)",
        country=japan,
        category=steam,
        quantity=10000,
        type=True,
        d_method=balance_japan,
        d_type=0,
        price=100
    )
    p = await Product.get(description="DS23D-OJG9F-FDED6-KDF3A (10000Y Steam Japan)")
    await p.images.add(steam_1000_1_1, steam_1000_1_2)
    await Stock.update_or_create(product=p, country=japan, type=True, category=steam,
                                 d_method=balance_japan, d_type=p.d_type, quantity=p.quantity)

    # Baby roshan offile preorder
    await Product.update_or_create(
        description="Please contact operator to confirm your address",
        country=russia,
        category=baby_roshan_2022,
        quantity=1,
        type=False,
        d_method=collectibles_ru,
        d_type=4,
        price=1000
    )
    p = await Product.get(description="Please contact operator to confirm your address", category=baby_roshan_2022)
    await Stock.update_or_create(product=p, country=russia, type=False, category=baby_roshan_2021,
                                 d_method=collectibles_ru, d_type=p.d_type, quantity=p.quantity)

    # Baby roshan online order
    await Product.update_or_create(
        description="Please contact operator to confirm your address",
        country=russia,
        category=baby_roshan_2021,
        quantity=1,
        type=True,
        d_method=collectibles_ru,
        d_type=1,
        price=1000
    )
    p = await Product.get(description="Please contact operator to confirm your address", category=baby_roshan_2021)
    await p.images.add(baby_roshan2021_1)
    await Stock.update_or_create(product=p, country=russia, type=True, category=baby_roshan_2021,
                                 d_method=collectibles_ru, d_type=p.d_type, quantity=p.quantity)

    # GTA V game code (usa)
    await Product.update_or_create(
        description="GJRT-FD23-0KRE-9L6O (GTA V USA)",
        country=usa,
        category=gta_v,
        quantity=1,
        type=True,
        d_method=game_code_usa,
        d_type=0,
        price=25
    )
    p = await Product.get(description="GJRT-FD23-0KRE-9L6O (GTA V USA)")
    await p.images.add(gta_v_us_1, gta_v_us_2)
    await Stock.update_or_create(product=p, country=usa, type=True, category=gta_v,
                                 d_method=game_code_usa, d_type=p.d_type, quantity=p.quantity)

    # GTA V game code (jp)
    await Product.update_or_create(
        description="FDNS-KD43-HDYE-3JD9 (GTA V JAPAN)",
        country=japan,
        category=gta_v,
        quantity=1,
        type=True,
        d_method=game_code_japan,
        d_type=0,
        price=25
    )
    p = await Product.get(description="FDNS-KD43-HDYE-3JD9 (GTA V JAPAN)")
    await p.images.add(gta_v_jp_1, gta_v_jp_2)
    await Stock.update_or_create(product=p, country=japan, type=True, category=gta_v,
                                 d_method=game_code_japan, d_type=p.d_type, quantity=p.quantity)

    # GTA V game code (ru)
    await Product.update_or_create(
        description="FKEK-6JDN0-4HD9-KDJE (GTA V RUSSIA)",
        country=russia,
        category=gta_v,
        quantity=1,
        type=True,
        d_method=game_code_ru,
        d_type=0,
        price=25
    )
    p = await Product.get(description="FKEK-6JDN0-4HD9-KDJE (GTA V RUSSIA)")
    await p.images.add(gta_v_ru_1, gta_v_ru_2)
    await Stock.update_or_create(product=p, country=russia, type=True, category=gta_v,
                                 d_method=game_code_ru, d_type=p.d_type, quantity=p.quantity)

    logging.info("Test entries were created successfully")
