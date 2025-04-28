#!/bin/python3
import client

def main():
    my_client = client.Client()
    print(my_client.get_sch_ids("NTU"))
    print(my_client.get_sch_ids("NCKU"))
    my_client.dump_sch_ids()


if __name__ == "__main__":
    main()
