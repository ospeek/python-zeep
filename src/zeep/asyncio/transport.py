import httpx
import logging

import aiohttp
from requests import Response

from zeep.asyncio import bindings
from zeep.exceptions import TransportError
from zeep.transports import Transport
from zeep.utils import get_version
from zeep.wsdl.utils import etree_to_string

__all__ = ["AsyncTransport"]


class AsyncTransport(Transport):
    """Asynchronous Transport class using aiohttp."""

    binding_classes = [bindings.AsyncSoap11Binding, bindings.AsyncSoap12Binding]

    def __init__(
        self,
        client=None,
        cache=None,
        timeout=300,
        operation_timeout=None,
        session=None,
        verify_ssl=True,
        proxy=None,
    ):

        self.cache = cache
        self.client = client or httpx.AsyncClient()
        self.load_timeout = timeout
        self.operation_timeout = operation_timeout
        self.logger = logging.getLogger(__name__)

        self.verify_ssl = verify_ssl
        self.proxy = proxy
        self.client.headers = {
            "User-Agent": "Zeep/%s (www.python-zeep.org)" % (get_version())
        }

    async def _load_remote_data(self, url):
        response = await self.client.get(url, timeout=self.load_timeout)
        result = response.read()
        response.raise_for_status()
        return result

    async def post(self, address, message, headers):
        self.logger.debug("HTTP Post to %s:\n%s", address, message)
        response = await self.client.post(
            address,
            data=message,
            headers=headers,
            # verify=self.verify_ssl,
            # proxy=self.proxy,
            timeout=self.operation_timeout,
        )
        self.logger.debug(
            "HTTP Response from %s (status: %d):\n%s",
            address,
            response.status_code,
            response.read(),
        )
        return response

    async def post_xml(self, address, envelope, headers):
        message = etree_to_string(envelope)
        response = await self.post(address, message, headers)
        return self.new_response(response)

    async def get(self, address, params, headers):
        response = await self.client.get(
            address,
            params=params,
            headers=headers,
            verify_ssl=self.verify_ssl,
            proxy=self.proxy,
            timeout=self.operation_timeout
        )
        return self.new_response(response)

    def new_response(self, response):
        """Convert an aiohttp.Response object to a requests.Response object"""
        body = response.read()
        print(body)

        new = Response()
        new._content = body
        new.status_code = response.status_code
        new.headers = response.headers
        new.cookies = response.cookies
        new.encoding = response.encoding
        return new
