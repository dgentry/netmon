import re
import requests
import subprocess
import time
from time import sleep

from log import log, RED, WHT, GRN, YEL

# Named Constants

# A local host that should always be up (ideally, the gateway router)
Local_Host = "192.168.1.1"
# The internet host that should always be up (Google DNS,for example)
Internet_Host = "8.8.8.8"

smallest_outage_to_report = 30 # seconds

# Twitter Account of your Internet Provider.
#Tweet_To = "@ask_spectrum"
My_City = "SomeCity"

Thingspeak_Host = "api.thingspeak.com"
# replace 'K' sequence by your API_KEY of ThingTweet
Api_Key = 'KKKKKKKKKKKKKKKK'
# replace 'W' sequence by your WriteAPIKey (from your thingSpeak channel settings)
Write_Api_Key = 'WWWWWWWWWWWWWWWW'

Report_File = "netmon.log"


def send_tweet(message):
    Tweet_Path = "apps/thingtweet/1/statuses/update"
    payload = {'api_key': Api_Key, 'status': message}
    r = requests.post(f"https://{Thingspeak_Host}/{Tweet_Path}", params=payload)

def send_down_tweet(duration, My_City):
    send_tweet(f"{tweet_to}, internet was down: {str(duration)} s."
              f"I'm in {My_City}. #DownTimeDetected")

def send_start_tweet():
    send_tweet("Downtime monitor was started.")

def send_thingspeak(duration):
    args = {'field1': str(duration), 'key': write_api_key}
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"}
    path = "/update"
    r = requests.post(f"https://{thingspeak_host}/{path}", params=args, headers=headers)


def host_down(host):
    """Return (True, '') if host is down, (False, latency) if up.
    """
    latency = ''
    try:
        pipe = subprocess.PIPE
        r = subprocess.run(f"ping -c 1 {host}",
                           shell=True, stdout=pipe, stderr=pipe)
    except subprocess.CalledProcessError as err:
        print('ERROR:', err)
        exit(1)
    else:
        output = r.stdout.decode('utf-8')
        if len(r.stderr) > 0:
            err = r.stderr.decode('utf-8')
            log(f"Surprising error:  {YEL}{err}")
        ms_match = re.search("time=([0-9.]+) ms", output)
        if ms_match:
            latency = ms_match.group(1)
        down = r.returncode > 0
        return (down, latency)

def check_down(local, internet):
    """Returns (True, '') if internet is down, (False, latency) if up,
    None if it's not possible to check because the local net is down.
    """

    inet_down, inet_latency = host_down(internet)
    if inet_down:
        # Internet seems down, but are we even locally connected?
        local_down, local_latency = host_down(local)
        if local_down:
            # Locally disconnected, can't tell anything
            return (None, None)
    return (inet_down, inet_latency)


#  MAIN LOOP

if __name__ == "__main__":
    send_start_tweet()
    log(f"{WHT} -- DownTime Monitor --\n")
    attempt_num = 0
    was_offline = False
    start_of_outage = 0
    total_downtime = 0
    outage_count = 0

    while True:
        attempt_num += 1
        latency = ''
        log(f"{YEL}#{attempt_num}, {outage_count} outage(s).  ", end="")
        try:
            is_down, latency = check_down(Local_Host, Internet_Host)
            sleep(5)
        except Exception as e:
            log(f"{RED}Fail:{e}")
            sleep(5)
            continue
        except KeyboardInterrupt:
            log(f"{WHT}Goodbye!")
            exit(1)

        if is_down is None:
            print(f"{now()}: Disconnected from local network.")
            continue
        elif is_down:
            log_add(f"{WHT}Internet is {RED}down...")
        else:
            log_add(f"{WHT}Internet is up.  (latency {GRN}{latency}{WHT})")

        # Internet went down after previous check
        if is_down and not was_offline:
            start_of_outage = time.time()
            was_offline = True
            continue

        # Internet came up after previous check
        if not is_down and was_offline:
            total_downtime = round(time.time() - start_of_outage, 1)
            outage_count = outage_count + 1
            was_offline = False

            if (total_downtime > smallest_outage_to_report):
                dt_str = log(f"DownTime above limit: {total_downtime} s offline\n")
                with open(DowntimeReportFile, "a") as TxtFile:
                    TxtFile.write(dt_str)
                SendTweet(total_downtime)
            SendThingSpeak(total_downtime)
