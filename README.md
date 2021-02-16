This is a tutorial (with code sample) for scraping job contents from job searching pages such as 
[_itviec_](itviec.com)
, [_vietnamwork_](https://www.vietnamworks.com/)
, [_jobhopin_](https://jobhopin.com/)
using Python's [`requests`](https://requests.readthedocs.io/en/master/)

### Scraping Jobhopin.com
First we go to the target url: https://jobhopin.com/viec-lam/vi?cities=ho-chi-minh&type=job

This is what we'd see:

![index.png](img/jobhopin/1.png)

If we open it via Chrome's Developer Console, we get an entirely different page:

![chrome_dev.png](img/jobhopin/2.png)

**Jobhopin.com** is built by a client-side-rendered framework (like _Reactjs_), meaning the web server just 
returns a bunch of Javascript code to the browser instead of an HTML page like normal, so tools like 
`requests` can not see the contents if we request the above link.

In this case, we can check if the job data is already embedded into the JS codes itself (this is a technique 
called **data de-hydration** by front-end gurus). Open up search drawer (CTRL+SHIFT+F12) in Devtool and search 
by company name (because company name is likely not affected translation libraries and easily searchable):

![search_result.png](img/jobhopin/3.png)

Nothing's found, data might be coming from an external API request, we need to investigate the Network tab more 
thoroughly (_tips: filter requests by __XHR___):

![portal.png](img/jobhopin/4.png)

As guessed, the info can be easily retrievable by making `GET` requests to [admin.jobhop.vn](admin.jobhop.vn/api/public/jobs);
open up another browser tab and paste in
[this link](https://admin.jobhop.vn/api/public/jobs/?cities=79&industries=&levels=&jobTypes=&salaryMin=0&page=1&pageSize=10&ordering=)

![img_1.png](img/jobhopin/6.png)

Now we can easily get what we need:
```python
import requests

url = 'https://admin.jobhop.vn/api/public/jobs/?cities=79&format=json&industries=&jobTypes=&levels=&ordering=&page=1&pageSize=10&salaryMin=0'

print(requests.get(url).json()['data'])
```

**One more thing, the salary**

If we did not log in, the API will not display `salary` information, `salaryMin` & `salaryMax` would show `null`
like the above image

Log in the web page and catch the Network request again, salary info will be returned from API:

![salary.png](img/jobhopin/7.png)

Comparing with previously non-logged in request, we see that this time the request header includes a **Bearer token**
(see OAuth2.0 authorization [document](https://tools.ietf.org/html/rfc6750)):

![bearer.png](img/jobhopin/8.png)

If this time we use Postman to send the `GET` request with this token attached, we can retrieve the salary info 
just like normal; or via code:
```python
import requests

url = 'https://admin.jobhop.vn/api/public/jobs/?cities=79&format=json&industries=&jobTypes=&levels=&ordering=&page=1&pageSize=10&salaryMin=0'
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOjE2MTQwMDU2NTgsInN1YiI6IjEzMGM0ZWNlLWI4NWItNGQzZC04Y2M0LTJjZjMzODVhMTVjMCIsImlhdCI6MTYxMzQ2MjA1OSwiZXhwIjoxNjIyMTAyMDU5fQ.mOicukGrkSTyHb1O1Dj10Wj3dKhOOw7WaO5zUV4faPM'

json = requests.get(url, headers={
    'Authorization': f'Bearer {token}'
}).json()['data']['collection']

result = filter(lambda v: True if v['salaryMin'] is not None else False, json)
print(*result)
```

The access token has an expiry date (normally, 1 or 2 months), so if you're fine with manually "refreshing" the code
after a while, then we're basically done; if not, then read on.

**How to get access token?**

In the above example, I used my Google's account to log in, so the token was coming from their Oauth2 [service](https://developers.google.com/identity/protocols/oauth2/openid-connect#sendauthrequest),
but for simplicity's sake, we're going to retrieve the access token from Jobhopin's own authorization service.

Register a Jobhopin account, navigate to their login page, Open Network tab & log in again:

![img.png](img/jobhopin/9.png)

We can see that the token is returned from their server at endpoint `/account/api/v1/login/` if we include
correct credentials in the request body:
```python
import requests

token = requests.post(
    'https://admin.jobhop.vn/account/api/v1/login/',
    json={'usernameOrEmail': '[your email]', 'password': '[your password]', 'role': 'ROLE_JOBSEEKER'},
).json()['data']['accessToken']

url = 'https://admin.jobhop.vn/api/public/jobs/?cities=79&format=json&industries=&jobTypes=&levels=&ordering=&page=1&pageSize=10&salaryMin=0'

json = requests.get(url, headers={
    'Authorization': f'Bearer {token}'
}).json()['data']['collection']

result = filter(lambda v: True if v['salaryMin'] is not None else False, json)
print(*result)
```

---

## Install
`pip install -r requirements.txt`

## Start Server
`python server.py`
