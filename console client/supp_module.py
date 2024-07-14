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
    
    login = str(input("Введите логин: "))
    password = str(input("Введите пароль: "))
    
    json = {
        "login": f"{login}",
        "password": f"{password}"
    }
    
    # Выполнение POST-запроса
    response = requests.post(url+"/account/register", json=json)
    
    # Проверка успешности запроса
    if response.status_code == 200:
        print(response.json())
        print("Аккаунт успешно создан!")
    else:
        print(f"Ошибка: {response.status_code}")
    pass

def login(str):
    pass