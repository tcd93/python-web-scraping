This is a tutorial (with code sample) for scraping job contents from job searching pages such as 
[_itviec_](itviec.com)
, [_vietnamworks_](https://www.vietnamworks.com/)
, [_jobhopin_](https://jobhopin.com/)
using Python's [`requests`](https://requests.readthedocs.io/en/master/)

---

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
### Scraping Itviec.com
Target url: https://itviec.com/it-jobs/ho-chi-minh-hcm

![img.png](img/itviec/0.png)

Again, by checking the site from Devtool's _preview_ tab, we can see that the contents stay mostly the same, 
except the right-hand side part:

![img.png](img/itviec/1.png)

Job details are fetched after the main page is loaded, and most of what we need is inside that details page, 
so we need a way to fetch these data.

This is the HTML structure of a job item from the list:

![img.png](img/itviec/2.png)

Notice the attribute `data-search--job-selection-job-url`, navigate to that [link](https://itviec.com/it-jobs/frontend-engineer-vuejs-reactjs-line-vietnam-5858/content) 
gives us a raw HTML page with all the details we need.

So, to scrap this page, there needs to be two steps:
1. fetch the main page, parse the HTML, get the link from attribute `data-search--job-selection-job-url`
2. fetch the page from that link, parse the HTML, get the data

Parsing the HTML contents is very easy in Python with [_BeautifulSoup_](https://pypi.org/project/beautifulsoup4/), 
checkout the code in `scrapper.py` for working example.

**Getting the salary**

Like the previous website, the salary info of jobs are hidden behind a login, we need to identify what authorization 
technique is used.

By debugging the login workflow from Network tab, you'll notice a id stored in Cookie after `/sign_in` request:

![img.png](img/itviec/3.png)

That ID is what let the server knows _who_ the client is, without it, it'll treat the client as anonymous and do not 
return the salary information.

By attaching that ID into each request's cookie, you'll _trick_ the server into thinking that this request is made 
by a valid, logged-in user (well, it is, technically):

```python
import requests

session = '5j1C3ZA...' ## your session ID here
url = 'https://itviec.com/it-jobs/ho-chi-minh-hcm'
page = requests.get(url, cookies={'_ITViec_session': session})
```

Now you can also scrap the salary range from returned HTML content.

**Automating stuff**

Just like the bearer token, session ID also has an expiry time, but you can use code to emulate a login; steps are 
very similar to previous example, but this time we'd need to include something called __CSRF token__ (`authenticity_token`) 
in the login `POST` request, here's a valid form data from `/sign-in` page:

![img.png](img/itviec/4.png)

This token's purpose is to prevent [_phishing_ attacks](https://owasp.org/www-community/attacks/csrf), it's a random-generated 
string by the server upon first request, and it's attached to the HTML page (usually as a hidden input)

![img.png](img/itviec/5.png)

With that, we can now use Python's `requests` package to "automate" logins and retrieve session id from response header. 
I'm too lazy to include code here (because _itviec_'s session expiry time is actually quite long, and does not expire 
upon logout! no need to write extra codes, lol)

---

### Scraping Vietnamworks.com

This one is the easiest of the bunch, because they don't store job data at their server; instead, they delegate that task to a 3rd party service called [Algolia search](https://www.algolia.com/products/search/).

So we don't even need to touch their site to get the contents (the job list is loaded dynamically, `requests` would not work anyway). 
What we need is the `app_id` and `api_id` for the Algolia [search client](https://github.com/algolia/algoliasearch-client-python) to connect to their service, to catch those keys, Chrome's devtool is your best friend, but I'm going to simplify your work and write them out:
```python
from algoliasearch.search_client import SearchClient
index = SearchClient.create('JF8Q26WWUD', 'ecef10153e66bbd6d54f08ea005b60fc').init_index('vnw_job_v2')
search_result = index.search(...)
```

---

## Conclusion

No website is like another, understanding how it's made is key to scraping it effectively.

`selenium` is (most of the time) overrated when you have basic knowledge about HTML & common authorization techniques.

---

## Requirement
Python 3.9

## Install
`pip install -r requirements.txt`

## Start Server
`python server.py`
