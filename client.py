import requests
import json
from bs4 import BeautifulSoup
import re

class NfuClient:
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
        if sch_abbr not in NfuClient.sch_ids:
            res = self.session.get(f"https://house.nfu.edu.tw/{sch_abbr}")
            if res.status_code != 200:
                raise Exception(f"Failed to get sch_ids, status code: {res.status_code}")
            matches = re.findall(r'sch_id&quot;:(\d+)', res.text)
            sch_ids = list(set(int(sch_id) for sch_id in matches if sch_id != '0'))
            NfuClient.sch_ids[sch_abbr] = sch_ids
        return NfuClient.sch_ids[sch_abbr]
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
            json.dump(NfuClient.sch_ids, sch_ids_file, indent=4)

def tuple_to_str(origin: str|tuple[int], destination: str|tuple[int], mode: str) -> str:
    if isinstance(origin, str):
        origin = origin.replace(" ", "")
    if isinstance(destination, str):
        destination = destination.replace(" ", "")
    return f"{origin}_{destination}_{mode}"
class GoogleClient:
    '''
    A class to get data from Google Map routes api
    '''
    # Docs: https://developers.google.com/maps/documentation/routes/compute_route_matrix
    with open("data/google_map.json", "r") as google_map_file:
        google_map = json.load(google_map_file)
    def __init__(self, api_key: str):
        self.api_key = api_key
        return

    def fetch_data(self, origin: str|tuple[int], destination: str|tuple[int], mode: str = "BICYCLE") -> dict:
        if tuple_to_str( origin, destination, mode ) in GoogleClient.google_map:
            return GoogleClient.google_map[{"origin": origin, "destination": destination}]
        url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "duration,distanceMeters"
        }
        body = {
            "origins": [
                {
                    "waypoint": 
                    ({"address":origin} if isinstance(origin, str) else {"location":{"latLng": {"latitude": origin[0], "longitude": origin[1]}}})
                }
            ],
            "destinations": [
                {
                    "waypoint": 
                    ({"address":destination} if isinstance(destination, str) else {"location":{"latLng": {"latitude": destination[0], "longitude": destination[1]}}})
                }
            ],
            "travelMode": mode,
            "units": "METRIC",
            "regionCode": "TW"
        }
        try:
            response = requests.post(url, headers=headers, json=body)
            print(response.text)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            GoogleClient.google_map[tuple_to_str(origin, destination,mode)] = data
            return data 
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    def dump_data(self,file_path: str = "data/google_map.json"):
        with open(file_path, "w") as google_map_file:
            json.dump(GoogleClient.google_map, google_map_file, indent=4)
        return 
