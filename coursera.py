import time
import random
import sys

import requests

from bs4 import BeautifulSoup
from openpyxl import Workbook
from lxml import etree


def get_urls_from_feed(xml_feed, urls_to_choice):
    urls = []
    xml_content = requests.get(xml_feed).text
    root_free = etree.fromstring(xml_content.encode())
    for url_free in root_free.getchildren():
        for loc_free in url_free.getchildren():
            urls.append(loc_free.text)
    return urls


def withdraw_random_url(urls):
    url = random.choice(urls)
    urls.remove(url)
    return url


def request_content(url):
    requests_data = requests.get(url)
    requests_data.encoding = 'utf-8'
    return requests_data.text


def is_coursera_returns_404(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    description = soup.find('h1').string
    return description == 'ooops... HTTP 404'


def get_course_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    description = soup.find('h1').string
    language = soup.find('div', {'class': 'rc-Language'}).contents[1]

    start_date = soup.find(
        'div', {'class': 'startdate rc-StartDateString caption-text'}
    ).span.string

    try:
        weeks_amount = len(
            soup.find(
                'div', {'class': 'rc-WeekView'}
            ).findAll('div', {'class': 'week'})
        )
    except AttributeError:
        weeks_amount = 'No course plan'

    try:
        rating = soup.find(
            'div', {'class': 'ratings-text bt3-hidden-xs'}
        ).contents[1].split()[-1]
    except AttributeError:
        rating = 'Not rated'

    return url, description, language, start_date, weeks_amount, rating


def output_courses_info_to_xlsx(course_info_list, filepath):

    workbook = Workbook()
    worksheet = workbook.active

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
    workbook.save(filepath)


if __name__ == '__main__':

    xml_feed = 'https://www.coursera.org/sitemap~www~courses.xml'
    urls_to_choice = 50
    wait_before_requests_sec = 2

    if len(sys.argv) == 1:
        sys.exit('Syntax: coursera.py <file.xlsx>')

    xlsx_file = sys.argv[1]
    urls = get_urls_from_feed(xml_feed, urls_to_choice)
    course_info_list = []
    url_count = 0
    print('Start getting course info')

    print(
        'Press CTRL+C to terminate',
        'and write data to {} immediately'.format(xlsx_file)
    )

    try:
        while url_count < urls_to_choice and len(urls) > 0:
            url = withdraw_random_url(urls)
            time.sleep(wait_before_requests_sec)
            html_content = request_content(url)

            if is_coursera_returns_404(html_content):
                continue
            print('Loading info from {}'.format(url))
            course_info = get_course_info(html_content)
            course_info_list.append(course_info)
            url_count += 1
    except KeyboardInterrupt:
        pass
    print('There are {} pages processed'.format(url_count))
    print('Writing data to {}'.format(xlsx_file))
    output_courses_info_to_xlsx(course_info_list, xlsx_file)
