import unittest
from unittest.mock import patch
from opencuts import Salon
import requests


class TestSalon(unittest.TestCase):
    def setUp(self):
        self.salon = Salon(
            salon_id="1234",
            regis_api_key="12345678abc",
        )

    @patch("opencuts.requests.get")
    def test_get_salon(self, mock_get):
        mock_get.return_value.json.return_value = {
            "zenoti_api_key": "dummy_api_key",
            "zenoti_id": "dummy_id",
            "pos_type": "any_pos",
        }
        api_key, zenoti_id, pos_type = self.salon.get_salon()
        # Assertions to verify that the response is processed correctly
        self.assertEqual(api_key, "dummy_api_key")
        self.assertEqual(zenoti_id, "dummy_id")
        self.assertEqual(pos_type, "any_pos")

    @patch("opencuts.requests.get")
    def test_get_salon_api_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException

        result = self.salon.get_salon()
        self.assertIsNone(result)

    # Additional tests for other methods like find_stylist_by_name, get_therapists_working, etc.


if __name__ == "__main__":
    unittest.main()
