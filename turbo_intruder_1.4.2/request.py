import json
import os
import time
import socket
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def raw_http(data):
    req = ' '.join([data['method'], data['endpoint'], data['version']])
    for header, value in data['headers'].items():
        req += '\n' + ': '.join([header, value])
    req += '\n\n'
    if data['body']:
        req += data['body']
    return req


def receive_len(n):
    data = b''
    while len(data) < n:
        packet = s.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def queueRequests(target, wordlists):
    conf = json.loads(os.getenv('turbo_request_conf'))
    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=conf['concurrentConnections'],
        requestsPerConnection=conf['requestsPerConnection'],
        pipeline=conf['pipeline'],
        maxRetriesPerRequest=conf['maxRetriesPerRequest'],
        engine=conf['engine']
    )

    engine.queue(
        raw_http({'method': 'GET', 'endpoint': '/', 'version': 'HTTP/1.1', 'headers': {}, 'body': None}), label='init')
    s.connect(("localhost", int(target.baseInput)))

    while True:
        length = struct.unpack('>I', s.recv(4))[0]
        request_json = json.loads(receive_len(length))
        engine.queue(raw_http(request_json), label=request_json['label'])


def handleResponse(req, interesting):
    if req.label == 'init':
        return

    data = json.dumps({
        'label': req.label,
        'status': req.status,
        'id': req.id,
        'time': req.time,
        'response': list(req.responseAsBytes),
    }).encode('utf-8')
    s.sendall(struct.pack('>I', len(data)) + data)
