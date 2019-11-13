#!/usr/bin/env python
from google.cloud import pubsub_v1
from google.oauth2 import service_account

import redis
import settings
import sys
import json
from pprint import pprint

r = redis.StrictRedis(**settings.REDIS_CONNECT_KWARGS)



credentials = service_account.Credentials.from_service_account_file("cloudrunevents-pullsub.json")
publisher = pubsub_v1.PublisherClient(credentials=credentials)
topic_path = publisher.topic_path(credentials.project_id, "ingestion")

if len(sys.argv) != 2:
    print("no device")
    sys.exit(1)

device_id = sys.argv[1]

device = r.hgetall(device_id)
if len(device) == 0:
    print("unknown device")
    sys.exit(1)

device["lat"] = round(float(device["lat"]), 7)
device["lng"] = round(float(device["lng"]), 7)
device["tempc"] = round(float(device["tempc"]), 2)
device["seq_num"] = int(device["seq_num"])

def _callback(_):
    r.hincrby(device_id, "seq_num")
    print("sent..")
    pprint(device)

future = publisher.publish(topic_path, json.dumps(device).encode("utf-8"), contentType="text/json")
future.add_done_callback(_callback)

