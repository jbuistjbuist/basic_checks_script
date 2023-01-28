from google_sheets import get_order_IDs, initialize_sheets, write_status_to_sheet


def main():

  initialize_sheets()

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

  
  sheet_updates.append([f"{count * 2} bites the dust"])
    
  if write_status_to_sheet(count, sheet_updates):
    print("Script completed, sheet updated")


main()