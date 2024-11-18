# auth.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase

class Authentication:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(st.secrets["textkey"])
            firebase_admin.initialize_app(cred)

        self.firebase_config = {
            "apiKey": st.secrets["firebase"]["apiKey"],
            "authDomain": "todo-app-9fc2d.firebaseapp.com",
            "projectId": "todo-app-9fc2d",
            "storageBucket": "todo-app-9fc2d.appspot.com",
            "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
            "appId": st.secrets["firebase"]["appId"]
        }
        
        self.firebase = pyrebase.initialize_app(self.firebase_config)
        self.auth = self.firebase.auth()

    def sign_in(self, email, password):
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            st.session_state.user_info = user
            return True
        except:
            return False

    def sign_up(self, email, password):
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            st.session_state.user_info = user
            return True
        except:
            return False

    def reset_password(self, email):
        try:
            self.auth.send_password_reset_email(email)
            return True
        except:
            return False

    def sign_out(self):
        st.session_state.clear()

# main.py
import streamlit as st
from google.oauth2 import service_account
from google.cloud import firestore
from datetime import datetime
import uuid
from login import show_login_page

credentials = service_account.Credentials.from_service_account_info(st.secrets["textkey"])
db = firestore.Client(credentials=credentials, project="todo-app-9fc2d")

st.title("Todo App")

if 'user_info' not in st.session_state:
    show_login_page()
else:
    col1, col2 = st.columns([3, 1])
    with col1:
        task = st.text_input("Task")
    with col2:
        due_date = st.date_input("Due Date")

    submit = st.button("Add Task")

    if task and submit:
        task_id = str(uuid.uuid4())
        doc_ref = db.collection("tasks").document(task_id)
        doc_ref.set({
            "user_id": st.session_state.user_info['localId'],
            "task": task,
            "due_date": due_date.strftime("%Y-%m-%d"),
            "completed": False
        })

    tasks_ref = db.collection("tasks").where("user_id", "==", st.session_state.user_info['localId'])
    for doc in tasks_ref.stream():
        data = doc.to_dict()
        st.write(f"Task: {data['task']} - Due: {data['due_date']}")

    if st.button("Sign Out"):
        from auth import Authentication
        auth = Authentication()
        auth.sign_out()
        st.rerun()