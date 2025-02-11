import os
import requests
from urllib import parse

def getItemPrice(itemName):
    
    url = "https://open.api.nexon.com/mabinogi/v1/auction/list"
    
    headers = {
        "x-nxopen-api-key": os.getenv("NEXON_TOKEN"),
        "Content-Type": "application/json"
    }

    params = parse.urlencode({
        "item_name": itemName
    })

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:

        errorCode = errorHandling(response.status_code, response.json().get("error", {}).get("name"))

        return errorCode
    
    elif response.status_code == 200:
        data = response.json()
        auction_item = data.get("auction_item", [])

        if not auction_item:
            return "검색 결과가 없습니다."

        # 가장 싼 아이템 찾기 ( 검증 해봐야 함 )
        cheapest_item = min(auction_item, key=lambda x: x['auction_price_per_unit'])

    # 가격 포맷
    formatted_price = f"{cheapest_item['auction_price_per_unit']:,}"

    result = {
        "status_code": response.status_code,
        "item": cheapest_item['item_display_name'],
        "price": formatted_price,
        "expire": cheapest_item['date_auction_expire']
    }

    return result

# Error handling
def errorHandling(statusCode, errorCode):

    # OPENAPI00001	500	Internal Server Error	서버 내부 오류
    # OPENAPI00002	403	Forbidden	권한이 없는 경우
    # OPENAPI00003	400	Bad Request	유효하지 않은 식별자
    # OPENAPI00004	400	Bad Request	파라미터 누락 또는 유효하지 않음
    # OPENAPI00005	400	Bad Request	유효하지 않은 API KEY
    # OPENAPI00006	400	Bad Request	유효하지 않은 게임 또는 API PATH
    # OPENAPI00007	429	Too Many Requests	API 호출량 초과
    # OPENAPI00009	400	Bad Request	데이터 준비 중
    # OPENAPI00010	400	Bad Request	게임 점검 중
    # OPENAPI00011	503	Service Unavailable	API 점검 중
    
    if errorCode == "OPENAPI00001":
        return {"statusCode" : statusCode, "errorCode" : "서버 내부 오류"}
    elif errorCode == "OPENAPI00002":
        return {"statusCode" : statusCode, "errorCode" : "API 권한이 없습니다."}
    elif errorCode == "OPENAPI00003":
        return {"statusCode" : statusCode, "errorCode" : "유효하지 않은 식별자입니다."}
    elif errorCode == "OPENAPI00004":
        return {"statusCode" : statusCode, "errorCode" : "존재하지 않는 아이템입니다."}
    elif errorCode == "OPENAPI00005":
        return {"statusCode" : statusCode, "errorCode" : "유효하지 않은 API"}
    elif errorCode == "OPENAPI00006":
        return {"statusCode" : statusCode, "errorCode" : "유효하지 않은 게임 또는 API PATH"}
    elif errorCode == "OPENAPI00007":
        return {"statusCode" : statusCode, "errorCode" : "API 호출량이 초과되었습니다."}
    elif errorCode == "OPENAPI00009":
        return {"statusCode" : statusCode, "errorCode" : "데이터 준비 중"}
    elif errorCode == "OPENAPI00010":
        return {"statusCode" : statusCode, "errorCode" : "게임 점검 중"}
    elif errorCode == "OPENAPI00011":
        return {"statusCode" : statusCode, "errorCode" : "API 점검 중"}

