import streamlit as st


def check_password(st):
    """Returns `True` jika pengguna memasukkan password yang benar."""

    def password_entered():
        """Memeriksa apakah password yang dimasukkan pengguna benar."""
        # Mengambil password dari st.secrets atau menggunakan default
        password = st.secrets["PASSWORD"] if "PASSWORD" in st.secrets else "pass123"

        if st.session_state["password"] == password:
            st.session_state["password_correct"] = True
            # menghapus password dari session state
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Pertama kali dijalankan, tampilkan input password
        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password salah, tampilkan input dan pesan error
        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password benar
        return True
