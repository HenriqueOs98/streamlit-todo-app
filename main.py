import streamlit as st
import json
from google.oauth2 import service_account
from google.cloud import firestore

# Load the Firestore key from Streamlit secrets
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="streamlit-todo")

# Streamlit widgets to let a user create a new task
task = st.text_input("Task")
submit = st.button("Add Task")

# Once the user has submitted, upload it to the database
if task and submit:
    doc_ref = db.collection("tasks").document(task)
    doc_ref.set({"task": task})

# And then render each task
tasks_ref = db.collection("to-dos")
for doc in tasks_ref.stream():
    task = doc.to_dict()["task"]

    st.write(f"- {task}")