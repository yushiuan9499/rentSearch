#!/bin/python3
import client

def main():
    my_client = client.Client()
    print(my_client.get_house_data_by_abbr("NCKU"))


if __name__ == "__main__":
    main()
