#import the google sheets functions made in the google_sheets file
from scripts.google_sheets import *
from scripts.selenium_checks import initialize_webdriver


#main flow of the project, this is the file to run when running the script
def main():

  initialize_sheets()
  #initialize_webdriver()

  order_IDs = get_order_IDs()

  count = 0
  sheet_updates = []

  for id in order_IDs:
    count += 1

    #order_details = get_hqm_details(id)

    #if order_details == 'Approved' or 'Cancelled': 
      #sheet_updates.append([order_details])
      #continue
    
    #ekata_info = get_ekata_info(order_details)

    # if post_hqm_comment(ekata_info):
        #sheet_updates.append(['checks done ✨]')
    # else: 
        #sheets_updates.append(['failed 😰, manual review required'])

  
    sheet_updates.append([f"{count * 2} bites the dust", '=HYPERLINK("https://www.google.ca/maps/@45.4594449,-73.5716899,3a,75y,3.95h,90t/data=!3m7!1e1!3m5!1sS5KFQhAl0peCyc6ymaknsA!2e0!6shttps:%2F%2Fstreetviewpixels-pa.googleapis.com%2Fv1%2Fthumbnail%3Fpanoid%3DS5KFQhAl0peCyc6ymaknsA%26cb_client%3Dmaps_sv.tactile.gps%26w%3D203%26h%3D100%26yaw%3D3.9452515%26pitch%3D0%26thumbfov%3D100!7i13312!8i6656", "CATS")', 'hi', 'hi', 'hi'])
    
  if write_status_to_sheet(count, sheet_updates):
    update_success()
    print("Script completed, sheet updated")


main()