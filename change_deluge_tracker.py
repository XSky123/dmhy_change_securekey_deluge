from deluge_client import DelugeRPCClient
import requests
import json
import time
# ****************
# CHANGE INFO BELOW
# ****************
__APIURL__ = "" # Get yours From https://u2.dmhy.org/privatetorrents.php
__DE_URL__ = "" # Don't include protocol (http/https)
__DE_PORT__ = 11111 # Number not string, it's NOT your WEBUI port, get this from WEBUI Connection Manager
__DE_USER__ = ""
__DE_PW__ = ""
# ****************
# CHANGE INFO ABOVE
# ****************

count = 0
__MAX_REQ__ = 100
__SLEEP__ = 5

client = DelugeRPCClient(__DE_URL__, __DE_PORT__, __DE_USER__, __DE_PW__) 
print("Connecting to Deluge...")
client.connect()
print("Fetching DMHY torrents from Deluge...")
torrent_list = client.core.get_torrents_status({},['trackers'])
dmhy_torrent_hash_list = [hash_ for hash_ in torrent_list if "dmhy" in str(torrent_list[hash_][b'trackers'][0][b'url'])]
dmhy_req_list = []
requested_secure_list = []

# Thx to makii@U2 with distributed requests (per 100 torrents)
# Thx to Ender@U2 and 流哲@VoiceMemories who reported this problem.
req = 1
for i, hash_ in enumerate(dmhy_torrent_hash_list):
    dmhy_req_list.append({"jsonrpc": "2.0", "method": "query", "params": [str(hash_)[2:-1]], "id":i+1})
    if (i+1) % __MAX_REQ__ == 0:
        print("Fetching Secure Code... Time {}".format(req))
        resp = requests.post(__APIURL__, json=dmhy_req_list)
        if resp.status_code != 200:
            raise(Exception("Error with Code {} Pls Try Again!".format(resp.status_code)))
        
        requested_secure_list.extend(resp.json())
        print("Sleep {} sec".format(__SLEEP__))
        time.sleep(__SLEEP__)
        req += 1
        dmhy_req_list = []

print("Fetching Secure Code... Time {}".format(req))
resp = requests.post(__APIURL__, json=dmhy_req_list)
if resp.status_code != 200:
       raise(Exception("Error with Code {} Pls Try Again!".format(resp.status_code)))
print("Total requested secure list count: {}".format(len(requested_secure_list)))	

error_torrent_hash_list = []
print("Begin Updating...")
for i, hash_ in enumerate(dmhy_torrent_hash_list):
    if "result" in requested_secure_list[i]:
        count += 1
        client.core.set_torrent_trackers(hash_, [{'url':"https://daydream.dmhy.best/announce?secure={}".format(requested_secure_list[i]["result"]), 'tier':0}])
        print("Edited Tracker for {} ({}/{})".format(str(hash_)[2:-1], count, len(requested_secure_list)))
    elif "error" in requested_secure_list[i]:
        print("Editing Tracker for {} failed {}. {}".format(str(hash_)[2:-1], 
        requested_secure_list[i]["error"]["code"], requested_secure_list[i]["error"]["message"]))
        error_torrent_hash_list.append(str(hash_)[2:-1])
    else:
        print("Editing Tracker for {} failed.".format(str(hash_)[2:-1]))
        error_torrent_hash_list.append(str(hash_)[2:-1])

print()
print("Successfully edited {} of {} torrents with errors occurred below:".format(count, len(requested_secure_list)))
for each in error_torrent_hash_list:
    print(each)

print()
for i in range(2):
    print("Retry Time {}".format(i+1))

    dmhy_req_list.clear()
    dmhy_torrent_hash_list.clear()
    count = 0

    for i, hash_ in enumerate(error_torrent_hash_list):
        dmhy_torrent_hash_list.append(hash_)
        dmhy_req_list.append({"jsonrpc": "2.0", "method": "query", "params": [hash_], "id":i+1})

    print("Fetching Secure Code...")
    resp = requests.post(__APIURL__, json=dmhy_req_list)

    if resp.status_code != 200:
        print("Failed to fetch secure code, retry later")
        time.sleep(20)
        continue

    requested_secure_list = resp.json()
    error_torrent_hash_list.clear()

    print("Begin Updating...")

    for i, hash_ in enumerate(dmhy_torrent_hash_list):
        if "result" in requested_secure_list[i]:
            count += 1
            client.core.set_torrent_trackers(hash_, [{'url':"https://daydream.dmhy.best/announce?secure={}".format(requested_secure_list[i]["result"]), 'tier':0}])
            print("Edited Tracker for {} ({}/{})".format(str(hash_)[2:-1], count, len(requested_secure_list)))
        elif "error" in requested_secure_list[i]:
            print("Editing Tracker for {} failed {}. {}".format(str(hash_)[2:-1], 
            requested_secure_list[i]["error"]["code"], requested_secure_list[i]["error"]["message"]))
            error_torrent_hash_list.append(str(hash_)[2:-1])
        else:
            print("Editing Tracker for {} failed.".format(str(hash_)[2:-1]))
            error_torrent_hash_list.append(str(hash_)[2:-1])

    print("Successfully edited {} of {} torrents with errors occurred below:".format(count, len(requested_secure_list)))
    if len(error_torrent_hash_list) == 0:
        break
