import base64
import json
import urllib.parse
import urllib.request
import urllib.error


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
    unsupported = kwargs.keys() & {'cookies', 'files', 'proxies', 'verify', 'stream', 'cert'}
    if unsupported:
        raise Exception(f'{unsupported} is not supported.')
    if not kwargs.get('allow_redirects', True):
        raise Exception('allow_redirects must be True.')

    headers = kwargs.get('headers') or {}

    purl = urllib.parse.urlparse(url)
    auth = kwargs.get('auth')
    if purl.username and purl.password:
        host = purl.netloc.rsplit('@', 1)[-1]
        auth = (purl.username, purl.password)
        url = urllib.parse.urlunparse(purl._replace(netloc=host))
    if kwargs.get('params'):
        url = f'{url}?{urllib.parse.urlencode(kwargs["params"])}'

    if auth:
        headers['Authorization'] = 'Basic ' + base64.b64encode(f'{auth[0]}:{auth[1]}'.encode()).decode()

    data = kwargs.get('data')
    if data is not None:
        if isinstance(data, str):
            data = data.encode()
        if isinstance(data, bytes):
            headers['Content-Type'] = 'text/plain'
        if isinstance(data, dict):
            data = list(data.items())
        if isinstance(data, list):
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            data = urllib.parse.urlencode(data, doseq=True).encode()
    elif kwargs.get('json') and kwargs['json'] is not None:
        data = json.dumps(kwargs['json']).encode()
        headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data, headers, method=method.upper())
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
