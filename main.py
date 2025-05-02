#!/bin/python3
import managers
import filter_sorter
import json
import client


def main():
    map_manager = managers.OSRMManager()
    # map_manager.build_osrm("tainan-urban-bicycle")
    # map_manager.stop_server(5000)
    # map_manager.start_server("tainan-urban-bicycle")

    osrm_client = client.OSRMClient()
    school_location = (120.22165175769095, 22.997918650159388)
    test_data = [(120.2205935, 22.9923589),(120.2530783866288,22.997724060898566)]
    # 180s 16mmin
    # 750m 4km
    for item in test_data:
        res = osrm_client.route(school_location, item,"bicycle")
        if res is not None:
            print(f"Distance: {res['distance'] / 1000} km")
            print(f"Duration: {res['duration'] / 60} min")
        else:
            print("No route found.")
    return
    # return

    filter = filter_sorter.Filter()
    min_price = input("Enter the minimum price: ")
    if min_price != "":
        filter.min_price = int(min_price)
    max_price = input("Enter the maximum price: ")
    if max_price != "":
        filter.max_price = int(max_price)
    max_travel_time = input("Enter the maximum travel time: ")
    if max_travel_time != "":
        filter.max_travel_time = float(max_travel_time)
    max_distance = input("Enter the maximum distance: ")
    if max_distance != "":
        filter.max_distance = float(max_distance)
    gender = input("Enter the gender(M/F): ")
    if gender != "":
        filter.gender = gender
    rent_types = input("Enter the rent types(input as array) : ")
    if rent_types != "":
        filter.rent_types = list(map(str, rent_types.split(",")))
    house_types = input("Enter the house types(input as array) : ")
    if house_types != "":
        filter.house_types = list(map(str, house_types.split(",")))
    materials = input("Enter the materials(input as array) : ")
    if materials != "":
        filter.materials = list(map(str, materials.split(",")))
    room_types = input("Enter the room types(input as array) : ")
    if room_types != "":
        filter.room_types = list(map(str, room_types.split(",")))
    min_area = input("Enter the min area: ")
    if min_area != "":
        filter.min_area = int(min_area)
    max_area = input("Enter the max area: ")
    if max_area != "":
        filter.max_area = int(max_area)

    sorter = filter_sorter.Sort()
    school_location = input("Enter the school location: ")
    if school_location != "":
        filter.school_location = tuple(map(float, school_location.split(",")))
    print("Enter the sort priority(positive for ascending, negative for descending): ")
    min_price_sort = input("Enter the min price sort: ")
    if min_price_sort != "":
        sorter.min_price = int(min_price_sort)
    max_price_sort = input("Enter the max price sort: ")
    if max_price_sort != "":
        sorter.max_price = int(max_price_sort)
    max_travel_time_sort = input("Enter the max travel time sort: ")
    if max_travel_time_sort != "":
        sorter.travel_time = int(max_travel_time_sort)
    max_distance_sort = input("Enter the max distance sort: ")
    if max_distance_sort != "":
        sorter.distance = int(max_distance_sort)
    area_sort = input("Enter the area sort: ")
    if area_sort != "":
        sorter.area = int(area_sort)
    print(filter,sorter)
    print("Filter and Sorter initialized.")
    print("Filtering and sorting data...")
    filtered_data = filter_sorter.sortNfilter(data, sorter,filter)
    print("Filtered and sorted data:")
    for item in filtered_data:
        print(item)



if __name__ == "__main__":
    main()
