import requests
import json
from bs4 import BeautifulSoup
import re
import time
from lxml import html

def tuple_to_str(origin: str|tuple[float,float], destination: str|tuple[float,float], mode: str) -> str:
    if isinstance(origin, str):
        origin = origin.replace(" ", "")
    if isinstance(destination, str):
        destination = destination.replace(" ", "")
    return f"{origin}_{destination}_{mode}"
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

    def get_precise_data(self,house_id: int) -> dict:
        '''
            Get precise data from NFU
        '''
        if self.headers["X-CSRF-TOKEN"] is None:
            self.get_csrf_token()
        # get html from house id
        url = f"https://house.nfu.edu.tw/NCKU/{house_id}"
        res = self.session.get(url, headers=self.headers)
        if res.status_code != 200:
            raise Exception(f"Failed to get precise data, status code: {res.status_code}")
        # Parse the HTML content
        content = html.fromstring(res.content)
        # Extract the data using XPath
        ret = {}
        ret["no_smoking"] = (content.xpath("/html/body/main/div[2]/div/div[1]/div[4]/div[6]/div[4]/text()")[0] == "是")
        ret["room_data"] = [
            ' '.join(text.split())
            for text in content.xpath("/html/body/main/div[2]/div/div[1]/div[4]/div[1]/div[2]/div/div/text()")
            if text.strip() != ''
        ]
        ret["identity_limit"] = [
            ' '.join(text.split())
            for text in content.xpath("/html/body/main/div[2]/div/div[1]/div[4]/div[7]/div[4]/text()")
            if text.strip() != ''
        ]
        ret["equipment"] = content.xpath('//div[@class="clearfix"]/span[@class="rh-criteria-more"]/text()')
        return ret

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
    def get_house_data_by_id(self,sch_ids: list[int]) -> list[dict]|None:
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
            for house in data:
                precise_data = self.get_precise_data(house["house_id"])
                house.update(precise_data)
            return data
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

    def get_house_data_by_abbr(self, sch_abbr: str) -> list[dict]|None:
        sch_ids = self.get_sch_ids(sch_abbr)
        return self.get_house_data_by_id(sch_ids)
    def dump_sch_ids(self):
        with open("cache/sch_ids.json", "w") as sch_ids_file:
            json.dump(NfuClient.sch_ids, sch_ids_file, indent=4)

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

    def fetch_data(self, origin: str|tuple[float,float], destination: str|tuple[float,float], mode: str = "BICYCLE") -> dict|None:
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
        with open(file_path, "w",encoding="utf-8") as google_map_file:
            json.dump(GoogleClient.google_map, google_map_file, indent=4)
        return 

class OSRMClient:
    with open("data/osrm.json", "r") as osrm_file:
        osrm_data = json.load(osrm_file)
    def __init__(self, host="localhost", port=5000):
        self.base_url = f"http://{host}:{port}/route/v1"

    def route(self, origin: tuple[float,float], destination: tuple[float,float] ,mode: str) -> dict:
        """
        :param mode: 'car', 'bicycle', or 'motorcycle'
        :param start: (lon, lat)
        :param end: (lon, lat)
        :return: dict with duration (sec) and distance (meters)
        """
        if tuple_to_str( origin, destination, mode ) in GoogleClient.google_map:
            return OSRMClient.osrm_data[tuple_to_str(origin, destination,mode)]
        coords = f"{origin[0]},{origin[1]};{destination[0]},{destination[1]}"
        url = f"{self.base_url}/{mode}/{coords}"
        params = {
            "overview": "false",
            "alternatives": "false",
            "steps": "false"
        }
        resp = requests.get(url, params=params)
        data = resp.json()
        if "routes" in data and len(data["routes"]) > 0:
            route = data["routes"][0]
            OSRMClient.osrm_data[tuple_to_str(origin, destination,mode)] = {
                "distance": route["distance"], 
                "duration": route["duration"]
            }
            return {
                "distance": float(route["distance"]),
                "duration": float(route["duration"])
            }
        else:
            raise Exception(f"Routing error: {data}")
    def dump_data(self,file_path: str = "data/osrm.json"):
        with open(file_path, "w",encoding="utf-8") as osrm_file:
            json.dump(OSRMClient.osrm_data, osrm_file, indent=4)
        return

# Use ArcGIS APT to geocode
class ArcGISClient:
    '''
    A class to get data from ArcGIS geocode api
    '''
    with open("cache/arcgis.json", "r") as arcgis_file:
        arcgis_data = json.load(arcgis_file)
    def preprocess_address(self, address: str) -> str:
        # Remove all space \n \t _ and anything shouldn't exist
        address = re.sub(r"[\s\n\t_]", "", address)
        # Remove characters after "號"
        address = re.sub(r"號.*", "號", address)
        # Remove characters before "市" "縣" "鄉" "鎮" "區" and that character
        address = re.sub(r".*(市|縣|鄉|鎮|區|里)", "", address)
        # Remove numbers + "鄰" 
        address = re.sub(r"\d+鄰", "", address)
        return address

        
    def __init__(self):
        self.base_url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer"
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.params = {
            "f": "json",
            "outSr": 4326,
            "maxLocations": 2,
            "countryCode": "TW",
        }
    def geocode(self, city: str, neighborhood: str|None, address: str) -> dict|None:
        '''
        :param region: Region name
        :param neighborhood: Neighborhood name
        :param address: Address to geocode
        :return: dict with lat and lon
        '''
        if neighborhood is None:
            # 不知道為什麼，資料就是會出現 None
            neighborhood = ""
        # Preprocess address
        address = self.preprocess_address(address)
        if tuple_to_str(city, neighborhood, address) in ArcGISClient.arcgis_data:
            location = ArcGISClient.arcgis_data[tuple_to_str(city, neighborhood, address)]["candidates"][0]["location"]
            return {
                "lat": float(location["y"]),
                "lon": float(location["x"])
            }
        # Geocode
        url = f"{self.base_url}/findAddressCandidates"
        self.params["city"] = city 
        self.params["neighborhood"] = neighborhood
        self.params["address"] = address
        self.params["SingleLine"] = city + neighborhood + address
        print(f"Geocoding {city} {neighborhood} {address}")
        try:
            response = requests.get(url, headers=self.headers, params=self.params)
            time.sleep(0.7)  # Avoid hitting the rate limit
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            ArcGISClient.arcgis_data[tuple_to_str(city, neighborhood, address)] = data
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if candidate["extent"]["xmax"] - candidate["extent"]["xmin"] > 0.01 or candidate["extent"]["ymax"] - candidate["extent"]["ymin"] > 0.01:
                    raise Exception(f"Geocoding error is too big: {city}{neighborhood}{address}, {candidate}")
                return {
                    "lat": float(candidate["location"]["y"]),
                    "lon": float(candidate["location"]["x"])
                }
            else:
                raise Exception(f"Geocoding error: {city}{neighborhood}{address}, {data}")
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    def dump_data(self,file_path: str = "cache/arcgis.json"):
        with open(file_path, "w",encoding="utf-8") as arcgis_file:
            json.dump(ArcGISClient.arcgis_data, arcgis_file, indent=4,ensure_ascii=False)
        return
