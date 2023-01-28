from google_sheets import get_order_IDs, initialize_sheets, write_status_to_sheet

initialize_sheets()

order_IDs = get_order_IDs()

count = 0
sheet_updates = []

for x in order_IDs:
  count += 1
  sheet_updates.append([f"{count * 2} bites the dust"])
  
if write_status_to_sheet(count, sheet_updates):
  print("Script finished successfully, sheet updated")
