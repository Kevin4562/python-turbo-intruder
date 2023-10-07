import base64
import json
import os
import time
import socket
import struct
from base64 import b64encode, b64decode
import traceback

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def raw_http(data):
    req = ' '.join([data['method'], data['endpoint'], data['version']])
    for header, value in data['headers'].items():
        req += os.linesep + ': '.join([header.title(), value])
    req += os.linesep*2
    if data['body']:
        req += data['body']
    return req


def receive_len(n):
    data = b''
    while len(data) < n:
        data += s.recv(n - len(data))
    return data


def queueRequests(target, wordlists):
    conf = json.loads(os.getenv('turbo_request_conf'))
    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=conf['concurrentConnections'],
        requestsPerConnection=conf['requestsPerConnection'],
        pipeline=conf['pipeline'],
        maxRetriesPerRequest=conf['maxRetriesPerRequest'],
        timeout=conf['timeout'],
        engine=conf['engine'],
    )

    engine.queue(
        raw_http({'method': 'GET', 'endpoint': '/', 'version': 'HTTP/1.1', 'headers': {}, 'body': None}), label='init')
    s.connect(("localhost", int(target.baseInput)))

    while True:
        length = struct.unpack('>I', receive_len(4))[0]
        request_json = json.loads(receive_len(length))
        raw_request = raw_http(request_json)
        engine.queue(raw_request, label=request_json['label'])


def handleResponse(req, interesting):
    if req.label == 'init':
        return

    data = json.dumps({
        'label': req.label,
        'status': req.status,
        'id': req.id,
        'time': req.time,
        'response': b64encode(req.responseAsBytes),
    }).encode('utf-8')
    s.sendall(struct.pack('>I', len(data)) + data)
