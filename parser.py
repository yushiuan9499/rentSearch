#!/bin/python3
import json
import client

arcgis_client = client.ArcGISClient()
def parse_item(item: dict) -> dict|tuple[dict, dict]:
    """
    Parses the given data and returns a dictionary with the parsed data.

    Args:
        item (dict): The data to be parsed.

    Returns:
        dict: A dictionary with the parsed data.
    """
    ret = {}
    # get url
    ret["url"] = item["house_url"]
    if ret["url"] == None:
        # if url is None, use house_id
        ret["url"] = item["house_id"]
    # get type
    # 先去除空白

    item["house_type"] = item["house_type"].replace(" ", "")
    if item["house_type"] == "學舍":
        ret["house_type"] = "dormitory"
    elif item["house_type"] == "透天":
        ret["house_type"] = "townhouse"
    elif item["house_type"] == "公寓":
        ret["house_type"] = "apartment"
    elif item["house_type"] == "華廈":
        ret["house_type"] = "condominium"
    elif item["house_type"] == "大樓":
        ret["house_type"] = "building"
    else:
        raise ValueError(f"Unknown house type: {item['house_type']}")
    # get rent type
    if not item["rent_type"] is None:
        item["rent_type"] = item["rent_type"].replace(" ", "")
        if item["rent_type"] == "房間分租":
            ret["rent_type"] = "room_share"
        elif item["rent_type"] == "獨立套房":
            ret["rent_type"] = "suite"
        elif item["rent_type"] == "整棟出租" or item["rent_type"] == "整戶出租":
            ret["rent_type"] = "whole"
        else:
            raise ValueError(f"Unknown rent type: {item['rent_type']}")
    else: 
        ret["rent_type"] = "unknown"
    if item["material"] == "水泥":
        ret["material"] = "cement"
    else:
                         raise ValueError(f"Unknown material: {item['material']}")
    ret["rest_room_num"] = item["rest_room_num"]
    # get price
    ret["min_price"] = int(item["rentalx"])
    ret["max_price"] = int(item["rentaly"])
    if item["deposit"][1:3] == "個月":
        if item["deposit"][0] == "一":
            ret["min_deposit"] = ret["min_price"] * 1
            ret["max_deposit"] = ret["max_price"] * 1
        elif item["deposit"][0] == "二":
            ret["min_deposit"] = ret["min_price"] * 2
            ret["max_deposit"] = ret["max_price"] * 2
        elif item["deposit"][0] == "三":
            ret["min_deposit"] = ret["min_price"] * 3
            ret["max_deposit"] = ret["max_price"] * 3
    elif '-' in item["deposit"]:
        tmp = item["deposit"].split("-")
        ret["min_deposit"] = int(tmp[0])
        ret["max_deposit"] = int(tmp[1])
    elif '~' in item["deposit"]:
        tmp = item["deposit"].split("~")
        ret["min_deposit"] = int(tmp[0])
        ret["max_deposit"] = int(tmp[1])
    else:
        try:
            ret["min_deposit"] = int(item["deposit"])
            ret["max_deposit"] = int(item["deposit"])
        except :
            print(f"Error parsing deposit: {item['house_id']} {item['deposit']}")
            ret["min_deposit"] = 0
            ret["max_deposit"] = 0
    ret["ammeter"] = (item["ammeter"] == "有")
    # get location
    ret["city"] = item["house_city"]
    ret["town"] = item["house_town"]
    ret["address"] = item["house_address"]
    try:
        ret["coordinates"] = (float(item["longitude"]), float(item["latitude"]))
    except:
        # try to geocode the address
        res = arcgis_client.geocode(ret["city"], ret["town"], ret["address"])
        if res is None:
            print(f"Error geocoding address: {item['house_id']}")
            ret["coordinates"] = (0.0, 0.0)
        else:
            ret["coordinates"] = (res["lon"], res["lat"])
    # get limit
    if item["sex_limit"] == "男":
        ret["gender"] = "M"
    elif item["sex_limit"] == "女":
        ret["gender"] = "F"
    else:
        ret["gender"] = "N/A"
    # get area
    tmp = item["house_area"].split()
    room_area = -1
    suite_area = -1
    for i in tmp:
        if i[0:2] == "套房":
            try:
                suite_area = int(i[2:-1])
            except :
                print(f"Error parsing suite area: {i} {i[2:-1]}")
        elif i[0:2] == "雅房":
            try:
                room_area = int(i[2:-1])
            except :
                print(f"Error parsing suite area: {i} {i[2:-1]}")
        else:
            raise ValueError(f"Unknown area type: {i}")
    if room_area == -1:
        ret["room_type"] = "suite"
        ret["area"] = suite_area
        return ret
    if suite_area == -1:
        ret["room_type"] = "room"
        ret["area"] = room_area
        return ret
    ret1 = ret
    ret2 = ret.copy()
    ret1["room_type"] = "room"
    ret1["area"] = room_area
    ret2["room_type"] = "suite"
    ret2["area"] = suite_area
    return ret1, ret2

def parse_list(data: list[dict]) -> list[dict]:
    """
    Parses the given data and returns a list of dictionaries with the parsed data.

    Args:
        data (list[dict]): The data to be parsed.

    Returns:
        list[dict]: A list of dictionaries with the parsed data.
    """
    parsed_data = [
        x
        for item in data
        if (res := parse_item(item))
        for x in (res if isinstance(res, tuple) else (res,))
        if isinstance(x, dict)
    ]
    return parsed_data

def convert(filename: str):
    with open("data/houses-raw/"+filename, "r",encoding='utf-8') as file:
        data = json.load(file)
    parsed_data = parse_list(data)
    with open("data/houses/"+filename, "w",encoding='utf-8') as file:
        json.dump(parsed_data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    convert("NCKU.json")
    arcgis_client.dump_data()
