#defines an object in which we will store the order information from HQM for a specific order ID
class Order:
  def __init__(variable, member_email, shipping_address=None, billing_address=None, paypal_email=None, paypal_verified=None):
    variable.shipping_address = shipping_address
    variable.member_email = member_email
    variable.billing_address = billing_address
    variable.paypal_email = paypal_email
    variable.paypal_verified = paypal_verified

  #simple object method to return whether or not the shipping address is equal to the billing address
  def check_sa_equals_ba(variable):
    if variable.billing_address == None:
      return True
    if variable.billing_address.address == variable.shipping_address.address:
      return True
    return False

  
#defines an object to store an address 
class Address:
  def __init__(variable, address, city, state, postal_code, first_name=None, last_name=None):
    variable.first_name=first_name or None
    variable.last_name=last_name or None
    variable.address = address
    variable.city = city
    variable.state = state
    variable.postal_code = postal_code

#defines the object to store results from Ekata regarding an order
class Ekata_Info:
  def __init__(variable, member_email_check, shipping_details, billing_details=None, paypal_email_check=None):
    variable.member_email_check=member_email_check
    variable.shipping_details=shipping_details
    variable.billing_details=billing_details
    variable.paypal_email_check=paypal_email_check

#for use in the ekata info object, defines how we will store the information gained from checking an address in ekata
class Address_Check: 
  def __init__(variable, wpp_result, multi_unit):
    variable.wpp_result = wpp_result
    variable.multi_unit = multi_unit
