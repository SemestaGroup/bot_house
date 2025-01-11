import streamlit as st

import pages
from utils import hide_st
from password import check_password
from config import CONFIG, read_config


CONFIG = read_config()

st.set_page_config(
    page_title="Advanced Bot Configuration",
    page_icon="👾",
)
hide_st(st)


num = len(CONFIG.bots)
if check_password(st):
    st.subheader("Bot Pages", divider="blue")
    if num == 0:
        st.write("There is currently no registered bot available at this time")
    else:
        bot_lists = []
        for i in range(num):
            if CONFIG.bots[i].bot_name:
                label = CONFIG.bots[i].bot_name
            else:
                label = f"Bot {i+1}"
            bot_lists.append(f"{label}")

        selected_bot = st.sidebar.selectbox("Select bot", bot_lists)
        id_bot = bot_lists.index(selected_bot)
        page_names_to_funcs = CONFIG.bots[id_bot].pages

        if page_names_to_funcs:
            bot_pages = pages.load_pages(id_bot)
            selected_page = st.sidebar.selectbox(
                "Select a page", page_names_to_funcs)

            if bot_pages:
                for bot_page in bot_pages:
                    for menu, func in bot_page.items():
                        if menu == selected_page:
                            func.page()
                            break
