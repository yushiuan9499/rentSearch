import requests
import json
from bs4 import BeautifulSoup
import re

class Client:
    '''
    A class to get house data from NFU
    '''
    with open("cache/sch_ids.json", "r") as sch_ids_file:
        sch_ids = json.load(sch_ids_file)
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
            "Accept": "application/json, text/plain, */*",
            "X-CSRF-TOKEN": None,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json;charset=utf-8"
        }

    def get_sch_ids(self,sch_abbr: str) -> list[int]:
        if sch_abbr not in Client.sch_ids:
            res = self.session.get(f"https://house.nfu.edu.tw/{sch_abbr}")
            if res.status_code != 200:
                raise Exception(f"Failed to get sch_ids, status code: {res.status_code}")
            matches = re.findall(r'sch_id&quot;:(\d+)', res.text)
            sch_ids = list(set(int(sch_id) for sch_id in matches if sch_id != '0'))
            Client.sch_ids[sch_abbr] = sch_ids
        return Client.sch_ids[sch_abbr]
    def get_csrf_token(self):
        # Get CSRF token
        # <meta name="csrf-token" content="token_value">
        url = "https://house.nfu.edu.tw/NCKU" # Root can't get csrf token
        res = self.session.get(url, headers=self.headers)
        if res.status_code != 200:
            raise Exception(f"Failed to get CSRF token, status code: {res.status_code}")
        soup = BeautifulSoup(res.text, "html.parser")
        self.headers["X-CSRF-TOKEN"] = soup.find("meta", attrs={"name": "csrf-token"})["content"]
        return 
    def get_house_data_by_id(self,sch_ids: list[int]) -> dict:
        '''
            Get house data from NFU
        '''
        if self.headers["X-CSRF-TOKEN"] is None:
            self.get_csrf_token()
        url = "https://house.nfu.edu.tw/data/house"
        data = {"arrSchId": sch_ids}
        try:
            response = self.session.post(url, headers=self.headers, json=data)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

    def get_house_data_by_abbr(self, sch_abbr: str) -> dict:
        sch_ids = self.get_sch_ids(sch_abbr)
        return self.get_house_data_by_id(sch_ids)
    def dump_sch_ids(self):
        with open("cache/sch_ids.json", "w") as sch_ids_file:
            json.dump(Client.sch_ids, sch_ids_file, indent=4)
