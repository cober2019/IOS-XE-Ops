import csv
import os


def read_csv(filepath, filename):
    
    rows = []
    file_location = os.getcwd() + filepath + filename

    with open(file_location) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                #print ("Skip first Line")
                line_count += 1
            else:
                try:
                    ips = row[1].split('-')
                    rows.append({'host': row[0], 'rec_ip': ', '.join(ips), 'svi': row[2]})
                except IndexError:
                    pass
                
    return rows


