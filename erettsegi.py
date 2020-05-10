import bs4
import requests
import json
from time import sleep
import re


class Erettsegi:
    def __init__(self, time, level, subject, links):
        self.time = time.strip()
        self.level = level.strip()
        self.subject = subject.strip()
        self.links = links

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __str__(self):
        return self.time+self.subject+self.level

    def __lt__(self, other):
        return self.time > other.time


def clear_tags(s):
    return re.sub(r"<[\w/=;\"\-#:\s_\.]*>", "", s)


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
                for e in row.td.children:
                    found = False
                    if not type(e) == bs4.element.NavigableString:
                        if e.name == 'a':
                            if e.string:
                                if e.string.strip() != '':
                                    found = True
                        for a in e.find_all('a', recursive=True):
                            if a.string:
                                if a.string.strip() != '':
                                    found = True
                    if not found:
                        if (e.name == 'p' or e.name == 'span' or type(e) == bs4.element.NavigableString) and e.string:
                            if e.string.strip() != '':
                                if e.string.strip() != subject:
                                    if ('Vizsgatárgy' not in subject) and links:
                                        subject_dict[subject] = links.copy()
                                    subject = e.string.strip()
                                    links.clear()
            for a in row.find_all('a', recursive=True):
                if a.string:
                    if a.string.strip() != '':
                        print(a['href'])
                        links.append(a['href'])
        if ('Vizsgatárgy' not in subject) and links:
            subject_dict[subject] = links
    print(subject_dict)
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


blacklist = ['2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005']


def main():
    okatas_response = requests.get('https://www.oktatas.hu/kozneveles/erettsegi/feladatsorok')
    oktatas_soup = bs4.BeautifulSoup(okatas_response.content, 'html.parser')
    erettsegi_list = list()
    existing = list()

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
                    erettsegi = Erettsegi(time, 'k', subject, erettsegik[subject])
                    if (subject.strip() != '') and (time[:4] not in blacklist) and (len(erettsegik[subject]) > 0) and (str(erettsegi) not in existing):
                        existing.append(str(erettsegi))
                        erettsegi_list.append(erettsegi)

        for link in erettsegi_linkek_emelt:
            if not link.endswith('.pdf'):
                erettsegik = getErettsegikPdf(link)
                for subject in erettsegik:
                    erettsegi = Erettsegi(time, 'e', subject, erettsegik[subject])
                    if (subject.strip() != '') and (time[:4] not in blacklist) and (len(erettsegik[subject]) > 0) and (str(erettsegi) not in existing):
                        existing.append(str(erettsegi))
                        erettsegi_list.append(erettsegi)

        n += 1
    erettsegi_list.sort()
    with open('erettsegi.json', 'w', encoding='utf8') as json_file:
        json.dump(erettsegi_list, json_file, default=lambda o: o.__dict__, ensure_ascii=False)

    with open('erettsegi.txt', 'w', encoding='utf8') as txt_file:
        for erettsegi in erettsegi_list:
            txt_file.write(';'.join([erettsegi.level, erettsegi.subject, erettsegi.time, ' '.join(erettsegi.links)]) + '\n')



if __name__ == '__main__':
    #getErettsegikPdf('/kozneveles/erettsegi/feladatsorok/kozepszint_2017tavasz/kozep_10nap')
    #getErettsegikPdf('/kozneveles/erettsegi/feladatsorok/kozepszint_2018tavasz/kozep_9nap')
    #getErettsegikPdf('/kozneveles/erettsegi/feladatsorok/kozepszint_2019osz/kozep_10nap')
    #getErettsegikPdf('/kozneveles/erettsegi/feladatsorok/emelt_szint_2019osz/emelt_5nap')
    main()
