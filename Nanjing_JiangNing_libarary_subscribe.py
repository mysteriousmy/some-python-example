import json
import datetime
import httpx

client = httpx.Client(http2=True)
headers = {
    'authority': 'alipay.jieshu.me',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'clientinfo': '{"libcode":"null","platform":"embed_jieshu_aliyun","channel":"embed_jieshu_aliyun","orgChannel":"embed_jieshu_aliyun","clientSource":"null","appEnvironment":"production","thirdpartEmbed":"3"}',
    'content-type': 'application/json',
    'cookie': "YouCookie",
    'dnt': '1',
    'origin': 'https://alipay.jieshu.me',
    'sec-ch-ua': r'" Not A;Brand";v="99", "Chromium";v="101", "Microsoft Edge";v="101"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "Windows",
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
    'x-requested-with': 'XMLHttpRequest'
}

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
tomorrow = today + datetime.timedelta(days=1)

data = {
    'appointTime': str(tomorrow),
    'bindId': "bindId",
    'bookcartid': "idcard",
    'cardType': "01",
    'channel': "embed_jieshu_aliyun",
    'chepai': "",
    'from': "17:30",
    'imgData': "",
    'isHealth': "0",
    'isInGeli': "0",
    'isInSuzhou': "0",
    'isMiqie': "0",
    'libcode': "jiangning",
    'mobile': "YourPhone",
    'qrid': "YourQRid",
    'roomName': "",
    'subLib': "九龙湖阅读分中心",
    'to': "19:45",
    'ucardno': "",
    'uname': "YouSubName",
    'vertifyCode': "",
    'xtr': []
}


url_search = 'https://alipay.jieshu.me/cloudils//api/usersAppointMent/accessOpen/addAppoint'

r = client.post(url_search, data=json.dumps(data), headers=headers)
print(r.text)
