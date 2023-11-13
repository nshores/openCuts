import logging
import sys
from datetime import datetime
import requests
import uuid
import os

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
         - Support for all pos_types



"""
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

POS_TYPES = [
    "Zenoti",
    "Supersalon",
    "opensalonpro",
]  # Only Zenoti supported for now. Other POS_TYPES require calling api-booking.regiscorp.com instead of zentoi directly


BASE_REGIS_API_URL = "https://api.regiscorp.com"
BASE_REGIS_BOOKING_API_URL = "https://api-booking.regiscorp.com/v1/"
ZENOTI_API_URL = "https://api.zenoti.com/v1/"


class RegisSalon:
    def __init__(self, salon_id, regis_api_key, regis_boking_api_key):
        """
        Initialize a new Salon instance with specific salon ID and Regis API key.

        Args:
            salon_id (str): The unique identifier for a specific salon.
            regis_api_key (str): API key used for authorization with Regis properties' services.

        This method initializes the Salon instance with the provided salon ID and Regis API key. It also sets default values for various instance properties such as API URLs, store ID, POS type, available services, and the current date.
        """
        self.salon_id = salon_id
        self.regis_api_key = regis_api_key
        self.regis_api_booking_key = regis_boking_api_key
        self.base_regis_api_url = BASE_REGIS_API_URL
        self.base_regis_booking_api_url = BASE_REGIS_BOOKING_API_URL
        self.zenoti_api_url = ZENOTI_API_URL
        self.store_id = None
        self.pos_type = None
        self.store_services = None
        self.today_date = datetime.now().strftime("%Y-%m-%d")
        self.therapists = []
        self.storeaddress = None
        self.storename = None
        self.storephone = None

        # UUID Logic
        # Generate and store UUID only once
        if not os.path.exists("device_uuid"):
            with open("device_uuid", "w") as f:
                device_uuid = uuid.uuid4()
                self.device_uuid_str = str(
                    device_uuid
                )  # Convert the UUID object to a string
                f.write(self.device_uuid_str)
        f = open("device_uuid", "r")
        self.device_uuid_str = str(f.read())
        f.close()

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
        # Get some additonal info if this is a differnet POS system
        if self.pos_type.lower() != "zenoti":
            headers = {
                "x-api-key": self.regis_api_booking_key,
            }
            payload = {
                "salonId": self.salon_id,
                "siteId": "1",
            }
            logging.info("Getting Store Details")
            request_url = self.base_regis_booking_api_url + "getsalondetails"
            try:
                response = requests.post(request_url, headers=headers, json=payload)
                response = response.json()
                self.storeaddress = response["Salon"]["address"]
                self.storename = response["Salon"]["name"]
                self.storephone = response["Salon"]["phonenumber"]
                self.storephone = self.storephone.replace("-", "")
            except Exception as error:
                logging.error("Error Store Details %s", error)
                return None

    def get_salon_services(self):
        """
        Retrieve salon information using its unique identifier and set essential details.

        This method makes an API request to retrieve salon information, including the Zenoti API key, store ID, and POS type, using the salon's unique identifier.

        Returns:
            tuple: A tuple containing the Zenoti API key, store ID, and POS type if the request is successful, otherwise None.
        """
        if self.pos_type.lower() == "zenoti":
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
        # Handle a non-zenoti type store
        headers = {
            "x-api-key": self.regis_api_booking_key,
        }
        payload = {"salonId": self.salon_id, "siteId": 1}
        logging.info("Getting Salon Services")
        request_url = self.base_regis_booking_api_url + "getsalondetails"
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            self.store_services = response.json().get("Services", None)
        except Exception as error:
            logging.error("Error Geting Store Services %s", error)
            return None
        return self.store_services

    def get_therapists_working(self):
        if self.pos_type.lower() == "zenoti":
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
        # Handle a non-zenoti type store
        headers = {
            "x-api-key": self.regis_api_booking_key,
        }
        payload = {"salonId": self.salon_id, "siteId": 1}
        logging.info("Getting Salon Stylists")
        request_url = self.base_regis_booking_api_url + "getsalondetails"
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            self.therapists = response.json().get("Stylists", None)
        except Exception as error:
            logging.error("Error Geting Store Stylists %s", error)
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
            if "personal_info" in stylist:
                if (
                    stylist["personal_info"]["first_name"].lower()
                    == stylist_name.lower()
                ):
                    return stylist
            else:
                stylist["name"].lower() == stylist_name.lower()
                return stylist
        return None  # If no stylist found with that name

    def find_service_by_name(self, service_name):
        for service in self.store_services:
            if "catalog_info" in service:
                if (
                    service["catalog_info"]["display_name"].lower()
                    == service_name.lower()
                ):
                    return service
            else:
                for category in self.store_services:
                    for service in category["services"]:
                        if service["service"] == service_name:
                            return service["id"]
                return None
        return None  # If no service found with that name

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
        request_url = self.zenoti_api_url + "bookings"
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
        logging.info("Getting Booking Slot")
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
        logging.info("Retriving Guest Detail")
        request_url = self.zenoti_api_url + "guests/search"
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
        request_url = self.zenoti_api_url + "guests"
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
        logging.info("Retriving Guest Appointments")
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
        logging.info("Cancelling Appointment")
        request_url = self.zenoti_api_url + f"invoices/{invoice_id}/cancel"
        try:
            response = requests.put(request_url, headers=headers, json=payload)
            response = response.json()
            return response
        except Exception as error:
            logging.error("Error Cancelling Appointment %s", error)
            return None

    # for the service you want, who's availble?
    def get_availability_of_salon(self, serviceid):
        # input needs to be a string
        # Handle a non-zenoti type store
        headers = {
            "x-api-key": self.regis_api_booking_key,
        }
        payload = {
            "salonId": self.salon_id,
            "serviceIds": serviceid,
            "siteId": "1",
            "date": datetime.now().strftime("%Y%m%d"),
        }
        logging.info("Getting Salon Availability")
        request_url = self.base_regis_booking_api_url + "getavailabilityofsalon"
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            self.availability = response.json()
        except Exception as error:
            logging.error("Error Geting Store availability %s", error)
            return None
        return self.availability

    def add_check_in(
        self,
        firstname: str,
        lastname: str,
        phonenumber: str,
        serviceid: str,
        services: list,
        stylistid: str,
        stylistname: str,
        time: str,
        emailaddress: str,
    ):
        """
        Add a check-in for a customer at a salon. The sourceID is temporary value generated by a function in the browser normally, but
        here we are using a static value which seems to work fine.

        Args:
            firstname (str): The first name of the customer.
            lastname (str): The last name of the customer.
            phonenumber (str): The phone number of the customer.
            serviceid (str): The ID of the service being availed.
            services (list): A list of services being availed.
            stylistid (str): The ID of the stylist chosen.
            stylistname (str): The name of the stylist chosen.
            time (str): The time of the appointment.
            date (datetime): The date of the appointment.
            emailaddress (str): The email address of the customer.

        Returns:
            checkin_reuslt[Dict[]]: A dict containning the results of the checkin.
            checkin_id(str): A strin containing a unique checkin_id.


        Raises:
            Exception: If there's an error in the API request.

        This function sends a request to the salon's booking system to add a check-in with the provided details.
        """
        device_uuid = "SC-W-" + self.device_uuid_str
        headers = {
            "x-api-key": self.regis_api_booking_key,
        }
        payload = {
            "firstName": firstname,
            "lastName": lastname,
            "phoneNumber": phonenumber,
            "salonId": int(self.salon_id),
            "serviceId": serviceid,
            "services": services,
            "siteId": "1",
            "source": "SCWEB",
            "sourceId": device_uuid,
            "storeAddress": self.storeaddress,
            "storeName": self.storename,
            "storePhone": self.storephone,
            "stylistId": str(stylistid),
            "stylistName": stylistname,
            "time": time,
            "date": int(datetime.now().strftime("%Y%m%d")),
            "profileId": None,
            "emailAddress": emailaddress,
            "gender": 0,
        }
        logging.info("Checking in")
        request_url = self.base_regis_booking_api_url + "addcheckin"
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            checkin = response.json()
            checkin_result = response.json().get("apiResult", None)
            checkin_id = response.json().get("checkinId", None)
        except Exception as error:
            logging.error("Error Checking in %s", error)
            return None
        return checkin_result, checkin_id

    def get_check_in_by_source(self):
        headers = {
            "x-api-key": self.regis_api_booking_key,
        }
        payload = {
            "sourceId": "SC-W-" + self.device_uuid_str,
            "profileId": None,
        }
        logging.info("Getting Checkins")
        request_url = self.base_regis_booking_api_url + "getcheckinbysource"
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            checkins = response.json()
        except Exception as error:
            logging.error("Error Geting Checkins %s", error)
            return None
        return checkins

    def cancel_checkin(self, checkinid):
        """Cancels a checkin using the api-booking regis API

        Args:
            checkinid (_type_): _description_

        Returns:
            _type_: _description_
        """
        headers = {
            "x-api-key": self.regis_api_booking_key,
        }
        payload = {
            "checkinId": checkinid,
        }
        logging.info("Cancelling checkin")
        request_url = self.base_regis_booking_api_url + "cancelcheckin"
        try:
            response = requests.post(request_url, json=payload, headers=headers)
            cancel_checkin = response.json()
        except Exception as error:
            logging.error("Error Cancelling Checkin %s", error)
            return None
        return cancel_checkin
