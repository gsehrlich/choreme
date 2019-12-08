#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py
Based on https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import parser, gsheet
import requests
import datetime, pytz
import os.path

# Location of variables we don't want published on Github
from private.config import port_number, bot_id, spreadsheet_shortlink
from private.config import destination_sheetname, destination_table_corner
from private.config import record_format
from private.config import server_timezone, desired_timezone
from private.config import bot_post_url

# Where to log the POST requests received and any errors
LOG_DIRECTORY = "logs"
LOG_FILENAME_TEMPLATE = "%Y-%m-%d_%H-%M-%S_server_log.out"

# What the log entries should look like
# https://docs.python.org/3/howto/logging.html#changing-the-format-of-displayed-messages
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

<<<<<<< HEAD
=======
def record_chores(chore_list):
    "Accept a list of dicts containing post_data and the return_val from parser.parse"
    # make a deep copy in order not to edit the one that was passed
    chore_list = chore_list[:]

    for chore in chore_list:
        # We'll use `post_data` to fill in the data we'll send to
        # the spreadsheet, so add the timestamp in there too
        chore["post_data"]["local_timestamp"] = parser.convert_unix_timestamp(
            chore["post_data"]["created_at"])
     
        # We'll use `post_data` to fill in the row to be
        # sent to the spreadsheet, so get the time and rooms
        # the parser found and add them in.
        chore["post_data"]["time"] = chore["return_val"]["time"]
        chore["post_data"]["rooms"] = chore["return_val"]["rooms"]

    # should be a list of lists (i.e. two-dimensional)
    # the outer dimension is the row; inner, column.
    # `var` should be formattable strings specifying keys
    # in post_data to fill in, e.g. "{text}" to fill in
    # the message.
    # `record_format` should be a list of those, i.e.,
    # what row should the bot add to the spreadsheet?
    values = [[var.format(**chore["post_data"]) for var in record_format]
              for chore in chore_list]
    
    # Write to the sheet. Log the summary of what happened
    response = gsheet.write(destination_sheetname + "!" +
                            destination_table_corner, values)
    return response

def record_chore(post_data, return_val):
    return record_chores([{"post_data": post_data, "return_val": return_val}])

>>>>>>> 83ad0cf... Made groupy_hack.py go through all chores since last one entered
class ChoreMeRequestHandler(BaseHTTPRequestHandler):
    """Instantiated each time the server receives a request."""

    def _send_complete_response(self):
        """HTTP etiquette saying the request was processed"""

        # Send HTTP code ("OK")
        self.send_response(200)

        # Send HTTP header
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Send a standard response
        # `encode` turns str into bytes
        self.wfile.write(
            "POST request for {}".format(self.path).encode('utf-8')
            )


    def do_POST(self):
        """Receive HTTP POST requests."""

        try:
            # Get the data from the received request
            # `decode` gets str from bytes
            # post_data has everything we need to know
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length).decode('utf8'))

            # Log the received request
            logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                    str(self.path), str(self.headers), post_data)

            # We'll use `post_data` to fill in the data we'll send to
            # the spreadsheet, so add the timestamp in there too
            post_data["local_timestamp"] = parser.convert_unix_timestamp(
                post_data["created_at"])
 
            # HTTP etiquette
            self._send_complete_response()
            
            # Ignore message sent by this bot (and other bots)
            # Avoids infinite loops in which the bot responds to itself
            if post_data["sender_type"] == "bot": return

            # Pass the received message to the parser
            # `return_val` tells us what the parser found
            return_val = parser.parse(post_data["text"])
            # If the parser found no #chore hashtag, ignore the message
            # and quit
            if return_val == "no hashtag":
                return

            # If the parser found a #chore hashtag but couldn't figure out
            # how much time to record, don't record anything in the Google
            # Sheet. Instead, prepare to message the group this info.
            elif return_val == "time unknown":
                text = "I wasn't sure how much chore time to record."

            # If return value is anything else, the parser found a #chore
            # hashtag and the amount of time to record. Record it and
            # prepare to message the group about the recorded chore.
            else:
                # We'll use `post_data` to fill in the row to be
                # sent to the spreadsheet, so get the time and rooms
                # the parser found and add them in.
                post_data["time"] = return_val["time"]
                post_data["rooms"] = return_val["rooms"]

                # should be a list of lists (i.e. two-dimensional)
                # the outer dimension is the row; inner, column.
                # `var` should be formattable strings specifying keys
                # in post_data to fill in, e.g. "{text}" to fill in
                # the message.
                # `record_format` should be a list of those, i.e.,
                # what row should the bot add to the spreadsheet?
                values = [[var.format(**post_data) for var in record_format]]
                
                # Write to the sheet. Log the summary of what happened
                response = gsheet.write(destination_sheetname_range, values)
                logging.info(response)

                # Message the group about the success
                text = "Chore recorded! (See the spreadsheet at {} .)".format(
                       spreadsheet_shortlink)

            # Send the message to the group
            post_data = {
                "bot_id": bot_id,
                "text": text
            }
            requests.post(url=bot_post_url, data=post_data)
        except:
            logging.exception("Error while receiving POST:")
            raise

def run(server_class=HTTPServer, handler_class=ChoreMeRequestHandler):
    # Get the current local time to put at the beginning of log filenames
    now_utc = pytz.timezone(server_timezone).localize(
            datetime.datetime.now())
    now_central = now_utc.astimezone(pytz.timezone(desired_timezone))

    # Set up logging (is used to log POST requests and exceptions)
    # Use log filename that starts with a timestamp
    logging.basicConfig(
            format=LOG_FORMAT,
            datefmt=DATE_FORMAT,
            filename=os.path.join(LOG_DIRECTORY,
                now_central.strftime(LOG_FILENAME_TEMPLATE)),
            level=logging.INFO)

    # Create the server
    server_address = ('', port_number)
    httpd = server_class(server_address, handler_class)

    # Start serving
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    # Allow user to stop server gracefully by pressing Ctrl+C
    except KeyboardInterrupt:
        pass
    # If something else goes wrong, log it first
    except:
        logging.exception("Error in server_forever:")
        raise

    # Stop the server gracefully
    httpd.server_close()
    logging.info('Closed httpd.\n')

if __name__ == '__main__':
    run()
