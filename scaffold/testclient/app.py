from locust import HttpLocust, Locust

from task_sets import DeviceStatusTaskSet
import random


def random_waiting(l):
    return random.expovariate(1) * 1000


class MyLocust(Locust):
    task_set = DeviceStatusTaskSet
    wait_function = random_waiting

