from datetime import datetime, timedelta

from krules_core.base_functions import  \
    CheckPayload, SetSubjectProperty, SetSubjectProperties, SetSubjectExtendedProperty, FlushSubject, \
    OnSubjectPropertyChangedNotIn, OnSubjectPropertyChangedIn, Route, DispatchPolicyConst, SetPayloadProperty, \
    OnSubjectPropertyChangedValue, PyCall, with_self as _, CheckPayloadPropertyValue, Check, \
    OnSubjectPropertyChanged

from krules_core import RuleConst as Const, messages




## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors

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
    Store temp property
    """,
    {
        rulename: "on-data-received-store-temp",
        subscribe_to: "data-received",
        ruledata: {
            filters: [
                Check(_(lambda _self: "tempc" in _self.payload["data"]))
            ],
            processing: [
                SetSubjectProperty("tempc", _(lambda _self: float(_self.payload["data"]["tempc"])))
            ]
        }
    },

    """
    Set temp_status COLD 
    """,
    {
        rulename: "on-tempc-changed-check-cold",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("tempc"),
                Check(_(lambda _self:
                                float(_self.payload.get("value")) < float(_self.subject.temp_min)
                )),
            ],
            processing: [
                SetSubjectProperty("temp_status", "COLD"),
            ],
        }
    },

    """
    Set temp_status NORMAL 
    """,
    {
        rulename: "on-tempc-changed-check-normal",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("tempc"),
                Check(_(lambda _self:
                                float(_self.subject.temp_min) <= float(_self.payload.get("value")) < float(_self.subject.temp_max)
                )),
            ],
            processing: [
                SetSubjectProperty("temp_status", "NORMAL"),
            ],
        }
    },

    """
    Set temp_status OVERHEATED 
    """,
    {
        rulename: "on-tempc-changed-check-overheated",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("tempc"),
                Check(_(lambda _self:
                                float(_self.payload.get("value")) >= float(_self.subject.temp_max)
                ))
            ],
            processing: [
                SetSubjectProperty("temp_status", "OVERHEATED"),
            ],
        }
    },

    """
    Since we have already intercepted the prop changed event inside the container we need to send it out explicitly
    for 'temp_status' property
    """,
    {
        rulename: "temp-status-propagate",
        subscribe_to: messages.SUBJECT_PROPERTY_CHANGED,
        ruledata: {
            filters: [
                OnSubjectPropertyChanged("temp_status"),
            ],
            processing: [
                Route(dispatch_policy=DispatchPolicyConst.DIRECT)
            ]
        },
    }
]
