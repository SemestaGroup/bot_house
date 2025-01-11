import os
import streamlit as st

from utils import hide_st, get_list
from password import check_password


st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)
hide_st(st)


def env_file_isexists() -> bool:
    """Check if env exists"""
    cur_dir = os.getcwd()
    env_path = os.path.join(cur_dir, ".env")
    return bool(os.path.isfile(env_path))


def read_env_file(filename) -> str:
    with open(filename, 'r') as fp:
        lines = fp.read().strip()
    return lines


def write_env_file(filename, env_file):
    with open(filename, 'w') as fp:
        fp.write(env_file)


def assign_new_password(new_password):
    os.environ["PASSWORD"] = new_password


if check_password(st):
    # Show the home page only when the correct password is entered.
    st.subheader("Dashboard")

    env_content = ""
    if env_file_isexists():
        env_content = read_env_file(".env")

    with st.expander("Security"):
        env_file = st.text_area(
            "ENV",
            env_content,
            height=150,
            placeholder="PASSWORD=YOUR_PASSWORD"
        )

        if st.button("Save ENV File"):
            write_env_file(".env", env_file)

            env_list = get_list(env_file)
            for env in env_list:
                if "password" in env.lower():
                    assign_new_password(env.split("=")[-1])
                    break

            st.success("ENV file saved successfully", icon="✅")
