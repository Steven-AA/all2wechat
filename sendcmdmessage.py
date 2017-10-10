from subprocess import Popen, PIPE, STDOUT
import sys
from sendtofilehelper import webwxsendmsgtome, dic
from sendmessage import webwxsendmsg
import argparse
import re
mode = {'p': '([0-9]+%)|Done'}
powershell = "C:\Windows.old\WINDOWS\SysWOW64\WindowsPowerShell\v1.0\powershell.exe"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--user", help="username or nickname to send(default send to filehelper)", type=str)
    parser.add_argument("--file", help="if cmd will get a file name")
    parser.add_argument("--cmd", help="cmd or filename", type=str)
    parser.add_argument("-m",
                        '--mode', help="re mode, choose this --re will not work", type=str)
    parser.add_argument("-r", "--re", help="regular express", type=str)
    args = parser.parse_args()
    if args.re != None:
        patten = re.compile(args.re)
    if args.mode != None:
        try:
            patten = re.compile(mode[args.mode])
        except:
            print("No mode named {}".format(args.mode))
            sys.exit()
    if args.file:
        # todo
        pass
    else:
        launch_str = args.cmd
        p = Popen(launch_str, stdout=PIPE, stderr=STDOUT, shell=True)
    flag = True
    while True:
        line = p.stdout.readline()
        if not line:
            break
        if args.re != None or args.mode != None:
            try:
                line = patten.findall(line)[0]
            except:
                print("Ignore:\t" + line)
                continue
        if args.user != None:
            if not webwxsendmsg(friend, line):
                print('Fail')
            else:
                print('Send\t' + line)
        else:
            if not webwxsendmsgtome(line):
                print('Fail')
            else:
                print('Send\t' + line)


if __name__ == '__main__':
    main()
