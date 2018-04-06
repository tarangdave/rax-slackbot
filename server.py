from flask import Flask, request, Response
import requests
import os
import datetime as DT
import json
from slackclient import SlackClient

slack_token = ''
sc = SlackClient(slack_token)

today = DT.date.today()
week_ago = today - DT.timedelta(days=7)

GIT_URL = "https://api.github.com/search/repositories?q=created:>{1}+language:{0}&sort=stars&order=desc?per_page=20"

app = Flask(__name__)

@app.route('/raxgt', methods=['GET','POST'])
def hello():
	input_text = request.form.get('text').lower()
	if input_text == "":
		return "Hello, use '/raxgt lang' to get top repositories for that language"
	response_url = request.form.get("response_url")

	payload = {"text":"Hold on. Receiving response...",
                "username": "bot"}

	requests.post(response_url,data=json.dumps(payload))
	print GIT_URL.format(input_text, week_ago)
	r = requests.get(GIT_URL.format(input_text, week_ago))
	all_keys =  r.json()["items"]
	final_list = []
	count = 0
	for key in all_keys:
		if count < 5:
			new_settings = {
				"fallback": "Github top repositories in last one week",
				"color": "#36a64f",
				"author_name": key["full_name"],
				"author_link": key["html_url"],
				"author_icon": key["owner"]["avatar_url"],
				"title": key["name"],
				"text": key["description"],
				"fields": [{"title": "stars", "value": key["stargazers_count"], "short": False},
							{"title": "Forks", "value": key["forks"], "short": False},
							{"title": "Watchers", "value": key["watchers"], "short": False}]
			}
			final_list.append(new_settings)
		count += 1

	#print final_list

	sc.api_call("chat.postMessage", token=slack_token, channel='C0DJ6JRV0', text="Here are top 5 repositories created last week", attachments=json.dumps(final_list), as_user=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)