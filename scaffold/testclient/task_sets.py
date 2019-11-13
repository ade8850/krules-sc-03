import json

from locust import TaskSet, task, HttpLocust
import random
import redis
import settings
import requests
import sys

r = redis.StrictRedis(**settings.REDIS_CONNECT_KWARGS)

device_count = 0

from google.cloud import pubsub_v1
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("cloudrunevents-pullsub.json")
publisher = pubsub_v1.PublisherClient(credentials=credentials)
topic_path = publisher.topic_path(credentials.project_id, "ingestion")


def next_device():
    global device_count
    device_count += 1
    return (
        format(device_count, 'X').rjust(6, '0'),
        ['classB', 'classA'][device_count % 2]
    )


class DeviceStatusTaskSet(TaskSet):

    @task(10)
    def publish(self):
        sys.stdout.write("publish {}".format(self.device_id))

        device = r.hgetall(self.device_id)
        device["lat"] = round(float(device["lat"]), 7)
        device["lng"] = round(float(device["lng"]), 7)
        device["tempc"] = round(float(device["tempc"]), 2)
        device["seq_num"] = int(device["seq_num"])

        sys.stdout.write("{}".format(device))

        future = publisher.publish(topic_path, json.dumps(device).encode("utf-8"), contentType="text/json")
        future.add_done_callback(lambda _: r.hincrby(self.device_id, "seq_num"))

        # resp = self.client.post(
        #      settings.SERVER_ENTRY_POINT_URL,
        #      json=device,
        #      headers=settings.SERVER_ENTRY_POINT_HEADERS
        #  )
        #if resp.status_code == 200:
        #r.hincrby(self.device_id, "seq_num")
        #else:
        #    sys.stdout.write("err: {}".format(resp.status_code))

    # @task(0)
    # def move(self):
    #     print("move {}".format(self.device_id))

    def on_start(self):

        global devices
        self.device_id, device_type = next_device()
        sys.stdout.write("init {}!".format(self.device_id))

        if len(r.hgetall(self.device_id)) == 0:
            r.hmset(self.device_id, {
                'deviceid': self.device_id,
                'lat': round(random.randint(450000000, 452000000) / 10000000, 7),
                'lng': round(random.randint(76000000, 76500000) / 10000000, 7),
                'tempc': round(random.randint(150, 370) / 10, 1),
                'seq_num': 0
            })



