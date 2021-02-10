import requests
from bs4 import BeautifulSoup

Entry = dict['elem_id': str,
             'title': str,
             'url': str,
             'company': str,
             'address': str,
             'benefits': str]


def scrap_itviec(page_num=1, limit=8) -> list[Entry]:
    results: list[Entry] = []

    url = f'https://itviec.com/it-jobs/ho-chi-minh-hcm?page={page_num}'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    container = soup.find(id='container')
    elems = container.find_all(class_='job', limit=limit)

    for elem in elems:
        data: Entry = dict()

        data['elem_id'] = elem.attrs['id']
        data['title'] = elem.find(class_='title').text.strip()
        data['url'] = elem.attrs['data-search--job-selection-job-url']

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
