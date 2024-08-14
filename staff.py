import streamlit as st
import sqlite3
import pandas as pd
from sqlite3 import Error
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import os
import altair as alt
import pytz

class StaffView:
    """Handles the UI for staff allocation."""

    def render_staff_allocation_form(self):
        st.subheader("Staff Allocation")

        roles = ["Entry gate A staff", "Exit gate B staff", "Parking staff", "Traffic Marshal"]
        selected_role = st.selectbox("Select Role", roles)
        staff_name = st.text_input("Staff Name")

        if st.button("Allocate Staff"):
            return staff_name, selected_role
        return None, None

    def render_staff_allocation_list(self, staff_allocations):
        st.subheader("Current Staff Allocations")

        if staff_allocations.empty:
            st.write("No staff allocations yet.")
        else:
            st.write(staff_allocations)

class StaffModel:
    """Handles database interactions related to staff allocations."""

    def __init__(self, conn):
        self.conn = conn
        self.create_staff_table()

    def create_staff_table(self):
        """Creates the staff allocation table if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff_allocation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_name TEXT,
                role TEXT,
                allocation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_staff_allocation(self, staff_name, role):
        """Saves staff allocation to the database."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO staff_allocation (staff_name, role) VALUES (?, ?)", 
                       (staff_name, role))
        self.conn.commit()

    def fetch_staff_allocations(self):
        """Fetches current staff allocations from the database."""
        query = "SELECT staff_name, role, allocation_time FROM staff_allocation ORDER BY allocation_time DESC"
        return pd.read_sql_query(query, self.conn)

class StaffAllocationController:
    """Handles the logic for staff allocation."""

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def process_staff_allocation(self):
        """Processes the staff allocation form submission."""
        staff_name, role = self.view.render_staff_allocation_form()
        
        if staff_name and role:
            self.model.save_staff_allocation(staff_name, role)
            st.success(f"{staff_name} allocated to {role} successfully!")

    def display_staff_allocations(self):
        """Displays the current staff allocations."""
        staff_allocations = self.model.fetch_staff_allocations()
        self.view.render_staff_allocation_list(staff_allocations)
        
class Database:
    def __init__(self, db_file):
        self.conn = self.create_connection(db_file)

    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None

    def close_connection(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=()):
        try:
            c = self.conn.cursor()
            c.execute(query, params)
            self.conn.commit()
        except Error as e:
            print(e)

    def fetch_all(self, query, params=()):
        try:
            c = self.conn.cursor()
            c.execute(query, params)
            rows = c.fetchall()
            return rows
        except Error as e:
            print(e)
            return []

    def fetch_dataframe(self, query):
        try:
            return pd.read_sql_query(query, self.conn)
        except Error as e:
            print(e)
            return pd.DataFrame()
            
def main():
    st.set_page_config(page_title="Vehicle Check-In System", layout="wide")
    
    # Initialize the Model, View, and Controller for vehicle check-ins
    conn = sqlite3.connect("car_park_management.db")

    # Initialize the Model, View, and Controller for staff allocation
    staff_model = StaffModel(conn)
    staff_view = StaffView()
    staff_controller = StaffAllocationController(staff_model, staff_view)
    
   

    # Process and display staff allocations
    staff_controller.process_staff_allocation()
    staff_controller.display_staff_allocations()

if __name__ == "__main__":
    main()
