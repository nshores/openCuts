import logging
import sys
from datetime import datetime

import requests

""" openCuts - an opensource library for interacting with Regis Properties Salons. Currentley supports Supercuts but in the future will support other Regis properties that use the same API's. 
    - User is expected to include the regis_api_key, and salon_id
    - Features:
        - Get Salon Services
        - Get Therapists working at store at a specified date
        - Get people on schedule for the specified salon and date
        #TODO - Get available time slots for combination of stylist and service
        #TODO - schedule appointment (reserve slot)
        #TODO - cancel appointment for user
        #TODO - see upcoming appointments for user
        #TODO - Support for all pos_types



"""

# # Flow to create a booking
# 1. Search for your Salon and get the salonID (Manual) and
# 2. Pass the salonID to https: //api.regiscorp.com/sis/api/salon?salon-number={salonID}.
# 3. Take your API key (zenoati_api_key) and {zenoti_ID} (Unique Salon Identifier) and get information about the salon services https: //api.zenoti.com/v1/centers/{zeonti_ID}/services?catalog_enabled=true&expand=additional_info&expand=catalog_info&size=100&0=us . Use this to get your {service_id}
# 4. Get the therapists working at the salon - https: //api.zenoti.com/v1/centers/{zenoti_id}/therapists?date=2023-11-06&0=us
# 5. Take your {zenoti_ID}, {therapist_id}, {service_id} and a unique identiifer and POST this to https: //api.zenoti.com/v1/bookings?0=us . This returns a unique {slot_id }for the combination of the service and therapist.
# 6. Take your {booking_id} and GET  https: //api.zenoti.com/v1/bookings/{slot_id}/slots?0=us
# 7. Available slots for the therapist and service combination will be returned.
# 8. POST a slot to reserve a booking.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

POS_TYPES = [
    "Zenoti",
    "Supersalon",
    "opensalonpro",
]  # Only Zenoti supported for now. Other POS_TYPES require calling api-booking.regiscorp.com instead of zentoi directly (good)


BASE_REGIS_API_URL = "https://api.regiscorp.com"
ZENOTI_API_URL = "https://api.zenoti.com/v1/"


class Salon:
    def __init__(self, salon_id, regis_api_key):
        self.salon_id = salon_id
        self.regis_api_key = regis_api_key
        self.base_regis_api_url = BASE_REGIS_API_URL
        self.zenoti_api_url = ZENOTI_API_URL
        self.store_id = None
        self.pos_type = None
        self.store_services = None
        self.today_date = datetime.now().strftime("%Y-%m-%d")
        self.therapists = []

    def get_salon(self):
        headers = {
            "Authorization": self.regis_api_key,
        }
        params = {"salon-number": self.salon_id}
        logging.info("Getting Zenoti API Key")
        request_url = self.base_regis_api_url + "/sis/api/salon?" + self.salon_id
        try:
            response = requests.get(request_url, headers=headers, params=params)
            self.zenoti_api_key = response.json().get("zenoti_api_key", None)
            self.store_id = response.json().get("zenoti_id", None)
            self.pos_type = response.json().get("pos_type", None)
        except Exception as error:
            logging.error("Error getting Zenoti API Key %s", error)
            sys.exit(1)
        return self.zenoti_api_key, self.store_id, self.pos_type

    def get_salon_services(self):
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        logging.info("Getting Salon Services")
        request_url = (
            self.zenoti_api_url
            + f"centers/{self.store_id}/services?catalog_enabled=true&expand=additional_info&expand=catalog_info&size=100&0=us"
        )
        try:
            response = requests.get(request_url, headers=headers)
            self.store_services = response.json().get("services", None)
        except Exception as error:
            logging.error("Error Geting Store Services %s", error)
            sys.exit(1)
        return self.store_services

    def get_therapists_working(self):
        params = {"date": self.today_date}
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        logging.info("Getting Salon Therapists")
        request_url = self.zenoti_api_url + f"centers/{self.store_id}/therapists"
        try:
            response = requests.get(request_url, headers=headers, params=params)
            self.therapists = response.json().get("therapists", None)
        except Exception as error:
            logging.error("Error Geting Store therapists %s", error)
            sys.exit(1)
        return self.therapists

    def get_attendance(self, name):
        for person in self.therapists:
            # check if the name key is present
            if person["personal_info"]["name"].lower() == name.lower():
                employee_id = person["id"]
        params = {
            "center_id": self.store_id,
            "start_date": self.today_date,
            "end_date": self.today_date,
        }
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        logging.info("Getting Therapist Attendance")
        request_url = self.zenoti_api_url + f"employees/{employee_id}/attendance"
        try:
            response = requests.get(request_url, headers=headers, params=params)
            self.attendance = response.json().get("attendance", None)
            self.attendance_total = response.json().get("total_records", None)
        except Exception as error:
            logging.error("Error Geting Store Therapist Attendance %s", error)
            sys.exit(1)
        return self.attendance, self.attendance_total

    def find_stylist_by_name(self, stylist_name):
        for stylist in self.therapists:
            if stylist["personal_info"]["name"].lower() == stylist_name.lower():
                return stylist
        return None  # If no stylist found with that name

    def find_service_by_name(self, service_name):
        for service in self.store_services:
            if service["catalog_info"]["display_name"].lower() == service_name.lower():
                return service
        return None  # If no stylist found with that name

    # https://docs.zenoti.com/reference/create-a-service-booking
    def create_service_booking(self, service, stylist):
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        payload = {
            "date": self.today_date,
            "is_only_catalog_employes": True,
            "center_id": self.store_id,
            "guests": [
                {
                    "id": "b216878c-727a-4c77-a2e8-6d899855952c",
                    "items": [
                        {
                            "item": {"id": service["id"]},
                            "therapist": {
                                "id": stylist["id"],
                                "Gender": stylist["personal_info"]["gender"],
                            },
                        }
                    ],
                }
            ],
        }
        logging.info("Getting Service booking_id")
        request_url = self.zenoti_api_url + f"bookings"
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            booking_id = response.json()
        except Exception as error:
            logging.error("Error Getting service_id %s", error)
            sys.exit(1)
        return booking_id

    def get_booking_slot(self, slot_id):
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        payload = {
            "date": self.today_date,
            "is_only_catalog_employes": True,
            "center_id": self.store_id,
            "guests": [
                {
                    "id": "b216878c-727a-4c77-a2e8-6d899855952c",
                    "items": [
                        {
                            "item": {"id": service["id"]},
                            "therapist": {
                                "id": stylist["id"],
                                "Gender": stylist["personal_info"]["gender"],
                            },
                        }
                    ],
                }
            ],
        }
        logging.info("Getting Service booking_id")
        request_url = self.zenoti_api_url + f"bookings"
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            booking_id = response.json()
        except Exception as error:
            logging.error("Error Getting service_id %s", error)
            sys.exit(1)
        return booking_id
