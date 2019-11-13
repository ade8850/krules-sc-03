from datetime import datetime, timedelta

from krules_core.base_functions import  \
    CheckPayload, SetSubjectProperty, SetSubjectProperties, SetSubjectExtendedProperty, FlushSubject, \
    OnSubjectPropertyChangedNotIn, OnSubjectPropertyChangedIn, Route, DispatchPolicyConst, SetPayloadProperty

from krules_core.base_functions import with_self as _

from krules_core import RuleConst as Const, messages

## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory
from krules_env import publish_results_errors

from base_functions import IsEnabled

import pprint

from base_functions import Schedule

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
    When data received set device status 'ACTIVE',
    then, schedule the message to set it 'INACTIVE'
    Each time some data is received, the change of state to inactive is delayed
    """,
    {
        rulename: "on-data-received-set-status-active",
        subscribe_to: "data-received",
        ruledata: {
            filters: [
                IsEnabled(),
            ],
            processing: [
                SetSubjectProperty("status", 'ACTIVE'),
                Schedule("set-device-status", payload={'value': 'INACTIVE'},
                         when=lambda _self: datetime.now()+timedelta(seconds=int(_self.subject.rate)), replace=True)
            ],
        },
    },


    """
    Set device status to INACTIVE
    """,
    {
        rulename: 'on-set-device-status',
        subscribe_to: "set-device-status",
        ruledata: {
            processing: [
                SetSubjectProperty("status", _(
                    lambda _self: _self.payload["value"]
                ))
            ]
        }
    },


]
