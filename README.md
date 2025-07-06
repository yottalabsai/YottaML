# Yottalabs Public API Connector Python

This is a lightweight library that works as a connector to Yottalabs public API

- Supported APIs:
    - `/openapi/v1/*`
- Inclusion of examples
- Customizable base URL, request timeout and HTTP proxy

## Installation

```bash
pip install yottactl
```

[//]: # (## Documentation)

## RESTful APIs

Usage examples:

```python
from yotta.pod import PodApi

# API key is required for user data endpoints
client = PodApi(api_key='<api_key>')

# Post a new order
params = {
    "image": "yottalabsai/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04-2025050802",
    "gpu_type": "NVIDIA_L4_24G",
    "gpu_count": 1,
    "expose": [
        {
            "port": 22,
            "protocol": "SSH"
        }
    ]
}

response = client.new_pod(**params)
print(response)
```

Please find `examples` folder to check for more endpoints.

- In order to set your API for use of the examples, create a file `examples/config.ini` with your keys.
- Eg:
    ```ini
    # examples/config.ini
    [keys]
    api_key=abc123456
    ```

### Base URL

If `base_url` is not provided, it defaults to `https://api.yottalabs.ai`.

### Timeout

`timeout` is available to be assigned with the number of seconds you find most appropriate to wait for a server
response.<br/>
Please remember the value as it won't be shown in error message _no bytes have been received on the underlying socket
for timeout seconds_.<br/>
By default, `timeout` is None. Hence, requests do not time out.

```python
from yotta.pod import PodApi

client = PodApi(timeout=1)
```

### Display logs

Setting the log level to `DEBUG` will log the request URL, payload and response text.

### Error

There are 2 types of error returned from the library:

- `yotta.error.ClientError`
    - This is thrown when server returns `4XX`, it's an issue from client side.
    - It has 5 properties:
        - `status_code` - HTTP status code
        - `error_code` - Server's error code, e.g. `10001`
        - `error_message` - Server's error message, e.g. `Unknown order sent.`
        - `header` - Full response header.
        - `error_data`* - Additional detailed data which supplements the `error_message`.
            - **Only applicable on select endpoints, eg. `cancelReplace`*
- `yotta.error.ServerError`
    - This is thrown when server returns `5XX`, it's an issue from server side.
