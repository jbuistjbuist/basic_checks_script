#import csv module

import csv
import copy
import datetime

datetoday = str(datetime.datetime.today())

datetoday = datetoday.replace(" ", "_")
datetoday = datetoday.replace(".", "_")
datetoday = datetoday.replace(":", "_")
datetoday = datetoday.strip()

def write_updates_to_file(cell_table, order_ids):

    fields = ['Order ID', 'Member Email', 'PayPal Email', 'Shipping Match', 'SA Map', 'SA MU', 'SA Zillow', 'Billing Match', 'BA Map', 'BA MU', 'BA Zillow']

    rows = copy.deepcopy(cell_table)

    count = 0;

    for row in rows:
        row.insert(0, order_ids[count])
        count += 1

    with open(datetoday + '.csv', 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(fields)
        csv_writer.writerows(rows)

    return datetoday + '.csv' 
              
    
