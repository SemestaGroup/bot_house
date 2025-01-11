from typing import Dict, Any, List
from importlib import import_module

from config import read_config, write_config

CONFIG = read_config()
bot_len = len(CONFIG.bots)


class BotPages:
    bot_name: str = "bot_name"

    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def page(self):
        """Your bot streamlit page"""


def load_pages(id: int) -> List[Dict[str, Any]]:
    """Load all pages from selected bot"""
    if not CONFIG.bots[id].pages:
        return

    i = 0
    bot_modules = []
    bot_name = CONFIG.bots[id].bot_name
    while True:
        i += 1
        try:
            bot_module = import_module(f"pages.bot_pages.{bot_name}.page_{i}")
        except:
            break
        bot_modules.append(bot_module)

    if not bot_modules:
        print("Bot modules not found!")
        CONFIG.bots[id].pages = []
        write_config(CONFIG)
        return
    
    bot_class_name = f"{bot_name.capitalize()}Pages" # BotnamePages
    page_lists = []
    for i, bot_module in enumerate(bot_modules):
        try:
            bot_class = getattr(bot_module, bot_class_name)
            if not issubclass(bot_class, BotPages):
                print(f"Bot class {bot_class_name} does not inherit BotPages")
                continue

            # {ttloli_bot: {"bot_pid": 0, ...}}
            page: BotPages = bot_class({bot_name: CONFIG.bots[id]}) 
            if not page.bot_name == bot_name:
                print(f"Bot name for page {bot_name} does not match expected bot name")
                continue
        except AttributeError as err:
            print(f"Found page for {bot_name}, but page class not found")
            continue
        else:
            _pages = {}
            _pages.update({f"Page {i+1}": page})
            page_lists.append(_pages)

    return page_lists
