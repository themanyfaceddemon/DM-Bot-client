import getpass
import os

import requests
import pickle

url = ""

def register(str):
    # Доставание словаря из бинарного файла
    with open("data_info.bin", "rb") as f:
        loaded_dict = pickle.load(f)
        ip = loaded_dict[ip]
        url = f"http://{ip}"
        response = requests.post(url)
    
    
    pass

def login(str):
    pass