from google_sheets import get_order_IDs, initialize_sheets, write_status_to_sheet

initialize_sheets()

order_IDs = get_order_IDs()

count = 0

for x in order_IDs:
  count += 1
  write_status_to_sheet(count, 'poopoopeepee')
  