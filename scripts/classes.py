#defines an object in which we will store the order information from HQM for a specific order ID
class Order:
  def __init__(self, member_email, shipping_address, billing_address=None, paypal_email=None, paypal_verified=None, cc_f_name=None, cc_l_name=None):
    self.shipping_address = shipping_address
    self.member_email = member_email
    self.billing_address = billing_address
    self.paypal_email = paypal_email
    self.paypal_verified = paypal_verified
    self.cc_f_name = cc_f_name
    self.cc_l_name = cc_l_name

  #simple object method to return whether or not the shipping address is equal to the billing address
  def check_sa_equals_ba(self):
    if self.billing_address == None or self.billing_address.address == self.shipping_address.address:
      return True
    return False

  
#defines an object to store an address 
class Address:
  def __init__(self, address, city, state, postal_code, first_name=None, last_name=None):
    self.first_name=first_name or None
    self.last_name=last_name or None
    self.address = address
    self.city = city
    self.state = state
    self.postal_code = postal_code

#defines the object to store results from Ekata regarding an order
class Ekata_Info:
  def __init__(self, member_email_check, shipping_details, billing_details=None, paypal_email_check=None):
    self.member_email_check=member_email_check
    self.shipping_details=shipping_details
    self.billing_details=billing_details
    self.paypal_email_check=paypal_email_check

#for use in the ekata info object, defines how we will store the information gained from checking an address in ekata
class Address_Check: 
  def __init__(self, wpp_result, multi_unit):
    self.wpp_result = wpp_result
    self.multi_unit = multi_unit
