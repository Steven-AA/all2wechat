# encoding:utf8
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
import mimetypes
import threading

import requests
from termcolor import colored


class wx:
    def __init__(self):
        self.dic = {}
        self.deviceId = 'e000000000000000'
        self.SyncKey = []
        self.ContactList = []
        self.s = requests.Session()
        self.s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'})
        # 'Connection': 'keep-alive',
        # 'Content-type': 'text/html; charset=utf-8'})
        self.file_index = 0
        self.qr_terminal = ''
        # if args.recent:
        #     _print('Trying to use last login info ...')
        #     try:
        #         init()
        #         if webwxsendmsgtome('hello'):
        #             _print('Success')
        #     except:
        #         new_login()
        # else:
        self.new_login()
        # if args.scl:
        self._print('Syncing contactlist')
        self.webwxgetcontact()
        self._print('done')
        t = threading.Thread(target=self.keep_login)
        t.start()

    def get_uuid(self):
        url = 'https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_=' + \
            str(int(time.time()))
        text = self.s.get(url).text

        p1 = re.compile(
            'window.QRLogin.code = (...); window.QRLogin.uuid = "(.{12})";')
        match = p1.match(text)
        return_code = match.group(1)
        if return_code == '200':
            self.dic['UUID'] = match.group(2)
            return True
        else:
            return False

    def login(self):
        if 'linux' in platform:
            #        os.system('eog QRcode.jpg')
            print(qr_terminal)
        else:
            os.system('QRcode.jpg')
        while True:
            url = "https://login.wx2.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={}&tip=0&r=1140907481&_={}".format(
                self.dic['UUID'], str(int(time.time())))
            text = self.s.get(url, stream=True).text
            p = re.compile('window.code=(...)')
            code = p.match(text).group(1)
            if code == '200':
                self._print('Log in success')
                # _print text
                # window.redirect_uri="https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=AxNVJPVI0qe7OUFhvGSbT73N@qrticket_0&uuid=wZePRtQbgw==&lang=zh_CN&scan=1506394610";
                p = re.compile('window.redirect_uri="(.*)";')
                match = p.findall(text)[0]
                self.dic['redirect_uri'] = match + "&fun=new&version=v2"
                self.dic['base_uri'] = self.dic['redirect_uri'][:self.dic['redirect_uri'].rfind(
                    '/')]
                # _print redirect_uri
                # _print base_uri
                text = self.s.get(self.dic['redirect_uri']).text
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
                        self.dic['pass_ticket'] = node.childNodes[0].data
                # _print (skey, wxsid, wxuin, pass_ticket)

                self.dic['BaseRequest'] = {
                    'Uin': int(wxuin),
                    'Sid': wxsid,  # .encode('unicode_escape'),
                    'Skey': skey,  # .encode('unicode_escape'),
                    'DeviceID': self.deviceId,
                }
                return True
            elif code == '201':
                pass
            elif code == '408':
                self._print('Time Out')
            else:
                sys.exit(code)
            time.sleep(1)

    def responseState(self, func, BaseResponse):
        ErrMsg = BaseResponse['ErrMsg']
        Ret = BaseResponse['Ret']
        if Ret != 0:
            self._print('func: %s, Ret: %d, ErrMsg: %s' % (func, Ret, ErrMsg))

        if Ret != 0:
            return False

        return True

    def webwxinit(self):
        url = self.dic['base_uri'] + \
            "/webwxinit?r=-1746916482&lang=zh_CN&pass_ticket=" + \
            self.dic['pass_ticket']
        payload = {'BaseRequest': self.dic['BaseRequest']}
        headers = {'ContentType': 'application/json; charset=UTF-8'}
        r = self.s.post(url, json=payload, headers=headers)
        data = r.text
        #.encode('unicode_escape').decode('string_escape')
        tdic = json.loads(data)
        self.dic['My'] = tdic['User']
        self.SyncKey = tdic['SyncKey']
        state = self.responseState('webwxinit', tdic['BaseResponse'])
        return state

    def webwxgetcontact(self):
        self._print('Getting contactlist')
        url = self.dic['base_uri'] + "/webwxgetcontact?r=" + str(int(
            time.time()))
        r = self.s.post(url, json={})
        content = r.text
        #.encode('unicode_escape').decode('string_escape')
        self.ContactList = json.loads(content)['MemberList']
        self.dic['ContactList'] = self.ContactList
        # with open('contactlist.log', 'w') as f:
        # f.write(str(self.ContactList))
        self._print('Contactlist get')

    def striphtml(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)

    def get_QRcode(self):
        url = "https://login.weixin.qq.com/l/" + self.dic['UUID']
        # urllib.request.urlretrieve(url, 'QRcode.jpg')
        qr = pyqrcode.create(url)
        qr.png('QRcode.jpg', scale=8)
        self.qr_terminal = qr.terminal(quiet_zone=1)

    def _try(self, fun, times=5, failmessage=None, successmessage=None):
        for i in range(times):
            if not fun():
                if 'linux' in platform:
                    self._print(colored(failmessage, 'red'))
                    self._print(
                        colored('Fail {} time(s)'.format(i + 1), 'red'))
                else:
                    self._print('Fail {} time(s)'.format(i + 1))
                time.sleep(1)
            else:
                self._print('' + successmessage)
                return True
        return False

    def record():
        with open("logininfo.log", 'w') as f:
            f.write(time.ctime() + '\n')
            f.write(str(self.dic))
            self._print('Login finish')

    def keep_login(self):
        while 1:
            if self.webwxsendmsgtome("hello"):
                self._print('Sended')
            else:
                self._print('Failed')
            time.sleep(300)

    def _print(self, s):
        print(time.ctime().split(' ')[3] + '\t' + s)

    def webwxsendmsgtome(self, content):
        clientMsgId = str(int(time.time()))
        url = self.dic['base_uri'] + \
            "/webwxsendmsg?lang=zh_CN&pass_ticket=" + self.dic['pass_ticket']
        Msg = {
            'Type': '1',
            'Content': content,
            'ClientMsgId': clientMsgId,  # .encode('unicode_escape'),
            # .encode('unicode_escape'),
            'FromUserName': self.dic['My']['UserName'],
            'ToUserName': "filehelper",  # .encode('unicode_escape'),
            'LocalID': clientMsgId  # .encode('unicode_escape')
        }
        payload = {'BaseRequest': self.dic['BaseRequest'], 'Msg': Msg}
        headers = {'ContentType': 'application/json; charset=UTF-8'}
        data = json.dumps(payload, ensure_ascii=False)
        # data = plaload

        r = self.s.post(url, data=data, headers=headers)
        # time.sleep(1)
        resp = json.loads(r.text)
        if 'BaseResponse' in resp:
            if 'Ret' in resp['BaseResponse']:
                if resp['BaseResponse']['Ret'] == 0:
                    return True
        return False

    def init(self):
        try:
            with open("./logininfo.log", 'r') as f:
                self._print('login info time:\t' +
                            f.readline()[:-1])
                self.dic = f.readline()
                self.dic = eval(self.dic)
        except:
            if 'linux' in platform:
                path = '/home/stevi/all2wechat/logininfo.log'
            else:
                path = 'E:/Github/all2wechat/logininfo.log'
            with open(path, 'r') as f:
                self._print('login info time:\t' +
                            f.readline()[:-1])
                self.dic = f.readline()
                self.dic = eval(self.dic)

    def new_login(self):
        self._print('Getting UUID ...')
        if not self._try(self.get_uuid, successmessage='UUID get'):
            return
        self._print('Getting QRcode ...')
        self.get_QRcode()
        self._print('QRcode get')
        if not self.login():
            self._print('Login failed')
            return
        if not self.webwxinit():
            self._print('Init failed')
        self.dic['webwx_data_ticket'] = self.s.cookies['webwx_data_ticket']
        # self.record()

    def upload_media(self, fpath, is_img=False):
        if not os.path.exists(fpath):
            self._print('File not exists')
            return None
        url = 'https://file.wx2.qq.com/cgi-bin/mmwebwx-bin/webwxuploadmedia?f=json'
        flen = str(os.path.getsize(fpath))
        ftype = mimetypes.guess_type(fpath)[0] or 'application/octet-stream'
        files = {
            'id': (None, 'WU_FILE_%s' % str(self.file_index)),
            'name': (None, os.path.basename(fpath)),
            'type': (None, ftype),
            'lastModifiedDate': (None, time.strftime('%m/%d/%Y, %H:%M:%S GMT+0800 (CST)')),
            'size': (None, flen),
            'mediatype': (None, 'pic' if is_img else 'doc'),
            'uploadmediarequest': (None, json.dumps({
                'BaseRequest': self.dic['BaseRequest'],
                'ClientMediaId': int(time.time()),
                'TotalLen': flen,
                'StartPos': 0,
                'DataLen': flen,
                'MediaType': 4,
            })),
            'webwx_data_ticket': (None, self.s.cookies['webwx_data_ticket']),
            'pass_ticket': (None, self.dic['pass_ticket']),
            'filename': (os.path.basename(fpath), open(fpath, 'rb'), ftype.split('/')[1]),
        }
        self.file_index += 1
        try:
            r = self.s.post(url, files=files)
            if json.loads(r.text)['BaseResponse']['Ret'] != 0:
                r = self.s.post(url, files=files)
                if json.loads(r.text)['BaseResponse']['Ret'] != 0:
                    self._print('Upload media failure.')
                    return None
            mid = json.loads(r.text)['MediaId']
            return mid
        except:
            return None

    def send_img(self, fpath, friend):
        mid = self.upload_media(fpath, is_img=True)
        if mid is None:
            return False
        url = self.dic['base_uri'] + '/webwxsendmsgimg?fun=async&f=json'
        data = {
            'BaseRequest': self.dic['BaseRequest'],
            'Msg': {
                'Type': 3,
                'MediaId': mid,
                'FromUserName': self.dic['My']['UserName'],
                'ToUserName': friend["UserName"],  # .encode('unicode_escape'),
                'LocalID': str(time.time() * 1e7),
                'ClientMsgId': str(time.time() * 1e7), }, }
        try:
            r = self.s.post(url, data=json.dumps(data))
            res = json.loads(r.text)
            if res['BaseResponse']['Ret'] == 0:
                return True
            else:
                return False
        except:
            return False

    def send_img_by_name(self, fpath, name):
        for f in self.dic['ContactList']:
            if f['RemarkName'] == name or f['NickName'] == name:
                if self.send_img(fpath, f):
                    self._print('Img Sended')
                else:
                    self._print('Img Send Failed')
                return
        self._print('Failed to find the user')


def main():
    w = wx()
    name = u'00000001'
    # name.decode
    w.send_img_by_name(
        'D:/workspace/Python/Falldetect/Data/pic/1/1_frame_0.jpg', name)


if __name__ == '__main__':
    main()
