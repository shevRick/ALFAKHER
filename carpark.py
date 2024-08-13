import sqlite3
import pandas as pd
from sqlite3 import Error
from datetime import datetime
import pytz

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

class VehicleManagement:
    def __init__(self, database):
        self.db = database
        self.local_tz = pytz.timezone('Africa/Nairobi')

    def insert_vehicle_and_checkin(self, license_plate, vehicle_type, owner_gender, passengers, image_path):
        vehicle = self.db.fetch_all("SELECT * FROM Vehicles WHERE license_plate = ?", (license_plate,))
        if not vehicle:
            self.db.execute_query(
                "INSERT INTO Vehicles (license_plate, vehicle_type, image_path) VALUES (?, ?, ?)",
                (license_plate, vehicle_type, image_path)
            )

        active_checkin = self.db.fetch_all(
            "SELECT * FROM VehicleMovements WHERE license_plate = ? AND checked_in = TRUE AND checked_out = FALSE",
            (license_plate,)
        )
        if active_checkin:
            return "Vehicle is already checked in."
        else:
            checkin_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.db.execute_query(
                '''INSERT INTO VehicleMovements (license_plate, owner_gender, checked_in, checkin_time, passengers)
                   VALUES (?, ?, TRUE, ?, ?)''',
                (license_plate, owner_gender, checkin_time, passengers)
            )
            return "Vehicle checked in successfully!"

    def update_vehicle_checkout(self, license_plate):
        checked_in = self.db.fetch_all(
            "SELECT checked_in FROM VehicleMovements WHERE license_plate=? AND checked_in=? AND checked_out=?", 
            (license_plate, True, False)
        )
        if not checked_in:
            return "Vehicle is not currently checked in or already checked out."

        checkout_time = datetime.now(self.local_tz).strftime('%Y-%m-%d %H:%M:%S')
        self.db.execute_query(
            """
            UPDATE VehicleMovements 
            SET checked_out = ?, checked_in = ?, checkout_time = ? 
            WHERE license_plate=? AND checked_in=? AND checked_out=?
            """, 
            (True, False, checkout_time, license_plate, True, False)
        )
        return "Vehicle checked out successfully!"

    def get_checked_in_vehicles(self):
        return self.db.fetch_dataframe("SELECT * FROM VehicleMovements WHERE checked_in = TRUE AND checked_out = FALSE")

    def get_checked_out_vehicles(self):
        return self.db.fetch_dataframe("SELECT * FROM VehicleMovements WHERE checked_in = FALSE AND checked_out = TRUE")

    def get_all_reservations(self):
        return self.db.fetch_dataframe("SELECT * FROM Reservations")

    def add_reservation(self, license_plate, reservation_start, reservation_end, slot_number):
        count = self.db.fetch_all(
            "SELECT COUNT(*) FROM Reservations WHERE license_plate = ? AND status = 'active'",
            (license_plate,)
        )[0][0]
        if count > 0:
            return "Vehicle is already reserved."

        reserved_on = datetime.now(self.local_tz).strftime('%Y-%m-%d %H:%M:%S')
        self.db.execute_query(
            """INSERT INTO Reservations (license_plate, reservation_start, reservation_end, slot_number, status)
               VALUES (?, ?, ?, ?, 'active')""",
            (license_plate, reservation_start, reservation_end, slot_number)
        )
        self.update_slot_status(slot_number, 'occupied')
        return "Reservation added successfully!"

    def cancel_reservation(self, license_plate, slot_number):
        self.db.execute_query("UPDATE Reservations SET status=? WHERE license_plate=?", ('cancelled', license_plate))
        self.update_slot_status(slot_number, 'available')
        return f"Reservation {license_plate} cancelled successfully."

    def update_slot_status(self, slot_number, status):
        self.db.execute_query("UPDATE ParkingSlots SET status=? WHERE slot_number=?", (status, slot_number))

import streamlit as st
from streamlit_option_menu import option_menu
import os

