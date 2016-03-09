# -*- coding: utf-8 -*-
from __future__ import absolute_import
import time
import csv
import io
import unicodedata
from selenium import webdriver

#driver = webdriver.PhantomJS(executable_path='/usr/local/lib/node_modules/phantomjs/lib/phantom/bin/phantomjs')
states =["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
        "AB", "BC", "MB", "NB", "NS", "ON", "QC", "SK"]


countries = ["Algeria", "Costa%20Rica", "Argentina", "Australia", "Austria", "Bahamas", "Bahrain",
            "Belgium", "Bolivia", "Brazil", "Chile", "China", "Colombia",
            "Dominican%20Republic", "Ecuador", "Egypt", "Ethiopia", "Finland", "France",
            "Germany", "Greece", "Guatemala", "Honduras", "Hong Kong", "India", "Indonesia",
            "Iran", "Iraq", "Ireland", "Israel", "Italy", "Japan", "Jordan", "Kuwait",
            "Lebanon", "Lithuania", "Malaysia", "Mexico", "Netherlands", "New%20Zealand",
            "Nicaragua", "Nigeria", "Norway", "Pakistan", "Panama", "Peru", "Philippines",
            "Poland", "Puerto%20Rico", "Qatar", "Romania", "Russia", "Saudi%20Arabia",
            "Singapore", "South%20Africa", "South%20Korea", "Spain", "Switzerland", "Taiwan",
            "Thailand", "Tunisia", "Turkey", "Ukraine", "United%20Arab%20Emirates", "United%20Kingdom",
            "Uzbekistan", "Venezuela", "Virgin Islands,%20U.S."]

def parseName(name):
    name = name.replace(',', '')
    name = name.replace('.', '')
    name = name.replace('"', '')
    names = name.split()
    return names

def addNameAndSuffix(item, name):
    parsedName = parseName(name)

    # remove suffixes
    allSuffixes = ['MD', 'DDS', 'DMD', 'II', 'III', 'Phd', 'PhD', 'Jr', 'FACS', 'PC', 'DO']
    suffixes = []
    for word in parsedName:
        if word in allSuffixes:
            suffixes.append(word)
    parsedName = [x for x in parsedName if x not in suffixes]

    if len(parsedName) == 1:
        item['fname'] = parsedName[0]
        item['lname'] = ''
        item['MI'] = ''
    elif len(parsedName) == 2:
        item['fname'] = parsedName[0]
        item['lname'] = parsedName[1]
        item['MI'] = ''
    elif len(parsedName) == 3:
        item['fname'] = parsedName[0]
        item['MI'] = parsedName[1]
        item['lname'] = parsedName[2]
    else:
        item['fname'] = parsedName[0]
        item['MI'] = parsedName[1]
        lname = ''
        for i in range(2, len(parsedName)):
            lname += ' ' + parsedName[i]
        item['lname'] = lname

    sufstr = ''
    for suffix in suffixes:
        sufstr += ' ' + suffix
    item['suffix'] = sufstr.strip()

def normalizePhone(phone):
    phone = phone.replace('(', '')
    phone = phone.replace(')', '-')
    phone = phone.replace(' ', '')
    return phone

def asciify(item):
    try:
        item['lname'] = unicodedata.normalize('NFKD', item['lname']).encode('ascii','ignore')
        item['fname'] = unicodedata.normalize('NFKD', item['fname']).encode('ascii','ignore')
        item['MI'] = unicodedata.normalize('NFKD', item['MI']).encode('ascii','ignore')
        item['suffix'] = unicodedata.normalize('NFKD', item['suffix']).encode('ascii','ignore')
        item['address'] = unicodedata.normalize('NFKD', item['address']).encode('ascii','ignore')
        item['phone'] = unicodedata.normalize('NFKD', item['phone']).encode('ascii','ignore')
    except TypeError:
        pass

def parseSurgeonList(url, driver, writer, international):
    writer.writerow(['Last Name', 'First Name', 'Middle Initial/Name', 'Suffixes'])
    driver.get(url)
    try:
        names = driver.find_elements_by_xpath("//td[2]/h3/a")
    except:
        time.sleep(10)
        driver.get(url)
        names = driver.find_elements_by_xpath("//td[2]/h3/a")
    contactInfo = driver.find_elements_by_xpath('//td[2]/p')
    x = 0
    y = 1
    for i in range(len(names)):
        item = {}
        print names[i].text
        item['address'] = contactInfo[x].text.replace('\n', ' ')
        if not international:
            item['phone'] = normalizePhone(contactInfo[y].text)
        else:
            item['phone'] = contactInfo[y].text
        addNameAndSuffix(item, names[i].text)
        asciify(item)
        writer.writerow([item['lname'], item['fname'], item['MI'], item['suffix'], item['address'], item['phone']])
        x += 2
        y += 2
    nextBtn = driver.find_element_by_link_text("Next")

    while (nextBtn.get_attribute('disabled') != 'true'):
        print "clicking button"
        nextBtn.click()
        print "sleeping"
        print "*********************************************************"
        time.sleep(5)
        names = driver.find_elements_by_xpath("//td[2]/h3/a")
        contactInfo = driver.find_elements_by_xpath('//td[2]/p')
        x = 0
        y = 1
        for i in range(len(names)):
            tem = {}
            print names[i].text
            item['address'] = contactInfo[x].text.replace('\n', ' ')
            if not international:
                item['phone'] = normalizePhone(contactInfo[y].text)
            else:
                item['phone'] = contactInfo[y].text
            addNameAndSuffix(item, names[i].text)
            asciify(item)
            writer.writerow([item['lname'], item['fname'], item['MI'], item['suffix'], item['address'], item['phone']])
            x += 2
            y += 2
        nextBtn = driver.find_element_by_link_text("Next")
        print "*********************************************************"

print "crawl finished"

driver = webdriver.Firefox()
csvfile = open('international.csv', 'wb')
csvfile2 = open('us2.csv', 'wb')
intwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
uswriter = csv.writer(csvfile2, delimiter=',', quoting=csv.QUOTE_MINIMAL)
#for country in countries:
#    url = "http://www1.plasticsurgery.org/find_a_surgeon/?country=" + country
#    parseSurgeonList(url, driver, uswriter, True)
for state in states:
    url = "http://www1.plasticsurgery.org/find_a_surgeon/?state=" + state
    parseSurgeonList(url, driver, uswriter, False)
