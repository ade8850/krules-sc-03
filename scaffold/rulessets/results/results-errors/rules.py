import requests

from krules_core.base_functions import SubjectMatch, Check, CheckPayload, Route, PyCall

from krules_core import RuleConst as Const, TopicsDefault
from krules_core import messages
import os

from krules_core.base_functions import with_self as _

import jsonpath_rw_ext as jp

from krules_core.base_functions.processing import SetPayloadProperty
from dateutil.parser import parse

## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory
#from krules_env import publish_results_default

# import pprint
# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
# results_rx_factory().subscribe(
#     on_next=publish_results_default,
# )

from krules_mongodb import WithDatabase, WithCollection, MongoDBInsertOne

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING


rulesdata = [


    """
    give the chance to subscribe specific error conditions 
    from the source originating the error
    """,
    {
        rulename: 'on-errors-propagate',
        subscribe_to: TopicsDefault.RESULTS,
        ruledata: {
            filters: [
                CheckPayload(lambda p: p["got_errors"] is True)
            ],
            processing: [
                Route(
                    _(lambda _self: "{}-errors".format(_self.payload["_event_info"]["Source"])),
                    _(lambda _self: _self.payload["subject"]),
                    _(lambda _self: _self.payload),
                )
            ]

        }
    },

    """
    Notify on mattermost
    """,
    {
        rulename: 'on-errors-notify',
        subscribe_to: TopicsDefault.RESULTS,
        ruledata: {
            filters: [
                CheckPayload(lambda p: p["got_errors"] is True)
            ],
            processing: [
                PyCall(
                    requests.post,
                    os.environ["MATTERMOST_CHANNEL_URL"],
                    json=_(lambda _self: {
                        "text": ":ambulance:  \n```python\n{}\n```".format(
                            "\n".join(jp.match1("$.processing[*].exc_info", _self.payload))
                        )
                    })
                ),
            ]
        }
    },
]