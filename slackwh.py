import requests
import json

class slacknotif:
    """docstring for slacknotif."""

    def attach(self,color,author,authorlink,title,titlelink,text,state,footer,footericon,webhook):
        data = {
            "attachments": [
                {
                    "fallback": text,
                    "color": color,
                    "author_name": author,
                    "author_link": authorlink,
                    "title": title,
                    "title_link": titlelink,
                    "text": text,
                    "fields": [
                        {
                            "title": "State",
                            "value": state,
                            "short": "false"
                        }
                    ],
                    "footer": footer,
                    "footer_icon": footericon
                }
            ]
        }
        response = requests.post(webhook, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        return response.status_code

    def text(self,text,webhook):
        data = {
            "text":text
        }
        response = requests.post(webhook, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        return response.status_code
