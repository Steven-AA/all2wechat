from sendtofilehelper import dic
import sys

def main():
    print(dic)
    sys.argv

def webwxsendmsg(friend, content):
    clientMsgId = str(int(time.time()))
    url = base_uri + "/webwxsendmsg?lang=zh_CN&pass_ticket=" + pass_ticket
    Msg = {
        'Type': '1',
        'Content': content,
        'ClientMsgId': clientMsgId.encode('unicode_escape'),
        'FromUserName': My['UserName'].encode('unicode_escape'),
        'ToUserName': friend["UserName"].encode('unicode_escape'),
        'LocalID': clientMsgId.encode('unicode_escape')
    }
    payload = {'BaseRequest': BaseRequest, 'Msg': Msg}
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