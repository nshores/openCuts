# Zenoti/Regis Process Documentation

## Flow to check for a booking

1. Search for your Salon and get the salonID (Manual) and
2. Pass the salonID to https: //api.regiscorp.com/sis/api/salon?salon-number={salonID}.
3. Take your API key (zenoati_api_key) and {zenoti_ID} (Unique Salon Identifier) and get information about the salon services https: //api.zenoti.com/v1/centers/{zeonti_ID}/services?catalog_enabled=true&expand=additional_info&expand=catalog_info&size=100&0=us . Use this to get your {service_id}
4. Get the therapists working at the salon - https: //api.zenoti.com/v1/centers/{zenoti_id}/therapists?date=2023-11-06&0=us
5. Take your {zenoti_ID}, {therapist_id}, {service_id} and a unique identiifer and POST this to https: //api.zenoti.com/v1/bookings?0=us . This returns a unique {slot_id }for the combination of the service and therapist.
6. Take your {slot_id} and GET  https: //api.zenoti.com/v1/bookings/{slot_id}/slots?0=us
7. Available slots for the therapist and service combination will be returned.

## Flow to check current attendance at a salon

1. Search for your Salon and get the salonID (Manual) and
2. Pass the salonID to https: //api.regiscorp.com/sis/api/salon?salon-number={salonID}.
3. Take your API key (zenoati_api_key) and {zenoti_ID} (Unique Salon Identifier) and get information about the salon services https: //api.zenoti.com/v1/centers/{zeonti_ID}/services?catalog_enabled=true&expand=additional_info&expand=catalog_info&size=100&0=us . Use this to get your {service_id}
4. Get the therapists working at the salon - https: //api.zenoti.com/v1/centers/{zenoti_id}/therapists?date=2023-11-06&0=us
5. Take your {therapist_id }and {zenoti_ID } and Perform a GET against <https://api.zenoti.com/v1/employees/{therapist_id}/attendance?center_id={zenoti_ID}&start_date=2023-11-07&end_date=2023-11-07&expand=work_task&0=us>
