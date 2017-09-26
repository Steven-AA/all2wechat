import json
import os
import re
import shutil
import sys
import time
import urllib
import xml.dom.minidom
from sys import platform

import requests
from termcolor import colored

LOGGINURL = "https://wx.qq.com/"
UUID = ''
redirect_uri = ''
base_uri = ''
skey = ''
wxsid = ''
wxuin = ''
pass_ticket = ''
BaseRequest = {}
deviceId = 'e000000000000000'

My = {}
SyncKey = []
ContactList = []

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Connection': 'keep-alive',
    'Content-type': 'text/html; charset=utf-8'})


def get_uuid():
    global UUID
    url = 'https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_=' + \
        str(int(time.time()))
    text = s.get(url).text
    p1 = re.compile(
        'window.QRLogin.code = (...); window.QRLogin.uuid = "(.{12})";')
    match = p1.match(text)
    return_code = match.group(1)
    if return_code == '200':
        UUID = match.group(2)
        return True
    else:
        return False


def login():
    global redirect_uri, base_uri, skey, wxsid, wxuin, pass_ticket, BaseRequest
    if 'linux' in platform:
        os.system('eog QRcode.jpg')
    else:
        os.system('QRcode.jpg')
    while True:
        url = "https://login.wx2.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={}&tip=0&r=1140907481&_={}".format(
            UUID, str(int(time.time())))
        text = s.get(url, stream=True).text
        p = re.compile('window.code=(...)')
        code = p.match(text).group(1)
        if code == '200':
            print('Log in success')
            # print text
            # window.redirect_uri="https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=AxNVJPVI0qe7OUFhvGSbT73N@qrticket_0&uuid=wZePRtQbgw==&lang=zh_CN&scan=1506394610";
            p = re.compile('window.redirect_uri="(.*)";')
            match = p.findall(text)[0]
            redirect_uri = match + "&fun=new&version=v2"
            base_uri = redirect_uri[:redirect_uri.rfind('/')]
            # print redirect_uri
            # print base_uri
            text = s.get(redirect_uri).text
            # print text
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
                    pass_ticket = node.childNodes[0].data
            # print (skey, wxsid, wxuin, pass_ticket)

            BaseRequest = {
                'Uin': int(wxuin),
                'Sid': wxsid.encode('unicode_escape'),
                'Skey': skey.encode('unicode_escape'),
                'DeviceID': deviceId,
            }
            return True
        elif code == '201':
            pass
        elif code == '408':
            print('Time Out')
        else:
            sys.exit(code)
        time.sleep(1)


def responseState(func, BaseResponse):
    ErrMsg = BaseResponse['ErrMsg']
    Ret = BaseResponse['Ret']
    if Ret != 0:
        print('func: %s, Ret: %d, ErrMsg: %s' % (func, Ret, ErrMsg))

    if Ret != 0:
        return False

    return True


def webwxinit():
    global My, SyncKey

    url = base_uri + "/webwxinit?r=-1746916482&lang=zh_CN&pass_ticket=" + pass_ticket
    payload = {'BaseRequest': BaseRequest}
    headers = {'ContentType': 'application/json; charset=UTF-8'}
    r = s.post(url, json=payload, headers=headers)
    data = r.text.encode('unicode_escape').decode('string_escape')
    dic = json.loads(data)
    My = dic['User']
    SyncKey = dic['SyncKey']
    state = responseState('webwxinit', dic['BaseResponse'])
    return state


def webwxgetcontact():
    global ContactList
    url = base_uri + "/webwxgetcontact?r=" + str(int(
        time.time()))
    r = s.post(url, json={})
    content = r.text.encode('unicode_escape').decode('string_escape')
    ContactList = json.loads(content)['MemberList']




def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


def get_QRcode():
    global UUID
    url = "https://login.weixin.qq.com/qrcode/" + UUID
    urllib.urlretrieve(url, 'QRcode.jpg')


def _try(fun, times=5, failmessage=None, successmessage=None):
    for i in range(times):
        if not fun():
            if 'linux' in platform:
                print(colored(failmessage, 'red'))
                print(colored('Fail {} time(s)'.format(i + 1), 'red'))
            else:
                print('Fail {} time(s)'.format(i + 1))
            time.sleep(1)
        else:
            print(successmessage)
            return True
    return False

def record():
    with open("logininfo.log", 'w') as f:
        f.write(time.ctime()+'\n')
        dic = {
            'UUID': UUID,
            'redirect_uri': redirect_uri,
            'base_uri': base_uri,
            'pass_ticket':pass_ticket,
            'BaseRequest': BaseRequest,
            'My':My,
            'ContactList':ContactList
        }
        f.write(str(dic))
        print('Login finish')

def main():
    print('Getting UUID ...')
    if not _try(get_uuid, successmessage='UUID get'):
        return
    print('Getting QRcode ...')
    get_QRcode()
    print('QRcode get')
    if not login():
        print('Login failed')
        return
    if not webwxinit():
        print('Init failed')
    webwxgetcontact()
    record()


if __name__ == '__main__':
    main()
