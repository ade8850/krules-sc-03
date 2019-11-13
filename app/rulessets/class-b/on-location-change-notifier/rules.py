import os
from datetime import datetime, timedelta

import requests

from krules_core.base_functions import \
    CheckPayload, SetSubjectProperty, SetSubjectProperties, SetSubjectExtendedProperty, FlushSubject, \
    OnSubjectPropertyChangedNotIn, OnSubjectPropertyChangedIn, Route, DispatchPolicyConst, SetPayloadProperty, \
    OnSubjectPropertyChangedValue, PyCall, with_self as _, CheckPayloadPropertyValue, Check, \
    OnSubjectPropertyChanged, CheckPayloadPropertyValueNotIn, PayloadConst

from krules_core import RuleConst as Const, messages

from geopy.geocoders import Nominatim
from geopy import distance
geolocator = Nominatim(user_agent="KRules")

## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors, publish_results_all

import pprint

# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
results_rx_factory().subscribe(
    on_next=publish_results_errors,
)

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING


rulesdata = [

    """
    Store coordinates in subject, skip when under the tolerance
    """,
    {
        rulename: "on-location-changed-notify",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                CheckPayloadPropertyValueNotIn(PayloadConst.OLD_VALUE, (None,))
            ],
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": ":kick_scooter: device **{}** moved to {}".format(
                            _self.subject.name,
                            geolocator.reverse("{}, {}".format(eval(_self.payload.get("value"))[0], eval(_self.payload.get("value"))[1]))
                        )
                    })
                ),
            ]
        }
    },
]
