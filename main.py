import streamlit as st
import json
from google.oauth2 import service_account
from google.cloud import firestore
from datetime import datetime
import uuid

# Load the Firestore key from Streamlit secrets
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="todo-app")

st.title("Todo App ")

# Streamlit widgets for task creation
col1, col2 = st.columns([3, 1])
with col1:
    task = st.text_input("Task")
with col2:
    due_date = st.date_input("Due Date")

submit = st.button("Add Task")

# Add task to database
if task and submit:
    task_id = str(uuid.uuid4())
    doc_ref = db.collection("tasks").document(task_id)
    doc_ref.set({
        "task": task,
        "due_date": due_date.strftime("%Y-%m-%d"),
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    })

# Display tasks grouped by due date
st.subheader("📅 Tasks by Due Date")
tasks_ref = db.collection("tasks").order_by("due_date")

for doc in tasks_ref.stream():
    data = doc.to_dict()
    task_id = doc.id
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # Checkbox for task completion
        completed = st.checkbox(
            data["task"], 
            value=data["completed"], 
            key=task_id
        )
        if completed != data["completed"]:
            db.collection("tasks").document(task_id).update({"completed": completed})
    
    with col2:
        st.write(f"Due: {data['due_date']}")
    
    with col3:
        if st.button("🗑️", key=f"delete_{task_id}"):
            db.collection("tasks").document(task_id).delete()
            st.experimental_rerun()

# Add calendar view
st.subheader("📅 Calendar View")
tasks_by_date = {}
for doc in tasks_ref.stream():
    data = doc.to_dict()
    date = data["due_date"]
    if date in tasks_by_date:
        tasks_by_date[date].append(data["task"])
    else:
        tasks_by_date[date] = [data["task"]]

for date, tasks in tasks_by_date.items():
    st.write(f"**{date}**")
    for task in tasks:
        st.write(f"- {task}")