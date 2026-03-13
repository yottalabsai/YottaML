# YottaML

[![PyPI version](https://img.shields.io/pypi/v/yottaml.svg)](https://pypi.org/project/yottaml/)
[![Python versions](https://img.shields.io/pypi/pyversions/yottaml.svg)](https://pypi.org/project/yottaml/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/yottalabsai/YottaML/actions/workflows/ci.yml/badge.svg)](https://github.com/yottalabsai/YottaML/actions/workflows/ci.yml)

Python SDK and CLI for the [YottaML public API](https://docs.yottalabs.ai).

## Requirements

- Python 3.9 or higher

## Installation

```bash
pip install yottaml
```

This installs both the `yottaml` Python package and the `yotta` CLI.

---

## CLI

### Authentication

Set your API key as an environment variable (recommended):

```bash
export YOTTA_API_KEY=your-api-key
```

Or pass it directly to any command:

```bash
yotta --api-key your-api-key pods list
```

### Global options

| Option | Default | Description |
|--------|---------|-------------|
| `--api-key` | `$YOTTA_API_KEY` | API key |
| `--base-url` | `https://api.yottalabs.ai` | API base URL |
| `--debug` | off | Enable debug logging |

---

### `yotta pods` — Manage pods

```bash
# List all pods
yotta pods list

# Filter by region and/or status
yotta pods list --region us-east-3 --status 1

# Get pod details
yotta pods get <pod_id>

# Create a pod
yotta pods create \
  --image nvidia/cuda:12.1.0-base-ubuntu22.04 \
  --gpu-type NVIDIA_RTX_4090_24G \
  --gpu-count 1 \
  --region us-east-3 \
  --name my-pod

# Create with environment variables and exposed ports
yotta pods create \
  --image myrepo/myimage:latest \
  --gpu-type NVIDIA_RTX_4090_24G \
  --gpu-count 1 \
  --env MODEL_PATH=/models \
  --env DEBUG=1 \
  --expose '[{"port":8080,"protocol":"http"}]'

# Pause / resume / delete
yotta pods pause  <pod_id>
yotta pods resume <pod_id>
yotta pods delete <pod_id>
```

**`pods create` options:**

| Option | Required | Description |
|--------|----------|-------------|
| `--image` | Yes | Container image |
| `--gpu-type` | Yes | GPU type, e.g. `NVIDIA_RTX_4090_24G` |
| `--gpu-count` | No (default 1) | Number of GPUs (must be power of 2) |
| `--region` | No | Acceptable region(s), repeatable |
| `--name` | No | Pod name |
| `--resource-type` | No | `GPU` (default) or `CPU` |
| `--container-volume` | No | Container volume in GB |
| `--persistent-volume` | No | Persistent volume in GB |
| `--persistent-mount-path` | No | Persistent volume mount path |
| `--image-registry` | No | Docker registry URL for private images |
| `--credential-id` | No | Stored registry credential ID |
| `--image-public-type` | No | `PUBLIC` or `PRIVATE` |
| `--init-cmd` | No | Initialization command |
| `--env KEY=VALUE` | No | Environment variable, repeatable |
| `--expose` | No | JSON array of ports, e.g. `'[{"port":22,"protocol":"SSH"}]'` |
| `--min-vram` | No | Minimum single-card VRAM in GB |
| `--min-ram` | No | Minimum single-card RAM in GB |
| `--min-vcpu` | No | Minimum single-card vCPU count |
| `--shm` | No | Shared memory in GB |

---

### `yotta serverless` — Manage serverless endpoints

```bash
# List all deployments
yotta serverless list

# Filter by status
yotta serverless list --status RUNNING --status STOPPED

# Get deployment details
yotta serverless get <deployment_id>

# Create a deployment
yotta serverless create \
  --name my-endpoint \
  --image yottalabsai/pytorch:latest \
  --resources '[{"region":"us-east","gpuType":"NVIDIA_RTX_4090_24G","gpuCount":1}]' \
  --workers 1 \
  --service-mode QUEUE \
  --volume 256

# List workers
yotta serverless workers <deployment_id>

# Scale workers
yotta serverless scale <deployment_id> --workers 3

# Stop / start / delete
yotta serverless stop   <deployment_id>
yotta serverless start  <deployment_id>
yotta serverless delete <deployment_id>
```

**`serverless create` options:**

| Option | Required | Description |
|--------|----------|-------------|
| `--name` | Yes | Endpoint name (max 20 chars) |
| `--image` | Yes | Container image |
| `--resources` | Yes | JSON array: `[{"region":"...","gpuType":"...","gpuCount":N}]` |
| `--workers` | Yes | Initial worker count |
| `--service-mode` | Yes | `ALB`, `QUEUE`, or `CUSTOM` |
| `--volume` | Yes | Container volume in GB (min 20) |
| `--image-registry` | No | Image registry URL |
| `--credential-id` | No | Registry credential ID |
| `--init-cmd` | No | Initialization command |
| `--env KEY=VALUE` | No | Environment variable, repeatable |
| `--expose-port` | No | Port to expose |
| `--expose-protocol` | No | Expose protocol (e.g. `HTTP`) |
| `--webhook` | No | Webhook URL for worker status notifications |

---

### `yotta tasks` — Manage serverless tasks

```bash
# Submit a task
yotta tasks create \
  --endpoint-id <deployment_id> \
  --worker-port 8080 \
  --process-uri /process \
  --input '{"prompt":"hello"}'

# Get task details
yotta tasks get --endpoint-id <deployment_id> <task_id>

# List tasks (paginated)
yotta tasks list --endpoint-id <deployment_id>
yotta tasks list --endpoint-id <deployment_id> --status SUCCESS --page 2 --page-size 20

# Get queued/processing task count
yotta tasks count --endpoint-id <deployment_id>
```

---

### `yotta gpus` — Query GPU availability

```bash
yotta gpus list
```

---

### `yotta credentials` — Manage container registry credentials

```bash
# List credentials
yotta credentials list

# Get a credential
yotta credentials get <credential_id>

# Create a credential
yotta credentials create \
  --name my-registry \
  --type DOCKER_HUB \
  --username myuser \
  --password mytoken

# Update a credential
yotta credentials update <credential_id> --password newtoken

# Delete a credential
yotta credentials delete <credential_id>
```

---

## Python SDK

### `PodApi` — Pods

```python
from yottaml.pod import PodApi

client = PodApi(api_key="your-api-key")

# List pods
client.get_pods()
client.get_pods(region_list=["us-east-3"])

# Get a pod
client.get_pod("12345")

# Create a pod
client.new_pod(
    image="nvidia/cuda:12.1.0-base-ubuntu22.04",
    gpu_type="NVIDIA_RTX_4090_24G",
    gpu_count=1,
    regions=["us-east-3"],
    name="my-pod",
    expose=[{"port": 22, "protocol": "SSH"}],
)

# Pause / resume / delete
client.pause_pod("12345")
client.resume_pod("12345")
client.delete_pod("12345")
```

### `ElasticApi` — Serverless endpoints

```python
from yottaml.elastic import ElasticApi

client = ElasticApi(api_key="your-api-key")

# List deployments
client.get_deployments()
client.get_deployments(status_list=["RUNNING"])

# Get one deployment
client.get_deployment_detail(42)

# Create a deployment
client.create_deployment(
    name="my-endpoint",
    image="yottalabsai/pytorch:latest",
    resources=[{"region": "us-east", "gpuType": "NVIDIA_RTX_4090_24G", "gpuCount": 1}],
    workers=1,
    service_mode="QUEUE",
    container_volume_in_gb=256,
)

# Scale workers
client.scale_workers(42, workers=3)

# Stop / start / delete
client.stop_deployment(42)
client.start_deployment(42)
client.delete_deployment(42)

# List workers
client.get_workers(42)
```

### `SkywalkerTaskApi` — Tasks

```python
from yottaml.skywalker import SkywalkerTaskApi

client = SkywalkerTaskApi(api_key="your-api-key")

# Submit a task
client.create_task(
    endpoint_id=42,
    worker_port=8080,
    process_uri="/process",
    input={"prompt": "hello"},
    webhook="https://example.com/hook",
)

# Get task detail
client.get_task(endpoint_id=42, task_id="abc123")

# List tasks
client.list_tasks(endpoint_id=42, status="SUCCESS", page=1, page_size=20)

# Get processing count
client.get_processing_count(endpoint_id=42)
```

### `GpuApi` — GPU types

```python
from yottaml.gpu import GpuApi

client = GpuApi(api_key="your-api-key")
client.get_gpus()
```

### `CredentialApi` — Container registry credentials

```python
from yottaml.credential import CredentialApi

client = CredentialApi(api_key="your-api-key")

client.create_credential(name="my-reg", type="DOCKER_HUB", username="user", password="token")
client.get_credentials()
client.get_credential("1")
client.update_credential("1", password="newtoken")
client.delete_credential("1")
```

---

## Configuration

All API clients accept these keyword arguments:

```python
client = PodApi(
    api_key="your-api-key",          # or set YOTTA_API_KEY env var
    base_url="https://api.yottalabs.ai",  # optional override
    timeout=30,                       # request timeout in seconds
    debug=True,                       # log requests and responses
)
```

---

## Error Handling

```python
from yottaml.error import ClientError, ServerError

try:
    client.get_pod("99999")
except ClientError as e:
    print(e.status_code)    # HTTP status code (4xx)
    print(e.error_code)     # API error code
    print(e.error_message)  # API error message
except ServerError as e:
    print(e)                # 5xx server error
```

---

## License

[Apache 2.0](LICENSE)
