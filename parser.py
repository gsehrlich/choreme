import re
import datetime, pytz
import os.path

from private.config import server_timezone, desired_timezone

# The regular expression used to look for a hashtag containing 'chore'
hashtag_pattern = r"#\w*chore\w*"

# The hashtag used to figure out how much time to record
time_pattern = r"([0-9]+) min"

# The place where we store info we don't want published on Github
_private_info_dir = "../private"

# Check whether we're running Python from the right directory.
# We need to be able to find the private folder from here.
# If not, raise an error and explain the problem to the user.
if not os.path.isdir(_private_info_dir):
        raise Exception("Couldn't find directory '{}'. Try running this program "
                            "again from the same directory as server.py.".format(
                                                _private_info_dir))

# Location on the computer of the list of rooms/chores                            
_room_list_filename = "room_list.txt"
_room_list_path = os.path.join(_private_info_dir, _room_list_filename)

# The datetime format into which UNIX timestamps are converted
DATE_FMT = "%Y-%m-%d %H:%M:%S"

def load_rooms():
    """Get the regular expression used for identifying rooms"""

    # Get the list of rooms from the file
    with open(_room_list_path) as f:
        rooms = f.read().strip().split('\n')

    # Create the regular expression
    # The parentheses indicate a group
    # The pipes mean "or"
    room_pattern = "(" + '|'.join(rooms) + ")"
    return room_pattern

def parse(message):
    """Parse hashtags, chore time, and rooms cleaned"""

    # Check if a hashtag containing 'chore' appears. If not,
    # ignore the message and tell whoever called this function so.
    if len(re.findall(hashtag_pattern, message, flags=re.IGNORECASE)) == 0:
        return "no hashtag"

    # Pick out the ### from each appearance of '### min.' If that
    # string doesn't appear or appears more than once, quit and tell
    # whoever called the function so.
    times = re.findall(time_pattern, message, flags=re.IGNORECASE)
    if len(times) == 0 or len(times) >= 2:
        return "time unknown"

    # Pick out all the rooms cleaned from the message.
    # Use a lowercase version of the message so that the rooms found
    # are all lowercase.
    # Load the rooms each time so that they can be edited without
    # shutting the server down
    room_pattern = load_rooms()
    rooms = ', '.join(re.findall(room_pattern, message.lower()))

    # Return information about the time and rooms we picked out
    return {"time": times[0], "rooms": rooms}

def convert_unix_timestamp(timestamp_str):
    """Get a readable datetime string out of a UNIX timestamp"""

    # First convert to a timezone-naive Python datetime.datetime object
    dt_tz_naive = datetime.datetime.fromtimestamp(int(timestamp_str))

    # Express the datetime in U.S. Central time
    dt_utc = pytz.timezone(server_timezone).localize(dt_tz_naive)
    dt_central = dt_utc.astimezone(pytz.timezone(desired_timezone))

    # Return a nicely formatted string
    formatted_str = dt_central.strftime(DATE_FMT)
    return formatted_str
