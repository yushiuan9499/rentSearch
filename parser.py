#!/bin/python3
import json
def parse(item: dict) -> dict:
    """
    Parses the given data and returns a dictionary with the parsed data.

    Args:
        item (dict): The data to be parsed.

    Returns:
        dict: A dictionary with the parsed data.
    """
    ret = {}
    ret["url"] = item["house_url"]
    if ret["url"] == None:
        ret["url"] = item["house_id"]
    ret["city"] = item["house_city"]
    ret["town"] = item["house_town"]
    ret["address"] = item["house_address"]
    ret["house_type"] = item["house_type"]
    ret["rent_type"] = item["rent_type"]
    if item["material"] == "水泥":
        ret["material"] = "cement"
    else:
        ret["material"] = item["material"]
    tmp = item["house_area"].split()
    for i in tmp:
        if i[0:2] == "套房":
            try:
                ret["suite_area"] = int(i[2:-1])
            except :
                print(f"Error parsing suite area: {i} {i[2:-1]}")
        elif i[0:2] == "雅房":
            try:
                ret["room_area"] = int(i[2:-1])
            except :
                print(f"Error parsing suite area: {i} {i[2:-1]}")
        else:
            raise ValueError(f"Unknown area type: {i}")
    ret["min_price"] = int(item["rentalx"])
    ret["max_price"] = int(item["rentaly"])
    ret["ammeter"] = (item["ammeter"] == "有")
    try:
        ret["coordinates"] = (float(item["longitude"]), float(item["latitude"]))
    except :
        print(f"Error parsing coordinates: {item['house_id']} {item['longitude']} {item['latitude']}")
        ret["coordinates"] = (0.0, 0.0)
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
    if item["sex_limit"] == "男":
        ret["gender"] = "M"
    elif item["sex_limit"] == "女":
        ret["gender"] = "F"
    else:
        ret["gender"] = "N/A"
    return ret

def convert(filename: str):
    with open("data/houses-raw/"+filename, "r",encoding='utf-8') as file:
        data = json.load(file)
    parsed_data = [parse(item) for item in data]
    with open("data/houses/"+filename, "w",encoding='utf-8') as file:
        json.dump(parsed_data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    convert("ncku.json")
