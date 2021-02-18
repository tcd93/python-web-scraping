from typing import TypedDict
import requests
from bs4 import BeautifulSoup
from algoliasearch.search_client import SearchClient

Entry = TypedDict('Entry', {'elem_id': str,
                            'title': str,
                            'url': str,
                            'company': str,
                            'address': str,
                            'benefits': str,
                            'salary': str})


# simulate a login to get salary range
# get this session from real login, this may expires after a while
# to retrieve the session id from cookie: https://developers.google.com/web/tools/chrome-devtools/storage/cookies
# then copy the string of key "_ITViec_session" at site itviec.com and paste it here
session = '[input the string of _ITViec_session]'

def scrap_itviec(page_num: int, limit: int) -> list[Entry]:
    results: list[Entry] = []

    url = f'https://itviec.com/it-jobs/ho-chi-minh-hcm?page={page_num}'
    page = requests.get(url, cookies={'_ITViec_session': session})

    soup = BeautifulSoup(page.content, 'html.parser')

    container = soup.find(id='container')
    elems = container.find_all(class_='job', limit=limit)

    for elem in elems:
        data: Entry = dict()

        data['elem_id'] = elem.attrs['id']
        data['title'] = elem.find(class_='title').text.strip()
        data['url'] = elem.attrs['data-search--job-selection-job-url']
        data['salary'] = elem.find(class_='svg-icon__text').text.strip()

        if data['url'] is not None:
            jd_link = f"https://itviec.com/{data['url']}"
            jd_page = requests.get(jd_link)
            jd_soup = BeautifulSoup(jd_page.content, 'html.parser')
            data['company'] = jd_soup.find(class_='job-details__sub-title').text.strip()
            data['address'] = jd_soup.find(class_='job-details__address-map').findPreviousSibling('span').text.strip()

        benefits = elem.find(class_='benefits')
        if benefits is not None:
            data['benefits'] = benefits.get_text(strip=True, separator=', ')

        results.append(data)

    return results


def scrap_vietnamwork(page_num: int, limit: int) -> list[Entry]:
    # In GG Chrome Network tab, filter by "queries?" call when refresh page to catch api key & app id
    index = SearchClient.create('JF8Q26WWUD', 'ecef10153e66bbd6d54f08ea005b60fc').init_index('vnw_job_v2')
    search_result = index.search(
        '',
        request_options={
            'attributesToRetrieve': ['jobId', 'company', 'alias', 'objectID', 'jobTitle', 'jobLocations', 'benefits'],
            'facetFilters': [["locationIds:29"]],  # filter jobs by HCM city
            'page': page_num - 1,
            'hitsPerPage': limit,
        }
    )['hits']

    return [*map(lambda r: Entry(elem_id=r['jobId'],
                                 title=r['jobTitle'],
                                 company=r['company'],
                                 address=r['jobLocations'][0],
                                 url='/' + r['alias'] + '-' + r['objectID'] + '-jv',  # append '-je' for Vietnamese page
                                 benefits=', '.join([*map(lambda b: b['benefitName'], r['benefits'])])
                                 ), search_result)]
