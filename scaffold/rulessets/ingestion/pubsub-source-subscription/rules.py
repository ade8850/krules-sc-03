from datetime import datetime

from krules_core.base_functions import SubjectMatch, CheckPayloadPropertyValue, SetPayloadProperty, \
    WithPayload, Route, SetSubjectProperty

from krules_core.base_functions import with_self as _

from base_functions import IsNotOutdated
from krules_core import RuleConst as Const

## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory, message_router_factory, subject_factory
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
    Just emit "data-received" event
    Data should be handled by application specific logic
    """,
    {
        rulename: "on-data-received-propagate",
        subscribe_to: "google.pubsub.topic.publish",
        ruledata: {
            filters: [
                IsNotOutdated(lambda _self: "data-received#{}".format(_self.payload.get("deviceid")))
            ],
            processing: [
                SetSubjectProperty("m_lastSeen", datetime.now().isoformat()),
                Route("data-received",                                 # message
                      _(lambda _self: _self.payload.pop("deviceid")),  # subject
                      _(lambda _self: {                                # payload
                          "receivedAt": _self.payload["_event_info"]["Time"],
                          "data": _self.payload
                      })),
            ],
        }
    }
]
