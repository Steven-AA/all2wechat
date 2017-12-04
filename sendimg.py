
# coding: utf-8

# In[ ]:


import json
import sys
import time
import os
import mimetypes
from sys import platform

from login import s, _print

dic = {}


file_index = 0


def upload_media(fpath, is_img=False):
    global file_index
    if not os.path.exists(fpath):
        _print('File not exists')
        return None
    url = 'https://file.wx2.qq.com/cgi-bin/mmwebwx-bin/webwxuploadmedia?f=json'
    flen = str(os.path.getsize(fpath))
    ftype = mimetypes.guess_type(fpath)[0] or 'application/octet-stream'
    files = {
        'id': (None, 'WU_FILE_%s' % str(file_index)),
        'name': (None, os.path.basename(fpath)),
        'type': (None, ftype),
        'lastModifiedDate': (None, time.strftime('%m/%d/%Y, %H:%M:%S GMT+0800 (CST)')),
        'size': (None, flen),
        'mediatype': (None, 'pic' if is_img else 'doc'),
        'uploadmediarequest': (None, json.dumps({
            'BaseRequest': dic['BaseRequest'],
            'ClientMediaId': int(time.time()),
            'TotalLen': flen,
            'StartPos': 0,
            'DataLen': flen,
            'MediaType': 4,
        })),
        'webwx_data_ticket': (None, dic['webwx_data_ticket']),
        'pass_ticket': (None, dic['pass_ticket']),
        'filename': (os.path.basename(fpath), open(fpath, 'rb'), ftype.split('/')[1]),
    }
    file_index += 1
    try:
        r = s.post(url, files=files)
        if json.loads(r.text)['BaseResponse']['Ret'] != 0:
            r = s.post(url, files=files)
            if json.loads(r.text)['BaseResponse']['Ret'] != 0:
                _print('Upload media failure.')
                return None
        mid = json.loads(r.text)['MediaId']
        return mid
    except Exception, e:
        print(e)
        return None


def send_img(fpath, friend):
    mid = upload_media(fpath, is_img=True)
    if mid is None:
        return False
    url = dic['base_uri'] + '/webwxsendmsgimg?fun=async&f=json'
    data = {
        'BaseRequest': dic['BaseRequest'],
        'Msg': {
            'Type': 3,
            'MediaId': mid,
            'FromUserName': dic['My']['UserName'],
            'ToUserName': friend["UserName"].encode('unicode_escape'),
            'LocalID': str(time.time() * 1e7),
            'ClientMsgId': str(time.time() * 1e7), }, }
    if fpath[-4:] == '.gif':
        url = dic['base_uri'] + '/webwxsendemoticon?fun=sys'
        data['Msg']['Type'] = 47
        data['Msg']['EmojiFlag'] = 2
    try:
        r = s.post(url, data=json.dumps(data))
        res = json.loads(r.text)
        if res['BaseResponse']['Ret'] == 0:
            return True
        else:
            print(res)
            return False
    except Exception, e:
        print(e)
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
            if send_img('D:/workspace/Python/Falldetect/Data/pic/1/1_frame_0.jpg', f):
                #             webwxsendmsg(f, sys.argv[2])
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
