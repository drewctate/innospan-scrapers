import usaddress
from usaddress import RepeatedLabelError
import csv

readfile = open('uscleaned.csv', 'rb')
reader = csv.reader(readfile)
new_rows = []
problem_rows = []
for row in reader:
    row[4] = row[4].replace('US', '')
    print row[4]
    try:
        address = usaddress.tag(row[4])[0]
        try:
            city = address['PlaceName']
        except KeyError:
            city = ''
        try:
            state = address['StateName']
        except KeyError:
            state = ''
        try:
            zipcode = address['ZipCode']
        except KeyError:
            zipcode = ''
        try:
            country = address['Country']
        except KeyError:
            country = ''
        address['PlaceName'] = None
        address['StateName'] = None
        address['ZipCode'] = None
        addressstr = ''
        for i in range(len(address)):
            part = address.popitem(last=False)[1]
            if part is not None:
                addressstr += ' ' + part
        new_rows.append([row[0], row[1], row[2], row[3], row[5],
        addressstr, city, state, zipcode, country])
    except RepeatedLabelError:
        new_rows.append([row[0], row[1], row[2], row[3], row[5],
        row[4], '', '', ''])
        problem_rows.append(row)

writefile = open('usseparateaddresses.csv', 'wb')
writer = csv.writer(writefile)
writer.writerow(['Last Name', 'First Name', 'Middle Initial', 'Suffixes', 'Phone', 'Address', 'City', 'State', 'Zip', 'Country'])
for row in new_rows:
    try:
        writer.writerow(row)
    except UnicodeError:
        problem_rows.append(row)
        pass

print ''
print "%s problematic addresses: " % len(problem_rows)
for row in problem_rows:
    print row[4]
