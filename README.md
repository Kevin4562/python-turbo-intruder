# turbo-http 🚀

![Build Status](https://img.shields.io/badge/build-passing-green)
![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-brightgreen)

turbo-http is an asynchronous Python requests-like wrapper for PortSwigger's Turbo Intruder. Unleash the power of Turbo Intruder's lightning-fast HTTP request engine directly from your Python scripts. Perfect for cybersecurity tasks, mass API requests, and web scraping at scale!

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
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
response = await client.get(endpoint='/endpoint/example', params={'key': 'foo', 'page': 'bar'})

if response.status_code == 200:
    print(response.json())
```

Stay tuned for more examples and advanced usage tips in our upcoming documentation!

## Acknowledgments

turbo-http is made possible thanks to the incredible work done by the original authors of [Turbo Intruder](https://github.com/PortSwigger/turbo-intruder). This library is merely a humble wrapper, designed to bring the capabilities of Turbo Intruder into the hands of Python developers without the need to navigate Burp Suite. We extend our deepest gratitude and encourage all users to explore the fantastic tools offered by [PortSwigger](https://portswigger.net/).

## License

turbo-http is licensed under the Apache-2.0 License. However, it's important to note that this library is built upon the hard work of others, so please use responsibly and always give credit where credit is due.

