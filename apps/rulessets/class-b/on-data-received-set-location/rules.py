from datetime import datetime, timedelta

from krules_core.base_functions import \
    CheckPayload, SetSubjectProperty, SetSubjectProperties, SetSubjectExtendedProperty, FlushSubject, \
    OnSubjectPropertyChangedNotIn, OnSubjectPropertyChangedIn, Route, DispatchPolicyConst, SetPayloadProperty, \
    OnSubjectPropertyChangedValue, PyCall, with_subject, with_self as _, CheckPayloadPropertyValue, Check, \
    OnSubjectPropertyChanged

from krules_core import RuleConst as Const, messages

from geopy import distance

## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

import pprint

# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
results_rx_factory().subscribe(
    on_next=publish_results_errors,
)
results_rx_factory().subscribe(
    on_next=lambda result: publish_results_filtered(result, "$.processed", True)
)

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

rulesdata = [

    """
    Store coordinates for the first time, skip tolerance check
    """,
    {
        rulename: "on-data-received-store-coords-first-time",
        subscribe_to: "data-received",
        ruledata: {
            filters: [
                # we got coords
                Check(_(lambda _self: "lat" in _self.payload["data"] and "lng" in _self.payload["data"])),
                # coords is None
                Check(_(lambda _self: getattr(_self.subject, "coords", None) is None)),
            ],
            processing: [
                SetSubjectProperty("coords", _(lambda _self:
                                               str(  # TODO: need tuple stringification, solve in subject
                                                   (float(_self.payload["data"]["lat"]),
                                                    float(_self.payload["data"]["lng"]))
                                               )))
            ]
        }
    },

    """
    Store coordinates in subject, skip when under the tolerance
    """,
    {
        rulename: "on-data-received-store-coords-check-tolerance",
        subscribe_to: "data-received",
        ruledata: {
            filters: [
                # we got coords
                Check(_(lambda _self: "lat" in _self.payload["data"] and "lng" in _self.payload["data"]
                                      and getattr(_self.subject, "coords", False))),
                # store distance in payload to facilitate debugging
                SetPayloadProperty("distance",
                                   _(lambda _self: distance.distance(
                                       (float(_self.payload["data"]["lat"]), float(_self.payload["data"]["lng"])),
                                       eval(_self.subject.coords)
                                   ).meters)),
                # check distance in range
                Check(_(lambda _self: _self.payload["distance"] > float(_self.subject.tolerance))),
            ],
            processing: [
                SetSubjectProperty("coords", _(lambda _self:
                                               str(  # TODO: need tuple stringification, solve in subject
                                                   (float(_self.payload["data"]["lat"]),
                                                    float(_self.payload["data"]["lng"]))
                                               )))
            ]
        }
    },
]
