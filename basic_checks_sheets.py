# import the google sheets functions made in the google_sheets file
from scripts.google_sheets import *

# import the selenium checks functions from the selenium checks file
from scripts.selenium_checks import initialize_webdriver, quit_webdriver, get_ekata_info, get_hqm_details

# import write to file module
from scripts.csv_write import write_updates_to_file

# import to time how long it takes
import time


# main flow of the project, function that is run when running the script (python3 basic_checks.py)
def main():

    #prompt the user to provide a range of rows to read

    range = input("\nSpecify row range to process (start number to end number e.g. 2 202). Do not include row 1. If only start value is included, script will process all remaining orders beginning from start value.\n\n")
    range = range.strip()
    range = range.split(" ")
    begin = range[0]
    end = None
    if len(range) == 2:
      end = range[1]
    

    start = time.time()

    initialize_sheets()
    update_status("In Progress")
    initialize_webdriver()
    

    order_IDs = get_order_IDs(begin, end)
    cell_table = []
    count = 0
    num_of_orders = len(order_IDs)

    # for each order ID returned from the sheet, get the order details, and use the order details to perform the ekata checks.
    # the ekata info is returned as a list with 5 elements, which is inserted into the list of cell updates
    for id in order_IDs:
        
        count += 1
        
        hqm_tries = 0
        order = False

        while not order and (hqm_tries <= 3):
            hqm_tries = hqm_tries + 1
            order = get_hqm_details(id)

        if not order:
            cell_table.append(['', '', '', '', '', '', '', ''])
            continue

        check_info = False
        ekata_tries = 0

        while not check_info and (ekata_tries <= 3):
            ekata_tries = ekata_tries + 1
            check_info = get_ekata_info(order, zendesk=False)

        if not (check_info):
            cell_table.append(['', '', '', '', '', '', '', ''])
            continue
        
        cell_table.append(check_info)
        
        if (count % 10 == 0):
            print(f'{count} / {num_of_orders} completed')

    # try to update the sheet with all of the updates, if it fails for some reason, print the error message
    try:

        try: 
            filename = write_updates_to_file(cell_table, order_IDs)

            print('results were written to file: ' + filename)
        except Exception as e:
            print(e, "Error writing to file, will try to write to google sheet")
        
        write_updates_to_sheet(cell_table, begin)
        end = time.time()
        
        update_status('Completed')
        print(f'Script completed in {end - start} seconds, sheet updated')

    except Exception as e:
        print(e, "Script completed, error updating sheet")
        update_status('Failed')

    quit_webdriver()


main()
