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
        return "API 호출에 실패하였습니다."
    # elif response.json()["total"] == 0:
    #     return "검색 결과가 없습니다."
    # elif response.json()["total"] > 1:
    #     return "검색 결과가 너무 많습니다."
    else:
        data = response.json()
        auction_item = data.get("auction_item", [])

        if not auction_item:
            return "검색 결과가 없습니다."

        # 가장 싼 아이템 찾기 ( 검증 해봐야 함 )
        cheapest_item = min(auction_item, key=lambda x: x['auction_price_per_unit'])

    # 가격 포맷
    formatted_price = f"{cheapest_item['auction_price_per_unit']:,}"

    result = {
        "item": cheapest_item['item_display_name'],
        "price": formatted_price,
        "expire": cheapest_item['date_auction_expire']
    }

    #return f"{cheapest_item['item_display_name']}의 현재 가격은 {formatted_price} 골드 입니다."
    return result