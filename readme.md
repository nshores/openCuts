# openCuts

`openCuts` is an open-source library designed to interface with Regis Properties Salons, initially supporting Supercuts with plans to include other Regis properties in the future. It leverages the Regis API to provide a seamless experience for retrieving salon services, scheduling appointments, and more.

## Features

- Retrieve salon services.
- Get therapists working at a specified salon on a given date.
- List people scheduled at the salon.
- Check available time slots for a combination of stylist and service.
- **TODO**: Schedule appointments.
- **TODO**: Cancel appointments.
- **TODO**: View upcoming appointments for a user.
- **TODO**: Extend support for all `pos_types`.

## Installation

To install the library, clone this repository and include it in your project.

```bash
git clone https://github.com/nshores/openCuts.git
```

## Usage

To use the library, you will need an API key and salon ID. Here's a quick example to get you started:

```python
from openCuts import Salon

# Initialize the salon with your salon_id and API key
salon = Salon(salon_id="your_salon_id", regis_api_key="your_api_key")

# Get salon services
services = salon.get_salon_services()

# Get therapists working at the salon
therapists = salon.get_therapists_working()

# Retrieve available booking slots
booking_slots = salon.get_booking_slot(slot_id="your_slot_id")

# More functionalities can be added following the above pattern
```

## Contribution

Contributions to `openCuts` are welcome. Please ensure that your code adheres to the existing style and that all tests pass. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.

## Acknowledgments

- Regis Corporation for providing the APIs.
- All contributors who help in maintaining and extending this project.
