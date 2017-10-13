import argparse
import re
import sys
from subprocess import PIPE, STDOUT, Popen

from login import _print, webwxsendmsgtome, dic, init
from sendmessage import webwxsendmsg


mode = {'p': '([0-9]+%)|Done'}
powershell = 'C:\Windows.old\WINDOWS\SysWOW64\WindowsPowerShell\v1.0\powershell.exe'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--user', help='username or nickname to send(default send to filehelper)', type=str)
    parser.add_argument('--file', help='if cmd will get a file name')
    parser.add_argument('--cmd', '-c', help='cmd or filename', type=str)
    parser.add_argument('-m',
                        '--mode', help='re mode, choose this --re will not work', type=str)
    parser.add_argument('-r', '--re', help='regular express', type=str)
    args = parser.parse_args()
    init()
    if args.re != None:
        patten = re.compile(args.re)
    if args.mode != None:
        try:
            patten = re.compile(mode[args.mode])
        except:
            _print('No mode named {}'.format(args.mode))
            sys.exit()
    if args.file:
        # todo
        pass
    else:
        launch_str = args.cmd
        p = Popen(launch_str, stdout=PIPE, stderr=STDOUT, shell=True)
        _print('Running ' + launch_str)
    flag = True
    while True:
        try:
            line = p.stdout.readline()
            if not line:
                break
            if args.re != None or args.mode != None:
                try:
                    line = patten.findall(line)[0]
                except:
                    _print('Ignore:\t' + line.split('\n')[0])
                    continue
            if args.user != None:
                if not webwxsendmsg(friend, line):
                    _print('Fail')
                else:
                    _print('Send\t' + line.split('\n')[0])
            else:
                if not webwxsendmsgtome(line):
                    _print('Fail')
                else:
                    _print('Send\t' + line.split('\n')[0])
        except:
            _print('Send failed')


if __name__ == '__main__':
    main()
