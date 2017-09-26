import json
import time
from loggin import s

dic = ''

def webwxsendmsgtome(content):
    clientMsgId = str(int(time.time()))
    url = dic['base_uri'] + "/webwxsendmsg?lang=zh_CN&pass_ticket=" + dic['pass_ticket']
    Msg = {
        'Type': '1',
        'Content': content,
        'ClientMsgId': clientMsgId.encode('unicode_escape'),
        'FromUserName': dic['My']['UserName'].encode('unicode_escape'),
        'ToUserName': "filehelper".encode('unicode_escape'),
        'LocalID': clientMsgId.encode('unicode_escape')
    }
    payload = {'BaseRequest': dic['BaseRequest'], 'Msg': Msg}
    headers = {'ContentType': 'application/json; charset=UTF-8'}

    data = json.dumps(payload, ensure_ascii=False)

    r = s.post(url, data=data, headers=headers)

    resp = json.loads(r.text)
    if 'BaseResponse' in resp:
        if 'Ret' in resp['BaseResponse']:
            return int(resp['BaseResponse']['Ret'])
    return False

def init():
    global dic
    with open("./logininfo.log",'r') as f:
        print(f.readline())
        dic = f.readline()
        dic = eval(dic)

init()

def main():
    webwxsendmsgtome("hello")

if __name__ == '__main__':
    main()