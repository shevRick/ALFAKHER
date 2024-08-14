def main():
    st.set_page_config(page_title="Vehicle Check-In System", layout="wide")
    
    # Initialize the Model, View, and Controller for vehicle check-ins
    conn = sqlite3.connect("your_database.db")
    vehicle_model = DataModel(conn)
    vehicle_view = DashboardView()
    vehicle_controller = VehicleCheckinController(vehicle_model, vehicle_view)

    # Initialize the Model, View, and Controller for staff allocation
    staff_model = StaffModel(conn)
    staff_view = StaffView()
    staff_controller = StaffAllocationController(staff_model, staff_view)
    
    # Render the vehicle check-in form
    vehicle_controller.process_checkin_form()
    
    # Generate and render the daily check-ins chart
    daily_checkins_chart = vehicle_controller.generate_daily_checkins_chart()
    vehicle_view.render_dashboard(daily_checkins_chart)

    # Process and display staff allocations
    staff_controller.process_staff_allocation()
    staff_controller.display_staff_allocations()

if __name__ == "__main__":
    main()
