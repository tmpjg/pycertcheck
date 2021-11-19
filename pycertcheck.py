#!/usr/bin/env python2

import sys
import os
from datetime import date,datetime
import argparse
import socket
import subprocess
import re
import slackwh

parser = argparse.ArgumentParser(description='Check certs...' , usage="pycertcheck --lst domainstest.lst --dayswarning 60 --dayscritical 30 \
--slackwebhook https://hooks.slack.com/services/*** --timeout 60")
parser.add_argument('--lst', help='file with list of domains to check.',type=str,required=True)
parser.add_argument('--timeout', type=int, required=False, help='set timeout (sec).',default=60)
parser.add_argument('--oks', required=False, action='store_true', help='Show OKs.')
parser.add_argument('--dayswarning', help='set days to alert warnings...',type=int,default=60)
parser.add_argument('--dayscritical', help='set days to alert criticals...',type=int,default=30)
parser.add_argument('--slackwebhook', required=False, type=str, help='WebHook for Slack notification.')
parser.add_argument('--version', action='version', version='1.0.0')
args = parser.parse_args()

path = os.path.dirname(os.path.realpath(__file__))

proxy = "http://proxy.emea.prosegur.local:8080"

def listreader(listpath):
    with open(listpath) as f:
        list = f.read().splitlines()
        domains = []
        for domain in list:
            if not domain.startswith("#"):
                domain = domain.replace("http://","")
                domain = domain.replace("https://","")
                domain = [url.split('/')[0] for url in domain.split()][0]
                domains.append(domain)
        domains = set(domains)
    return sorted(domains)


def checkweb(domain):
    """ return days to expire """
    cmd = path+"/check_ssl_cert -s -A -H "+domain
    env = dict(os.environ)
    env['http_proxy'] = proxy
    env['https_proxy'] = proxy
    tst = "host -t a www.infobip.com"
    print(str(subprocess.check_output(tst, shell=True, stderr=subprocess.STDOUT,env=env)))
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, env=env)
    except Exception, e:
        output = str(e.output)
    deltadays = re.sub(r'.*days=','', output)
    deltadays = re.sub(r';.*\n','',deltadays)
    if 'was' in output:
        expdate = re.sub(r'.*was','was',output)
        expdate = re.sub(r'\).*\n','',expdate)
    else:
        expdate = re.sub(r'.*valid','valid',output)
        expdate = re.sub(r'\(.*\n','',expdate)
    return str(expdate), int(deltadays)
    

def slackattach(domain,status,detail,slackwebhook):
    sl=slackwh.slacknotif()
    color = "#999999"
    author = domain
    title = "PyCertCheck"
    titlelink = "https://"+domain
    text = "nulltext"
    state = status
    footer = ""
    footericon = ""

    if status == "OK":
        color = "#4cb336"
        text = ":heavy_check_mark: "+str(detail)+" days left..."
    elif status == "WARNING":
        color = "#f7f300"
        text = ":warning: "+str(detail)+" days left..."
    elif status == "CRITICAL":
        color = "#ff9d00"
        text = ":fire: "+str(detail)+" days left..."
    elif status == "EXPIRED":
        color = "#ff0000"
        text = ":no_entry: "+str(detail)+" days expired..."
    elif status == "ERROR":
        color = "#ff0000"
        text = ":x: "+str(detail)

    sl.attach(color,author,"#",title,"#",text,state,footer,"#",slackwebhook)
    return "notified..."

def slacktext(message,slackwebhook):
    sl=slackwh.slacknotif()
    text = "```\n"
    text += message + "\n"
    text += "```\n"
    sl.text(text,slackwebhook)
    return "notified..."

def main(arguments):
    try:
        dayswarning = arguments.dayswarning
        dayscritical = arguments.dayscritical
        domains = listreader(arguments.lst)
        checks = []
        for domain in domains:
            check = []
            try:
                c = checkweb(domain)
                expdate = c[0]
                deltadays = c[1]
                if deltadays > dayswarning:
                    status = "OK"
                    detail = deltadays
                elif deltadays < 0:
                    status = "EXPIRED"
                    detail = deltadays
                elif deltadays < dayscritical:
                    status = "CRITICAL"
                    detail = deltadays
                elif deltadays < dayswarning:
                    status = "WARNING"
                    detail = deltadays
            except Exception as e:
                status = "ERROR"
                detail = 0
                expdate = e
            check.append(domain) #0
            check.append(expdate)#1
            check.append(status) #2
            check.append(detail) #3
            checks.append(check)
        
        checks.sort(key=lambda x: x[3], reverse = True)

        # Send ALL report
        message = "######## PyCertCheck ########\n"
        for c in checks:
            if c[2] == "OK":
                detail = (str(c[3])+" days left...")
            elif c[2] == "WARNING":
                detail = (str(c[3])+" days left...")
            elif c[2] == "CRITICAL":
                detail = (str(c[3])+" days left...")
            elif c[2] == "EXPIRED":
                detail = (str(c[3])+" days expired...")
            elif c[2] == "ERROR":
                detail = (str(c[3]))
            message += "[%s] [%s] [%s] [%s] (%s) \n" % (str(datetime.today()),c[0],c[1],c[2],detail)
        print(message)
        slacktext(message,arguments.slackwebhook)

        # Send individual report
        for c in checks:
            if c[2] in ("WARNING","CRITICAL","ERROR","EXPIRED") and arguments.slackwebhook:
                slackattach(c[0],c[2],c[3],arguments.slackwebhook)


    except Exception as e:
        print(e)


if __name__ == '__main__':
    if args.timeout:
        socket.setdefaulttimeout(args.timeout)
    sys.exit(main(args))
