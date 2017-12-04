import json
import sys
import time
from sys import platform

from login import s, _print

dic = {}


def init():
    global dic
    try:
        with open("./logininfo.log", 'r') as f:
            _print('login info time:\t' +
                   f.readline()[:-1])
            dic = f.readline()
            dic = eval(dic)
    except:
        if 'linux' in platform:
            path = '/home/stevi/all2wechat/logininfo.log'
        else:
            path = 'E:/Github/all2wechat/logininfo.log'
        with open(path, 'r') as f:
            _print('login info time:\t' +
                   f.readline()[:-1])
            dic = f.readline()
            dic = eval(dic)


def webwxgetcontact():
    global dic
    try:
        with open("./contactlist.log", 'r') as f:
            ContactList = f.readline()
            ContactList = eval(ContactList)
            dic['ContactList'] = ContactList
    except:
        pass
        # todo
        if 'linux' in platform:
            path = '/home/stevi/all2wechat/logininfo.log'
        else:
            path = 'E:/Github/all2wechat/logininfo.log'
        with open(path, 'r') as f:
            _print('loading login data from ' + path)
            _print('login info time:\t' +
                   f.readline()[:-1])
            dic = f.readline()
            dic = eval(dic)
#    _print('Getting contactlist')
#    url = dic['base_uri'] + "/webwxgetcontact?r=" + str(int(
#        time.time()))
#    r = s.post(url, json={})
#    content = r.text.encode('unicode_escape').decode('string_escape')
#    ContactList = json.loads(content)['MemberList']
#    dic['ContactList'] = ContactList
#    with open('contactlist.log', 'w') as f:
#        f.write(str(ContactList))
#    _print('Contactlist get')


def main():
    global dic
    init()
    webwxgetcontact()
    try:
        name = sys.argv[1].decode('utf8')
    except:
        name = sys.argv[1].decode('gbk')
    for f in dic['ContactList']:
        if f['RemarkName'] == name or f['NickName'] == name:
            webwxsendmsg(f, sys.argv[2])
            print('Send')
            break


def webwxsendmsg(friend, content):
    clientMsgId = str(int(time.time()))
    url = dic['base_uri'] + \
        "/webwxsendmsg?lang=zh_CN&pass_ticket=" + dic['pass_ticket']
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
            return True
    return False


if __name__ == '__main__':
    main()
