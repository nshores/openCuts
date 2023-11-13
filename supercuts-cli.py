import configparser
import opencuts
import os
import sys

""" A CLI for Regis Salons.
"""
DRY_RUN = True

# Check to make sure the config exists
if not os.path.exists("config.ini"):
    print("Error: The config file does not exist.")
    sys.exit(1)

# Read the config
config = configparser.ConfigParser()
config.read("config.ini")


# Get values from the config file
SALON_ID = config.get("Opencuts", "salon_id")
REGIS_API_KEY = config.get("Opencuts", "regis_api_key")
REGIS_API_BOOKING_KEY = config.get("Opencuts", "regis_booking_api_key")
MY_SERVICE = config.get("Preferences", "my_service")
MY_STYLIST = config.get("Preferences", "my_stylist")
FIRST_NAME = config.get("Preferences", "first_name")
LAST_NAME = config.get("Preferences", "last_name")
PHONE_NUMBER = config.get("Preferences", "phone_number")
EMAIL_ADDRESS = config.get("Preferences", "email")


def clear_screen():
    # For Windows
    if os.name == "nt":
        _ = os.system("cls")
    # For macOS and Linux
    else:
        _ = os.system("clear")


# Our menu function and logic for each action
def main_menu():
    while True:
        clear_screen()
        print("openCuts is running! 💇\n")
        print("Salon Type:", mySalon.pos_type)
        print(
            "Store Info:", mySalon.storeaddress, mySalon.storename, mySalon.storephone
        )
        print(
            "My SALON_ID:",
            SALON_ID + "\n" "MY_SERVICE:",
            MY_SERVICE + "\n" "MY_STYLIST:",
            MY_STYLIST + "\n",
        )
        print("\nMain Menu:\n")
        print("1. Book an Appointment")
        print("2. View My Appointments")
        print("3. Cancel Appointment")
        print("4. View Store Services")
        print("5. View Store Stylists")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            if mySalon.pos_type.lower() == "zenoti":
                # look up the ID for the stylist and service
                selected_stylist = mySalon.find_stylist_by_name(MY_STYLIST)
                selected_service = mySalon.find_service_by_name(MY_SERVICE)

                # get some booking slots for the stylist and service selected
                booking_id = mySalon.create_service_booking(
                    selected_service, selected_stylist
                )
                booking_slots = mySalon.get_booking_slot(booking_id)
                # Present and select a slot if there are any slots available
                # TODO Perhaps move this to a method
                if len(booking_slots) > 0:
                    print(
                        "\n--------------------\n",
                        "Choose an open slot:",
                        "\n--------------------\n",
                    )
                    # Using enumerate with its default start value (0)
                    for slot_num, slot in enumerate(booking_slots["slots"]):
                        print(f"[{slot_num}] - Time Slot {slot['Time']} Available\n")
                    selected_slot = None
                    while selected_slot is None:
                        selected_slot_num = int(input("Select Slot:"))
                        # Directly use the input number as the index
                        selected_slot = booking_slots["slots"][selected_slot_num]
                    print("Selected Slot: " + selected_slot["Time"])
                    # If you select a slot, continue the rest of the booking flow
                    # TODO - Refactor this to a method
                    print("Looking up account information")
                    try:
                        account_id = mySalon.retrive_guest_detail(
                            first_name=FIRST_NAME,
                            last_name=LAST_NAME,
                            phone=PHONE_NUMBER,
                        )
                        account_id = account_id["id"]
                    except:
                        print("Coud not look up account information")
                    # Flow to handle creating an account if none exists
                    if not account_id:
                        print("You neeed to make an account - Creating one")
                        account_id = mySalon.create_account(
                            first_name=FIRST_NAME,
                            last_name=LAST_NAME,
                            phone_number=PHONE_NUMBER,
                        )
                        account_id = account_id["id"]
                    # Get another unique booking_ID passing in the user information this time
                    booking_id = mySalon.create_service_booking(
                        selected_service, selected_stylist, account_id
                    )
                    # Logic to actually reserve and confirm your slot
                    if not DRY_RUN:
                        print("Reserving slot")
                        try:
                            mySalon.reserve_selected_slot(selected_slot, booking_id)
                        except:
                            print("Could not reserve slot")
                            sys.exit()
                        print("Confirming Slot")
                        try:
                            mySalon.confirm_selected_slot(booking_id)
                        except:
                            print("Could not confirm slot")
            else:
                selected_service = str(mySalon.find_service_by_name(MY_SERVICE))
                booking_slots = mySalon.get_availability_of_salon(selected_service)
                # Present and select a slot if there are any slots available
                # Perhaps move this to a method
                if len(booking_slots) > 0:
                    if MY_STYLIST == "":
                        # Logic to choose a name since we don't have one defined
                        print(
                            "\n--------------------\n",
                            "Choose a name:",
                            "\n--------------------\n",
                        )
                        # Using enumerate with its default start value (0)
                        for slot_num, slot in enumerate(booking_slots):
                            print(f"[{slot_num}] Name: {slot['name']}\n")
                        selected_slot = None
                        while selected_slot is None:
                            selected_slot_num = int(input("Select Name:"))
                            # Directly use the input number as the index
                            selected_slot = booking_slots[selected_slot_num]
                    # We already have a name defined
                    else:
                        # Find the object containing the name we want to search for
                        for name in booking_slots:
                            if name["name"] == MY_STYLIST:
                                selected_slot = name
                    print("Available Timeslots: ")
                    timeslots = []
                    for hour_block in selected_slot["times"]["hours"]:
                        hour = hour_block["h"]
                        for slot, minute in enumerate(hour_block["m"]):
                            # Format the time as HH:MM
                            formatted_time = f"{hour:02d}:{minute:02d}"
                            timeslots.append(formatted_time)
                    for slot, time in enumerate(timeslots):
                        print(f"[{slot}] - Time {time}")
                    selected_time = int(input("Select a timeslot:"))
                    time = timeslots[selected_time]
                    selected_stylist = selected_slot["name"]
                    selected_stylist_id = selected_slot["employeeID"]
                    time = time.replace(
                        ":", ""
                    )  # format time to match what the API expects
                    # Create a list to send my service in
                    formatted_service = []
                    formatted_service.append(MY_SERVICE)
                    clear_screen()
                    print(f"Selected time: {timeslots[selected_time]}")
                    print(
                        f"Selected Stylist: {selected_stylist} - ID: {selected_stylist_id}  "
                    )
                    print(f"Selected Service: {MY_SERVICE} - ID: {selected_service} ")
                    # If you select a slot, continue the rest of the booking flow
                    choice = input("Ready to book? - Respond with Y/N:\n")
                    if choice == "Y":
                        checkin = mySalon.add_check_in(
                            firstname=FIRST_NAME,
                            lastname=LAST_NAME,
                            phonenumber=PHONE_NUMBER,
                            serviceid=selected_service,
                            services=formatted_service,
                            stylistid=selected_stylist_id,
                            stylistname=selected_stylist,
                            time=time,
                            emailaddress=EMAIL_ADDRESS,
                        )
                        print(checkin)
            input("Press any key to continue")
        elif choice == "2":
            # TODO - Refactor this to a method
            print("Looking up account information")
            try:
                account_id = mySalon.retrive_guest_detail(
                    first_name=FIRST_NAME, last_name=LAST_NAME, phone=PHONE_NUMBER
                )
                account_id = account_id["id"]
            except:
                print("Coud not look up account information")
            # Flow to handle creating an account if none exists
            if not account_id:
                print("You neeed to make an account - Creating one")
                account_id = mySalon.create_account(
                    first_name=FIRST_NAME,
                    last_name=LAST_NAME,
                    phone_number=PHONE_NUMBER,
                )
                account_id = account_id["id"]
            appointments = mySalon.get_appointments(account_id)
            if not appointments:
                print("No Appointments today")
            else:
                print("Your Appointments Today:")
                print(appointments)
            input("Press any key to continue")
        elif choice == "3":
            # TODO - Make this call a method.
            print("Looking up account information")
            try:
                account_id = mySalon.retrive_guest_detail(
                    first_name=FIRST_NAME, last_name=LAST_NAME, phone=PHONE_NUMBER
                )
                account_id = account_id["id"]
            except:
                print("Coud not look up account information")
            # Flow to handle creating an account if none exists
            if not account_id:
                print("You neeed to make an account - Creating one")
                account_id = mySalon.create_account(
                    first_name=FIRST_NAME,
                    last_name=LAST_NAME,
                    phone_number=PHONE_NUMBER,
                )
                account_id = account_id["id"]
            appointments = mySalon.get_appointments(account_id)
            print(appointments)
            if len(appointments) > 0:
                print("Appointment List:")
                # Using enumerate with its default start value (0)
                for slot_num, ap in enumerate(appointments):
                    print(
                        f"Slot Num {slot_num} - Time Slot {ap['appointment_services']['start_time']} \n"
                    )
                selected_slot = None
                while selected_slot is None:
                    selected_slot_num = int(input("Select Slot:"))
                    # Directly use the input number as the index
                    selected_appointment = appointments[selected_slot_num]
                print(
                    "Selected Appointment: "
                    + selected_appointment["appointment_services"]["start_time"]
                )
                print("Cancelling Appointment")
                mySalon.cancel_appointment(selected_appointment["invoice_id"])
            else:
                print("No Appointments found")
                input("Press any key to continue")

        elif choice == "4":
            print("\nStore Services:\n")
            # TODO -  move logic to a method
            if mySalon.pos_type.lower() == "zenoti":
                for service in mySalon.store_services:
                    print(
                        f"Service Name: {service['catalog_info']['display_name']}, ID: {service['id']}\n"
                    )
            else:
                for category in mySalon.store_services:
                    print(f"Category: {category['category']}\n")
                    for service in category["services"]:
                        print("  Service ID:", service["id"])
                        print("  Service Name:", service["service"])
            input("Press any key to continue")

        elif choice == "5":
            print("\nStore Stylists:\n")
            # TODO - move logic to a method
            if mySalon.pos_type.lower() == "zenoti":
                for therapist in mySalon.therapists:
                    print(
                        f"Stylist Name: {therapist['personal_info']['name']}, ID: {therapist['id']}\n"
                    )
            else:
                for therapist in mySalon.therapists:
                    print(f"Stylist Name: {therapist['name']}\n")
            input("Press any key to continue")

        elif choice == "6":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Instantiate the class and get some information about the salon
    mySalon = opencuts.Salon(SALON_ID, REGIS_API_KEY, REGIS_API_BOOKING_KEY)
    mySalon.get_salon()  # get salon information
    mySalon.get_salon_services()  # get all the services the salon offers
    mySalon.get_therapists_working()  # get the stylist information
    # start the menu mainu
    main_menu()
