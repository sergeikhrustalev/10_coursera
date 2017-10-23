import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook


courses = [
    'https://www.coursera.org/learn/solid-waste-management',
    'https://www.coursera.org/learn/research-proposal-initiating-research',
    'https://www.coursera.org/learn/western-christianity-200-1650',
    'https://www.coursera.org/learn/strategic-leadership-capstone',
    'https://www.coursera.org/learn/financial-markets-global',
    'https://www.coursera.org/learn/tdd-desenvolvimento-de-software-guiado-por-testes']



def get_courses_list(xml_feed='https://www.coursera.org/sitemap~www~courses.xml'):
    pass


def get_course_info(course_urls_list):

    course_info = []

    for url in course_urls_list:
        html_content = requests.get(url).text
        soup = BeautifulSoup(html_content, 'html.parser')
    
        description = soup.find('div', {'class': 'bt3-col-sm-9 bt3-col-sm-offset-3 header-container'}).h1.string
        language = soup.find('div', {'class': 'rc-Language'}).contents[1]
        start_date = soup.find('div', {'class': 'startdate rc-StartDateString caption-text'}).span.string
        weeks_amount = len(soup.find('div', {'class': 'rc-WeekView'}).findAll('div', {'class': 'week'}))
        rating = soup.find('div', {'class': 'ratings-text bt3-hidden-xs'}).contents[1].split()[-1] 
        course_info.append((description, language, start_date, weeks_amount, rating))

    return course_info


def output_courses_info_to_xlsx(course_info, filepath):

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(['Description', 'Language', 'Start Date', 'Weeks Amount', 'User Rating'])
    for course in course_info:
        worksheet.append(course)
    workbook.save(filepath)



if __name__ == '__main__':
    #course_info = get_course_info(courses)
    #output_courses_info_to_xlsx(course_info, 'sample.xlsx',)
    get_courses_list()
