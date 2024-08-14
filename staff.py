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
    """Handles the UI for staff allocation and staff details management."""

    def render_staff_registration_form(self):
        st.subheader("Register New Staff")

        name = st.text_input("Name")
        employee_id = st.text_input("Employee ID")
        contact_info = st.text_input("Contact Information")

        if st.button("Register Staff"):
            return name, employee_id, contact_info
        return None, None, None

    def render_staff_allocation_form(self, staff_list):
        st.subheader("Staff Allocation")

        roles = ["Entry gate A staff", "Exit gate B staff", "Parking staff", "Traffic Marshal"]
        shifts = ["Day", "Night"]

        selected_staff = st.selectbox("Select Staff", staff_list)
        selected_role = st.selectbox("Select Role", roles)
        selected_shift = st.selectbox("Select Shift", shifts)
        shift_date = st.date_input("Shift Date")
        start_time = st.time_input("Start Time")
        end_time = st.time_input("End Time")

        if st.button("Allocate Staff"):
            return selected_staff, selected_role, selected_shift, shift_date, start_time, end_time
        return None, None, None, None, None, None

    def render_staff_allocation_list(self, staff_allocations):
        st.subheader("Current Staff Allocations")

        if staff_allocations.empty:
            st.write("No staff allocations yet.")
        else:
            st.write(staff_allocations)


class StaffModel:
    """Handles database interactions related to staff details and allocations."""

    def __init__(self, conn):
        self.conn = conn
        self.create_staff_table()
        self.create_allocation_table()

    def create_staff_table(self):
        """Creates the staff details table if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                employee_id TEXT,
                contact_info TEXT
            )
        ''')
        self.conn.commit()

    def create_allocation_table(self):
        """Creates the staff allocation table if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff_allocation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER,
                role TEXT,
                shift TEXT,
                shift_date DATE,
                start_time TIME,
                end_time TIME,
                allocation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff(id)
            )
        ''')
        self.conn.commit()

    def save_staff(self, name, employee_id, contact_info):
        """Saves a new staff member to the database."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO staff (name, employee_id, contact_info) VALUES (?, ?, ?)",
                       (name, employee_id, contact_info))
        self.conn.commit()

    def get_staff_list(self):
        """Fetches the list of staff members from the database."""
        query = "SELECT id, name FROM staff"
        return pd.read_sql_query(query, self.conn)

    def save_staff_allocation(self, staff_id, role, shift, shift_date, start_time, end_time):
        """Saves staff allocation to the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO staff_allocation 
                (staff_id, role, shift, shift_date, start_time, end_time) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (staff_id, role, shift, shift_date, start_time, end_time))
            self.conn.commit()
            st.success(f"Staff allocation saved successfully!")
        except sqlite3.Error as e:
            st.error(f"An error occurred while saving staff allocation: {e}")

    def fetch_staff_allocations(self):
        """Fetches current staff allocations from the database."""
        query = '''
            SELECT s.name, sa.role, sa.shift, sa.shift_date, sa.start_time, sa.end_time 
            FROM staff_allocation sa
            JOIN staff s ON sa.staff_id = s.id
            ORDER BY sa.shift_date DESC, sa.start_time DESC
        '''
        return pd.read_sql_query(query, self.conn)

        return pd.read_sql_query(query, self.conn)

class StaffAllocationController:
    """Handles the logic for staff management and allocation."""

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def register_new_staff(self):
        """Processes the staff registration form submission."""
        name, employee_id, contact_info = self.view.render_staff_registration_form()

        if name and employee_id and contact_info:
            self.model.save_staff(name, employee_id, contact_info)
            st.success(f"{name} registered successfully!")

    def process_staff_allocation(self):
        """Processes the staff allocation form submission."""
        staff_list = self.model.get_staff_list()
        staff_names = staff_list["name"].tolist()

        selected_staff_name, role, shift, shift_date, start_time, end_time = self.view.render_staff_allocation_form(staff_names)

        if selected_staff_name and role and shift and shift_date and start_time and end_time:
            staff_id = staff_list.loc[staff_list['name'] == selected_staff_name, 'id'].iloc[0]
            self.model.save_staff_allocation(staff_id, role, shift, shift_date, start_time, end_time)
            st.success(f"{selected_staff_name} allocated to {role} for {shift} shift on {shift_date} successfully!")

    def display_staff_allocations(self):
        """Displays the current staff allocations."""
        staff_allocations = self.model.fetch_staff_allocations()
        self.view.render_staff_allocation_list(staff_allocations)

        
            
def main():
    st.set_page_config(page_title="Vehicle Check-In System", layout="wide")
    
    # Initialize the Model, View, and Controller for vehicle check-ins
    conn = sqlite3.connect("car_park_management.db")

    # Initialize the Model, View, and Controller for staff allocation
    staff_model = StaffModel(conn)
    staff_view = StaffView()
    staff_controller = StaffAllocationController(staff_model, staff_view)
    
    # Process and display staff registration
    staff_controller.register_new_staff()

    # Process and display staff allocations
    staff_controller.process_staff_allocation()
    staff_controller.display_staff_allocations()

if __name__ == "__main__":
    main()
