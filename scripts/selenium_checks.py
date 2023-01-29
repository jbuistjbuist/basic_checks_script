from classes import *
from pprint import pprint


#test data
shipping_address = Address('157 power line ct', 'Hamilton', 'Ontario', 'L9B1N6', 'Jeremy', 'Buist')
billing_address1 = Address('157 power line ct', 'Hamilton', 'Ontario', 'L9B1N6', 'Jeremy', 'Buist')
billing_address2 = Address('3511 Rue Ethel', 'Verdun', 'Quebec', 'H4G1R9', 'Jeremy', 'Buist')

sa_equals_ba = Order('jbuistjbuist@gmail.com', shipping_address, billing_address1)
sa_not_ba = Order('jbuistjbuist@gmail.com', shipping_address, billing_address2)
paypal_order = Order('jbuistjbuist@gmail.com', shipping_address, None, 'jeremy.j.buist@gmail.com', True)


