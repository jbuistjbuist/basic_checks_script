# import the google sheets functions made in the google_sheets file
from scripts.google_sheets import *

# import the selenium checks functions from the selenium checks file
from scripts.selenium_checks import initialize_webdriver, quit_webdriver, get_ekata_info, get_hqm_details


# main flow of the project, function that is run when running the script (python3 basic_checks.py)
def main():

    initialize_sheets()
    initialize_webdriver()

    order_IDs = get_order_IDs()
    cell_table = []

    # for each order ID returned from the sheet, get the order details, and use the order details to perform the ekata checks.
    # the ekata info is returned as a list with 5 elements, which is inserted into the list of cell updates
    for id in order_IDs:

        order = get_hqm_details(id)

        if not (order):
            cell_table.append(['Err/Manual', 'Err/Manual',
                              'Err/Manual', 'Err/Manual', 'Err/Manual'])
            continue

        check_info = get_ekata_info(order)

        if not (check_info):
            cell_table.append(['Err/Manual', 'Err/Manual',
                              'Err/Manual', 'Err/Manual', 'Err/Manual'])
            continue

        cell_table.append(check_info)

    # try to update the sheet with all of the updates, if it fails for some reason, print the error message
    try:

        write_updates_to_sheet(cell_table)
        update_status('Completed')
        print("Script completed, sheet updated")

    except Exception as e:
        print(e, "Script completed, error updating sheet")
        update_status('Failed')

    quit_webdriver()


main()
