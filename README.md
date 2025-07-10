# Yottalabs Public API Connector (Python)

A lightweight Python library for connecting to the [Yottalabs public API](https://api.yottalabs.ai).  
Easily interact with `/openapi/v1/*` endpoints, with support for custom base URLs, request timeouts, HTTP proxies, and more.


## Requirements

- Python 3.8 or higher

## Installation

```bash
pip install yottactl
```

## Quickstart

```python
from yotta.pod import PodApi

# API key is required for user data endpoints
client = PodApi(api_key='<api_key>')

params = {
    "image": "yottalabsai/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04-2025050802",
    "gpu_type": "NVIDIA_L4_24G",
    "gpu_count": 1,
    "expose": [
        {"port": 22, "protocol": "SSH"}
    ]
}

response = client.new_pod(**params)
print(response)
```

See the [`examples/`](examples/) folder for more usage examples.

## Configuration

To use the example scripts, create a `examples/config.ini` file with your API key:

```ini
[keys]
api_key=YOUR_API_KEY_HERE
```

## Customization

- **Base URL:**  
  If not provided, defaults to `https://api.yottalabs.ai`.

- **Timeout:**  
  Set the `timeout` parameter (in seconds) to control how long to wait for a server response.  
  By default, requests do not time out.

  ```python
  client = PodApi(timeout=1)
  ```

- **Logging:**  
  Set the log level to `DEBUG` to log request URLs, payloads, and responses.

  ```python
  client = PodApi(debug=True)
  ```

## Error Handling

Two types of errors are raised:

- `yotta.error.ClientError`  
  Raised for 4XX client errors. Properties:
  - `status_code`: HTTP status code
  - `error_code`: Server error code (if available)
  - `error_message`: Server error message
  - `header`: Full response headers
  - `error_data`: Additional data (if provided)

- `yotta.error.ServerError`  
  Raised for 5XX server errors.

## Contributing

Contributions are welcome! Please open issues or pull requests.

## License

[MIT](LICENSE)
