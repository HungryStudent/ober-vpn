import configparser

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["settings"]["TOKEN"]
ADMINS = [int(admin) for admin in config["settings"]["admins"].split(",")]
outline_price = int(config["settings"]["outline_price"])
outline_limit = int(config["settings"]["outline_limit"])
wireguard_price = int(config["settings"]["wireguard_price"])
BOT_NAME = config["settings"]["BOT_NAME"]


class DB:
    user = config["db"]["user"]
    password = config["db"]["password"]
    database = config["db"]["database"]
    host = config["db"]["host"]
    port = config["db"]["port"]
