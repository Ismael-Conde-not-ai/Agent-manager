import json
import os
from datetime import datetime


class DocumentEvents:

    def __init__(
        self,
        path="data/knowledge_events.json"
    ):

        self.path = path
        self.events = []

        self.load()

    def load(self):

        if not os.path.exists(self.path):

            self.events = []

            return

        try:

            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as file:

                self.events = json.load(file)

        except Exception:

            self.events = []

    def save(self):

        directory = os.path.dirname(
            self.path
        )

        if directory:

            os.makedirs(
                directory,
                exist_ok=True
            )

        with open(
            self.path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.events,
                file,
                indent=4,
                ensure_ascii=False
            )

    def add_event(
        self,
        event_type,
        source,
        details=None
    ):

        event = {
            "event": event_type,
            "source": source,
            "created_at": datetime.now().astimezone().isoformat(),
            "details": details or {}
        }

        self.events.append(event)

        self.save()

        return event

    def get_events(
        self,
        source=None
    ):

        if source is None:

            return self.events

        return [
            event
            for event in self.events
            if event["source"] == source
        ]