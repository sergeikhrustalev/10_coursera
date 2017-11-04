import time
import random
import sys

import requests

from bs4 import BeautifulSoup
from openpyxl import Workbook
from lxml import etree


def get_random_urls(
    xml_feed='https://www.coursera.org/sitemap~www~courses.xml',
    url_count=20
):
    urls = []

    xml_content = requests.get(xml_feed).text
    root_free = etree.fromstring(xml_content.encode())

    for url_free in root_free.getchildren():
        for loc_free in url_free.getchildren():
            urls.append(loc_free.text)

    random.shuffle(urls)
    return urls[:url_count]


def load_html_content(urls, delay_before_request=6):

    html_content = dict()

    try:
        for url in urls:
            time.sleep(delay_before_request)
            requests_data = requests.get(url)

            if requests_data.status_code != requests.codes.ok:
                continue

            requests_data.encoding = 'utf-8'
            html_content[url] = requests_data.text
    except KeyboardInterrupt:
        pass

    return html_content


def get_course_description(soup):
    return soup.find('h1').string


def get_course_language(soup):
    return soup.find('div', {'class': 'rc-Language'}).contents[1]


def get_course_start_date(soup):
    return soup.find(
        'div', {'class': 'startdate rc-StartDateString caption-text'}
    ).span.string


def get_course_weeks_amount(soup):
    try:

        return len(soup.find(
            'div', {'class': 'rc-WeekView'}
        ).findAll('div', {'class': 'week'}))

    except AttributeError:
        pass


def get_course_rating(soup):
    try:

        return soup.find(
            'div', {'class': 'ratings-text bt3-hidden-xs'}
        ).contents[1].split()[-1]

    except AttributeError:
        pass


def prepare_course_info(url, html):
    soup = BeautifulSoup(html, 'html.parser')

    description = get_course_description(soup)
    language = get_course_language(soup)
    start_date = get_course_start_date(soup)
    weeks_amount = get_course_weeks_amount(soup)
    rating = get_course_rating(soup)

    if weeks_amount is None:
        weeks_amount = 'No course plan'

    if rating is None:
        rating = 'Not rated'

    return url, description, language, start_date, weeks_amount, rating


if __name__ == '__main__':

    xlsx_file = 'course_info.xlsx' if len(sys.argv) == 1 else sys.argv[1]

    print('Start getting course info')
    print('Press CTRL+C to terminate and write data immediately')

    workbook = Workbook()
    worksheet = workbook.active

    worksheet.append([
        'URL ADDRESS', 'DESCRIPTION', 'LANGUAGE',
        'START DATE', 'WEEKS AMOUNT', 'RATING',
    ])

    html_content = load_html_content(get_random_urls())

    for html_content_item in html_content.items():
        course_info = prepare_course_info(*html_content_item)
        worksheet.append(course_info)

    workbook.save(xlsx_file)

    print('Course info was loaded to {}'.format(xlsx_file))
