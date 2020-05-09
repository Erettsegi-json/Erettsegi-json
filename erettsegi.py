import bs4
import requests
import json
from time import sleep


class Erettsegi:
    def __init__(self, time, level, subject, links):
        self.time = time.strip()
        self.level = level.strip()
        self.subject = subject.strip()
        self.links = links

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def getErettsegikPdf(path):
    sleep(0.5)
    response = requests.get('https://www.oktatas.hu' + path)
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table', {'class': 'stripped'})
    subject_dict = dict()

    for table in tables:
        subject = 'Vizsgatárgy'
        links = list()
        for row in table.tbody.findAll('tr'):
            if list(row.td.children):
                if type(list(row.td.children)[0]) == bs4.element.NavigableString:
                    if subject != 'Vizsgatárgy':
                        subject_dict[subject] = links
                    subject = str(list(row.td.children)[0])
                    links = [link['href'] for link in row.find_all('a')]
        if subject != 'Vizsgatárgy':
            subject_dict[subject] = links
    return subject_dict


def getErettsegik(path):
    response = requests.get('https://www.oktatas.hu' + path)
    print(path)
    links = set()
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    if soup.find('table', {'class': 'stripped'}):
        table = soup.find('table', {'class': 'stripped'}).tbody
        for row in table.findAll('tr'):
            for data in row.findAll('td'):
                if data.a:
                    links.add(data.findAll('a')[0]['href'])

    return links


def main():
    okatas_response = requests.get('https://www.oktatas.hu/kozneveles/erettsegi/feladatsorok')
    oktatas_soup = bs4.BeautifulSoup(okatas_response.content, 'html.parser')
    erettsegi_list = list()

    n = 0
    for row in oktatas_soup.findAll('tr', {"class": "odd"}) + oktatas_soup.findAll('tr', {"class": "even"}):
        print('n:', n)
        time = list(row.td.children)[0]
        kozep, emelt = tuple(row.td.find_next_siblings('td'))
        kozep_link, emelt_link = kozep.a['href'], emelt.a['href']
        erettsegi_linkek_kozep = getErettsegik(kozep_link)
        erettsegi_linkek_emelt = getErettsegik(emelt_link)

        for link in erettsegi_linkek_kozep:
            if not link.endswith('.pdf'):
                erettsegik = getErettsegikPdf(link)
                for subject in erettsegik:
                    if subject.strip() != '':
                        erettsegi_list.append(Erettsegi(time, 'közép', subject, erettsegik[subject]))

        for link in erettsegi_linkek_emelt:
            if not link.endswith('.pdf'):
                erettsegik = getErettsegikPdf(link)
                for subject in erettsegik:
                    if subject.strip() != '':
                        erettsegi_list.append(Erettsegi(time, 'emelt', subject, erettsegik[subject]))

        n += 1
        with open('erettsegi.json', 'w', encoding='utf8') as json_file:
            json.dump(erettsegi_list, json_file, default=lambda o: o.__dict__, ensure_ascii=False)


if __name__ == '__main__':
    main()
