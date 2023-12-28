dt_format = '%Y-%m-%d %H:%M:%S'
dt_format_filename = dt_format.replace(' ', '_').replace(':', '-')

LOGGER_PARAMS = {
    'rotation': '1024 MB',
    'retention': 1,
    'compression': 'tar.gz',
    'serialize': True,
    'enqueue': True,
}
