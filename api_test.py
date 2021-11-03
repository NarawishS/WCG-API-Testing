"""Narawish Sangsiriwut 6210545971"""
import random

import requests
import unittest

URL = "https://wcg-apis.herokuapp.com"
CITIZEN_ID = "1736210545971"


def reserve_path(citizen_id, site_name, vaccine_name):
    return URL + f"/reservation?citizen_id={citizen_id}&site_name={site_name}&vaccine_name={vaccine_name}"


class WCGApiTest(unittest.TestCase):

    def setUp(self):
        requests.delete(URL + f"/citizen?citizen_id={CITIZEN_ID}")
        register = URL + "/registration?" \
                         "name=jacky&" \
                         "surname=ssrw&" \
                         f"citizen_id={CITIZEN_ID}&" \
                         "birth_date=15-10-2000&" \
                         "occupation=student&" \
                         "address=flat land"
        response = requests.post(register)
        self.assertEqual({"feedback": "registration success!"}, response.json())

    def test_post_reservation(self):
        requests.delete(URL + f"/reservation?citizen_id={CITIZEN_ID}")
        endpoint = reserve_path(CITIZEN_ID, "OGYH Site", "Pfizer")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"feedback": "reservation success!"}, response.json())

        response = requests.get(URL + f'/reservation')
        self.assertEqual(200, response.status_code)
        reserve_data = response.json()
        post_data = reserve_data.pop()

        self.assertEqual(CITIZEN_ID, post_data.get("citizen_id"))
        self.assertEqual("OGYH Site", post_data.get("site_name"))
        self.assertEqual("Pfizer", post_data.get("vaccine_name"))

    def test_double_booking(self):
        requests.delete(URL + f"/reservation?citizen_id={CITIZEN_ID}")
        endpoint = reserve_path(CITIZEN_ID, "vaccine site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"feedback": "reservation success!"}, response.json())

        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)

        response_data = response.json()

        self.assertEqual('reservation failed: there is already a reservation for this citizen',
                         response_data.get('feedback'))

    def test_reserve_no_citizen_in_database(self):
        endpoint = reserve_path(random.randint(1000000000000, 9999999999999), "vaccine site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        response_data = response.json()
        self.assertEqual("reservation failed: citizen ID is not registered", response_data.get("feedback"))

    def test_reserve_blank_citizen_id(self):
        endpoint = reserve_path("", "OGYH Site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        response_data = response.json()
        self.assertEqual("reservation failed: missing some attribute", response_data.get('feedback'))

    def test_reserve_non_number_citizen_id(self):
        endpoint = reserve_path("citizen_id", "OGYH Site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        response_data = response.json()
        self.assertEqual("reservation failed: invalid citizen ID", response_data.get('feedback'))

    def test_reserve_citizen_id_not_13_digit(self):
        endpoint = reserve_path(random.randint(1, 999999999999), "OGYH Site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        response_data = response.json()
        self.assertEqual("reservation failed: invalid citizen ID", response_data.get('feedback'))

    def test_reserve_non_string_site_name(self):
        requests.delete(URL + f"/reservation?citizen_id={CITIZEN_ID}")
        endpoint = reserve_path(CITIZEN_ID, random.randint(1, 9999999999), "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"feedback": "reservation success!"}, response.json())

    def test_reserve_blank_site_name(self):
        requests.delete(URL + f"/reservation?citizen_id={CITIZEN_ID}")
        endpoint = reserve_path(CITIZEN_ID, "", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        response_data = response.json()
        self.assertEqual('reservation failed: missing some attribute', response_data.get("feedback"))

    def test_random_vaccine(self):
        requests.delete(URL + f"/reservation?citizen_id={CITIZEN_ID}")
        endpoint = reserve_path(CITIZEN_ID, "vaccine site", "all purpose vaccine")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"feedback": "report failed: invalid vaccine name"}, response.json())

    def test_cancel_vaccine_reservation(self):
        requests.delete(URL + f"/reservation?citizen_id={CITIZEN_ID}")
        endpoint = reserve_path(CITIZEN_ID, "OGYH Site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"feedback": "reservation success!"}, response.json())

        response = requests.delete(URL + f"/reservation?citizen_id={CITIZEN_ID}")
        self.assertEqual(200, response.status_code)
        self.assertEqual({"feedback": "cancel reservation successfully"}, response.json())

    def test_cancel_reservation_no_param(self):
        response = requests.delete(URL + "/reservation")
        self.assertEqual(400, response.status_code)

    def test_cancel_reservation_blank_citizen_id(self):
        response = requests.delete(URL + "/reservation?citizen_id=")
        self.assertEqual(200, response.status_code)
        self.assertEqual({"feedback": "cancel reservation failed: no citizen id is given"}, response.json())

    def test_cancel_reservation_no_reservation(self):
        requests.delete(URL + f"/reservation?citizen_id={CITIZEN_ID}")
        response = requests.delete(URL + f'/reservation?citizen_id={CITIZEN_ID}')
        self.assertEqual(200, response.status_code)
        self.assertEqual({"feedback": "cancel reservation failed: there is no reservation for this citizen"},
                         response.json())

    def test_cancel_reservation_no_citizen_in_database(self):
        response = requests.delete(URL + f'/reservation?citizen_id={random.randint(1000000000000, 9999999999999)}')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'feedback': 'reservation failed: citizen ID is not registered'}, response.json())
