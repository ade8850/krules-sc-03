from datetime import datetime

from dateutil.parser import parse
from pymongo import IndexModel, HASHED

from krules_core.base_functions import SubjectMatch, CheckPayloadPropertyValue, SetPayloadProperty, \
    WithPayload, Route, SetSubjectProperty

from krules_core.base_functions import with_self as _

from krules_core import RuleConst as Const

## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory, message_router_factory, subject_factory
from krules_env import publish_results_errors

import pprint

# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )
from krules_mongodb import WithDatabase, WithCollection, MongoDBInsertOne

results_rx_factory().subscribe(
    on_next=publish_results_errors,
)

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

DBNAME = "sc-03-data"

rulesdata = [
    {
        rulename: "on-data-redeived-store-mongodb",
        subscribe_to: "data-received",
        ruledata: {
            processing: [
                WithDatabase(DBNAME),
                WithCollection("data-received", indexes=[IndexModel([("deviceid", HASHED)])], capped=True, size=1000000,
                               exec_func=lambda c, _self:
                                   c.insert_one({
                                       "deviceid": _self.subject.name,
                                       "received_at": parse(_self.payload["receivedAt"]),
                                       "data": _self.payload["data"],
                                   }),
                               ),
            ],
        }
    }
]
