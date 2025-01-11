import os

from typing import List


def get_list(string: str):
    # string where each line is one element
    my_list = []
    for line in string.splitlines():
        clean_line = line.strip()
        if clean_line != "":
            my_list.append(clean_line)
    return my_list


def get_string(my_list: List):
    string = ""
    for item in my_list:
        string += f"{item}\n"
    return string


def hide_st(st):
    dev = os.getenv("DEV")
    if dev:
        return
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def check_exists(path: str) -> bool:
    return os.path.isdir(path)


def check_modules_exists(bot_name: str, get_path: bool=False):
    is_exists = check_exists(os.path.join(MODULES_PATH, bot_name))
    if get_path and is_exists:
        return os.path.join(MODULES_PATH, bot_name)
    return is_exists


def check_pages_exists(bot_name: str, get_path: bool=False):
    is_exists = check_exists(os.path.join(PAGES_PATH, bot_name))
    if get_path and is_exists:
        return os.path.join(PAGES_PATH, bot_name)
    return is_exists


MODULES_PATH = os.path.join(os.getcwd(), "bot_modules")
PAGES_PATH = os.path.join(os.getcwd(), "pages", "bot_pages")