class ParkingManagementApp:
    def __init__(self, vehicle_management):
        self.vehicle_management = vehicle_management
        st.set_page_config(page_title='Alfakher Parking Management', page_icon=':coin:', layout='wide')
        self.setup_ui()

    def setup_ui(self):
        self.display_menu()

    def display_menu(self):
        menu_tabs = ['Dashboard', 'Vehicles', 'CheckIN/OUT']
        selected_tab = option_menu(
            menu_title=None,
            options=menu_tabs,
            icons=['house-dash', 'car-front', 'check-circle'],
            orientation='horizontal'
        )
        if selected_tab == "Dashboard":
            self.show_dashboard()
        elif selected_tab == "Vehicles":
            self.manage_vehicles()
        elif selected_tab == "CheckIN/OUT":
            self.check_in_out()

    def show_dashboard(self):
        st.markdown('<p class="big-font">Overall Summary</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            total_vehicles_checked_in = len(self.vehicle_management.get_checked_in_vehicles())
            st.markdown(f"<div class='metric-card'>Total Vehicles Checked In: {total_vehicles_checked_in}</div>", unsafe_allow_html=True)

        with col2:
            total_vehicles_checked_out = len(self.vehicle_management.get_checked_out_vehicles())
            st.markdown(f"<div class='metric-card'>Total Vehicles Checked Out: {total_vehicles_checked_out}</div>", unsafe_allow_html=True)

        with col3:
            total_reservations = len(self.vehicle_management.get_all_reservations())
            st.markdown(f"<div class='metric-card'>Total Reservations: {total_reservations}</div>", unsafe_allow_html=True)

        st.markdown('<p class="big-font">Recent Check-INs</p>', unsafe_allow_html=True)
        checked_in_vehicles = self.vehicle_management.get_checked_in_vehicles()
        st.dataframe(checked_in_vehicles, use_container_width=True)

    def manage_vehicles(self):
        vehicle_expand = ['Checked-IN', 'Checked-OUT']
        vehicle_tab = option_menu(
            menu_title=None,
            options=vehicle_expand,
            icons=['car-front', 'car-front'],
            orientation='horizontal'
        )
        if vehicle_tab == "Checked-IN":
            st.subheader('Checked-In Vehicles')
            checked_in_vehicles = self.vehicle_management.get_checked_in_vehicles()
            self.display_vehicle_table(checked_in_vehicles)
        elif vehicle_tab == "Checked-OUT":
            st.subheader('Checked-Out Vehicles')
            checked_out_vehicles = self.vehicle_management.get_checked_out_vehicles()
            self.display_vehicle_table(checked_out_vehicles)

    def display_vehicle_table(self, vehicles):
        search_query = st.text_input("Search Vehicles")
        if not vehicles.empty:
            if search_query:
                filtered_vehicles = vehicles[vehicles.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
                st.dataframe(filtered_vehicles, use_container_width=True)
            else:
                st.dataframe(vehicles, use_container_width=True)
        else:
            st.info("No vehicles found.")

    def check_in_out(self):
        check_expand = ['IN', 'OUT', 'Reserve']
        check_tab = option_menu(
            menu_title=None,
            options=check_expand,
            icons=['check-circle', 'door-open', 'calendar-check'],
            orientation='horizontal'
        )

        if check_tab == "IN":
            license_plate = st.text_input("License Plate:")
            vehicle_type = st.selectbox("Vehicle Model:", [])  # Needs to be populated with models
            owner_gender = st.selectbox("Driver Gender:", ["Male", "Female"])
            passengers = st.selectbox("Passengers:", ["Y", "N"])
            vehicle_image = st.camera_input("Take a picture of the vehicle")

            if st.button('Check-IN'):
                if license_plate and vehicle_type and owner_gender and vehicle_image:
                    image_path = f"vehicle_images/{license_plate}.png"
                    os.makedirs("vehicle_images", exist_ok=True)
                    with open(image_path, "wb") as f:
                        f.write(vehicle_image.getvalue())

                    result = self.vehicle_management.insert_vehicle_and_checkin(license_plate, vehicle_type, owner_gender, passengers, image_path)
                    st.success(result)
                else:
                    st.error('Please provide all required information.')

        elif check_tab == "OUT":
            license_plate = st.text_input("License Plate:")
            if st.button('Check-OUT'):
                result = self.vehicle_management.update_vehicle_checkout(license_plate)
                st.success(result)

        elif check_tab == "Reserve":
            # Reservation logic (similar to the above)
            pass

if __name__ == '__main__':
    db = Database("car_park_management.db")
    vehicle_mgmt = VehicleManagement(db)
    ParkingManagementApp(vehicle_mgmt)
