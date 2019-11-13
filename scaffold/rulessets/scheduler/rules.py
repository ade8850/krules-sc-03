from datetime import datetime, timedelta
from dateutil.parser import parse

from krules_core.base_functions import with_payload, \
    CheckPayload, SetSubjectProperty, SetSubjectProperties, SetSubjectExtendedProperty, FlushSubject, \
    OnSubjectPropertyChangedNotIn, OnSubjectPropertyChangedIn, Route, DispatchPolicyConst, SetPayloadProperty, \
    with_self, RuleFunctionBase

from krules_core import RuleConst as Const, messages

## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory, message_router_factory, subject_factory
from krules_env import publish_results_errors, publish_results_all, publish_results_filtered

import pprint

from krules_mongodb import WithDatabase, WithCollection, MongoDBInsertOne, MongoDBUpdateOne, MongoDBFind, \
    MongoDBDeleteByIds
from base_functions import SCHEDULE_MESSAGE, Schedule

from pymongo import IndexModel, HASHED, TEXT

# results_rx_factory().subscribe(
#     on_next=pprint.pprint
# )

results_rx_factory().subscribe(
    on_next=lambda result: publish_results_filtered(result, "$.rule_name", "on-schedule-received")
)
results_rx_factory().subscribe(
    on_next=lambda result: publish_results_filtered(result, "$.._ids_deleted_count", lambda x: x and x > 0)
)

rulename = Const.RULENAME
subscribe_to = Const.SUBSCRIBE_TO
ruledata = Const.RULEDATA
filters = Const.FILTERS
processing = Const.PROCESSING

DBNAME = "sc-03-support"
COLLECTION = "scheduler"
INDEXES = [IndexModel([("message", TEXT), ("subject", TEXT)])]

rulesdata = [

    """
    Store schedule info
    """,
    {
        rulename: "on-schedule-received",
        subscribe_to: SCHEDULE_MESSAGE,
        ruledata: {
            processing: [
                WithDatabase(DBNAME),
                WithCollection(COLLECTION, indexes=INDEXES,
                               exec_func=lambda c, _self: (
                                    _self.payload.get("replace") and c.delete_many({
                                        "message": _self.payload["message"],
                                        "subject": _self.payload["subject"],
                                    }),
                                    c.insert_one({
                                        "message": _self.payload["message"],
                                        "subject": _self.payload["subject"],
                                        "payload": _self.payload["payload"],
                                        "_when": parse(_self.payload["when"])
                                    })
                               )
                )
            ],
        },
    },

    """
    Do schedules
    """,
    {
        rulename: "on-tick-do-schedules",
        subscribe_to: "krules.heartbeat",
        ruledata: {
            processing: [
                SetPayloadProperty("_ids", []),
                WithDatabase(DBNAME),
                WithCollection(COLLECTION, indexes=INDEXES),
                MongoDBFind(
                    lambda _self: {"_when": {"$lt": datetime.now()}},  # query
                    lambda x, _self: (  # foreach
                        message_router_factory().route(x["message"],
                                                       subject_factory(x["subject"]),
                                                       x["payload"]),
                        _self.payload["_ids"].append(str(x["_id"]))
                    ),
                ),
                MongoDBDeleteByIds(payload_from="_ids")
            ]
        }
    },

]
