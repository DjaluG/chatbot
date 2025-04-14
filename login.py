import streamlit as st
import os
st.set_page_config(page_title="Chit Chat", page_icon=":books:")


# Akun-akun dummy untuk login (bisa diganti dengan database)
USERS = {
    "admin": "password123",
    "user1": "hello123",
}

def login():
    st.title("Login to Chit Chat")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            st.rerun() 
        else:
            st.error("Invalid username or password")

def logout():
    st.sidebar.write(f"Logged in as: {st.session_state.get('username', '')}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()


def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        logout()
        # Setelah login, jalankan app utama
        from app import main as app_main
        app_main()
    else:
        login()

def ensure_user_folder(username):
    user_folder = os.path.join("uploads", username)
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

if __name__ == "__main__":
    main()
