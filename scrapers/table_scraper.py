import datetime
import re
import sys
import pandas
from IPython.core.debugger import Tracer; debug_here = Tracer()
from bs4 import BeautifulSoup


Program = [
    ('Computer Engineering', 'ECE'),
    ('Computer Enginnerin', 'ECE'),
    ('Electrical', 'ECE'),
    ('ECE', 'ECE'),
    ('Computer Sc', 'CS'),
    ('Computer  Sc', 'CS'),
    ('Computer Sicen', 'CS'),
    ('Computer Sien', 'CS'),
    ('Computer S Cience', 'CS'),
    ('Computer,', 'CS'),
    ('Computers,', 'CS'),
    ('ComputerScience', 'CS'),
    ('Human Computer Interaction', 'HCI'),
    ('Human-Computer Interaction', 'HCI'),
    ('Human-computer Interaction', 'HCI'),
    ('software engineering', 'CS'),
    ('Embedded', 'ECE'),
    ('Computer Eng', 'ECE'),
    ('Computer Vision', 'CS'),
    ('Information', 'IS'),
    ('Infomation', 'IS'), ]


Degree = [
    (' MFA', 'MFA'),
    (' M Eng', 'MEng'),
    (' MEng', 'MEng'),
    (' M.Eng', 'MEng'),
    (' MS', 'MS'),
    (' MA', 'MA'),
    (' Masters', 'MS'),
    (' PhD', 'PhD'),
    (' MBA', 'MBA'),
    (' Other', 'Other'),
    (' EdD', 'Other'),
]

Status = {
    'A': 'American',
    'U': 'International with US Degree',
    'I': 'International',
    'O': 'Other',
}

errlog = {'major': [], 'gpa': [], 'general': [], 'subject': []}


