import sqlite3
import pandas as pd
from sqlite3 import Error
from datetime import datetime
import pytz

class Database:
    def __init__(self, db_file):
        self.conn = self.create_connection(db_file)
        self.create_tables()

    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None
        
    def create_tables(self):
        try:
            c = self.conn.cursor()

            # Create Vehicles table
            c.execute('''
            CREATE TABLE IF NOT EXISTS Vehicles (
                id INTEGER PRIMARY KEY,
                license_plate TEXT UNIQUE,
                vehicle_type TEXT
            )
            ''')

            # Create VehicleMovements table
            c.execute('''
            CREATE TABLE IF NOT EXISTS VehicleMovements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_plate TEXT,
                owner_gender TEXT,
                checked_in BOOLEAN DEFAULT FALSE,
                checked_out BOOLEAN DEFAULT FALSE,
                checkin_time TEXT,
                checkout_time TEXT,
                passengers TEXT,
                FOREIGN KEY (license_plate) REFERENCES Vehicles(license_plate)
            )
            ''')

            # Create Transactions table
            c.execute('''
            CREATE TABLE IF NOT EXISTS Transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                slot_id INTEGER NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES Vehicles (id),
                FOREIGN KEY (slot_id) REFERENCES ParkingSlots (id)
            )
            ''')

            # Create Users table
            c.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
            ''')

            # Create Payments table
            c.execute('''
            CREATE TABLE IF NOT EXISTS Payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_time TEXT NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES Transactions (id)
            )
            ''')

            # Create Car Models table
            c.execute('''
            CREATE TABLE IF NOT EXISTS car_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                model TEXT NOT NULL
            )
            ''')

            # Create Reservations table
            c.execute('''
            CREATE TABLE IF NOT EXISTS Reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_plate TEXT NOT NULL,
                reservation_start TIMESTAMP NOT NULL,
                reservation_end TIMESTAMP NOT NULL,
                slot_number INTEGER NOT NULL,
                reserved_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
            ''')

            # Create Parking Slots table
            c.execute('''
            CREATE TABLE IF NOT EXISTS ParkingSlots (
                slot_number INTEGER PRIMARY KEY,
                status TEXT DEFAULT 'available'
            )
            ''')

            # Prepopulate car models table
            car_models = [
                ('Toyota', 'Corolla'), ('Toyota', 'Camry'), ('Toyota', 'RAV4'),
                ('Honda', 'Civic'), ('Honda', 'Accord'), ('Honda', 'CR-V'),
                ('Ford', 'Focus'), ('Ford', 'Fusion'), ('Ford', 'Mustang'),
                ('Chevrolet', 'Malibu'), ('Chevrolet', 'Cruze'), ('Chevrolet', 'Equinox'),
                ('Nissan', 'Altima'), ('Nissan', 'Sentra'), ('Nissan', 'Maxima'),
                ('BMW', '3 Series'), ('BMW', '5 Series'), ('BMW', '7 Series'),
                ('Mercedes-Benz', 'C-Class'), ('Mercedes-Benz', 'E-Class'), ('Mercedes-Benz', 'S-Class'),
                ('Audi', 'A3'), ('Audi', 'A4'), ('Audi', 'A6'),
                ('Volkswagen', 'Golf'), ('Volkswagen', 'Passat'), ('Volkswagen', 'Jetta'),
                ('Hyundai', 'Elantra'), ('Hyundai', 'Sonata'), ('Hyundai', 'Tucson'),
                ('Kia', 'Optima'), ('Kia', 'Forte'), ('Kia', 'Sportage'),
                ('Subaru', 'Impreza'), ('Subaru', 'Legacy'), ('Subaru', 'Outback'),
                ('Tesla', 'Model S'), ('Tesla', 'Model 3'), ('Tesla', 'Model X')
            ]
            c.executemany('INSERT INTO car_models (brand, model) VALUES (?, ?)', car_models)

            # Prepopulate parking slots table
            parking_slots = [
                (1, 'available'), (2, 'available'), (3, 'available'), (4, 'available'), (5, 'available'),
                (6, 'available'), (7, 'available'), (8, 'available'), (9, 'available'), (10, 'available')
            ]
            c.executemany('INSERT INTO ParkingSlots (slot_number, status) VALUES (?, ?)', parking_slots)

            self.conn.commit()

        except sqlite3.Error as e:
            print(f"An error occurred while creating the tables: {e}")
            
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

    def get_vehicle_models(self):
        """Fetches vehicle models from the database."""
        query = "SELECT brand || ' ' || model AS full_model FROM car_models"
        try:
            c = self.db.conn.cursor()
            c.execute(query)
            models = [row[0] for row in c.fetchall()]
            return models
        except sqlite3.Error as e:
            print(f"An error occurred while fetching vehicle models: {e}")
            return []

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
            vehicle_type = st.selectbox("Vehicle Model:", self.vehicle_management.get_vehicle_models())
            owner_gender = st.selectbox("Driver Gender:", ["Male", "Female"])
            passengers = st.selectbox("Passengers:", ["Y", "N"])

            if st.button('Check-IN'):
                if license_plate and vehicle_type and owner_gender:
                    result = self.vehicle_management.insert_vehicle_and_checkin(license_plate, vehicle_type, owner_gender, passengers, None)
                    st.success(result)
                else:
                    st.error("Please fill out all fields.")

        elif check_tab == 'OUT':
            st.subheader('Checked-In Vehicles')
            checked_in_vehicles = self.vehicle_management.get_checked_in_vehicles()

            search_query = st.text_input("Search Checked-In Vehicles")

            if not checked_in_vehicles.empty:
                if search_query:
                    filtered_vehicles = checked_in_vehicles[checked_in_vehicles.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
                    st.dataframe(filtered_vehicles, use_container_width=True)
                    st.session_state['searched_vehicle'] = search_query
                else:
                    st.dataframe(checked_in_vehicles, use_container_width=True)
            else:
                st.info("No vehicles are currently checked in.")

            if 'searched_vehicle' in st.session_state and st.session_state['searched_vehicle']:
                if st.button('Checkout'):
                    result = self.vehicle_management.update_vehicle_checkout(st.session_state['searched_vehicle'])
                    st.success(result)
                    st.session_state['searched_vehicle'] = None

        elif check_tab == 'Reserve':
            reserve_expand = ['Reservations', 'Add', 'Cancel']
            reserve_tab = st.selectbox("Select Reservation Operation", reserve_expand)

            if reserve_tab == "Reservations":
                st.subheader('All Reservations')
                reservations = self.vehicle_management.get_all_reservations()

                search_query = st.text_input("Search Reservations")

                if not reservations.empty:
                    if search_query:
                        filtered_reservations = reservations[reservations.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
                        st.dataframe(filtered_reservations, use_container_width=True)
                    else:
                        st.dataframe(reservations, use_container_width=True)
                else:
                    st.info("No reservations found.")

            elif reserve_tab == "Add":
                st.subheader('Reserve Parking Slot')
                available_slots = self.vehicle_management.get_available_slots()

                if available_slots:
                    reservation_license_plate = st.text_input('License Plate for Reservation')
                    reservation_start = st.date_input('Reservation Start Date')
                    reservation_start_time = st.time_input('Reservation Start Time')
                    reservation_end = st.date_input('Reservation End Date')
                    reservation_end_time = st.time_input('Reservation End Time')
                    slot_number = st.selectbox('Slot Number', available_slots)

                    if st.button('Add Reservation'):
                        start_datetime = datetime.combine(reservation_start, reservation_start_time).strftime('%Y-%m-%d %H:%M:%S')
                        end_datetime = datetime.combine(reservation_end, reservation_end_time).strftime('%Y-%m-%d %H:%M:%S')
                        result = self.vehicle_management.add_reservation(reservation_license_plate, start_datetime, end_datetime, slot_number)
                        st.success(result)
                else:
                    st.write("No available slots")

            elif reserve_tab == "Cancel":
                st.subheader('Cancel Reservations')
                reservations = self.vehicle_management.get_all_reservations()

                search_query = st.text_input("Search Reservations")

                if not reservations.empty:
                    if search_query:
                        filtered_reservations = reservations[reservations.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
                        st.dataframe(filtered_reservations, use_container_width=True)
                        st.session_state['searched_vehicle'] = search_query
                        st.session_state['slot_number'] = filtered_reservations.iloc[0]['slot_number']
                    else:
                        st.dataframe(reservations, use_container_width=True)
                else:
                    st.info("No reservations found.")

                if 'searched_vehicle' in st.session_state and st.session_state['searched_vehicle']:
                    if st.button('Cancel'):
                        slot_number = int(st.session_state['slot_number'])
                        result = self.vehicle_management.cancel_reservation(st.session_state['searched_vehicle'], slot_number)
                        st.success(result)
                        st.session_state['slot_number'] = None
                        st.session_state['searched_vehicle'] = None


if __name__ == '__main__':
    db = Database("car_park_management.db")
    vehicle_mgmt = VehicleManagement(db)
    ParkingManagementApp(vehicle_mgmt)
