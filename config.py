import os
import sys
import logging

from typing import Dict, List, Optional, Union
from dotenv import load_dotenv
from pydantic import BaseModel
# from pymongo import MongoClient

import storage as stg

pwd = os.getcwd()
env_file = os.path.join(pwd, ".env")

load_dotenv(env_file)

CONFIG_FILE_NAME = "bot_house.config.json"


class BotConfig(BaseModel):
    bot_pid: int = 0
    bot_ready: bool = False
    bot_name: str = ""
    api_id: int = 0
    api_hash: str = ""
    user_type: int = 0  # 0:bot, 1:user
    phone_no: str = ""
    username: str = ""
    bot_token: str = ""
    telethon_session: str = ""
    pyrogram_session: str = ""
    datas: dict = {}
    pages: list = []


class Config(BaseModel):
    dev: bool = True
    bots: List[BotConfig] = []


def copy_config_to_bot_modules(bot_config: BotConfig, bot_name: str):
    base_path = os.path.join(os.getcwd(), BASE_BOT_MODULE_PATH, bot_name)
    if not os.path.exists(base_path):
        return
    
    with open(os.path.join(base_path, "config.json"), "w", encoding="utf8") as file:
        file.write(bot_config.model_dump_json())


def write_config_to_file(config: Config):
    with open(CONFIG_FILE_NAME, "w", encoding="utf8") as file:
        file.write(config.model_dump_json())


def detect_config_type() -> int:
    # if os.getenv("MONGO_CON_STR"):
    #     if MONGO_CON_STR:
    #         logging.info("Using mongo db for storing config!")
    #         client = MongoClient(MONGO_CON_STR)
    #         stg.mycol = setup_mongo(client)
    #     return 2
    if CONFIG_FILE_NAME in os.listdir():
        logging.info(f"{CONFIG_FILE_NAME} detected!")
        return 1

    else:
        logging.info(
            "config file not found. mongo not found. creating local config file."
        )
        cfg = Config()
        write_config_to_file(cfg)
        logging.info(f"{CONFIG_FILE_NAME} created!")
        return 1


def read_config(count=1) -> Config:
    """Load the configuration defined by user."""
    if count > 3:
        logging.warning("Failed to read config, returning default config")
        return Config()
    if count != 1:
        logging.info(f"Trying to read config time:{count}")
    try:
        if stg.CONFIG_TYPE == 1:
            with open(CONFIG_FILE_NAME, encoding="utf8") as file:
                return Config.model_validate_json(file.read())
        # elif stg.CONFIG_TYPE == 2:
        #     return read_db()
        else:
            return Config()
    except Exception as err:
        logging.warning(err)
        stg.CONFIG_TYPE = detect_config_type()
        return read_config(count=count + 1)


def write_config(config: Config, persist=True):
    """Write changes in config back to file."""
    if stg.CONFIG_TYPE == 1 or stg.CONFIG_TYPE == 0:
        write_config_to_file(config)
    # elif stg.CONFIG_TYPE == 2:
    #     if persist:
    #         update_db(config)


def get_env_var(name: str, optional: bool = False) -> str:
    """Fetch an env var."""
    var = os.getenv(name, "")

    while not var:
        if optional:
            return ""
        var = input(f"Enter {name}: ")
    return var


# def setup_mongo(client):
#     mydb = client[MONGO_DB_NAME]
#     mycol = mydb[MONGO_COL_NAME]
#     if not mycol.find_one({"_id": 0}):
#         mycol.insert_one({"_id": 0, "author": "tgcf",
#                          "config": Config().dict()})

#     return mycol


# def update_db(cfg):
#     stg.mycol.update_one({"_id": 0}, {"$set": {"config": cfg.dict()}})


# def read_db():
#     obj = stg.mycol.find_one({"_id": 0})
#     cfg = Config(**obj["config"])
#     return cfg


CONFIG = read_config()

BASE_BOT_MODULE_PATH = os.getenv("BASE_BOT_MODULE_PATH", "bot_modules")
BASE_BOT_PAGES_PATH = os.getenv("BASE_BOT_PAGES_PATH", "pages/bot_pages")
PASSWORD = os.getenv("PASSWORD", "pass123")

MONGO_CON_STR = os.getenv("MONGO_CON_STR")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "bot_warehouse")
MONGO_COL_NAME = os.getenv("MONGO_COL_NAME", "base-config")

stg.CONFIG_TYPE = detect_config_type()

if PASSWORD == "pass123":
    logging.warn("The default password is `pass123`")

from_to = {}
reply_to = {}
client = None  # percobaan

is_bot: Optional[bool] = None

logging.info("config.py got executed")
