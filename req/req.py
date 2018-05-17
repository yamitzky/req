import urllib
import json


def get(url, params=None, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('get', url, params=params, **kwargs)


def options(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('options', url, **kwargs)


def head(url, **kwargs):
    kwargs.setdefault('allow_redirects', False)
    return request('head', url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    return request('post', url, data=data, json=json, **kwargs)


def put(url, data=None, **kwargs):
    return request('put', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    return request('patch', url, data=data, **kwargs)


def delete(url, **kwargs):
    return request('delete', url, **kwargs)


def request(method, url, **kwargs):
    kwargs = kwargs.copy()
    unsupported = kwargs.keys() & {'cookies', 'files', 'auth', 'proxies', 'verify', 'stream', 'cert'}
    if unsupported:
        raise Exception(f'{unsupported} is not supported.')
    if not kwargs.get('allow_redirects', True):
        raise Exception('allow_redirects must be True.')

    if kwargs.get('params'):
        url = f'{url}?{urllib.parse.urlencode(kwargs["params"])}'
    req = urllib.request.Request(url)
    if kwargs.get('headers'):
        req.headers = kwargs['headers']
    if kwargs.get('data'):
        data = kwargs['data']
        if isinstance(data, dict):
            data = list(data.items())
        if isinstance(data, bytes):
            req.data = data
        elif isinstance(data, list):
            req.headers['Content-Type'] = 'application/x-www-form-urlencoded'
            req.data = urllib.parse.urlencode(data, doseq=True)
    elif kwargs.get('json') and kwargs['json'] is not None:
        req.data = json.dumps(kwargs['json']).encode()
        req.headers['Content-Type'] = 'application/json'

    try:
        kwargs = {k: v for k, v in kwargs.items() if k in {'timeout'}}
        with urllib.request.urlopen(req, **kwargs) as res:
            return Response(res)
    except urllib.error.HTTPError as e:
        return Response(e)


class Response:
    def __init__(self, response):
        self.raw = response
        self.content = response.read()

    def __repr__(self):
        return f'<Response [{self.status_code}]>'

    def json(self, **kwargs):
        return json.loads(self.content, **kwargs)

    @property
    def url(self):
        return self.raw.geturl()

    @property
    def status_code(self):
        return self.raw.code

    @property
    def headers(self):
        return self.raw.headers

    @property
    def ok(self):
        try:
            self.raise_for_status()
        except urllib.error.HTTPError:
            return False
        return True

    def raise_for_status(self):
        if isinstance(self.raw, urllib.error.HTTPError):
            raise self.raw

    @property
    def reason(self):
        return self.raw.reason

    @property
    def text(self):
        return self.content.decode()
