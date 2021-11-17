import random
import requests
import unittest

from decouple import config

URL = config('URL')
CITIZEN_ID = "1736210545971"


def post_reservation(citizen_id, site_name, vaccine_name):
    return URL + f"/reservation?citizen_id={citizen_id}&site_name={site_name}&vaccine_name={vaccine_name}"


class WCGApiTest(unittest.TestCase):

    def setUp(self):
        """Register citizen to db"""
        requests.delete(URL + f"/registration/{CITIZEN_ID}")
        register = URL + "/registration?" \
                         "name=jacky&" \
                         "surname=ssrw&" \
                         f"citizen_id={CITIZEN_ID}&" \
                         "birth_date=15-10-2000&" \
                         "occupation=student&" \
                         "address=flat land&" \
                         "phone_number=0880545971&" \
                         "is_risk=False"
        response = requests.post(register)
        self.assertEqual(201, response.status_code)
        self.assertEqual("registration success!", response.json().get("feedback"))

    def test_post_reservation(self):
        requests.delete(URL + f"/reservation/{CITIZEN_ID}")
        endpoint = post_reservation(CITIZEN_ID, "OGYH Site", "Pfizer")
        response = requests.post(endpoint)
        self.assertEqual(201, response.status_code)
        self.assertEqual("reservation success!", response.json().get("feedback"))

        response = requests.get(URL + f'/reservation/{CITIZEN_ID}')
        self.assertEqual(200, response.status_code)
        reserve_data = response.json()
        db_data = reserve_data.pop()

        self.assertEqual(CITIZEN_ID, db_data["citizen_id"])
        self.assertEqual("OGYH Site", db_data["site_name"])
        self.assertEqual("Pfizer", db_data["vaccine_name"])

    def test_double_booking(self):
        requests.delete(URL + f"/reservation/{CITIZEN_ID}")
        endpoint = post_reservation(CITIZEN_ID, "vaccine site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(201, response.status_code)
        self.assertEqual("reservation success!", response.json().get("feedback"))

        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)

        response_data = response.json()

        self.assertEqual('reservation failed: there is already a reservation for this citizen',
                         response_data.get("feedback"))

    def test_reserve_no_citizen_in_database(self):
        endpoint = post_reservation(random.randint(1000000000000, 9999999999999), "vaccine site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        response_data = response.json()
        self.assertEqual("reservation failed: citizen ID is not registered", response_data.get("feedback"))

    def test_reserve_blank_citizen_id(self):
        endpoint = post_reservation("", "OGYH Site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        response_data = response.json()
        self.assertEqual("reservation failed: missing some attribute", response_data.get('feedback'))

    def test_reserve_non_number_citizen_id(self):
        endpoint = post_reservation("citizen_id", "OGYH Site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        response_data = response.json()
        self.assertEqual("reservation failed: invalid citizen ID", response_data.get('feedback'))

    def test_reserve_citizen_id_not_13_digit(self):
        endpoint = post_reservation(random.randint(1, 999999999999), "OGYH Site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        response_data = response.json()
        self.assertEqual("reservation failed: invalid citizen ID", response_data.get('feedback'))

    def test_reserve_non_string_site_name(self):
        requests.delete(URL + f"/reservation/{CITIZEN_ID}")
        endpoint = post_reservation(CITIZEN_ID, random.randint(1, 9999999999), "Astra")
        response = requests.post(endpoint)
        self.assertEqual(201, response.status_code)
        self.assertEqual("reservation success!", response.json().get('feedback'))

    def test_reserve_blank_site_name(self):
        requests.delete(URL + f"/reservation/{CITIZEN_ID}")
        endpoint = post_reservation(CITIZEN_ID, "", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        response_data = response.json()
        self.assertEqual('reservation failed: missing some attribute', response_data.get("feedback"))

    def test_random_vaccine(self):
        requests.delete(URL + f"/reservation?citizen_id={CITIZEN_ID}")
        endpoint = post_reservation(CITIZEN_ID, "vaccine site", "all purpose vaccine")
        response = requests.post(endpoint)
        self.assertEqual(200, response.status_code)
        self.assertEqual('reservation failed: invalid vaccine name', response.json().get('feedback'))

    def test_cancel_vaccine_reservation(self):
        requests.delete(URL + f"/reservation/{CITIZEN_ID}")
        endpoint = post_reservation(CITIZEN_ID, "OGYH Site", "Astra")
        response = requests.post(endpoint)
        self.assertEqual(201, response.status_code)
        self.assertEqual("reservation success!", response.json().get('feedback'))

        response = requests.delete(URL + f"/reservation/{CITIZEN_ID}")
        self.assertEqual(200, response.status_code)
        self.assertEqual("cancel reservation success!", response.json().get('feedback'))

    def test_cancel_reservation_no_reservation(self):
        requests.delete(URL + f"/reservation/{CITIZEN_ID}")
        response = requests.delete(URL + f'/reservation/{CITIZEN_ID}')
        self.assertEqual(200, response.status_code)
        self.assertEqual("cancel reservation failed: there is no reservation for this citizen",
                         response.json().get('feedback'))

    def test_cancel_reservation_no_citizen_in_database(self):
        response = requests.delete(URL + f'/reservation/{random.randint(1000000000000, 9999999999999)}')
        self.assertEqual(200, response.status_code)
        self.assertEqual('cancel reservation failed: citizen ID is not registered', response.json().get('feedback'))
