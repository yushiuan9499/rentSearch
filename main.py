#!/bin/python3
import client
import json
import managers
import client

def main():
    map_manager = managers.OSRMManager()
    # map_manager.download_extract_region("tainan-urban-car", 23.5, 22.5, 120.5, 120.0,"car")
    # map_manager.download_extract_region("tainan-urban-bicycle", 23.5, 22.5, 120.5, 120.0,"bicycle")
    # map_manager.download_extract_region("tainan-urban-motorcycle", 23.5, 22.5, 120.5, 120.0,"motorcycle")
    # map_manager.build_osrm("tainan-urban-car")
    # map_manager.build_osrm("tainan-urban-bicycle")
    # map_manager.build_osrm("tainan-urban-motorcycle")
    map_manager.stop_server(5000)
    # map_manager.start_server("tainan-urban-car")

    osrm_client = client.OSRMClient()
    print(osrm_client.route((120.22189878167627,22.99802634394306),(120.2071239442969,22.98485846409672), "car"))
    osrm_client.dump_data()
    # nfu_client = client.NfuClient()
    # with open("data/houses/ncku.json", "w", encoding="utf-8") as nfu_file:
    #     json.dump(nfu_client.get_house_data_by_abbr("NCKU"), nfu_file, indent=4,ensure_ascii=False)


if __name__ == "__main__":
    main()
