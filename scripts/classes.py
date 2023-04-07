# defines a class to store order details
class Order:
    def __init__(self, member_email, shipping_address, billing_address=None, paypal_email=None, cc_f_name=None, cc_l_name=None):
        self.shipping_address = shipping_address
        self.member_email = member_email
        self.billing_address = billing_address
        self.paypal_email = paypal_email
        self.cc_f_name = cc_f_name
        self.cc_l_name = cc_l_name

    # simple object method to return whether or not the shipping address is equal to the billing address.
    def sa_equals_ba(self):
        if self.billing_address == None or (self.billing_address.address == self.shipping_address.address):
            return True
        return False

    def mb_equals_pp(self):
        if (self.member_email == self.paypal_email):
            return True
        return False
            

    # specifies what to print if you attempt to print an object instance to the console
    def __repr__(self):
        return "Order shipping_address=% s member_email=% s billing_address=% s paypal_email=% s cc_f_name=% s cc_l_name=% s" % (self.shipping_address,
                                                                                                                                 self.member_email,
                                                                                                                                 self.billing_address, self.paypal_email, self.cc_f_name,
                                                                                                                                 self.cc_l_name)

# defines a class to store an address
class Address:
    def __init__(self, address, country, postal_code, first_name=None, last_name=None):
        self.first_name = first_name or None
        self.last_name = last_name or None
        self.address = address
        self.postal_code = postal_code
        self.country = country

    def __repr__(self):
        return "Address first_name=% s last_name=% s address=% s postal_code=% s country=% s" % (self.first_name, self.last_name,
                                                                                                 self.address, self.postal_code, self.country)
