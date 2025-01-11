import streamlit as st

from utils import hide_st
from password import check_password


st.set_page_config(
    page_title="Bot Analytics",
    page_icon="📊",
)
hide_st(st)

if check_password(st):
    st.write("OK")