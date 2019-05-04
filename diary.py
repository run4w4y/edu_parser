import requests
from bs4 import BeautifulSoup
from url_helper import *
from exceptions import *
from datetime import datetime


def get_timestamp(date):
    base_date = datetime.strptime('01.05.2019', '%d.%m.%Y')
    base_timestamp = 1556658000
    new_timestamp = base_timestamp + (date - base_date).days * 86400
    return new_timestamp


class DiaryGrade:
    def __init__(self, data):
        self.grade = data.div.string
        self.comment = data['title']


    def __repr__(self):
        return 'grade {} with a comment "{}"'.format(self.grade, self.comment)


    def __str__(self):
        return '({}, {})'.format(self.grade, self.comment)


class DiarySubject:
    def __init__(self, data):
        self.data = {}

        self.time_start = data[0].contents[0]
        self.data['time_start'] = self.time_start

        self.time_end = data[0].contents[-1]
        self.data['time_end'] = self.time_end

        self.time = '{} - {}'.format(self.time_start, self.time_end)
        self.data['time'] = self.time
        
        self.name = data[1].string
        self.data['time_start'] = self.time_start

        if data[2].p is not None:
            self.homework = data[2].p.string
        else:
            self.homework = ''
        self.data['homework'] = self.homework

        if data[3].i is not None:
            self.comment = data[3].i.string
        else:
            self.comment = ''
        self.data['comment'] = self.comment

        if data[4].find('table', attrs={'class': 'marks'}) is not None:
            cols = data[4].tr.find_all('td')
            self.grades = [DiaryGrade(col) for col in cols]
            self.data['grades'] = self.grades
        else:
            self.grades = []
            self.data['grades'] = self.grades
    

    def __repr__(self):
        return 'instance of DiarySubject class with name {}'.format(self.name)


    def __str__(self):
        return str(self.data)



class DiaryDay:
    def __init__(self, session, date=datetime.today().strftime('%d.%m.%Y')):
        self.date = datetime.strptime(date, '%d.%m.%Y')
        self.date_str = date
        self.weekday = self.date.weekday()
        response = session.get(diary_day_url + str(get_timestamp(self.date)))

        if 'не найден' in response.text:
            raise LoginError('it appears that you are not logged in')
        
        html = BeautifulSoup(response.text, 'html.parser')
        main_table = html.find('table', attrs={'class': 'main'})
        rows = main_table.find_all('tr')
        
        self.subjects = []
        for row in rows[1:]:
            cols = row.find_all('td')
            try:
                cols[0]['title']
            except KeyError:
                self.subjects.append(DiarySubject(
                    [col for col in cols]
                ))
    

    def __repr__(self):
        return 'instance of DiaryDay class with date {}'.format(self.date_str)

    
    def __str__(self):
        return '{}, {}, {}'.format(self.weekday, self.date_str, str(self.subjects))
