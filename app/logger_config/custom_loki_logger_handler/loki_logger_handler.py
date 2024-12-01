import copy
import json
import typing
import uuid

from loki_logger_handler import loki_logger_handler


class UUIDEncoder(json.JSONEncoder):
    def default(self, o):  # type: ignore[no-untyped-def]
        if isinstance(o, uuid.UUID):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomLokiLoggerHandler(loki_logger_handler.LokiLoggerHandler):
    def _put(self, log_record: dict[str, typing.Any]) -> None:
        labels = copy.deepcopy(self.labels)

        for key in self.label_keys:
            if key in log_record.keys():
                labels[key] = str(log_record[key])

        log_record = json.loads(
            json.dumps(log_record, ensure_ascii=False, cls=UUIDEncoder)
        )

        self.buffer.put(CustomLogLine(labels, log_record))


class CustomLogLine:
    def __init__(self, labels: dict[str, str], line: dict[str, str]) -> None:
        self.labels = labels
        self.key = self.key_from_labels(labels)
        self.line = line

    @staticmethod
    def key_from_labels(labels: dict[str, str]) -> str:
        kv_list = sorted([f'{key}.{value}' for key, value in labels.items()])
        return '_'.join(kv_list)
