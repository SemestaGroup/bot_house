import os
import sys
import time
import signal
import subprocess
import streamlit as st

from utils import hide_st
from password import check_password
from config import CONFIG, read_config, write_config


CONFIG = read_config()

st.set_page_config(
    page_title="Bot Deployment",
    page_icon="👾",
)

hide_st(st)


def set_path(id_bot: int, file: str) -> str:
    return os.path.join(os.getcwd(), "bot_modules", CONFIG.bots[id_bot].bot_name, file)
    

def termination(id_bot: int):
    CONFIG = read_config()
    st.code("process terminated!")
    os.rename(
        set_path(id_bot, "logs.txt"), 
        set_path(id_bot, f"old_logs.txt")
    )
    with open(set_path(id_bot, f"old_logs.txt"), "r") as f:
        st.download_button(
            "Download last logs", data=f.read(), 
            file_name="logs.txt"
        )

    CONFIG.bots[id_bot].bot_pid = 0
    write_config(CONFIG)
    st.button("Refresh page")


if check_password(st):
    st.subheader("Bot Deployment")

    num = len(CONFIG.bots)
    if num == 0:
        st.write("There is currently no registered bot available at this time")
    else:
        tab_id = []
        tab_title = []

        for i in range(num):
            if not CONFIG.bots[i].bot_ready:
                continue

            if CONFIG.bots[i].bot_name:
                label = CONFIG.bots[i].bot_name
            else:
                label = f"Bot {i+1}"
            if CONFIG.bots[i].bot_ready:
                status = "🟢"
            else:
                status = "🟡"

            tab_id.append(i)
            tab_title.append(f"{status} {label}")

        if tab_title:
            tabs = st.tabs(list(tab_title))
            for i, id_bot in enumerate(tab_id):
                with tabs[i]:
                    bot = i + 1
                    name = CONFIG.bots[id_bot].bot_name
                    if name:
                        label = f"{bot} [{name}]"
                    else:
                        label = bot

                    check = False

                    if CONFIG.bots[id_bot].bot_pid == 0:
                        check = st.button(
                            f"Run {name}", key=f"run {bot}", type="primary")

                    if CONFIG.bots[id_bot].bot_pid != 0:
                        st.warning(
                            "You must click stop and then re-run bot to apply changes in config."
                        )
                        # check if process is running using pid
                        try:
                            os.kill(CONFIG.bots[id_bot].bot_pid, signal.SIGCONT)
                        except Exception as err:
                            st.code("The process has stopped.")
                            st.code(err)
                            CONFIG.bots[id_bot].bot_pid = 0
                            write_config(CONFIG)
                            time.sleep(1)
                            st.rerun()

                        stop = st.button(
                            "Stop", key=f"stop {bot}", type="primary")
                        if stop:
                            try:
                                os.kill(CONFIG.bots[id_bot].bot_pid, signal.SIGSTOP)
                            except Exception as err:
                                st.code(err)

                                CONFIG.bots[id_bot].bot_pid = 0
                                write_config(CONFIG)
                                st.button("Refresh Page", key=f"refresh {bot}")

                            else:
                                termination(id_bot)

                    if check:
                        bot_main = set_path(id_bot, "main.py")
                        with open(set_path(id_bot, "logs.txt"), "w") as logs:
                            process = subprocess.Popen(
                                [f"{sys.executable}", bot_main],
                                stdout=logs,
                                stderr=subprocess.STDOUT,
                            )
                        CONFIG.bots[id_bot].bot_pid = process.pid
                        write_config(CONFIG)
                        time.sleep(2)

                        st.rerun()

                    try:
                        lines = st.slider(
                            "Lines of logs to show", min_value=100, max_value=1000, step=100, key=f"slider {bot}"
                        )
                        temp_logs = set_path(id_bot, f"logs_n_lines.txt")
                        os.system(f"rm {temp_logs}")
                        with open(set_path(id_bot, "logs.txt"), "r") as file:
                            pass

                        os.system(f"tail -n {lines} {set_path(id_bot, 'logs.txt')} >> {temp_logs}")
                        with open(temp_logs, "r") as file:
                            st.code(file.read())
                    except FileNotFoundError as err:
                        st.write("No present logs found")
                    st.button("Load more logs", key=f"load_more {bot}")
