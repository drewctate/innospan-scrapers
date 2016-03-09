import csv

infile = open('us.csv', 'rb')
reader = csv.reader(infile)
new_rows = []
for row in reader:
    if row[0] != 'Last Name':
        new_rows.append(row)

outfile = open('uscleaned.csv', 'wb')
writer = csv.writer(outfile)
for row in new_rows:
    writer.writerow(row)
