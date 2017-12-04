import json
import os
import re
import shutil
import sys
import time
import urllib
import xml.dom.minidom
from sys import platform
import argparse
import pyqrcode

import requests
from termcolor import colored


LOGGINURL = "https://wx.qq.com/"

Request = {}
deviceId = 'e000000000000000'

My = {}
SyncKey = []
ContactList = []

dic = {}

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'})
    # 'Connection': 'keep-alive',
    # 'Content-type': 'text/html; charset=utf-8'})

qr_terminal = ''

def get_uuid():
    global dic
    url = 'https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_=' + \
        str(int(time.time()))
    text = s.get(url).text

    p1 = re.compile(
        'window.QRLogin.code = (...); window.QRLogin.uuid = "(.{12})";')
    match = p1.match(text)
    return_code = match.group(1)
    if return_code == '200':
        dic['UUID'] = match.group(2)
        return True
    else:
        return False


def login():
    global dic
    if 'linux' in platform:
        #        os.system('eog QRcode.jpg')
        print(qr_terminal)
    else:
        os.system('QRcode.jpg')
    while True:
        url = "https://login.wx2.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={}&tip=0&r=1140907481&_={}".format(
            dic['UUID'], str(int(time.time())))
        text = s.get(url, stream=True).text
        p = re.compile('window.code=(...)')
        code = p.match(text).group(1)
        if code == '200':
            _print('Log in success')
            # _print text
            # window.redirect_uri="https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=AxNVJPVI0qe7OUFhvGSbT73N@qrticket_0&uuid=wZePRtQbgw==&lang=zh_CN&scan=1506394610";
            p = re.compile('window.redirect_uri="(.*)";')
            match = p.findall(text)[0]
            dic['redirect_uri'] = match + "&fun=new&version=v2"
            dic['base_uri'] = dic['redirect_uri'][:dic['redirect_uri'].rfind(
                '/')]
            # _print redirect_uri
            # _print base_uri
            text = s.get(dic['redirect_uri']).text
            # _print text
            doc = xml.dom.minidom.parseString(text)
            root = doc.documentElement

            for node in root.childNodes:
                if node.nodeName == 'skey':
                    skey = node.childNodes[0].data
                elif node.nodeName == 'wxsid':
                    wxsid = node.childNodes[0].data
                elif node.nodeName == 'wxuin':
                    wxuin = node.childNodes[0].data
                elif node.nodeName == 'pass_ticket':
                    dic['pass_ticket'] = node.childNodes[0].data
            # _print (skey, wxsid, wxuin, pass_ticket)

            dic['BaseRequest'] = {
                'Uin': int(wxuin),
                'Sid': wxsid.encode('unicode_escape'),
                'Skey': skey.encode('unicode_escape'),
                'DeviceID': deviceId,
            }
            return True
        elif code == '201':
            pass
        elif code == '408':
            _print('Time Out')
        else:
            sys.exit(code)
        time.sleep(1)


def responseState(func, BaseResponse):
    ErrMsg = BaseResponse['ErrMsg']
    Ret = BaseResponse['Ret']
    if Ret != 0:
        _print('func: %s, Ret: %d, ErrMsg: %s' % (func, Ret, ErrMsg))

    if Ret != 0:
        return False

    return True


def webwxinit():
    global SyncKey

    url = dic['base_uri'] + \
        "/webwxinit?r=-1746916482&lang=zh_CN&pass_ticket=" + dic['pass_ticket']
    payload = {'BaseRequest': dic['BaseRequest']}
    headers = {'ContentType': 'application/json; charset=UTF-8'}
    r = s.post(url, json=payload, headers=headers)
    data = r.text.encode('unicode_escape').decode('string_escape')
    tdic = json.loads(data)
    dic['My'] = tdic['User']
    SyncKey = tdic['SyncKey']
    state = responseState('webwxinit', tdic['BaseResponse'])
    return state


def webwxgetcontact():
    global ContactList, dic
    _print('Getting contactlist')
    url = dic['base_uri'] + "/webwxgetcontact?r=" + str(int(
        time.time()))
    r = s.post(url, json={})
    content = r.text.encode('unicode_escape').decode('string_escape')
    ContactList = json.loads(content)['MemberList']
    dic['ContactList'] = ContactList
    with open('contactlist.log', 'w') as f:
        f.write(str(ContactList))
    _print('Contactlist get')


def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


def get_QRcode():
    global qr_terminal
    url = "https://login.weixin.qq.com/l/" + dic['UUID']
    # urllib.request.urlretrieve(url, 'QRcode.jpg')
    qr = pyqrcode.create(url)
    qr.png('QRcode.jpg', scale=8)
    qr_terminal = qr.terminal(quiet_zone=1)


def _try(fun, times=5, failmessage=None, successmessage=None):
    for i in range(times):
        if not fun():
            if 'linux' in platform:
                _print(colored(failmessage, 'red'))
                _print(colored('Fail {} time(s)'.format(i + 1), 'red'))
            else:
                _print('Fail {} time(s)'.format(i + 1))
            time.sleep(1)
        else:
            _print('' + successmessage)
            return True
    return False


def record():
    with open("logininfo.log", 'w') as f:
        f.write(time.ctime() + '\n')
        f.write(str(dic))
        _print('Login finish')


def keep_login():
    while 1:
        if webwxsendmsgtome("hello"):
            _print('Sended')
        else:
            _print('Failed')
        time.sleep(360)


def _print(s):
    print(time.ctime().split(' ')[3] + '\t' + s)


def webwxsendmsgtome(content):
    clientMsgId = str(int(time.time()))
    url = dic['base_uri'] + \
        "/webwxsendmsg?lang=zh_CN&pass_ticket=" + dic['pass_ticket']
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
    # time.sleep(1)
    resp = json.loads(r.text)
    if 'BaseResponse' in resp:
        if 'Ret' in resp['BaseResponse']:
            return True
    return False


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


def new_login():
    _print('Getting UUID ...')
    if not _try(get_uuid, successmessage='UUID get'):
        return
    _print('Getting QRcode ...')
    get_QRcode()
    _print('QRcode get')
    if not login():
        _print('Login failed')
        return
    if not webwxinit():
        _print('Init failed')
    dic['webwx_data_ticket'] = s.cookies['webwx_data_ticket']
    record()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scl', '-s', help='sync contactlist',
                        const=True, default=False, type=bool, nargs='?')
    parser.add_argument('--recent', '-r', help='auto login with recent info',
                        default=False, type=bool, const=True, nargs='?')
    args = parser.parse_args()
    if args.recent:
        _print('Trying to use last login info ...')
        try:
            init()
            if webwxsendmsgtome('hello'):
                _print('Success')
        except:
            new_login()
    else:
        new_login()
    if args.scl:
        _print('Syncing contactlist')
        webwxgetcontact()
        _print('done')
    keep_login()


if __name__ == '__main__':
    main()
