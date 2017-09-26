import json
import time
from sys import platform
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
    time.sleep(1)
    resp = json.loads(r.text)
    if 'BaseResponse' in resp:
        if 'Ret' in resp['BaseResponse']:
            return True
    return False

def init():
    global dic
    try:
        with open("./logininfo.log",'r') as f:
            print(f.readline())
            dic = f.readline()
            dic = eval(dic)
    except:
        if 'linux' in platform:
            path = '~/all2wechat/logininfo.log'
        else:
            path = 'E:/Github/all2wechat/logininfo.log'
        with open(path,'r') as f:
            print(f.readline())
            dic = f.readline()
            dic = eval(dic)
init()

def main():
    webwxsendmsgtome("hello")

if __name__ == '__main__':
    main()