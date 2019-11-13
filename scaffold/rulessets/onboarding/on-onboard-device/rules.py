from krules_core.base_functions import \
    CheckPayload, SetSubjectProperty, SetSubjectProperties, SetSubjectExtendedProperty, FlushSubject, PyCall

from krules_core import RuleConst as Const

from krules_core.base_functions import with_self as _

## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory
from krules_env import publish_results_all

from base_functions import SetEnabled

import time

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
    Set the basic properties of the device and the initial status as 'READY'
    The status will become 'ACTIVE' upon receipt of the first message
    """,
    {
        rulename: "on-onboard-device-store-properties",
        subscribe_to: "onboard-device",
        ruledata: {
            filters: [
                CheckPayload(lambda x: "data" in x and "class" in x)
            ],
            processing: [
                FlushSubject(),  # just4dev...
                SetSubjectProperties(_(lambda _self: _self.payload["data"])),
                SetSubjectExtendedProperty("deviceclass", _(lambda _self: _self.payload["class"])),
                SetSubjectProperty('status', 'READY'),
                SetEnabled(),
            ],
        },
    }

]
