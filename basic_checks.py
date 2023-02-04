# import the google sheets functions made in the google_sheets file
from scripts.google_sheets import *
from scripts.selenium_checks import initialize_webdriver, quit_webdriver, get_ekata_info, get_hqm_details


# main flow of the project, this is the file to run when running the script
def main():

    initialize_sheets()
    # initialize_webdriver()

    order_IDs = get_order_IDs()
    cell_table = []

    for id in order_IDs:

        # order = get_hqm_details(id)

        # if not (order):
        #    cell_table.append(['Manual', 'Manual', 'Manual', 'Manual', 'Manual'])
        #    continue



        # check_info = get_ekata_info(order_details)
        #if not (check_info):
        #    cell_table.append(['Manual', 'Manual', 'Manual', 'Manual', 'Manual'])
        #    continue
       

        # cell_table.append(check_info)

        cell_table.append(["bites the dust", '=HYPERLINK("https://www.google.ca/maps/@45.4594449,-73.5716899,3a,75y,3.95h,90t/data=!3m7!1e1!3m5!1sS5KFQhAl0peCyc6ymaknsA!2e0!6shttps:%2F%2Fstreetviewpixels-pa.googleapis.com%2Fv1%2Fthumbnail%3Fpanoid%3DS5KFQhAl0peCyc6ymaknsA%26cb_client%3Dmaps_sv.tactile.gps%26w%3D203%26h%3D100%26yaw%3D3.9452515%26pitch%3D0%26thumbfov%3D100!7i13312!8i6656", "CATS")', 'hi', 'hi', 'hi'])

    try:

        write_updates_to_sheet(cell_table)
        update_status('Completed')
        print("Script completed, sheet updated")

    except:

        print("Script completed, error updating sheet")

    quit_webdriver()


main()
