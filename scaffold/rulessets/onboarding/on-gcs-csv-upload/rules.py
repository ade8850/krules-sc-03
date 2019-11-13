from krules_cloudstorage import DeleteBlob
from krules_cloudstorage.csv import ProcessCSV_AsDict
from krules_core.base_functions import SubjectMatch, CheckPayloadPropertyValue, SetPayloadProperty, \
    CheckPayload

from krules_core.base_functions import with_self as _

from krules_core import RuleConst as Const

## ENABLE RESULTS ##########
from krules_core.providers import results_rx_factory, message_router_factory, subject_factory
from krules_env import publish_results_all

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

from cloudstorage.drivers.google import GoogleStorageDriver

rulesdata = [

    """
    Subscribe to storage, import csv
    """,
    {
        rulename: "on-csv-upload-import-devices",
        subscribe_to: "google.storage.object.finalize",
        ruledata: {
            filters: [
                SubjectMatch("onboarding/import/(?P<deviceclass>.+)/(?P<filename>.+)", payload_dest="path_info"),
                CheckPayloadPropertyValue("contentType", "text/csv"),
            ],
            processing: [
                ProcessCSV_AsDict(
                    driver=GoogleStorageDriver,
                    bucket=_(lambda _self: _self.payload["bucket"]),
                    path=_(lambda _self: _self.payload["name"]),
                    func=lambda device_data, _self: (
                        message_router_factory().route(
                            "onboard-device",
                            subject_factory(device_data.pop("deviceid"), event_info=_self.subject.event_info()),
                            {
                                "data": device_data,
                                "class": _self.payload["path_info"]["deviceclass"]
                            }),
                    )
                )
            ],
        }
    },

    """
    Catch csv upload errors, reject file
    """,
    {
        rulename: 'on-csv-upload-import-devices-error',
        subscribe_to: "on-gcs-csv-upload-errors",
        ruledata: {
            filters: [
                CheckPayload(lambda p: p["rule_name"] == "on-csv-upload-import-devices")
            ],
            processing: [
                # reject file
                DeleteBlob(
                    driver=GoogleStorageDriver,
                    bucket=_(lambda _self: _self.payload["payload"]["bucket"]),
                    path=_(lambda _self: _self.payload["payload"]["name"])
                )
            ]

        }
    },

]
