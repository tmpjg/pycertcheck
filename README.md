# Pycertcheck

Tool for check expiration date of SSL certificates.

#### Usage:
```bash
pycertcheck -h

usage: pycertcheck --lst domainstest.lst --dayswarning 60 --dayscritical 30 --slackwebhook https://hooks.slack.com/services/***

Check certs...

optional arguments:
  -h, --help            show this help message and exit
  --lst LST             file with list of domains to check.
  --timeout TIMEOUT     set timeout (sec).
  --dayswarning DAYSWARNING
                        set days to alert warnings...
  --dayscritical DAYSCRITICAL
                        set days to alert criticals...
  --slackwebhook SLACKWEBHOOK
                        WebHook for Slack notification.
  --version             show program's version number and exit


```

#### Create binary

`pyinstaller pycertcheck.py --onefile`

## TODO

* add check for p12
* install script
