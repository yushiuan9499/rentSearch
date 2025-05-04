#!/bin/python3
import json
import client

equipment_map = {
    # 電器類
    "電冰箱": "refrigerator",
    "電視機": "tv",
    "烘乾機": "dryer",
    "洗衣機": "washing_machine",
    "冷氣機": "air_conditioner",
    "脫水機": "dehydrator",
    "飲水機": "water_dispenser",
    "中央空調": "central_air_conditioner",
    # 家具類
    "沙發": "sofa",
    "衣櫃": "closet",
    "書桌(椅)": "desk",
    "書櫃": "bookshelf",
    "單人床": "single_bed",
    "雙人床": "double_bed",
    "檯燈": "desk_lamp",
    "獨立陽台": "balcony",
    # 通訊相關
    "寬頻網路": "broadband",
    "第四台": "cable_tv",
    "數位電視": "digital_tv",
    "電話": "telephone",
    "光纖網路": "fiber_optic",
    # 加熱相關
    "天然瓦斯": "natural_gas",
    "桶裝瓦斯": "gas_tank",
    "瓦斯熱水器": "gas_water_heater",
    "電熱水器": "electric_water_heater",
    "太陽能熱水器": "solar_water_heater",
    # 公共設施
    "公共陽台": "public_balcony",
    "停車場": "parking_lot",
    "電梯": "elevator",
    "中庭": "atrium",
    "晒衣場": "laundry_area",
    "曬衣場": "laundry_area",
    "管理中心": "management_center",
}
arcgis_client = client.ArcGISClient()
def parse_room_data(room_data: str) -> dict:
    """
    Parses the given room data and returns a dictionary with the parsed data.

    Args:
        room_data (str): The room data to be parsed.

    Returns:
        dict: A dictionary with the parsed data.
    """
    ret = {}
    data = room_data.split()
    if data[0] == "[套房":
        ret["room_type"] = "suite"
    elif data[0] == "[雅房":
        ret["room_type"] = "room"
    else:
        raise ValueError(f"Unknown room type: {data[0]}")
    try:
        ret["area"] = int(data[1][1:])
    except ValueError:
        print(f"Error parsing area: {data[1][1:]}")
        ret["area"] = 0
    try:
        ret["room_num"] = int(data[3])
    except ValueError:
        print(f"Error parsing room number: {data[3]}")
        ret["room_num"] = 0
    try:
        ret["rest_room_num"] = int(data[6])
    except ValueError:
        print(f"Error parsing rest room number: {data[6]}")
        ret["rest_room_num"] = 0
    return ret
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
    ret["equipment"] = [
        equipment_map[equipment]
        for equipment in item["equipment"]
        if equipment in equipment_map or len(equipment) < 6 # 有些奇怪的東西，通常長過 6個字
    ]
    # get area and room type
    if len(item["room_data"]) == 2:
        ret1 = ret
        ret2 = ret.copy()
        ret1.update(parse_room_data(item["room_data"][0]))
        ret2.update(parse_room_data(item["room_data"][1]))
        return ret1, ret2
    if len(item["room_data"]) == 1:
        ret.update(parse_room_data(item["room_data"][0]))
        return ret
    raise ValueError(f"Unknown room data: {item['room_data']}")

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
    arcgis_client.dump_data()
    return parsed_data

def convert(filename: str):
    with open("data/houses-raw/"+filename, "r",encoding='utf-8') as file:
        data = json.load(file)
    parsed_data = parse_list(data)
    with open("data/houses/"+filename, "w",encoding='utf-8') as file:
        json.dump(parsed_data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    convert("NCKU.json")
