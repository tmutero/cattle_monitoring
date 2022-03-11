#!/bin/python

import requests
from dotenv import dotenv_values

env_vars = dotenv_values()
BASE_URL = "http://cattlemoniter.herokuapp.com"



def get_reading_data_history():
    transaction_history = None

    r = requests.get(f"{BASE_URL}/api/v1/data?limit=100")

    try: transaction_history = r.json()
    except: transaction_history = None
    return transaction_history



if __name__ == "__main__":
    print(get_reading_data_history())
