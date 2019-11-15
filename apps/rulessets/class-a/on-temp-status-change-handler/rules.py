from datetime import datetime, timedelta

from dateutil.parser import parse

from base_functions import Schedule
from krules_core.base_functions import  \
    CheckPayload, SetSubjectProperty, SetSubjectProperties, SetSubjectExtendedProperty, FlushSubject, \
    OnSubjectPropertyChangedNotIn, OnSubjectPropertyChangedIn, Route, DispatchPolicyConst, SetPayloadProperty, \
    OnSubjectPropertyChangedValue, PyCall, with_subject, with_self as _, CheckPayloadPropertyValue, \
    CheckPayloadPropertyValueNotIn, CheckPayloadPropertyValueIn, Check

from krules_core import RuleConst as Const, messages

import requests
import os


## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory
from krules_env import publish_results_all, publish_results_errors

import pprint

# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
results_rx_factory().subscribe(
    on_next=publish_results_all,
)

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING


rulesdata = [

    """
    On status NORMAL notify
    """,
    {
        rulename: "on-temp-status-back-to-normal",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadPropertyValue("value", "NORMAL"),
                CheckPayloadPropertyValueNotIn("old_value", (None,))  # skip initial state
            ],
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": " :sunglasses:  device **{}** temp status back to normal! ".format(_self.subject.name)
                    })
                ),
                SetSubjectProperty("m_lastTempStatusChanged", _(lambda _: datetime.now().isoformat()))

            ],
        },
    },

    """
    Status COLD or OVERHEATED notfiy then schedule a new check
    """,
    {
        rulename: "on-temp-status-bad",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadPropertyValueIn("value",  ("COLD", "OVERHEATED")),
            ],
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": ":scream:  device **{}** is **{}** ({}°C)".format(
                            _self.subject.name, _self.payload.get("value"), _self.subject.tempc
                        )
                    })
                ),
                SetSubjectProperty("m_lastTempStatusChanged", _(lambda _: datetime.now().isoformat())),
                Schedule(message="temp-status-recheck",
                         payload=_(lambda _self: {"old_value": _self.payload["value"]}),
                         when=_(lambda _: (datetime.now()+timedelta(seconds=30)).isoformat())),
            ],
        },
    },

    """
    Recheck
    """,
    {
        rulename: "on-temp-status-recheck",
        subscribe_to: "temp-status-recheck",
        ruledata: {
            filters: [
                Check(
                    _(lambda _self: _self.payload.get("old_value") == _self.subject.temp_status)
                )
            ],
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": ":neutral_face: device **{}** is still **{}** from {} secs".format(
                            _self.subject.name,
                            _self.payload.get("old_value"),
                            (datetime.now()-parse(_self.subject.m_lastTempStatusChanged)).seconds
                        )
                    })
                ),
                Schedule(message="temp-status-recheck",
                         payload=_(lambda _self: {"old_value": _self.payload["old_value"]}),
                         when=_(lambda _: (datetime.now()+timedelta(seconds=15)).isoformat())),
            ],
        },
    },

]
