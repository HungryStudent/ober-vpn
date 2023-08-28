import configparser

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["settings"]["TOKEN"]
ADMINS = [int(admin) for admin in config["settings"]["admins"].split(",")]
outline_prices = {int(price.split("|")[0]): int(price.split("|")[1]) for price in config["settings"]["outline_prices"].split(",")}
outline_limit = int(config["settings"]["outline_limit"])
wireguard_price = float(config["settings"]["wireguard_price"])
BOT_NAME = config["settings"]["BOT_NAME"]
YOOKASSA_TOKEN = config["settings"]["YOOKASSA_TOKEN"]
YOOKASSA_SHOP_ID = int(config["settings"]["YOOKASSA_SHOP_ID"])


class DB:
    user = config["db"]["user"]
    password = config["db"]["password"]
    database = config["db"]["database"]
    host = config["db"]["host"]
    port = config["db"]["port"]
