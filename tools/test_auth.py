import http.client, json, pathlib, sys
host='192.168.0.101'
port=8000

def do_request(method, path, body=None, headers=None):
    conn = http.client.HTTPConnection(host, port, timeout=10)
    if body is not None and isinstance(body, dict):
        body = json.dumps(body)
    conn.request(method, path, body=body, headers=headers or {})
    resp = conn.getresponse()
    data = resp.read().decode('utf-8', errors='ignore')
    headers = dict(resp.getheaders())
    conn.close()
    return resp.status, headers, data

email='pc_test@example.com'
password='Password123'
username='pc_test'

print('Attempting register...')
status, headers, body = do_request('POST','/api/v1/auth/register', {'username':username,'email':email,'password':password}, {'Content-Type':'application/json'})
print('REGISTER', status)
print('HEADERS:', headers.get('Set-Cookie'))
print('BODY:', body)

cookie = None
if status == 201:
    cookie = headers.get('Set-Cookie')
elif status == 409:
    print('User exists, trying login')
    status, headers, body = do_request('POST','/api/v1/auth/login', {'email':email,'password':password}, {'Content-Type':'application/json'})
    print('LOGIN', status)
    print('HEADERS:', headers.get('Set-Cookie'))
    print('BODY:', body)
    cookie = headers.get('Set-Cookie')
else:
    print('Unexpected status on register:', status)
    sys.exit(1)

if cookie:
    short_cookie = cookie.split(';')[0]
    print('Using cookie:', short_cookie)
    status, headers, body = do_request('GET','/api/v1/auth/me', headers={'Cookie':short_cookie})
    print('/auth/me', status)
    print('BODY:', body)
else:
    print('No Set-Cookie received.')
