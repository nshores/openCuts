# openCuts 💇 - Automate your Haircuts

**`openCuts`** 💇 is an open-source Python library designed to interface with popular salons using public and private API's. It provides a common interface to the  Zeonti (Supercuts), Regis (Supercuts) and StylewareTouch (Greatclips) API's to provide a seamless experience for retrieving salon services, scheduling appointments, and more. This is meant to be used to build future extensions for Home Assistant, Voice Assistants, etc.

## Disclaimer  ✂

<em>This project relies on private API's hosted by the Regis Corporation, Zenoti, and Greatclips for core functionality. This project is not endorsed or affiliated with those companies in any way. This is a private project not related to my {dayjob} and a completely independent work.

This is meant to be a light hearted attempt at solving a "first-world problem" (Automation of scheduling a hair cut) with Python for fun and learning. This is not meant to interfere with, replace, or degrade the services of any of the parent companies. Please do not use this library in a malicious way.  

This library can break at any time, as the companies can change the way their API functions, revoke the keys, or otherwise restrict the scope of programmatically interacting with their salons. </em>

## Currently Supported Salons 💈

- Supercuts
- Smartstyle
- Costcutters
- First  Choice Haircutters
- Roosters
- Pro-Cuts
- Holiday Hair
- Magicuts

## Future Salon Support

- Greatclips

## Features

- Retrieve salon services.
- Get therapists working at a specified salon on a given date.
- List people scheduled at the salon.
- Check available time slots for a combination of stylist and service.
- Schedule appointments.
- **TODO**: Cancel appointments.
- **TODO**: User account management (Create/Delete Account)
- **TODO**: View upcoming appointments for a user.
- **TODO**: Extend support for all Regis salons

## Installation

Install the Library with `pip`

```bash
pip install opencuts
```

## Configuration

You need to copy and fill out the `config-example` file to `config.ini` with

- The `api.regis.com` API Key obtained from their website
- The `api-booking.regis.com` API key obtained from their website
- Your local `Salon_ID`

The rest of the fields are optional but should be filled out if you want to use this non-interactively (In a script).

```
[Opencuts]
#Required
salon_id = 12345
#Required
regis_api_key = abc123
#required
regis_booking_api_key = abc123

[Preferences]
#All fields optional, will prompt for any missing fields.
email = Edward.Scissorhands@gmail.com
first_name = Edward 
last_name = Scissorhands
phone_number = 5558675309
my_service = Supercut
#If no stylist selected - It will default to "Next Available"
my_stylist = Sweeney
```

## Library Example Usage

To use the library, you will need an API key and salon ID. Here's a quick example to get you started:

```python
from opencuts import salon

SALON_ID = 1234
REGIS_API_KEY = abc123
MY_STYLIST = 
MY_SERVICE = Supercut

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

# Show Store Services
print("\nStore Services:\n")
for service in myStore.store_services:
    print(f"Service Name: {service['catalog_info']['display_name']}, ID: {service['id']}\n")
# Show Store Stylists
print("Store Therapists")
for therapist in myStore.therapists:
    print(f"Therapist Name: {therapist['personal_info']['name']}, ID: {therapist['id']}\n")
```

## Super-Cuts CLI

`supercuts-cli` is a full fledged program meant to interactively and non-interactively create and manage user bookings at a Supercuts or other regis location.  
  
Usage:

```
python supercuts-cli.py
```

## Contribution

Contributions to `openCuts` are welcome. Please ensure that your code adheres to the existing style and that all tests pass. For major changes, please open an issue first to discuss what you would like to change. If possible, I'd like to focus on adding more salons as the first order of business.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.
