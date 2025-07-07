import json
import logging
from json import JSONDecodeError

import requests

from yotta.__version__ import __version__
from yotta.error import ClientError, ServerError
from yotta.lib.utils import cleanNoneValue
from yotta.lib.utils import encoded_string


class API(object):
    def __init__(
            self,
            api_key=None,
            base_url=None,
            timeout=None,
            proxies=None,
            show_header=False,
            private_key=None,
            private_key_pass=None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        if self.base_url is None:
            self.base_url = "https://api.yottalabs.ai"

        self.timeout = timeout
        self.proxies = None
        self.show_header = False
        self.private_key = private_key
        self.private_key_pass = private_key_pass
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "Yottalabs-Python-SDK/" + __version__,
                "X-Api-Key": f"{api_key}",
            }
        )

        if show_header is True:
            self.show_header = True

        if type(proxies) is dict:
            self.proxies = proxies

        self._logger = logging.getLogger(__name__)
        return

    def http_get(self, url_path, payload=None):
        if payload is None:
            payload = {}

        url = self.base_url + url_path
        self._logger.debug("url: " + url)
        params = cleanNoneValue(
            {
                "params": self._prepare_params(payload),
                "timeout": self.timeout,
                "proxies": self.proxies,
            }
        )

        response = self.session.get(url=url, **params)

        self._logger.debug("http_get raw response from server:" + response.text)
        self._handle_exception(response)
        return response.json()

    def http_post(self, url_path, payload=None):
        if payload is None:
            payload = {}

        url = self.base_url + url_path
        self._logger.debug("url: " + url)
        params = cleanNoneValue(
            {
                "timeout": self.timeout,
                "proxies": self.proxies,
            }
        )

        response = self.session.post(url=url, json=payload, **params)

        self._logger.debug("http_post raw response from server:" + response.text)
        self._handle_exception(response)
        return response.json()

    def http_delete(self, url_path, payload=None):
        if payload is None:
            payload = {}

        url = self.base_url + url_path
        self._logger.debug("url: " + url)
        params = cleanNoneValue(
            {
                "params": self._prepare_params(payload),
                "timeout": self.timeout,
                "proxies": self.proxies,
            }
        )

        response = self.session.delete(url=url, **params)

        self._logger.debug("http_delete raw response from server:" + response.text)
        self._handle_exception(response)
        return response.json()

    def _prepare_params(self, params):
        return encoded_string(cleanNoneValue(params))

    def _dispatch_request(self, http_method):
        return {
            "GET": self.session.get,
            "DELETE": self.session.delete,
            "PUT": self.session.put,
            "POST": self.session.post,
        }.get(http_method, "GET")

    def _handle_exception(self, response):
        status_code = response.status_code
        if status_code < 400:
            return
        if 400 <= status_code < 500:
            try:
                err = json.loads(response.text)
            except JSONDecodeError:
                raise ClientError(
                    status_code, None, response.text, response.headers, None
                )
            error_data = None
            if "data" in err:
                error_data = err["data"]
            raise ClientError(
                status_code, err["code"], err["message"], response.headers, error_data
            )
        raise ServerError(status_code, response.text)
