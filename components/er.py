import os
import requests
from urllib import parse

def on_ready():

    # 언어팩 다운로드
    url = f"https://open-api.bser.io/v1/l10n/Korean"
    headers = {
        "x-api-key": os.getenv("ER_TOKEN"),
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return response.status_code
    
    data = response.json().get("data", []).get("l10Path", [])

    os.system("curl " + data + f" > ./data/er-l10n-Korean.txt")

    f = open('./data/er-l10n-Korean.txt', 'r', encoding='utf-8')
    
    file_data = f.readlines()

    with open('./data/er-l10n-Korean.txt', 'w', encoding='utf-8') as outfile:
        for i in file_data:
            if not i.startswith("GameResult/Character/Name/"):
                outfile.write(i)


# 데이터 요청
def getData(metaType, characterIds):

    url = f"https://open-api.bser.io/v2/data/{metaType}"

    headers = {
        "x-api-key": os.getenv("ER_TOKEN"),
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return response.status_code
    
    data = response.json().get("data", [])

    # result = [char for char in data if char["code"] in characterIds]

    return data


# 캐릭터 로테이션 가져오기
def freeCharacters():

    matchingMode = 2

    url = f"https://open-api.bser.io/v1/freeCharacters/{matchingMode}"

    headers = {
        "x-api-key": os.getenv("ER_TOKEN"),
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return response.status_code
    
    # data = response.json().get("freeCharacters")

    data = getData("Character", response.json().get("freeCharacters"))

    data = [char for char in data if char["code"] in response.json().get("freeCharacters")]

    result = []

    for char in data:
        result.append(char.get("name", []))

    return result