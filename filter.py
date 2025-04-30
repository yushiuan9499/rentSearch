from dataclasses import dataclass
import client

osrm_client = client.OSRMClient()

@dataclass
class Filter:
    """
    A class to represent a filter.

    Attributes:
        min_price (int): The minimum price for the filter.
        max_price (int): The maximum price for the filter.
        max_travel_time (int): The maximum travel time for the filter.
        max_distance (int): The maximum distance for the filter.
        gender (str): The gender for the filter.
        min_area (int): The minimum area for the filter.
        max_area (int): The maximum area for the filter.
        room_type (list[str]): The room type for the filter.
        school_location (str|tuple[float]): The school location for the filter.
        rent_type (list[str]): The rent type for the filter.
        house_type (list[str]): The house type for the filter.
        materials (list[str]): The materials for the filter.
    """

    min_price: int = 0
    max_price: int = 100000
    max_travel_time: int = 100000
    max_distance: int = 100000
    gender: str = "N/A"
    min_area: int = 0
    max_area: int = 100000
    room_types: list[str] = []
    school_location: tuple[float]|None = None
    rent_types: list[str] = []
    house_types: list[str] = []
    materials: list[str] = []

@dataclass
class Sort:
    """
    A class to represent a sort.

    Attributes:
        price (int): positive for ascending, negative for descending. 
        travel_time (int): positive for ascending, negative for descending. 
        distance (int): positive for ascending, negative for descending. 
        area (int): positive for ascending, negative for descending. 
        school_location (int): positive for ascending, negative for descending. 
        p.s. which has higher absolute value will be sorted first.
    """
    
    min_price: int = 0 
    max_price: int = 0
    travel_time: int = 0
    distance: int = 0
    area: int = 0


def fileter(item, filter:Filter):
    """
    Filters the given data based on the provided filter.

    Args:
        item (dict): The data to be filtered.
        filter (Filter): The filter to be applied to the data.

    """
    # filter the price
    if item["min_price"] < filter.min_price or item["max_price"] > filter.max_price:
        return False
    # filter the area
    if item["room_area"] < filter.min_area or item["room_area"] > filter.max_area:
        return False
    # filter the gender
    if fileter.gender == "M" and item["gender"] == "F" \
        or filter.gender == "F" and item["gender"] == "M":
        return False
    # filter the room type
    if len(filter.room_types) > 0 and item["room_type"] not in filter.room_types:
        return False
    # filter the rent type
    if len(filter.rent_types) > 0 and item["rent_type"] not in filter.rent_types:
        return False
    # filter the house type
    if len(filter.house_types) > 0 and item["house_type"] not in filter.house_types:
        return False
    # filter the materials
    if len(filter.materials) > 0 and item["material"] not in filter.materials:
        return False
    # filter travel time and distance
    if filter.school_location != None::
        # get the travel time and distance from the osrm client
        travel_time, distance = osrm_client.route(tuple(item["coordinates"]), filter.school_location,"bicycle")
        if travel_time > filter.max_travel_time or distance > filter.max_distance:
            return False
    return True
def sorter(data, sort:Sort):
    """
    Sorts the given data based on the provided sort criteria.

    Args:
        data (list): The list of data to be sorted.
        sort (Sort): The sort criteria to be applied to the data.

    Returns:
        list: The sorted data.
    """
    # Sort the data based on the sort criteria
    sort_order = []
    sort_order.append((sort.min_price, "min_price"))
    sort_order.append((sort.max_price, "max_price"))
    sort_order.append((sort.travel_time, "travel_time"))
    sort_order.append((sort.distance, "distance"))
    sort_order.append((sort.area, "area"))
    sort_order.sort(key=lambda x: abs(x[0]), reverse=False) # sort first mean less important
    for i in sort_order:
        if i[0] == 0:
            continue
        data.sort(key=lambda x: x[i[1]] * (1 if  i[0] > 0 else -1))
    return data

def sortNfilter(data, sort:Sort, filter:Filter):
    """
    Sorts and filters the given data based on the provided filter.

    Args:
        data (list): The list of data to be sorted and filtered.
        filter (str): The filter to be applied to the data.

    Returns:
        list: The sorted and filtered data.
    """
    # Filter the data based on the filter criteria
    filtered_data = [item for item in data if fileter(item, filter)]
    # Sort the filtered data based on the sort criteria
    sorted_data = sorter(filtered_data, sort)

    return sorted_data
