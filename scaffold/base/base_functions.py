from dateutil.parser import parse

from krules_core.base_functions import RuleFunctionBase, DispatchPolicyConst
from krules_core.providers import subject_factory, message_router_factory
from datetime import datetime
#from dateutil.parser import parse



class SetEnabled(RuleFunctionBase):

    def execute(self):

        self.subject.m_isEnabled = True


class IsEnabled(RuleFunctionBase):

    def execute(self):

        return getattr(self.subject, "m_isEnabled", False)


SCHEDULE_MESSAGE = "schedule-message"

class IsNotOutdated(RuleFunctionBase):

    def execute(self, key_func):

        key = key_func(self)
        event_time = parse(self.payload["_event_info"]["Time"])
        last_received = getattr(self.subject, key, None)
        if last_received is None:
            setattr(self.subject, key, event_time.isoformat())
            return True
        if parse(last_received) > event_time:
            return False
        setattr(self.subject, key, event_time.isoformat())
        return True



class Schedule(RuleFunctionBase):

    def execute(self, message=None, subject=None, payload=None, when=lambda _: datetime.now(), replace=False):

        if message is None:
            message = self.message
        if subject is None:
            subject = self.subject
        if payload is None:
            payload = self.payload

        if str(self.subject) != str(subject):
            subject = subject_factory(str(subject), event_info=self.subject.event_info())

        if callable(when):
            when = when(self)
        if type(when) is not str:
            when = when.isoformat()

        new_payload = {"message": message, "subject": str(subject), "payload": payload, "when": when, "replace": replace}

        message_router_factory().route(SCHEDULE_MESSAGE, subject, new_payload,
                                       dispatch_policy=DispatchPolicyConst.DIRECT)
