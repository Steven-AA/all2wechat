from sendtofilehelper import dic
import sys
import time
from loggin import s
import json


def webwxgetcontact():
    url = dic['base_uri'] + "/webwxgetcontact?r=" + str(int(
        time.time()))
    r = s.post(url, json={})
    content = r.text.encode('unicode_escape').decode('string_escape')
    ContactList = json.loads(content)['MemberList']

def main():
    name = sys.argv[1].decode('gbk')
    for f in dic['ContactList']:
        if f['RemarkName'] == name or f['NickName'] == name:
            webwxsendmsg(f, sys.argv[2].decode('gbk').encode('utf8'))
            print('Send')
            break;

def webwxsendmsg(friend, content):
    clientMsgId = str(int(time.time()))
    url = dic['base_uri'] + "/webwxsendmsg?lang=zh_CN&pass_ticket=" + dic['pass_ticket']
    Msg = {
        'Type': '1',
        'Content': content,
        'ClientMsgId': clientMsgId.encode('unicode_escape'),
        'FromUserName': dic['My']['UserName'].encode('unicode_escape'),
        'ToUserName': friend["UserName"].encode('unicode_escape'),
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
    return -1


if __name__ == '__main__':
    main()