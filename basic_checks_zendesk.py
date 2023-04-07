# import the google sheets functions made in the google_sheets file
from scripts.google_sheets import get_ss_info, update_check_outcome, initialize_sheets

# import the selenium checks functions from the selenium checks file
from scripts.selenium_checks import initialize_webdriver, quit_webdriver, get_ekata_info, get_hqm_details

#import zendesk functionality
from scripts.zendesk_api import update_ticket, initialize_zendesk

# main flow of the project, function that is run when running the script for zendesk
def main():

    initialize_sheets()
    initialize_zendesk()
    initialize_webdriver()

    ss_info = get_ss_info()

    count = 1

    for info in ss_info:

        order_id = info[0]
        ticket = info[1]

        count = count + 1
        
        hqm_tries = 0
        order = False

        while not order and (hqm_tries <= 3):
            hqm_tries = hqm_tries + 1
            order = get_hqm_details(order_id)

        if not order:
            update_check_outcome(count, "Fail")
            continue

        check_info = False
        ekata_tries = 0

        while not check_info and (ekata_tries <= 3):
            ekata_tries = ekata_tries + 1
            check_info = get_ekata_info(order, zendesk=True)

        if not (check_info):
            update_check_outcome(count, "Fail")
            continue

        try:
            comment = f' \n *Order {order_id}* \n --- \n **Member Email:** {check_info[0]}\n **PayPal Email:** {check_info[1] or "N/A"}\n \
                             --- \n **SA WPP:** {check_info[2]}\n **SA Map:** {check_info[3] or "N/A"}\n **SA Multi-unit:** {check_info[4]} \n \
                             **SA Zillow:** {check_info[5] or "N/A"}\n --- \n'
            
            if (check_info[6] != "SA = BA"):
                comment = comment + f'**BA WPP:** {check_info[6]}\n **BA Map:** {check_info[7] or "N/A"} \n **BA Multi-unit:** {check_info[8] or "N/A"} \n **BA Zillow:** {check_info[9] or "N/A"}\n --- \n'

            update_ticket(ticket, comment)
            update_check_outcome(count, "Posted")
        except Exception as e:
            print(e, order_id)
            update_check_outcome(count, "Fail")


    print("Script finished")
    quit_webdriver()

main()
