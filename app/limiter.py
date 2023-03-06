import slowapi
import slowapi.util as slowapi_util


limiter = slowapi.Limiter(key_func=slowapi_util.get_remote_address)