def process(index, col):
    global err
    inst, major, degree, season, decision, status, date_add, date_add_ts, comment = None, None, None, None, None, None, None, None, None
    decisionfin, method, decdate, decdate_ts = None, None, None, None
    gpafin, grev, grem, grew, new_gre, sub = None, None, None, None, None, None
    if len(col) != 6:
        print("Length of column not equal to 6")
    try:
        inst = col[0].text.strip()
    except Exception as e:
        print('starting error ', e)
    try:
        major = None
        progtext = col[1].text.strip()
        if not ',' in progtext:
            print('in major', progtext)
      
            errlog['major'].append((index, col))
        else:
            parts = progtext.split(',')
            major = parts[0].strip()
            progtext = ' '.join(parts[1:])
        degree = None
        for (d, deg) in Degree:
            if d in progtext:
                degree = deg
                break
        if not degree:
            degree = 'Other'

        season = None
        mat = re.search('\([SF][01][0-9]\)', progtext)
        if mat:
            season = mat.group()[1:-1]
        else:
            mat = re.search('\(\?\)', progtext)
            if mat:
                season = None
    except NameError  as e:
        print('mat error', e)
    except :
        print("Unexpected error:", sys.exc_info()[0])
    try:
        extra = col[2].find('a',class_='extinfo')
        gpafin, grev, grem, grew, new_gre, sub = None, None, None, None, None, None
        if extra:
            gre_text = extra.text.strip()
            gpa = re.search('Undergrad GPA: ((?:[0-9]\.[0-9]{1,2})|(?:n/a))', gre_text)
            general = re.search('GRE General \(V/Q/W\): ((?:1[0-9]{2}/1[0-9]{2}/(?:(?:[0-6]\.[0-9]{2})|(?:99\.99)|(?:56\.00)))|(?:n/a))',gre_text)
            new_gref = True
            subject = re.search('GRE Subject: ((?:[2-9][0-9]0)|(?:n/a))', gre_text)
            if not gpa:
                gpa = None
            if gpa:
                gpa = gpa.groups(1)[0]
                if not gpa == 'n/a':
                    try:
                        gpafin = float(gpa)
                    except:
                        print("Debug")
            else:
                errlog['gpa'].append((index, gre_text))
            if not general:
                general = re.search(
                    'GRE General \(V/Q/W\): ((?:[2-8][0-9]0/[2-8][0-9]0/(?:(?:[0-6]\.[0-9]{2})|(?:99\.99)|(?:56\.00)))|(?:n/a))',
                    gre_text)
                new_gref = False

            if general:
                general = general.groups(1)[0]
                if not general == 'n/a':
                    try:
                        greparts = general.split('/')
                        if greparts[2] == '99.99' or greparts[2] == '0.00' or greparts[2] == '56.00':
                            grew = None
                        else:
                            grew = float(greparts[2])
                        grev = int(greparts[0])
                        grem = int(greparts[1])
                        new_gre = new_gref
                        if new_gref and (grev > 170 or grev < 130 or grem > 170 or grem < 130 or (
                                grew and (grew < 0 or grew > 6))):
                            errlog['general'].append((index, gre_text))
                            grew, grem, grev, new_gre = None, None, None, None
                        elif not new_gref and (grev > 800 or grev < 200 or grem > 800 or grem < 200 or (
                                grew and (grew < 0 or grew > 6))):
                            errlog['general'].append((index, gre_text))
                            grew, grem, grev, new_gre = None, None, None, None
                    except Exception as e:
                        print("Debug")
            else:
                errlog['general'].append((index, gre_text))
                general = None

            if subject:
                subject = subject.groups(1)[0]
                if not subject == 'n/a':
                    sub = int(subject)
            else:
                errlog['subject'].append((index, gre_text))
                subject = None

            extra.extract()
        decision = col[2].text.strip()
        try:
            #decisionfin, method, decdate, decdate_ts = None, None, None, None
            (decisionfin, method, decdate) = re.search(
                '((?:Accepted)|(?:Rejected)|(?:Wait listed)|(?:Other)|(?:Interview))? ?via ?((?:E-[mM]ail)|(?:Website)|(?:Phone)|(?:Other)|(?:Postal Service)|(?:Unknown))? ?on ?([0-9]{1,2} [A-Z][a-z]{2} [0-9]{4})?',
                decision).groups()
            if decisionfin and decisionfin == 'Accepted':
                decisionfin = 'Accepted'
            elif decisionfin and decisionfin == 'Rejected':
                decisionfin = 'Rejected'
            elif decisionfin and decisionfin == 'Wait listed':
                decisionfin = 'Wait listed'
            elif decisionfin and decisionfin == 'Unknown':
                decisionfin = 'Other'
            elif decisionfin and decisionfin == 'Interview':
                decisionfin = 'Interview'
            else:
                decisionfin = None
            if method and method == 'E-Mail':
                method = 'E-mail'
            if method and method == 'Unknown':
                method = 'Other'
            if decdate:
                try:
                    decdate_date = datetime.datetime.strptime(decdate, '%d %b %Y')
                    decdate_ts = decdate_date.strftime('%d %b %Y')
                    decdate = (decdate_date.day, decdate_date.month, decdate_date.year)
                except Exception as e:
                    decdate_date, decdate_ts, decdate = None, None, None
            else:
                decdate = None
        except Exception as e:
            print('after decdate', e)
    except Exception as e:
        print('last error',e)
    try:
        statustxt = col[3].text.strip()
        if statustxt in Status:
            status = Status[statustxt]
        else:
            status = None
    except Exception as e:
        print('status text',e)
    try:
        date_addtxt = col[4].text.strip()
        date_add_date = datetime.datetime.strptime(date_addtxt, '%d %b %Y')
        date_add_ts = date_add_date.strftime('%d %b %Y')
        date_add = (date_add_date.day, date_add_date.month, date_add_date.year)
    except:
        print(col[4].text.strip()).encode('ascii', 'ignore')
        print("Debug")
    try:
        comment = col[5].text.strip()
    except:
        print("Debug")
    res = [inst, major, degree, season, decisionfin, method, decdate, decdate_ts, gpafin, grev, grem, grew, new_gre,
           sub, status, date_add, date_add_ts, comment]
    return res


data = []
for year in range(1,2425):
    with open('{0}.html'.format(year), 'r', encoding='utf8') as f:
        soup = BeautifulSoup(f,"html.parser")
        tables = soup.findAll('table', class_='submission-table')
        for tab in tables:
            rows = tab.findAll('tr')
            for row in rows[1:]:
                cols = row.findAll('td')
                pro = process(year, cols)
                if len(pro) > 0:
                    data.append(pro)
        print(year)
        #print(data)
#for d in data:
#    d[1] = d[1].encode('ascii', 'ignore')
df = pandas.DataFrame(data)
df.to_csv('Original_data.csv')
