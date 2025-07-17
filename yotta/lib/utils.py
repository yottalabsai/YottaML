import json
import time
import uuid
from urllib.parse import urlencode
from urllib.parse import urlparse

from yotta.error import (
    ParameterRequiredError,
    ParameterValueError,
    ParameterTypeError,
)


def clean_none_value(d) -> dict:
    out = {}
    for k in d.keys():
        if d[k] is not None:
            out[k] = d[k]
    return out


def check_required_parameter(value, name):
    if not value and value != 0:
        raise ParameterRequiredError([name])


def check_required_parameters(params):
    """Validate multiple parameters
    params = [
        ['value1', 'name1'],
        ['value2', 'name2']
    ]

    """
    for p in params:
        check_required_parameter(p[0], p[1])


def check_enum_parameter(value, enum_class):
    if value not in set(item.value for item in enum_class):
        raise ParameterValueError([value])


def check_type_parameter(value, name, data_type):
    if value is not None and not isinstance(value, data_type):
        raise ParameterTypeError([name, data_type])


def get_timestamp():
    return int(time.time() * 1000)


def encoded_string(query):
    return urlencode(query, True).replace("%40", "@")


def convert_list_to_json_array(symbols):
    if symbols is None:
        return symbols
    res = json.dumps(symbols)
    return res.replace(" ", "")


def config_logging(logging, logging_level, log_file: str = None):
    """Configures logging to provide a more detailed log format, which includes date time in UTC
    Example: 2021-11-02 19:42:04.849 UTC <logging_level> <log_name>: <log_message>

    Args:
        logging: python logging
        logging_level (int/str): For logging to include all messages with log levels >= logging_level. Ex: 10 or "DEBUG"
                                 logging level should be based on https://docs.python.org/3/library/logging.html#logging-levels
    Keyword Args:
        log_file (str, optional): The filename to pass the logging to a file, instead of using console. Default filemode: "a"
    """

    logging.Formatter.converter = time.gmtime  # date time in GMT/UTC
    logging.basicConfig(
        level=logging_level,
        filename=log_file,
        format="%(asctime)s.%(msecs)03d UTC %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_uuid():
    return str(uuid.uuid4())


def purge_map(map: map):
    """Remove None values from map"""
    return {k: v for k, v in map.items() if v is not None and v != "" and v != 0}


def parse_proxies(proxies: dict):
    """Parse proxy url from dict, only support http and https proxy, not support socks5 proxy"""
    proxy_url = proxies.get("http") or proxies.get("https")
    if not proxy_url:
        return {}

    parsed = urlparse(proxy_url)
    return {
        "http_proxy_host": parsed.hostname,
        "http_proxy_port": parsed.port,
        "http_proxy_auth": (
            (parsed.username, parsed.password)
            if parsed.username and parsed.password
            else None
        ),
    }


def check_is_positive_int(value, name: str):
    """Validate param type and value.
    
    Args:
        value: The param to validate
        
    Raises:
        ValueError: If param is not a valid integer or is negative
    """
    if not isinstance(value, (int, str)) or isinstance(value, bool):
        raise ValueError("%s must be a positive number" % name)

    # Convert string to int if needed
    if isinstance(value, str):
        try:
            value = int(value)
        except ValueError:
            raise ValueError("%s must be a positive number" % name)

    if value <= 0:
        raise ValueError("%s must be a positive number" % name)

    return


def none_to_zero(value, name) -> int:
    """Convert None to 0 for integer values. Also validates that non-None values are valid integers.
    
    Args:
        value: Value to convert/validate

    Returns:
        int: 0 if value is None, otherwise the validated integer value

    Examples:
        >>> none_to_zero(None)
        0
        >>> none_to_zero(5)
        5
        >>> none_to_zero("123")
        123
        >>> none_to_zero(1.5)  # Raises ValueError
    """
    if value is None:
        return 0

    # Handle string inputs
    if isinstance(value, str):
        return 0 if not value.strip() else int(value)

    # Handle numeric inputs
    if isinstance(value, (int, float, bool)):
        if isinstance(value, float) and not value.is_integer() or isinstance(value, bool):
            msg = f"{name} must be an integer" if name else "Value must be an integer"
            raise ValueError(msg)
        return int(value)

    msg = f"{name} must be an integer" if name else "Value must be an integer"
    raise ValueError(msg)


def check_gpu_count(gpu_count):
    """Validate that gpu_count is a positive number and power of 2.
    
    Args:
        gpu_count: The number of GPUs to validate
        
    Raises:
        ParameterTypeError: If gpu_count is not a number
        ParameterValueError: If gpu_count is not positive or not a power of 2
        
    Examples:
        >>> check_gpu_count(1)   # Valid
        >>> check_gpu_count(2)   # Valid
        >>> check_gpu_count(4)   # Valid
        >>> check_gpu_count(3)   # Raises ParameterValueError - not power of 2
        >>> check_gpu_count(0)   # Raises ParameterValueError - not positive
        >>> check_gpu_count(-2)  # Raises ParameterValueError - not positive
        >>> check_gpu_count("abc") # Raises ParameterTypeError - not a number
    """
    # Check if gpu_count is a number
    if not isinstance(gpu_count, int) or isinstance(gpu_count, bool):
        raise ParameterValueError(["gpu_count must be an integer"])

    # Check if gpu_count is an integer
    if not float(gpu_count).is_integer():
        raise ParameterValueError(["gpu_count must be an integer"])

    # Convert to int for power of 2 check
    gpu_count = int(gpu_count)

    # Check if positive
    if gpu_count <= 0:
        raise ParameterValueError(["gpu_count must be greater than 0"])

    # Check if power of 2
    if gpu_count & (gpu_count - 1) != 0:
        raise ParameterValueError(["gpu_count must be a power of 2 (1, 2, 4, 8, etc.)"])
