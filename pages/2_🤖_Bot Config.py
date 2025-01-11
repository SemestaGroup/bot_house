import os
import shutil
import zipfile
import streamlit as st

from utils import (
    hide_st,
    PAGES_PATH,
    MODULES_PATH,
    check_pages_exists,
    check_modules_exists

)
from password import check_password
from config import CONFIG, BotConfig, read_config, write_config, copy_config_to_bot_modules


CONFIG = read_config()

st.set_page_config(
    page_title="Bot Configuration",
    page_icon="🤖",
)
hide_st(st)


def input_bot_token(i, bot):
    CONFIG.bots[i].bot_token = st.text_input(
        "Bot Token",
        CONFIG.bots[i].bot_token,
        key=f"bot_token {bot}"
    )


def input_session_string(i, bot):
    CONFIG.bots[i].telethon_session = st.text_input(
        "Telethon Session String",
        CONFIG.bots[i].telethon_session,
        key=f"telethon_session {bot}"
    )
    CONFIG.bots[i].pyrogram_session = st.text_input(
        "Pyrogram Session String",
        CONFIG.bots[i].pyrogram_session,
        key=f"pyrogram_session {bot}"
    )


def change_folder_name(bot_name: str, new_bot_name: str):
    # check if bot modules exists, if not return
    if not check_modules_exists(bot_name):
        return
    
    old_bot_modules_folder = os.path.join(MODULES_PATH, bot_name)
    new_bot_modules_folder = os.path.join(MODULES_PATH, new_bot_modules_folder)
    os.rename(old_bot_modules_folder, new_bot_modules_folder)

    # check if bot pages exists, if not return
    if not check_pages_exists(bot_name):
        return
    
    old_bot_pages_folder = os.path.join(PAGES_PATH, bot_name)
    new_bot_pages_folder = os.path.join(PAGES_PATH, new_bot_name)
    os.rename(old_bot_pages_folder, new_bot_pages_folder)
    

def remove_modules(bot_name: str):
    modules_path = check_modules_exists(bot_name, True)
    if not modules_path:
        return
    shutil.rmtree(modules_path)
    page_path = check_pages_exists(bot_name, True)
    if not page_path:
        return
    shutil.rmtree(page_path)


if check_password(st):
    st.subheader("Bot Configuration")

    add_new = st.button("Add new bot")
    if add_new:
        CONFIG.bots.append(BotConfig())
        write_config(CONFIG)

    num = len(CONFIG.bots)
    if num == 0:
        st.write("There is currently no registered bot available at this time")
    else:
        tab_strings = []

        for i in range(num):
            if CONFIG.bots[i].bot_name:
                label = CONFIG.bots[i].bot_name
            else:
                label = f"Bot {i+1}"
            if CONFIG.bots[i].bot_ready:
                status = "🟢"
            else:
                status = "🟡"

            tab_strings.append(f"{status} {label}")

        tabs = st.tabs(list(tab_strings))
        for i in range(num):
            with tabs[i]:
                bot = i + 1
                name = CONFIG.bots[i].bot_name
                if name:
                    label = f"{bot} [{name}]"
                else:
                    label = bot

                with st.expander("Modify Metadata"):
                    st.write(f"Bot ID: **{bot}**")
                    new_bot_name = st.text_input(
                        "Name of the bot",
                        value=CONFIG.bots[i].bot_name,
                        key=bot,
                    )
                    if CONFIG.bots[i].bot_name and CONFIG.bots[i].bot_name != new_bot_name:
                        change_folder_name(CONFIG.bots[i].bot_name, new_bot_name)

                    CONFIG.bots[i].bot_name = new_bot_name
                    st.info(
                        "You can untick the below checkbox if the bot isn't ready", icon="ℹ️")
                    CONFIG.bots[i].bot_ready = st.checkbox(
                        "Bot ready to deploy",
                        value=CONFIG.bots[i].bot_ready,
                        key=f"use {bot}",
                    )
                    if CONFIG.bots[i].bot_ready:
                        copy_config_to_bot_modules(CONFIG.bots[i], CONFIG.bots[i].bot_name)


                with st.expander("API ID and API HASH"):
                    st.info(
                        "Go to api.telegram.com to get API ID & API HASH", icon="ℹ️")

                    CONFIG.bots[i].api_id = st.text_input(
                        "API ID",
                        value=CONFIG.bots[i].api_id,
                        key=f"api_id {bot}",
                    ).strip()

                    if not str(CONFIG.bots[i].api_id).isdigit():
                        st.error(
                            "Please input numerical values only for API ID")
                    else:
                        CONFIG.bots[i].api_id = int(CONFIG.bots[i].api_id)

                    CONFIG.bots[i].api_hash = st.text_input(
                        "API HASH",
                        value=CONFIG.bots[i].api_hash,
                        key=f"api_hash {bot}",
                    ).strip()

                with st.expander("Bot Type"):
                    int_val = CONFIG.bots[i].user_type
                    type_bot = st.checkbox("Bot", True if int_val in (0, 2) else False, key=f"type_bot {bot}")
                    type_userbot = st.checkbox("Userbot", True if int_val in (1, 2) else False, key=f"type_userbot {bot}")

                    if type_bot:
                        input_bot_token(i, bot)
                        CONFIG.bots[i].user_type = 0
                    if type_userbot:
                        input_session_string(i, bot)
                        CONFIG.bots[i].user_type = 1
                    if type_bot and type_userbot:
                        CONFIG.bots[i].user_type = 2

                with st.expander("Upload Bot Modules"):
                    st.info(
                        "Modules must contain main directory with the bot name", icon="ℹ️")
                    file = st.file_uploader(
                        "Choose a file", type="zip", key=f"upload_module {bot}")

                    if file is not None:
                        file_bytes = file.read()
                        folder_path = os.path.join(os.getcwd(), f"bot_modules")
                        path = os.path.join(folder_path, file.name)

                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)

                        with open(path, "wb") as f:
                            f.write(file_bytes)

                        folder_found = False
                        with zipfile.ZipFile(path, 'r') as zip_ref:
                            for file_info in zip_ref.infolist():
                                if file_info.filename.startswith(CONFIG.bots[i].bot_name):
                                    folder_found = True
                                    zip_ref.extractall(f"bot_modules")
                                    st.success(
                                        f"Modules for bot {CONFIG.bots[i].bot_name} added.", icon="✅")
                                    break
                            else:
                                st.error(
                                    f"No main directory with name '{CONFIG.bots[i].bot_name}' found!", icon="🚨")

                        os.remove(path)

                with st.expander("Delete this bot"):
                    st.warning(
                        f"Clicking the 'Remove' button will **delete** bot **{label}**. This action cannot be reversed once done.",
                        icon="⚠️",
                    )

                    if st.button(f"Remove bot **{label}**"):
                        remove_modules(CONFIG.bots[i].bot_name)
                        del CONFIG.bots[i]
                        write_config(CONFIG)
                        st.rerun()

    if st.button("Save"):
        write_config(CONFIG)
        st.rerun()
