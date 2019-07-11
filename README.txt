Start the Server
-------------------
Make sure you're logged in as choreme.
Navigate to ~/choreme.
Once you're there, type the following command into the command line (after the $ and the space):
$ ./start_server.sh
(After you've typed a command out, press Enter to tell the computer to run it.)
This script activates a Python virtual environment and then runs server.py.


To Check on the Server
----------------------
You can check the logs in ~/choreme/logs.


To Stop the Server
------------------
First, resume the tmux session running the server:
$ tmux attach -t choremeServerSession

Then, press Ctrl+C to interrupt Python. The server should now be offline.
Detach from that session again by typing Ctrl-B, releasing both keys,
and typing D.

Finally, end the session by entering the command
$ tmux kill-session -t choremeServerSession

Debugging
---------
It appears that sometimes the server gets stuck on a request. I tried typing Ctrl+C once with the
intention of shutting down the server and restarting it, but instead it just interrupted the
stuck request. The backlog of requests was then processed.


Action items
------------
-   Choose/make a Groupme account/phone number (tied to below Google account?) to own the bot
       -   make the bot
-   Choose/make a Google account to own the spreadsheet
    -   Make a project under the Google account to put in credentials.json
-   Documentation
    -   Put it on wiki? and in server directory?
