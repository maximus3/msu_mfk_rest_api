import traceback
import typing


def _update_formatted_by_extra(
    formatted: dict[str, typing.Any],
    extra: dict[str, typing.Any],
    extra_key: str | None = None,
) -> None:
    for key, value in extra.items():
        formatter_key = f'{extra_key}_{key}' if extra_key else key
        if formatter_key == 'body':
            formatted.update({formatter_key: str(value)})
        elif isinstance(value, dict):
            _update_formatted_by_extra(
                formatted, value, extra_key=formatter_key
            )
        else:
            formatted.update({formatter_key: value})


class CustomLoguruFormatter:
    def __init__(self) -> None:
        pass

    def format(self, record: typing.Any) -> dict[str, typing.Any]:
        formatted = {
            'message': record.get('message'),
            'timestamp': record.get('time').timestamp(),
            'process': record.get('process').id,
            'thread': record.get('thread').id,
            'function': record.get('function'),
            'module': record.get('module'),
            'name': record.get('name'),
            'level': record.get('level').name,
            'line': record.get('line'),
            'file_name': record.get('file').name,
            'file_path': record.get('file').path,
        }

        if record.get('extra'):
            if record.get('extra').get('extra'):
                _update_formatted_by_extra(
                    formatted=formatted, extra=record.get('extra').get('extra')
                )
            else:
                _update_formatted_by_extra(
                    formatted=formatted, extra=record.get('extra')
                )

        if record.get('level').name == 'ERROR':
            if record.get('exception'):
                exc_type, exc_value, exc_traceback = record.get('exception')
                formatted_traceback = traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                )
                formatted['stacktrace'] = ''.join(formatted_traceback)

        return formatted
