import streamlit as st
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('app.db')
c = conn.cursor()

# Create user_accounts table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS user_accounts
             (username TEXT PRIMARY KEY, password TEXT)''')
conn.commit()

# Create tasks table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS tasks
             (task_id INTEGER PRIMARY KEY AUTOINCREMENT, tower TEXT, task_description TEXT, user_assigned TEXT,
              status TEXT DEFAULT 'Open')''')
conn.commit()


def main():
    st.title("Task Management App")

    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        login()
    elif choice == "Sign Up":
        sign_up()


def login():
    st.subheader("Login")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.checkbox("Login"):
        c.execute("SELECT * FROM user_accounts WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        if user:
            st.success("Logged in as {}".format(username))
            if username == "admin":
                admin_dashboard()
            else:
                user_dashboard(username)
        else:
            st.error("Incorrect username or password")


def sign_up():
    st.subheader("Create a new account")

    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        c.execute("SELECT * FROM user_accounts WHERE username=?", (new_username,))
        existing_user = c.fetchone()

        if existing_user:
            st.warning("Username already exists. Please choose a different username.")
        else:
            c.execute("INSERT INTO user_accounts (username, password) VALUES (?, ?)", (new_username, new_password))
            conn.commit()
            st.success("Account created successfully. Please login.")


def admin_dashboard():
    st.subheader("Admin Dashboard")

    tower_options = ["AP", "AR", "FP&A", "TAX", "Other"]
    selected_tower = st.selectbox("Select Tower", tower_options)

    task_description = st.text_area("Task Description")

    user_options = ["Xolani Mthembu", "Rirhandzu Mahaule", "Carla"]
    selected_user = st.selectbox("Assign to: ", user_options)

    if st.button("Assign Task"):
        c.execute("INSERT INTO tasks (tower, task_description, user_assigned) VALUES (?, ?, ?)",
                  (selected_tower, task_description, selected_user))
        conn.commit()
        st.success("Task assigned successfully.")

    st.subheader("Tasks Assigned by Admin")

    c.execute("SELECT * FROM tasks")
    admin_tasks = c.fetchall()

    if admin_tasks:
        sorted_tasks = sorted(admin_tasks, key=lambda x: x[0])  # Sort tasks by task ID

        for task in sorted_tasks:
            st.write("Task ID: {}".format(task[0]))
            st.write("Tower: {}".format(task[1]))
            st.write("Task Description: {}".format(task[2]))
            st.write("User Assigned: {}".format(task[3]))
            st.write("Status: {}".format(task[4]))

            if st.button("Close Task #{}".format(task[0])):
                c.execute("DELETE FROM tasks WHERE task_id=?", (task[0],))
                conn.commit()
                st.success("Task #{} closed and removed.".format(task[0]))

            st.write("--------------------")
    else:
        st.write("No tasks assigned by admin.")


def user_dashboard(username):
    st.subheader("User Dashboard")

    st.write("Hello, {}".format(username))

    c.execute("SELECT * FROM tasks WHERE user_assigned=?", (username,))
    tasks = c.fetchall()

    if tasks:
        st.write("You have been assigned the following tasks:")
        for task in tasks:
            st.write("Task ID: {}".format(task[0]))
            st.write("Tower: {}".format(task[1]))
            st.write("Task Description: {}".format(task[2]))
            #st.write("Status: {}".format(task[4]))

            if st.button("Close Task #{}".format(task[0])):
                c.execute("DELETE FROM tasks WHERE task_id=?", (task[0],))
                conn.commit()
                st.success("Task #{} closed and removed.".format(task[0]))

                # Renumber the task IDs sequentially
                c.execute("SELECT task_id FROM tasks")
                task_ids = c.fetchall()
                task_ids = [task[0] for task in task_ids]

                for i, task_id in enumerate(task_ids, start=1):
                    c.execute("UPDATE tasks SET task_id=? WHERE task_id=?", (i, task_id))
                    conn.commit()

                st.info("Task IDs have been re-numbered.")

    else:
        st.write("You have no tasks assigned.")

    if st.button("Sign Out"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()
