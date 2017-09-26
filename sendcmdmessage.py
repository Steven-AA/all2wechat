from subprocess import Popen, PIPE, STDOUT
import sys
from sendtofilehelper import webwxsendmsgtome, dic
from sendmessage import webwxsendmsg

def main():
    p = Popen(sys.argv[1], stdout=PIPE, stderr=STDOUT, shell=True)
    try:
        name = sys.argv[2].decode('gbk')
        for f in dic['ContactList']:
            if f['RemarkName'] == name or f['NickName'] == name:
                sender = webwxsendmsg
                break;
    except:
        sender = webwxsendmsgtome
    while True:
        line = p.stdout.readline()
        if not line: break
        if not sender(line):
            print('Fail')
        else:
            print('Send\t'+ line)

if __name__ == '__main__':
    main()