import configparser
import opencuts
import os
import sys
from pprint import *

""" A CLI for Supercuts.
"""

if __name__ == "__main__":
    if not os.path.exists("config.ini"):
        print("Error: The config file does not exist.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read("config.ini")
    print("openCuts is running! 💇")

    # Get values from the config file
    SALON_ID = config.get("Opencuts", "salon_id")
    REGIS_API_KEY = config.get("Opencuts", "regis_api_key")
    MY_SERVICE = config.get("Opencuts", "my_service")
    MY_STYLIST = config.get("Opencuts", "my_stylist")

    # Instantiate the class and get some information about the salon
    myStore = opencuts.Salon(SALON_ID, REGIS_API_KEY)
    myStore.get_salon()  # get salon information
    myStore.get_salon_services()  # get all the services the salon offers
    myStore.get_therapists_working()  # get the stylist information

    # look up the ID for the stylist and service
    selected_stylist = myStore.find_stylist_by_name(MY_STYLIST)
    selected_service = myStore.find_service_by_name(MY_SERVICE)

    # get some booking slots for the stylist and service selected
    booking_id = myStore.create_service_booking(selected_service, selected_stylist)
    booking_slots = myStore.get_booking_slot(booking_id)
    # pprint(booking_slots["slots"])
    # Present and select a slot if there are any slots available
    if len(booking_slots) > 0:
        slot_num = 0
        for slot in booking_slots["slots"]:
            slot_num += 1
            print(f"Slot Num {slot_num} - Time Slot {slot['Time'] } Available")
        selected_slot = None
        while selected_slot is None:
            selected_slot = input("Select Slot:")
            selected_slot = booking_slots["slots"][
                selected_slot
            ]  # Assign the selected slot
        print("Selected Slot:" + selected_slot["Time"])
        print("Selecting slot")
        try:
            myStore.reserve_selected_slot()


##DEBUG
# # Show Store Information
# print(
#     "Store ID:" + myStore.store_id,
#     "\n" + "Zentoi_API_Key:" + myStore.zenoti_api_key,
#     "\n" + "POS_TYPE:" + myStore.pos_type,
# )
# # Show Store Services
# print("\nStore Services:\n")
# for service in myStore.store_services:
#     print(
#         f"Service Name: {service['catalog_info']['display_name']}, ID: {service['id']}\n"
#     )
# # Show Store Therapists
# print("Store Therapists")
# for therapist in myStore.therapists:
#     print(
#         f"Therapist Name: {therapist['personal_info']['name']}, ID: {therapist['id']}\n"
#     )
# # Check attendance
# working = []
# for therapist in myStore.therapists:
#     name = therapist["personal_info"]["name"]
#     print(f"Checking if {name} is working today")
#     myStore.get_attendance(name)
#     if myStore.attendance_total > 0:
#         print(f"{name} worked today!")
#         working.append(name)
#     else:
#         print(f"{name} did not work today!")
#     print(f"Attendance Record Total: {myStore.attendance_total}")
#     for attendance_record in myStore.attendance:
#         print(
#             f"Scheduled Checkin: {attendance_record['expected_checkin']}, Scheduled Checkout: {attendance_record['expected_checkout']}\n"
#         )
# print(f"Total Workers today: {working}")
