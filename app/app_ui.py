import streamlit as st
import requests

API_BASE = "http://localhost:8000"  # adjust if needed

def delete_message(username, message_id):
    if st.button("Delete", key=f"delete_{message_id}"):
        res = requests.delete(f"{API_BASE}/users/{username}/messages/{message_id}")
        if res.status_code == 200:
            st.session_state["messages"] = [
                m for m in st.session_state["messages"] if m["message_id"] != message_id
            ]
            st.rerun()
        else:
            st.error(f"Error {res.status_code}: {res.json().get('detail', 'Unknown error')}")

def display_message(msg, username):
    st.markdown("---")
    st.markdown(f"ID: `{msg['message_id']}`")
    st.markdown(f"Sender: `{msg['sender_id']}`")
    st.markdown(f"Time: `{msg['timestamp']}`")
    st.markdown(f"Read: `{msg['read']}`")
    st.markdown("Message:")
    st.code(msg['message'])
    delete_message(username, msg["message_id"])

def render_messages(username):
    for msg in st.session_state.get("messages", []):
        display_message(msg, username)

def refetch_messages(username):
    if st.session_state.get("messages"):
        params = {"filterUnread": False, "start": 0, "stop": 10}
        res = requests.get(f"{API_BASE}/users/{username}/messages", params=params)
        if res.status_code == 200:
            st.session_state["messages"] = res.json().get("messages", [])
        else:
            st.error("Could not refresh message list after deletion.")
    st.rerun()

def fetch_messages(username, unread=False):
    params = {"filterUnread": unread, "start": 0, "stop": 10}
    res = requests.get(f"{API_BASE}/users/{username}/messages", params=params)
    if res.status_code == 200:
        return res.json().get("messages", [])
    else:
        st.error(f"Error {res.status_code}: {res.json().get('detail', 'Unknown error')}")
        return None

st.title("Message Service UI")

username = st.text_input("Username")

if st.button("Fetch Unread Messages"):
    if not username:
        st.error("Please enter a username")
    else:
        messages = fetch_messages(username, unread=True)
        if messages is not None:
            if not messages:
                st.info("No unread messages found.")
                st.session_state["messages"] = []
            else:
                for msg in messages:
                    display_message(msg, username)
                res = requests.patch(f"{API_BASE}/users/{username}/messages")
                if res.status_code == 200:
                    st.success("Messages marked as read")
                else:
                    st.error(f"Error {res.status_code}: {res.json().get('detail', 'Unknown error')}")

if st.button("Fetch All Messages"):
    if not username:
        st.error("Please enter a username")
    else:
        messages = fetch_messages(username, unread=False)
        if messages is not None:
            st.session_state["messages"] = messages

render_messages(username)

st.markdown("---")
st.subheader("Send a Message")

sender = st.text_input("Sender Username")
recipient = st.text_input("Recipient Username")
message = st.text_area("Message")

if st.button("Send"):
    if not sender or not recipient or not message:
        st.error("Please fill in all fields to send a message")
    else:
        payload = {
            "sender_username": sender,
            "recipient_username": recipient,
            "message": message,
        }
        res = requests.post(f"{API_BASE}/users/{recipient}/messages", json=payload)
        if res.status_code == 200:
            st.success("Message sent successfully")
            refetch_messages(username)
        else:
            st.error(f"Error {res.status_code}: {res.json().get('detail', 'Unknown error')}")

st.markdown("---")
st.subheader("Delete Multiple Messages")

delete_ids = st.text_area("Enter message IDs to delete (comma separated)")

if st.button("Delete Multiple Messages"):
    if not delete_ids:
        st.error("Please enter at least one message ID")
    else:
        ids_list = [mid.strip() for mid in delete_ids.split(",") if mid.strip()]
        payload = {"ids": ids_list}
        res = requests.delete(f"{API_BASE}/users/{username}/messages", json=payload)
        if res.status_code == 200:
            st.success(f"Deleted {len(ids_list)} message(s) successfully")
            refetch_messages(username)
        else:
            st.error(f"Error {res.status_code}: {res.json().get('detail', 'Unknown error')}")
