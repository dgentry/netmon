# netmon
Monitor your network and tweet at your ISP after outages

Requires python 3.7.  Also needs Thingspeak API and Write API keys to
tweet.  Create an account at thingspeak.com and get your API keys
(It's free for more tweets per day than this should ever generate).
Edit netmon.py and replace the dummy `Api_Key` and `Write_Key.`

While you're there, add the address of your local router (if it's not
`192.168.1.1`) and the twitter handle of your ISP (assuming you want
to tweet at them).

Setup and run (in a venv):
```
python3 -m venv v
source v/bin/activate
pip install -r requirements.txt
python netmon.py
```
