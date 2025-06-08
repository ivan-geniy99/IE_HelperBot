import requests
import json

url = "https://ie-helperbot-ivan-geniy99.amvera.io/8115491073:AAFVkEN6p6T8OAYwd1SBFJsEsykfwDVeMjc"

update_example = {
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 11111111,
      "is_bot": False,
      "first_name": "Ivan",
      "username": "ivan"
    },
    "chat": {
      "id": 11111111,
      "first_name": "Ivan",
      "username": "ivan",
      "type": "private"
    },
    "date": 1697040000,
    "text": "/start"
  }
}

payload = json.dumps(update_example)
headers = {
  'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, data=payload)

print(response.status_code)
print(response.text)