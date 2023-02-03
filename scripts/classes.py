class Order:
    def __init__(self, member_email, shipping_address, billing_address=None, paypal_email=None, cc_f_name=None, cc_l_name=None):
        self.shipping_address = shipping_address
        self.member_email = member_email
        self.billing_address = billing_address
        self.paypal_email = paypal_email
        self.cc_f_name = cc_f_name
        self.cc_l_name = cc_l_name

    # simple object method to return whether or not the shipping address is equal to the billing address
    def sa_equals_ba(self):
        if self.billing_address == None or self.billing_address.address == self.shipping_address.address:
            return True
        return False

    def __repr__(self):
        return "Order shipping_address=% s member_email=% s billing_address=% s paypal_email=% s cc_f_name=% s cc_l_name=% s" % (self.shipping_address,
                                                                                                                                   self.member_email,
                                                                                                                                   self.billing_address, self.paypal_email, self.cc_f_name,
                                                                                                                                   self.cc_l_name)


# defines an object to store an address
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

# defines the object to store results from Ekata regarding an order


class Ekata_Info:
    def __init__(self, member_email_check, shipping_check, billing_check=None, paypal_email_check=None):
        self.member_email_check = member_email_check
        self.shipping_check = shipping_check
        self.billing_check = billing_check
        self.paypal_email_check = paypal_email_check

    def __repr__(self):
        return "Ekata_Info member_email_check=% s shipping_check=% s billing_check=% s paypal_email_check=% s" % (self.member_email_check, self.shipping_check,
                                                                                                 self.billing_check, self.paypal_email_check)

# for use in the ekata info object, defines how we will store the information gained from checking an address in ekata


class Address_Check:
    def __init__(self, sa_wpp, ba_wpp, multi_unit, cc_wpp=None, error=None):
        self.sa_wpp = sa_wpp
        self.ba_wpp = ba_wpp
        self.cc_wpp = cc_wpp
        self.error = error
        self.multi_unit = multi_unit

    def __repr__(self):
        return "Address_Check sa_wpp=% s ba_wpp=% s cc_wpp=% s error=% s multi_unit=% s" % (self.sa_wpp, self.ba_wpp,
                                                                                                 self.cc_wpp, self.error, self.multi_unit)

