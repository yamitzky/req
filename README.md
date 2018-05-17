# req

Single file alternative to python-requests

## Motivation

[requests](https://github.com/requests/requests) is an awesome Python library to make HTTP requests.

Unfortunately, `pip install`-ing is difficult in a serverless environment such as AWS Lambda.

`req` is a minimum(broken) port of `requests`, written in [single python file](https://raw.githubusercontent.com/yamitzky/req/master/req/req.py), and it has no dependency. It is incredibly easy to use, all you have to do is coping the file.

## Installation

Copy [req.py](https://raw.githubusercontent.com/yamitzky/req/master/req/req.py).

## Usage

Very similar to `requests`.

```python
import req

res = req.get('http://httpbin.org/headers', headers={'Some': 'Header'})
print(res.json())
```

## Limitation

- Only `UTF-8` encoding is supported
- No support for some arguments: `'cookies', 'files', 'auth', 'proxies', 'verify', 'stream', 'cert'`
- No support for some properties of response
- Not tested well
