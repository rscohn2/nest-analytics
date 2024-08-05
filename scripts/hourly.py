import requests

url = "http://127.0.0.1:8080/scheduler/hourly"
headers = {"X-Appengine-Cron": "true"}

response = requests.get(url, headers=headers)
print(response.status_code)
print(response.text)
