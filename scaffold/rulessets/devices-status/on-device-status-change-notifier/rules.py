from datetime import datetime, timedelta

from krules_core.base_functions import \
    CheckPayload, SetSubjectProperty, SetSubjectProperties, SetSubjectExtendedProperty, FlushSubject, \
    OnSubjectPropertyChangedNotIn, OnSubjectPropertyChangedIn, Route, DispatchPolicyConst, SetPayloadProperty, \
    OnSubjectPropertyChangedValue, PyCall, CheckPayloadPropertyValue

from krules_core.base_functions import with_self as _

from krules_core import RuleConst as Const, messages

import requests
import os


## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors

import pprint

# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
results_rx_factory().subscribe(
    on_next=publish_results_errors
)

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING


rulesdata = [

    """
    Notify onboarded (READY)
    """,
    {
        rulename: "on-device-ready-notify",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadPropertyValue("value", "READY"),
            ],
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": ":+1: device **{}** on board! ".format(_self.subject.name)
                    })
                ),

            ],
        },
    },

    """
    Notify ACTIVE
    """,
    {
        rulename: "on-device-active-notify",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadPropertyValue("value",  "ACTIVE"),
            ],
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": ":white_check_mark: device **{}** is now **{}**".format(
                            _self.subject.name, _self.payload.get("value")
                        )
                    })
                ),

            ],
        },
    },

    """
    Notify INACTIVE
    """,
    {
        rulename: "on-device-inactive-notify",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadPropertyValue("value",  "INACTIVE"),
            ],
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": ":ballot_box_with_check: device **{}** become **{}**".format(
                            _self.subject.name, _self.payload.get("value")
                        )
                    })
                ),
            ],
        },
    },

]
