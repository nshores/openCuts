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
        - Get available time slots for combination of stylist and service
        - schedule appointment (reserve slot)
        - search for a user
        - create a user
        - cancel appointment for user
        - see upcoming appointments for user
        #TODO - Support for all pos_types



"""
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
        """
        Initialize a new Salon instance with specific salon ID and Regis API key.

        Args:
            salon_id (str): The unique identifier for a specific salon.
            regis_api_key (str): API key used for authorization with Regis properties' services.

        This method initializes the Salon instance with the provided salon ID and Regis API key. It also sets default values for various instance properties such as API URLs, store ID, POS type, available services, and the current date.
        """
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
        """
        Retrieve salon information using its unique identifier and set essential details.

        This method makes an API request to retrieve salon information, including the Zenoti API key, store ID, and POS type, using the salon's unique identifier.

        Returns:
            tuple: A tuple containing the Zenoti API key, store ID, and POS type if the request is successful, otherwise None.
        """
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
            return None
        return self.zenoti_api_key, self.store_id, self.pos_type

    def get_salon_services(self):
        """
        Retrieve salon information using its unique identifier and set essential details.

        This method makes an API request to retrieve salon information, including the Zenoti API key, store ID, and POS type, using the salon's unique identifier.

        Returns:
            tuple: A tuple containing the Zenoti API key, store ID, and POS type if the request is successful, otherwise None.
        """
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
            return None
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
            return None
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
            return None
        return self.attendance, self.attendance_total

    def find_stylist_by_name(self, stylist_name):
        for stylist in self.therapists:
            if stylist["personal_info"]["first_name"].lower() == stylist_name.lower():
                return stylist
        return None  # If no stylist found with that name

    def find_service_by_name(self, service_name):
        for service in self.store_services:
            if service["catalog_info"]["display_name"].lower() == service_name.lower():
                return service
        return None  # If no stylist found with that name

    # https://docs.zenoti.com/reference/create-a-service-booking
    def create_service_booking(self, service, stylist, guest_id=None):
        """This method expects a service and stylist object.
        It will return a unique service ID that can be passed to get_booking_slot
        to get an object containing available booking slots for the combination of an service, stylist, and location.
        """
        # This defaults to "next available" if no stylist is defined.
        if not stylist:
            stylist = {}
            stylist["personal_info"] = {}
            stylist["personal_info"]["gender"] = "0"
            stylist["id"] = ""
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        payload = {
            "date": self.today_date,
            "is_only_catalog_employes": True,
            "center_id": self.store_id,
            "guests": [
                {
                    # Guest ID should be set when ready to mark a reservation.
                    "id": guest_id,
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
            return None
        return booking_id

    # Take your {booking_id} and GET  https: //api.zenoti.com/v1/bookings/{slot_id}/slots?0=us
    def get_booking_slot(self, slot_id):
        slot_id = slot_id["id"]
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        logging.info(f"Getting Booking Slot")
        request_url = self.zenoti_api_url + f"bookings/{slot_id}/slots"
        try:
            response = requests.get(request_url, headers=headers)
            booking_slots = response.json()
            if len(booking_slots["slots"]) < 1:
                print("No Booking slots available for the time and stylist requested")
                booking_slots = 0
                return {}
            return booking_slots
        except Exception as error:
            logging.error("Error Getting booking_slots %s", error)
            return None

    # reserve a slot
    def reserve_selected_slot(self, selected_slot, booking_id):
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        payload = {"slot_time": selected_slot["Time"]}
        request_url = self.zenoti_api_url + f"bookings/{booking_id['id']}/slots/reserve"
        logging.info("Trying to reserve your slot")
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            response = response.json()
        except Exception as error:
            logging.error("Error Reserving Slot %s", error)
            return None
        return response

    # Confirm your slot
    def confirm_selected_slot(self, booking_id):
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        payload = {
            "notes": "",
            "group_name": "",
        }
        request_url = self.zenoti_api_url + f"bookings/{booking_id['id']}/slots/confirm"
        logging.info("Trying to confirm your slot")
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            response = response.json()
        except Exception as error:
            logging.error("Error Confirming Slot %s", error)
            return None
        return response

    # retrive guest details to get a guest ID or create a new one
    # https://docs.zenoti.com/reference/search-for-a-guest
    def retrive_guest_detail(self, first_name=None, last_name=None, phone=None):
        params = {
            "center_id": self.store_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
        }
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        logging.info(f"Retriving Guest Detail")
        request_url = self.zenoti_api_url + f"guests/search"
        try:
            response = requests.get(request_url, headers=headers, params=params)
            guest = response.json()
            if len(guest["guests"]) < 1:
                print("No guest records returned")
                return {}
            return guest["guests"][
                -1
            ]  # Sometimes guests have multiple records so just return the latest one
        except Exception as error:
            logging.error("Error Getting Guest Detail %s", error)
            return None

    # Create a user account
    def create_account(self, first_name, last_name, phone_number):
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        payload = {
            "center_id": self.store_id,
            "personal_info": {
                "first_name": first_name,
                "last_name": last_name,
                "mobile_phone": {
                    "country_code": 225,  # America
                    "number": phone_number,
                },
                "email": "",
                "gender": -1,
            },
            "preferences": {
                "receive_transactional_email": True,  # Get upadtes about your appointment via email
                "receive_transactional_sms": True,  # Get upadtes about your appointment via sms
                "receive_marketing_email": False,  # Don't spam me
                "receive_marketing_sms": False,  # more spam
            },
        }
        request_url = self.zenoti_api_url + f"guests"
        logging.info("Trying to Create an account")
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            account = response.json()
        except Exception as error:
            logging.error("Creating Account %s", error)
            return None
        return account

    # Check appointments for user
    def get_appointments(self, guest_id, start_date=None, end_date=None):
        if start_date is None:
            start_date = self.today_date
        if end_date is None:
            end_date = self.today_date
        params = {
            "start_date": start_date,
            "end_date": end_date,
        }
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        logging.info(f"Retriving Guest Appointments")
        request_url = self.zenoti_api_url + f"guests/{guest_id}/appointments"
        try:
            response = requests.get(request_url, headers=headers, params=params)
            appointments = response.json()
            if len(appointments["appointments"]) < 1:
                # print("No guest appointments returned")
                return {}
            return appointments["appointments"]
        except Exception as error:
            logging.error("Error Getting Guest Appointments %s", error)
            return None

    # cancel appointsments for user
    def cancel_appointment(self, invoice_id):
        headers = {
            "Authorization": "apikey " + self.zenoti_api_key,
        }
        payload = {
            "comments": "Cannot Attend",
        }
        logging.info(f"Cancelling Appointment")
        request_url = self.zenoti_api_url + f"invoices/{invoice_id}/cancel"
        try:
            response = requests.put(request_url, headers=headers, payload=payload)
            response = response.json()
            return response
        except Exception as error:
            logging.error("Error Cancelling Appointment %s", error)
            return None

    # implement get_or_create_account
