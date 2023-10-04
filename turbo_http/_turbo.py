import os
import subprocess
import socket
import traceback
from threading import Thread
from urllib.parse import urlencode, urljoin, urlparse
import importlib.resources as resources
from contextlib import contextmanager
import json
import asyncio
import time


@contextmanager
def get_resource_path(package: str, resource: str):
    resource_path = resources.path(package, resource)
    with resource_path as p:
        yield p


class Request:
    def __init__(self, future, method, endpoint, params=None, headers=None, body=None, http2=False):
        self._future = future
        self.method = method
        self.endpoint = endpoint
        self.params = params
        self.headers = headers
        self.body = body
        self.http2 = http2

    def _payload(self):
        data = json.dumps({
            'label': str(id(self._future)),
            'version': 'HTTP/1.1' if not self.http2 else 'HTTP/2',
            'method': self.method,
            'endpoint': self.endpoint,
            'headers': self.headers,
            'body': self.body
        }).encode('utf-8')
        return len(data).to_bytes(4, 'big') + data


class Response:
    def __init__(self, _id, domain, raw, request, elapsed, status_code):
        self.id = _id
        self.url = urljoin(domain, request.endpoint)
        self.elapsed = elapsed
        self.status_code = status_code

        self.headers, self.content = self._parse_raw(raw)

    def json(self):
        return json.loads(self.content)

    def _parse_raw(self, raw):
        decoded = bytes(raw).decode('utf-8')
        header_part, content = decoded.split('\r\n\r\n', 1)
        start_line, headers = header_part.split('\r\n', 1)
        header_dict = {}
        for header in headers.split('\r\n'):
            key, value = header.split(': ', 1)
            header_dict[key] = value
        return header_dict, content


class Engine:
    #  BURP = 1
    THREADED = 2
    HTTP2 = 3
    #  BURP2 = 4
    #  SPIKE = 5


class TurboClient:
    futures = dict()
    port = 0

    def __init__(
            self,
            url,
            headers=None,
            concurrent_connections=100,
            requests_per_connection=1000,
            pipeline=True,
            max_retries_per_request=5,
            engine=Engine.HTTP2,
            http2=False,
            debug=False
    ):
        print('Warming TurboClient (25s)...')
        self.headers = {
            'host': urlparse(url).netloc,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'Connection': 'keep-alive'
        }
        if headers:
            self.headers.update(headers)

        with get_resource_path('turbo_http', 'turbo_intruder') as file_path:
            self.turbo_intruder = file_path

        self.url = url
        self.concurrent_connections = concurrent_connections
        self.requests_per_connection = requests_per_connection
        self.pipeline = pipeline
        self.max_retries_per_request = max_retries_per_request
        self.engine = engine
        self.http2 = http2

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._initialize_socket(s)

        self._find_java()
        self.process = self._spawn()
        if debug:
            self._observe()

        self.connection, _ = s.accept()
        self.loop = asyncio.get_event_loop()
        self.monitor_task = self.loop.create_task(self._monitor_socket())

    def _initialize_socket(self, s):
        s.bind(("localhost", 0))
        self.port = s.getsockname()[1]
        s.listen(5)

    def _find_java(self):
        java_home = os.environ.get("JAVA_HOME")
        self.java = f'{java_home}/bin/java.exe' if java_home else 'java'
        try:
            subprocess.Popen([self.java, "-version"], stderr=subprocess.PIPE)
        except FileNotFoundError:
            raise (Exception("Java executable not found. Install or update %JAVA_HOME%."))

    def _spawn(self):
        env = os.environ.copy()
        env['turbo_request_conf'] = json.dumps({
            'concurrentConnections': self.concurrent_connections,
            'requestsPerConnection': self.requests_per_connection,
            'pipeline': self.pipeline,
            'maxRetriesPerRequest': self.max_retries_per_request,
            'engine': self.engine
        })
        cmd = [self.java, '-jar', f'{self.turbo_intruder}/turbo.jar',
               f'{self.turbo_intruder}/request.py', f'{self.turbo_intruder}/request.txt', self.url, f'{self.port}']
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)

    async def _receive_len(self, n):
        data = b''
        while len(data) < n:
            packet = await self.loop.sock_recv(self.connection, n - len(data))
            if not packet:
                return None
            data += packet
        return data

    async def _monitor_socket(self):
        while True:
            length = await self.loop.sock_recv(self.connection, 4)
            data = await self._receive_len(int.from_bytes(length, 'big'))
            response = json.loads(data)
            request = self.futures.pop(response.get('label'))
            request._future.set_result(Response(
                _id=response.get('id'),
                domain=self.url,
                raw=response.get('response'),
                request=request,
                elapsed=response.get('time'),
                status_code=response.get('status')
            ))

    def _observe(self):
        def debug():
            for msg in iter(lambda: self.process.stdout.readline(), b""):
                print(msg.decode('utf-8'))

        observation = Thread(target=debug)
        observation.daemon = True
        observation.start()

    def request(self, method, endpoint, params=None, headers=None, data=None):
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        future = self.loop.create_future()
        request = Request(
            future=future,
            method=method,
            endpoint=urljoin(endpoint, f'?{urlencode(params)}') if params else endpoint,
            params=params,
            headers=request_headers,
            body=data,
            http2=self.http2
        )
        self.futures[str(id(future))] = request
        self.connection.sendall(request._payload())
        return future

    def get(self, endpoint, params=None, headers=None):
        return self.request('GET', endpoint, params, headers)

    def post(self, endpoint, params=None, headers=None, data=None):
        return self.request('POST', endpoint, params, headers, data)

    def put(self, endpoint, params=None, headers=None, data=None):
        return self.request('PUT', endpoint, params, headers, data)

    def delete(self, endpoint, params=None, headers=None):
        return self.request('DELETE', endpoint, params, headers)

    def patch(self, endpoint, params=None, headers=None):
        return self.request('PATCH', endpoint, params, headers)

    def head(self, endpoint, params=None, headers=None):
        return self.request('HEAD', endpoint, params, headers)
