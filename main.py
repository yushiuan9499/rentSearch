#!/bin/python3
import client
import json

def main():
    with open("config.json","r") as config_file:
        config = json.load(config_file)
    g_client = client.GoogleClient(config["google_api_key"])
    g_client.fetch_data("台北市大安區忠孝東路四段1號", "台北市大安區忠孝東路四段2號")
    g_client.dump_data()


if __name__ == "__main__":
    main()
