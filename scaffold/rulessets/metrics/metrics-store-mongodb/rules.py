from krules_core.base_functions import SubjectMatch, Check, CheckPayload

from krules_core import RuleConst as Const, TopicsDefault
from krules_core import messages
import os

from krules_core.base_functions import with_self as _

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

from pymongo import IndexModel, HASHED

DBNAME = "sc-03-metrics"

rulesdata = [

    """
    Save raw data
    """,
    {
        rulename: 'mongo-store-full-data',
        subscribe_to: TopicsDefault.RESULTS,
        ruledata: {
            processing: [
                WithDatabase(DBNAME),
                WithCollection("all", indexes=[IndexModel([("origin_id", HASHED)])], capped=True, size=1000000),
                SetPayloadProperty("origin_id", _(lambda _self: _self.payload["payload"]["_event_info"]["Originid"])),
                SetPayloadProperty("time", _(lambda _self: parse(_self.payload["payload"]["_event_info"]["Time"]))),
                MongoDBInsertOne(_(lambda _self: _self.payload)),
            ]
        }
    },

    """
    Store errors in a specific collection
    """,
    {
        rulename: 'mongo-store-errors',
        subscribe_to: TopicsDefault.RESULTS,
        ruledata: {
            filters: [
                Check(_(lambda _self: _self.payload["got_errors"] is True))
            ],
            processing: [
                WithDatabase(DBNAME),
                WithCollection("errors"),
                MongoDBInsertOne(_(lambda _self: _self.payload)),
            ]

        }
    },
]
