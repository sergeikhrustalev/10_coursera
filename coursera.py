import time
import random
import sys

import requests

from bs4 import BeautifulSoup
from openpyxl import Workbook
from lxml import etree


def get_urls_from_feed(xml_feed):
    urls = []
    xml_content = requests.get(xml_feed).text
    root_free = etree.fromstring(xml_content.encode())
    for url_free in root_free.getchildren():
        for loc_free in url_free.getchildren():
            urls.append(loc_free.text)
    return urls


def request_status_content(url):
    requests_data = requests.get(url)
    requests_data.encoding = 'utf-8'
    return requests_data.status_code, requests_data.text


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


def prepare_course_info_for_xlsx(url, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

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


def append_course_info_list_into_worksheet(worksheet, course_info_list):

    worksheet.append([
        'URL ADDRESS',
        'DESCRIPTION',
        'LANGUAGE',
        'START DATE',
        'WEEKS AMOUNT',
        'RATING',
    ])

    for course in course_info_list:
        worksheet.append(course)


if __name__ == '__main__':

    xml_feed = 'https://www.coursera.org/sitemap~www~courses.xml'
    urls_to_choice = 50
    wait_before_requests_sec = 2

    if len(sys.argv) == 1:
        sys.exit('Syntax: coursera.py <file.xlsx>')

    xlsx_file = sys.argv[1]
    urls = get_urls_from_feed(xml_feed)
    random.shuffle(urls)
    course_info_list = []
    url_count = 0
    print('Start getting course info')

    print(
        'Press CTRL+C to terminate',
        'and write data to {} immediately'.format(xlsx_file)
    )

    try:
        while url_count < urls_to_choice:
            url = urls[url_count]
            time.sleep(wait_before_requests_sec)
            http_status, html_content = request_status_content(url)

            if http_status != requests.codes.ok:
                continue

            print('Loading info from {}'.format(url))
            course_info = prepare_course_info_for_xlsx(url, html_content)
            course_info_list.append(course_info)
            url_count += 1
    except KeyboardInterrupt:
        pass

    print('There are {} pages processed'.format(url_count))
    print('Writing data to {}'.format(xlsx_file))

    workbook = Workbook()
    worksheet = workbook.active
    append_course_info_list_into_worksheet(worksheet, course_info_list)
    workbook.save(xlsx_file)
