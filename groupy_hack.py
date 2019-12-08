from groupy.client import Client
import datetime
import parser
from server import record_chores
import time
import gsheet
import requests

from private.config import destination_sheetname
from private.config import destination_date_column
from private.config import bot_id, bot_post_url
from private.config import gabes_access_token, choreme_group_id

# Access Groupme API
client = Client.from_token(gabes_access_token)
choreme_group = client.groups.get(choreme_group_id)

# Read Google sheet to figure out the last chore it recorded
last_update = gsheet.read(destination_sheetname + "!" +
                         destination_date_column)[-1][0]
last_update = datetime.datetime.strptime(last_update, parser.DATE_FMT)
local_tz = parser.pytz.timezone(parser.desired_timezone)
start_date = local_tz.localize(last_update)

# What time is it now?
server_tz = parser.pytz.timezone(parser.server_timezone)
end_date = datetime.datetime.now(server_tz)
now_local = end_date.astimezone(local_tz)

# Go through messages chronologically starting with the most recent,
# putting all the chores in a list
chores = []
for message in choreme_group.messages.list_all():
    if message.created_at > end_date:
        continue
    elif message.created_at <= start_date:
        break
    elif message.text is None:
        continue
    else:
        result = parser.parse(message.text)
        # check if it parsed succesfully by looking for a dict
        if type(result) is dict:
            chores.append({"post_data":message.data, "return_val":result})

# start the list the least recent
chores.reverse()

# Write them to the Google sheet n at a time:
n = 10
for chore_page_start in range(0, len(chores), n):
    record_chores(chores[chore_page_start:chore_page_start + n])

# Prepare the Groupme message
# Count how many chores each person did (that this program just found)
chore_doers = {}
for chore in chores:
    name = chore["post_data"]["name"]
    if name in chore_doers:
        chore_doers[name] += 1
    else:
        chore_doers[name] = 1

# Write the Groupme message
text = """------------
Chore update
------------
From: {}
To: {}

""".format(last_update.strftime(parser.DATE_FMT),
        now_local.strftime(parser.DATE_FMT))
if len(chore_doers) == 0:
    text += "No chores recorded."
else:
    for chore_doer in chore_doers:
        text += "{}: {} chore(s)\n".format(chore_doer, chore_doers[chore_doer])

# Send it to Groupme using the bot
post_data = {
    "bot_id": bot_id,
    "text": text
}
requests.post(url=bot_post_url, data=post_data)
