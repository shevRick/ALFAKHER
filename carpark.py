import streamlit as st
import sqlite3
import pandas as pd
from sqlite3 import Error
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import os
import altair as alt
import pytz

# Set your local time zone to Nairobi
LOCAL_TZ = pytz.timezone('Africa/Nairobi')



# Use the current working directory to store the database
path = os.getcwd()
db_file = os.path.join(path, 'car_park_management.db')


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connection to SQLite DB successful, DB file: {db_file}")
    except Error as e:
        print(f"Error '{e}' occurred while connecting to SQLite DB")
    return conn

def create_tables(conn):
    try:
        c = conn.cursor()
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS Vehicles (
            id INTEGER PRIMARY KEY,
            license_plate TEXT UNIQUE,
            vehicle_type TEXT
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS VehicleMovements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_plate TEXT,
            owner_gender TEXT,
            checked_in BOOLEAN DEFAULT FALSE,
            checked_out BOOLEAN DEFAULT FALSE,
            checkin_time TEXT,  -- Store as TEXT in 'YYYY-MM-DD HH:MM:SS' format
            checkout_time TEXT,  -- Store as TEXT in 'YYYY-MM-DD HH:MM:SS' format
            passengers TEXT,
            FOREIGN KEY (license_plate) REFERENCES Vehicles(license_plate)
        )
        ''')
        
        

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

        c.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS Payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_time TEXT NOT NULL,
            FOREIGN KEY (transaction_id) REFERENCES Transactions (id)
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS car_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL
        )
        ''')

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
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS ParkingSlots (
            slot_number INTEGER PRIMARY KEY,
            status TEXT DEFAULT 'available' -- 'available' or 'occupied'
        )
        ''')
        
        car_models = [
            ('Toyota', 'Corolla'),
            ('Toyota', 'Camry'),
            ('Toyota', 'RAV4'),
            ('Toyota', 'Highlander'),
            ('Toyota', 'Tacoma'),
            ('Toyota', 'Tundra'),
            ('Toyota', 'Prius'),
            ('Toyota', 'Sienna'),
            ('Honda', 'Civic'),
            ('Honda', 'Accord'),
            ('Honda', 'CR-V'),
            ('Honda', 'Pilot'),
            ('Honda', 'Fit'),
            ('Honda', 'HR-V'),
            ('Honda', 'Odyssey'),
            ('Honda', 'Ridgeline'),
            ('Ford', 'Focus'),
            ('Ford', 'Fusion'),
            ('Ford', 'Mustang'),
            ('Ford', 'Escape'),
            ('Ford', 'Explorer'),
            ('Ford', 'F-150'),
            ('Ford', 'Edge'),
            ('Ford', 'Expedition'),
            ('Chevrolet', 'Malibu'),
            ('Chevrolet', 'Cruze'),
            ('Chevrolet', 'Equinox'),
            ('Chevrolet', 'Tahoe'),
            ('Chevrolet', 'Suburban'),
            ('Chevrolet', 'Silverado'),
            ('Chevrolet', 'Traverse'),
            ('Chevrolet', 'Blazer'),
            ('Nissan', 'Altima'),
            ('Nissan', 'Sentra'),
            ('Nissan', 'Maxima'),
            ('Nissan', 'Rogue'),
            ('Nissan', 'Murano'),
            ('Nissan', 'Pathfinder'),
            ('Nissan', 'Frontier'),
            ('Nissan', 'Titan'),
            ('BMW', '3 Series'),
            ('BMW', '5 Series'),
            ('BMW', '7 Series'),
            ('BMW', 'X3'),
            ('BMW', 'X5'),
            ('BMW', 'X7'),
            ('BMW', 'Z4'),
            ('BMW', 'i3'),
            ('Mercedes-Benz', 'C-Class'),
            ('Mercedes-Benz', 'E-Class'),
            ('Mercedes-Benz', 'S-Class'),
            ('Mercedes-Benz', 'GLA'),
            ('Mercedes-Benz', 'GLC'),
            ('Mercedes-Benz', 'GLE'),
            ('Mercedes-Benz', 'GLS'),
            ('Mercedes-Benz', 'AMG GT'),
            ('Audi', 'A3'),
            ('Audi', 'A4'),
            ('Audi', 'A6'),
            ('Audi', 'Q3'),
            ('Audi', 'Q5'),
            ('Audi', 'Q7'),
            ('Audi', 'Q8'),
            ('Audi', 'R8'),
            ('Volkswagen', 'Golf'),
            ('Volkswagen', 'Passat'),
            ('Volkswagen', 'Jetta'),
            ('Volkswagen', 'Tiguan'),
            ('Volkswagen', 'Atlas'),
            ('Volkswagen', 'Touareg'),
            ('Volkswagen', 'Beetle'),
            ('Volkswagen', 'Arteon'),
            ('Hyundai', 'Elantra'),
            ('Hyundai', 'Sonata'),
            ('Hyundai', 'Tucson'),
            ('Hyundai', 'Santa Fe'),
            ('Hyundai', 'Palisade'),
            ('Hyundai', 'Kona'),
            ('Hyundai', 'Venue'),
            ('Hyundai', 'Ioniq'),
            ('Kia', 'Optima'),
            ('Kia', 'Forte'),
            ('Kia', 'Sportage'),
            ('Kia', 'Sorento'),
            ('Kia', 'Telluride'),
            ('Kia', 'Soul'),
            ('Kia', 'Stinger'),
            ('Kia', 'Seltos'),
            ('Subaru', 'Impreza'),
            ('Subaru', 'Legacy'),
            ('Subaru', 'Outback'),
            ('Subaru', 'Forester'),
            ('Subaru', 'Crosstrek'),
            ('Subaru', 'Ascent'),
            ('Subaru', 'WRX'),
            ('Subaru', 'BRZ'),
            ('Tesla', 'Model S'),
            ('Tesla', 'Model 3'),
            ('Tesla', 'Model X'),
            ('Tesla', 'Model Y'),
            ('Tesla', 'Roadster'),
            ('Tesla', 'Cybertruck')
        ]
        
        # Insert car models into the table
        c.executemany('INSERT INTO car_models (brand, model) VALUES (?, ?)', car_models)
        
        # Insert statements
        parking_slots = [
            "INSERT INTO ParkingSlots (slot_number, status) VALUES (1, 'available')",
            "INSERT INTO ParkingSlots (slot_number, status) VALUES (2, 'available')",
            "INSERT INTO ParkingSlots (slot_number, status) VALUES (3, 'available')",
            "INSERT INTO ParkingSlots (slot_number, status) VALUES (4, 'available')",
            "INSERT INTO ParkingSlots (slot_number, status) VALUES (5, 'available')",
            "INSERT INTO ParkingSlots (slot_number, status) VALUES (6, 'available')",
            "INSERT INTO ParkingSlots (slot_number, status) VALUES (7, 'available')",
            "INSERT INTO ParkingSlots (slot_number, status) VALUES (8, 'available')",
            "INSERT INTO ParkingSlots (slot_number, status) VALUES (9, 'available')",
            "INSERT INTO ParkingSlots (slot_number, status) VALUES (10, 'available')"
        ]

        # Execute each insert statement
        for slots in parking_slots:
            c.execute(slots)

        conn.commit()
        print("Tables created successfully.")
    except Error as e:
        print(f"Error '{e}' occurred while creating tables")


# Function to insert a transaction into the database
def insert_transaction(conn, vehicle_id, slot_id, entry_time):
    try:
        sql = '''INSERT INTO Transactions (vehicle_id, slot_id, entry_time) VALUES (?, ?, ?)'''
        cur = conn.cursor()
        cur.execute(sql, (vehicle_id, slot_id, entry_time))
        conn.commit()
        st.success("Transaction recorded successfully")
    except Error as e:
        st.error(f"Error '{e}' occurred while inserting transaction")
    conn.close()
        
# Function to insert a vehicle into the database
def insert_vehicle_and_checkin(conn, license_plate, vehicle_type, owner_gender, passengers):
    try:
        c = conn.cursor()
        # Check if the vehicle already exists
        c.execute("SELECT * FROM Vehicles WHERE license_plate = ?", (license_plate,))
        vehicle = c.fetchone()
        if not vehicle:
            # Insert the vehicle into the Vehicles table
            c.execute("INSERT INTO Vehicles (license_plate, vehicle_type) VALUES (?, ?)", (license_plate, vehicle_type))
            conn.commit()
            st.success(f"Vehicle with license plate {license_plate} added to the database.")
        else:
            st.info(f"Vehicle with license plate {license_plate} already exists in the database.")
        
        # Check if the vehicle is already checked in
        c.execute("SELECT * FROM VehicleMovements WHERE license_plate = ? AND checked_in = TRUE AND checked_out = FALSE", (license_plate,))
        active_checkin = c.fetchone()
        if active_checkin:
            st.error(f"Vehicle with license plate {license_plate} is already checked in.")
        else:
            # Insert the movement details into the VehicleMovements table
            checkin_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.execute('''INSERT INTO VehicleMovements (license_plate, owner_gender, checked_in, checkin_time, passengers)
                         VALUES (?, ?, TRUE, ?, ?)''', (license_plate, owner_gender, checkin_time, passengers))
            conn.commit()
            st.success("Vehicle checked in successfully!")
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")



    conn.close()
    


def delete_vehicle(conn, id):
    try:
        c = conn.cursor()
        c.execute("DELETE FROM Vehicles WHERE id=?", (id,))
        conn.commit()
    except Error as e:
        print(e)   

def add_model(conn, brand, model):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO car_models (brand, model) VALUES (?,?)", (brand, model,))
        conn.commit()
    except Error as e:
        print(e)

def get_model_L4D(conn):
    try:
        
        car_models = pd.read_sql_query("SELECT * FROM car_models", conn)
        #rows = c.fetchall()
        return car_models
    except Error as e:
        print(e)
      
    
# Define your database connection and functions here
def get_vehicle_details(conn, vehicle):
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM VehicleMovements WHERE license_plate=?", (vehicle,))
        rows = c.fetchall()
        col_names = [description[0] for description in c.description]
        details = pd.DataFrame(rows, columns=col_names)
        return details
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
        
   
    

def update_vehicle_checkout(conn, license_plate):
    try:
        c = conn.cursor()
        # Check if the vehicle is currently checked in
        c.execute("SELECT checked_in FROM VehicleMovements WHERE license_plate=? AND checked_in=? AND checked_out=?", 
                  (license_plate, True, False))
        if c.fetchone() is None:
            raise Exception("Vehicle is not currently checked in or already checked out.")
        
        # Update the vehicle record to set checked_out to True and checked_in to False, with checkout_time as current time
        checkout_time = datetime.now(pytz.timezone('Africa/Nairobi')).strftime('%Y-%m-%d %H:%M:%S')
        c.execute("""
            UPDATE VehicleMovements 
            SET checked_out = ?, checked_in = ?, checkout_time = ? 
            WHERE license_plate=? AND checked_in=? AND checked_out=?
        """, (True, False, checkout_time, license_plate, True, False))
        conn.commit()
        st.success('Vehicle checked out successfully!')
    except Exception as e:
        st.error(str(e))
        
      
def get_model(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT DISTINCT(brand) FROM car_models")
        rows = c.fetchall()
        names = [row[0] for row in rows]
        return names
    except Error as e:
        print(e)
   
    
def delete_model(conn, id):
    try:
        c = conn.cursor()
        c.execute("DELETE FROM car_models WHERE id=?", (id,))
        conn.commit()
    except Error as e:
        print(e) 
    
    
def export_vehicles_to_csv(conn):
  try:
      df = pd.read_sql_query("SELECT * FROM vehicles", conn)
      df.to_csv(path+'vehicles.csv', index=False)
      
  except Error as e:
      print(e)
 

# Function to add a parking reservation to the database
def add_reservation(conn, license_plate, reservation_start, reservation_end, slot_number):
    try:
        c = conn.cursor()
        
        # Check if the license plate is already reserved in the same or overlapping time period
        c.execute("""
            SELECT COUNT(*) FROM Reservations
            WHERE license_plate = ?
              AND status = 'active'
        """, (license_plate,))
        
        count = c.fetchone()[0]
        
        if count > 0:
            st.error(f"The vehicle with license plate {license_plate} is already reserved.")
            return
        
        # Add the reservation
        local_tz = pytz.timezone('Africa/Nairobi')
        reserved_on = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')
        c.execute("""
            INSERT INTO Reservations (license_plate, reservation_start, reservation_end, slot_number, status)
            VALUES (?, ?, ?, ?, 'active')
        """, (license_plate, reservation_start, reservation_end, slot_number))
        
        # Update slot status to 'occupied'
        update_slot_status(conn, slot_number, 'occupied')
        
        conn.commit()
        st.success("Reservation added successfully!")
        
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")



        
# Function to get all vehicles that have checked in and not checked out
def get_checked_in_vehicles(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM VehicleMovements WHERE checked_in = TRUE AND checked_out = FALSE")
        vehicles = c.fetchall()
        if vehicles:
            df = pd.DataFrame(vehicles, columns=[desc[0] for desc in c.description])
            return df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if no vehicles found
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

# Function to get all vehicles that have checked in and not checked out
def get_checked_out_vehicles(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM VehicleMovements WHERE checked_in = FALSE AND checked_out = TRUE")
        vehicles = c.fetchall()
        if vehicles:
            df = pd.DataFrame(vehicles, columns=[desc[0] for desc in c.description])
            return df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if no vehicles found
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

def get_all_checked_in_vehicles(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM VehicleMovements WHERE checked_out = FALSE")
        vehicles = c.fetchall()
        if vehicles:
            df = pd.DataFrame(vehicles, columns=[desc[0] for desc in c.description])
            return df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if no vehicles found
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()
        
def get_all_checked_out_vehicles(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM VehicleMovements WHERE checked_out = TRUE")
        vehicles = c.fetchall()
        if vehicles:
            df = pd.DataFrame(vehicles, columns=[desc[0] for desc in c.description])
            return df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if no vehicles found
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()
        
def get_all_reservations(conn):
    query = "SELECT * FROM Reservations"
    return pd.read_sql_query(query, conn)

# Function to cancel a reservation
def cancel_reservation(conn, license_plate, slot_number):
    status = 'cancelled'
    try:
        c = conn.cursor()
        c.execute("UPDATE Reservations SET status=? WHERE license_plate=?", (status, license_plate))
        conn.commit() 
        
        update_slot_status(conn, slot_number, 'available')
        st.success(f"Reservation {license_plate} cancelled successfully.")
    except sqlite3.Error as e:
        st.error(f"Error cancelling reservation {license_plate}: {e}")

# Function to get available slots
def get_available_slots(conn):
    query = "SELECT slot_number FROM ParkingSlots WHERE status = 'available'"
    cur = conn.cursor()
    cur.execute(query)
    available_slots = cur.fetchall()
    return [slot[0] for slot in available_slots]

# Function to update slot status
def update_slot_status(conn, slot_number, status):
    print(slot_number)
    print(status)
 
    try:
        c = conn.cursor()
        c.execute("UPDATE ParkingSlots SET status=? WHERE slot_number=?", (status, slot_number))
        conn.commit()
    except Error as e:
        st.error(f"Error updating slot status: {e}")
        
# Initialize Streamlit session state
if 'searched_vehicle' not in st.session_state:
    st.session_state['searched_vehicle'] = None

# Initialize Streamlit session state
if 'slot_number' not in st.session_state:
    st.session_state['slot_number'] = None
    
conn = create_connection(db_file)

create_tables(conn)

## Config streamlit page
st.set_page_config(page_title='Alfakher Parking Management', page_icon=':coin:', layout='wide')

## Menu Tabs 
menu_tabs = ['Dashboard', 'Vehicles', 'CheckIN/OUT' ]
selected_tab = option_menu(
  menu_title=None,
  options=menu_tabs,
  icons=['house-dash', 'car-front', 'check-circle'],
  orientation='horizontal'
)

#  Fill colouring for buttons
html_code = """
    <style>
    div.stButton > button:first-child {
        background-color: #ff4b4b;
        color: white;
    }
    
    </style>
"""
st.markdown(html_code, unsafe_allow_html=True)


st.markdown("""
    <style>
            .streamlit-expanderHeader > div:nth-child(1) > p:nth-child(1) > strong:nth-child(1) {
         font-size: 24px;
        color: red;
            }
    </style>
""", unsafe_allow_html=True)

## Expense Tab  
if selected_tab == "Dashboard":
    st.markdown('<p class="big-font">Overall Summary</p>', unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        .metric-card {
            background-color: #f0f0f0; /* Light grey background */
            border-radius: 8px; /* Rounded corners */
            padding: 16px; /* Padding inside the card */
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); /* Shadow effect */
            font-size: 1.2em; /* Font size */
        }
        .metric-label {
            color: #333; /* Darker text color for the label */
        }
        .metric-value {
            color: #007bff; /* Blue text color for the value */
        }
        </style>
    """, unsafe_allow_html=True)
    
   
    
    # Create a layout with 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        total_vehicles_checked_in = len(get_all_checked_in_vehicles(conn))
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Vehicles Checked In</div>
                <div class="metric-value">{total_vehicles_checked_in}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        total_vehicles_checked_out = len(get_all_checked_out_vehicles(conn))
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Vehicles Checked Out</div>
                <div class="metric-value">{total_vehicles_checked_out}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        total_reservations = len(get_all_reservations(conn))
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Reservations</div>
                <div class="metric-value">{total_reservations}</div>
            </div>
        """, unsafe_allow_html=True)
        
    
    
    st.markdown('<p class="big-font">Recent Check-INs</p>', unsafe_allow_html=True)
    checked_in_vehicles = get_all_checked_in_vehicles(conn)
    st.dataframe(checked_in_vehicles, use_container_width=True)
    
    st.markdown('<p class="big-font">Recent Reservations</p>', unsafe_allow_html=True)
    reservations = get_all_reservations(conn)
    st.dataframe(reservations, use_container_width=True)
    
    
    
    # Example Chart
    st.markdown('<p class="big-font">Check-INs Over Time</p>', unsafe_allow_html=True)
    if not checked_in_vehicles.empty:
        checked_in_vehicles['checkin_time'] = pd.to_datetime(checked_in_vehicles['checkin_time'])
        checkin_chart = alt.Chart(checked_in_vehicles).mark_bar().encode(
            x='yearmonthdate(checkin_time):T',
            y='count()',
            tooltip=['checkin_time', 'count()']
        ).interactive()
        st.altair_chart(checkin_chart, use_container_width=True)
    # Example Chart: Heatmap for Check-Ins by Hour and Day
    st.markdown('<p class="big-font">Check-Ins by Hour and Day</p>', unsafe_allow_html=True)
    if not checked_in_vehicles.empty:
        checked_in_vehicles['hour'] = checked_in_vehicles['checkin_time'].dt.hour
        checked_in_vehicles['day'] = checked_in_vehicles['checkin_time'].dt.day_name()
        heatmap = alt.Chart(checked_in_vehicles).mark_rect().encode(
            x='hour:O',
            y='day:O',
            color='count()',
            tooltip=['hour', 'day', 'count()']
        )
        st.altair_chart(heatmap, use_container_width=True)
    
    # Example Chart: Histogram for Check-In Durations
    st.markdown('<p class="big-font">Check-In Durations</p>', unsafe_allow_html=True)
    if not checked_in_vehicles.empty:
        checked_in_vehicles['duration'] = (
            pd.to_datetime(checked_in_vehicles['checkout_time']) - pd.to_datetime(checked_in_vehicles['checkin_time'])
        ).dt.total_seconds() / 3600  # Convert to hours
        histogram = alt.Chart(checked_in_vehicles).mark_bar().encode(
            x=alt.X('duration:Q', bin=alt.Bin(maxbins=30)),
            y='count()',
            tooltip=['duration', 'count()']
        ).interactive()
        st.altair_chart(histogram, use_container_width=True)
        
elif selected_tab == "Vehicles":    
    # st.title('Expense Tracker')

     ## Menu Tabs 
    vehicle_expand = ['Checked-IN', 'Checked-OUT' ]
    vehicle_tab = option_menu(
      menu_title=None,
      options=vehicle_expand,
      icons=['car-front', 'car-front', 'filetype-csv'],
      orientation='horizontal'
    )
    
            
    if vehicle_tab == "Checked-IN":
    
        st.subheader('Checked-In Vehicles')
        checked_in_vehicles = get_checked_in_vehicles(conn)
    
        # Display search bar
        search_query = st.text_input("Search Checked-In Vehicles")

        if not checked_in_vehicles.empty:
            # Filter dataframe based on search query
            if search_query:
                filtered_vehicles = checked_in_vehicles[checked_in_vehicles.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
                st.dataframe(filtered_vehicles, use_container_width=True)
            else:
                st.dataframe(checked_in_vehicles, use_container_width=True)
        else:
            st.info("No vehicles are currently checked in.")
        
    else:
    
        st.subheader('Checked-Out Vehicles')
        checked_out_vehicles = get_checked_out_vehicles(conn)
        # Display search bar
        search_query = st.text_input("Search Checked-Out Vehicles")

        if not checked_out_vehicles.empty:
            # Filter dataframe based on search query
            if search_query:
                filtered_vehicles = checked_out_vehicles[checked_out_vehicles.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
                st.dataframe(filtered_vehicles, use_container_width=True)
            else:
                st.dataframe(checked_out_vehicles, use_container_width=True)
        else:
            st.info("No vehicles are currently checked in.")
    
##_____HIDDEN in expander_____## 
  
    


elif selected_tab == "CheckIN/OUT":  
    
    ## Menu Tabs 
    check_expand = ['IN', 'OUT', 'Reserve' ]
    
    check_tab = option_menu(
      menu_title=None,
      options=check_expand,
      icons=['check-circle', 'door-open', 'calendar-check'],
      orientation='horizontal'
    )
    
   
    if check_tab == "IN":
    
        
        license_plate = st.text_input("License Plate:")
        vehicle_type = st.selectbox("Vehicle Model:", get_model(conn))
        owner_gender = st.selectbox("Driver Gender:", ["Male", "Female"])
        passengers = st.selectbox("Passengers:", ["Y", "N"])
        
        if st.button('Check-IN'):
            if license_plate and vehicle_type and owner_gender:
                insert_vehicle_and_checkin(conn, license_plate, vehicle_type, owner_gender,passengers)
                
            else:
                st.error("Please fill out all fields.")
                
    elif check_tab == 'OUT':
    
        st.subheader('Checked-In Vehicles')
        checked_in_vehicles = get_checked_in_vehicles(conn)
    
        # Display search bar
        search_query = st.text_input("Search Checked-In Vehicles")

        if not checked_in_vehicles.empty:
            # Filter dataframe based on search query
            if search_query:
                filtered_vehicles = checked_in_vehicles[checked_in_vehicles.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
                st.dataframe(filtered_vehicles, use_container_width=True)
                st.session_state['searched_vehicle'] = search_query
            else:
                st.dataframe(checked_in_vehicles, use_container_width=True)
        else:
            st.info("No vehicles are currently checked in.")

        # Display update button if a vehicle has been searched
        if st.session_state['searched_vehicle'] is not None:
            #st.subheader('Update Vehicle Checkout')
            if st.button('Checkout'):
                update_vehicle_checkout(conn, search_query)
                st.session_state['searched_vehicle'] = None
                
                
    else:
    
    
            reserve_expand = ['Reservations', 'Add', 'Cancel']
            reserve_tab = st.selectbox("Select Reservation Operation", reserve_expand)
            
            if reserve_tab == "Reservations":
                st.subheader('All Reservations')
                reservations = get_all_reservations(conn)
                
                # Display search bar
                search_query = st.text_input("Search Reservations")

                if not reservations.empty:
                    # Filter dataframe based on search query
                    if search_query:
                        filtered_reservations = reservations[reservations.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
                        st.dataframe(filtered_reservations, use_container_width=True)
                    else:
                        st.dataframe(reservations, use_container_width=True)
                else:
                    st.info("No reservations found.")
                
            elif reserve_tab == "Add":
                # Add parking reservation
                st.subheader('Reserve Parking Slot')
                
                available_slots = get_available_slots(conn)
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
                        
                        add_reservation(conn, reservation_license_plate, start_datetime, end_datetime, slot_number)
                else:
                
                    st.write("No available slots")
            
                
            else:
            
                st.subheader('Cancel Reservations')
                reservations = get_all_reservations(conn)
                
                # Display search bar
                search_query = st.text_input("Search Reservations")

                if not reservations.empty:
                    # Filter dataframe based on search query
                    if search_query:
                        filtered_reservations = reservations[reservations.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
                        st.dataframe(filtered_reservations, use_container_width=True)
                        st.session_state['searched_vehicle'] = search_query
                        st.session_state['slot_number'] = filtered_reservations.iloc[0]['slot_number']
                    else:
                        st.dataframe(reservations, use_container_width=True)    
                        
                else:
                    st.info("No reservations found.")
                       
                 # Display update button if a vehicle has been searched
                if st.session_state['searched_vehicle'] is not None:
                    #st.subheader('Update Vehicle Checkout')
                    if st.button('Cancel'):
                        slot_number = int(st.session_state['slot_number'])
                        cancel_reservation(conn, st.session_state['searched_vehicle'], slot_number)
                        
                        st.session_state['slot_number'] = None
                        st.session_state['searched_vehicle'] = None
              
             
