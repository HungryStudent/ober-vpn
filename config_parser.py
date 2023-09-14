import configparser

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["settings"]["TOKEN"]
ADMINS = [int(admin) for admin in config["settings"]["admins"].split(",")]
wireguard_price = float(config["settings"]["wireguard_price"])
BOT_NAME = config["settings"]["BOT_NAME"]
YOOKASSA_TOKEN = config["settings"]["YOOKASSA_TOKEN"]
YOOKASSA_SHOP_ID = int(config["settings"]["YOOKASSA_SHOP_ID"])
PAY_TOKEN = config["settings"]["PAY_TOKEN"]

outline_prices = {
    "1": {"name": "Бронза", "price": 100, "limit": 150},
    "2": {"name": "Серебро", "price": 170, "limit": 300},
    "3": {"name": "Золото", "price": 250, "limit": 500}
}


class DB:
    user = config["db"]["user"]
    password = config["db"]["password"]
    database = config["db"]["database"]
    host = config["db"]["host"]
    port = config["db"]["port"]
