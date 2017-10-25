import time
import random
import sys

import requests

from bs4 import BeautifulSoup
from openpyxl import Workbook
from lxml import etree


def get_course_urls(xml_feed, urls_to_choice):
    total_urls = []
    picked_urls = []

    xml_content = requests.get(xml_feed).text
    root_free = etree.fromstring(xml_content.encode())
    for url_free in root_free.getchildren():
        for loc_free in url_free.getchildren():
            total_urls.append(loc_free.text)

    for _ in range(urls_to_choice):
        choice_url = random.choice(total_urls)
        picked_urls.append(choice_url)
        total_urls.remove(choice_url)

    return picked_urls


def request_content(url):
    requests_data = requests.get(url)
    requests_data.encoding = 'utf-8'
    return requests_data.text


def get_course_info(url):
    html_content = request_content(url)
    soup = BeautifulSoup(html_content, 'html.parser')

    description = soup.find('h1').string
    # sometimes coursera.org response 404 page (but http status 200)
    # even if url is correct
    if description == 'ooops... HTTP 404':
        return

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


def get_course_info_list(course_urls, wait_before_requests_sec):
    course_info_list = []
    try:
        for url in course_urls:
            time.sleep(wait_before_requests_sec)
            course_info = get_course_info(url)
            if course_info is None:
                continue
            course_info_list.append(course_info)
    except KeyboardInterrupt:
        pass

    return course_info_list


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
    urls_to_choice = 25
    wait_before_requests_sec = 0

    if len(sys.argv) == 1:
        sys.exit('Syntax: coursera.py <file.xlsx>')

    output_xlsx = sys.argv[1]
    print('Loading {} urls from {}'.format(urls_to_choice, xml_feed))
    course_urls = get_course_urls(xml_feed, urls_to_choice)
    print('Start getting course info.')

    print(
        'Press CTRL+C to terminate and write data to {} immediately'
        .format(output_xlsx)
    )

    course_info_list = get_course_info_list(
        course_urls,
        wait_before_requests_sec
    )

    print('Writing data to file {}'.format(output_xlsx))
    output_courses_info_to_xlsx(course_info_list, output_xlsx)
