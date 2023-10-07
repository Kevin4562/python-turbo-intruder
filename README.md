# turbo-http 🚀

![Build Status](https://img.shields.io/badge/build-passing-green)
![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-brightgreen)

turbo-http is an asynchronous Python requests-like wrapper for PortSwigger's Turbo Intruder. Unleash the power of Turbo
Intruder's lightning-fast HTTP request engine directly from your Python scripts. Perfect for cybersecurity tasks, mass
API requests, and web scraping at scale!

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Performance](#performance)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Installation

Download and install the latest released version from [PyPI](https://pypi.org/project/turbo-http/):

```bash
pip install turbo-http
```

## Requirements

- [Java SE Development](https://www.oracle.com/java/technologies/downloads/) 17+

## Quick Start

Here's a simple example to get you started:

```python
from turbo_http import TurboClient

client = TurboClient(url='https://example.net')
response = await client.get('/endpoint/example', params={'key': 'foo', 'page': 'bar'})

response.url
"https://example.net/endpoint/example?key=foo&page=bar"

response.status_code
"200"

response.headers
"{'Content-Type': 'application/json; charset=utf-8', 'Content-Length': 'XX', 'Connection': 'keep-alive'}"

```

POST Requests:

```python
from turbo_http import TurboClient

client = TurboClient(url='https://fakestoreapi.com')
post_data = {
    'title': 'example product',
    'price': 14.4,
    'description': 'example desc'
}
response = await client.post('/products', json=post_data)
```

## Performance

Results are completely dependent on the target server, engine configuration, and network conditions. The following are only some basic examples to give an idea of the general speed. Turbo Intruder's author [mentions](https://portswigger.net/research/turbo-intruder-embracing-the-billion-request-attack) 30,000 RPS being the highest they were able to achieve.

```python
# THREADED Engine (default) 100 requests (116 requests per second)

with TurboClient(url='https://httpbin.org/') as client:
    tasks = []
    for i in range(1, 100):
        tasks.append(client.get(f'/get'))
    r = await asyncio.gather(*tasks)
        
Elapsed time: 0.8579223155975342 seconds.
```

```python
# THREADED Engine (default) 1,000 requests (371 requests per second)

with TurboClient(url='https://httpbin.org/') as client:
    tasks = []
    for i in range(1, 1000):
        tasks.append(client.get(f'/get'))
    r = await asyncio.gather(*tasks)
        
Elapsed time: 2.6971070766448975 seconds.
```

```python
# HTTP2 Engine 1,000 requests (760 requests per second)

with TurboClient(url='https://httpbin.org/', engine=Engine.HTTP2) as client:
    tasks = []
    for i in range(1, 1000):
        tasks.append(client.get(f'/get'))
    r = await asyncio.gather(*tasks)
        
Elapsed time: 1.3151829242706299 seconds.
```

```python
# HTTP2 Engine 10,000 requests (3,367 requests per second)

with TurboClient(url='https://httpbin.org/', engine=Engine.HTTP2) as client:
    tasks = []
    for i in range(1, 10000):
        tasks.append(client.get(f'/get'))
    r = await asyncio.gather(*tasks)
        
Elapsed time: 2.9748992919921875 seconds.
```


## Acknowledgments

turbo-http is made possible thanks to the incredible work done by the original authors
of [Turbo Intruder](https://github.com/PortSwigger/turbo-intruder). This library is merely a humble wrapper, designed to
bring the capabilities of Turbo Intruder into the hands of Python developers without the need to navigate Burp Suite. We
extend our deepest gratitude and encourage all users to explore the fantastic tools offered
by [PortSwigger](https://portswigger.net/).

## License

turbo-http is licensed under the Apache-2.0 License. However, it's important to note that this library is built upon the
hard work of others, so please use responsibly and always give credit where credit is due.

