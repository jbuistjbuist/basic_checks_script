import os

# import the classes defined in the classes file
from classes import *

# for debugging (printing complete objects to console)
from pprint import pprint

# selenium modules
import os

# import the classes defined in the classes file
from classes import *

# for debugging (printing complete objects to console)
from pprint import pprint

# selenium modules
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# function to pause the code for set num of seconds
import time

# import dotenv module to use env variables
from dotenv import load_dotenv

load_dotenv()

chrome_options = Options()
chrome_options.add_argument('--start-maximized')

# add this to driver initialization later to have headless chrome
chrome_options.add_argument('--headless')

# initialize chrome driver and env variables

chrome_drive = Service()
driver = webdriver.Chrome(service=chrome_drive, options=chrome_options)
driver.implicitly_wait(30)
ekata_password = os.getenv("ekata_password")
hqm_password = os.getenv("hqm_password")
email = os.getenv("agent_email")
hqm_username = os.getenv("hqm_username")


# this function opens an HQM and Ekata tab and logs into both. If login fails, will quit the script
def initialize_webdriver():

    # ekata sign in
    driver.get('https://app.ekata.com/sign_in')

    form = driver.find_element(By.CLASS_NAME, 'simple_form')
    form.find_element(By.ID, 'profile_password').send_keys(ekata_password)
    form.find_element(By.ID, 'profile_email').send_keys(email)
    form.find_element(By.CLASS_NAME, 'btn-primary').click()

    # saves ekata window handle so tab can be accessed easily later
    global ekata_window
    ekata_window = driver.current_window_handle

    time.sleep(3)

    # if redirected to correct page, success, otherwise, fail
    if driver.current_url == 'https://app.ekata.com/search':
        print('Ekata login OK')
    else:
        print('Ekata login failed, may be failing captcha test, script quitting')
        quit()

    # HQM sign in
    driver.switch_to.new_window('tab')
    global hqm_window
    hqm_window = driver.current_window_handle

    driver.get('https://hqm.ssense.com/core/auth/login')

    form = driver.find_element(By.ID, 'formAuthentication')
    form.find_element(By.ID, 'username').send_keys(hqm_username)
    form.find_element(By.ID, 'password').send_keys(hqm_password)
    form.find_element(By.ID, 'connexion_btn').click()

    time.sleep(3)

    # if redirected to correct page, success, otherwise, fail
    if driver.current_url == 'https://hqm.ssense.com/core/':
        print('HQM login OK')
    else:
        print('HQM login failed, script quitting')
        quit()


# function to get info from Ekata, based on provided order details
def get_ekata_info(order):

    driver.switch_to.window(ekata_window)
    app = driver.find_element(
        By.CLASS_NAME, 'css-1fe9b2j-ApplicationContainer')

    member_email_check = perform_email_checks(order.member_email, app)

    if (order.paypal_email):
        paypal_email_check = 'PayPal ' + \
            perform_email_checks(order.paypal_email, app)
        member_email_check = 'Member ' + member_email_check

    print(member_email_check, paypal_email_check)


# function to perform Ekata email check, for a given email and HTML section
def perform_email_checks(email, dom_section):

    driver.implicitly_wait(5)
    dom_section.find_element(By.XPATH, "//a[text()='Email']").click()
    email_input = dom_section.find_element(By.NAME, 'email')
    email_input.send_keys(Keys.COMMAND, 'a')
    email_input.send_keys(Keys.DELETE)
    email_input.send_keys(email)
    dom_section.find_element(
        By.CLASS_NAME, 'css-uw1vjm-StyledButton-primary').click()

    try:
        email_validity = dom_section.find_element(
            By.XPATH, '//div[2]/div[2]/div[2]').text
        online_presence_html = dom_section.find_element(
            By.XPATH, '//div[2]/div[3]')
        online_presence = online_presence_html.find_element(
            By.CLASS_NAME, 'e8160634').text

        try:
            driver.implicitly_wait(0)
            time_ago = online_presence_html.find_element(
                By.CLASS_NAME, 'e8160633').text
            online_presence = online_presence + f' ({time_ago})'
            driver.implicitly_wait(5)
        except NoSuchElementException:
            driver.implicitly_wait(5)

        creation = dom_section.find_element(By.XPATH, '//div[4]/div[2]').text
        domain_reputation = dom_section.find_element(
            By.XPATH, '//div[3]/div[4]/div[2]').text

        return f'Email - Validity: {email_validity}, Online Presence: {online_presence}, Creation: {creation}, Domain: {domain_reputation}'

    except NoSuchElementException:
        return 'Email - check Failed, please review manually'


# function which takes in an order id, and retrieves the order details for a provided order
def get_hqm_details(id):

    try:

        # switch to already opened HQM tab and navigate to the URL
        driver.switch_to.window(hqm_window)
        driver.get(
            f'https://hqm.ssense.com/customer-support/master-order/edit/{id}')
        driver.implicitly_wait(15)

        # set member email, and initialize other details (to be filled in or left as none)
        member_email = driver.find_element(By.ID, 'incoice_memberemail').text
        shipping_address = None
        billing_address = None
        cc_f_name = None
        cc_l_name = None
        paypal_email = None

        # make sure the shipping field is loaded before continuing

        driver.find_element(By.ID, 'export_shipping_ups')

        shipping_field = driver.find_element(
            By.CSS_SELECTOR, '.shipping.box-address')

        # try to get shipping details, shipping fields can have c292 or c293 classes so check both

        try:

            driver.implicitly_wait(1)

            first_name_html = shipping_field.find_element(
                By.ID, 'c292_firstName')
            first_name = first_name_html.get_attribute('value')
            last_name = shipping_field.find_element(
                By.ID, 'c292_lastName').get_attribute('value')
            address = shipping_field.find_element(
                By.ID, 'c292_address').get_attribute('value')
            postal_code = shipping_field.find_element(
                By.ID, 'c292_postalCode').get_attribute('value')
            country_select = Select(shipping_field.find_element(
                By.ID, 'c292_countryID')).first_selected_option
            country = country_select.text

            shipping_address = Address(
                address, country, postal_code, first_name, last_name)

            driver.implicitly_wait(15)

        except NoSuchElementException:

            driver.implicitly_wait(15)

            first_name = shipping_field.find_element(
                By.ID, 'c293_firstName').get_attribute('value')
            last_name = shipping_field.find_element(
                By.ID, 'c293_lastName').get_attribute('value')
            address = shipping_field.find_element(
                By.ID, 'c293_address').get_attribute('value')
            postal_code = shipping_field.find_element(
                By.ID, 'c293_postalCode').get_attribute('value')
            country_select = Select(shipping_field.find_element(
                By.ID, 'c293_countryID')).first_selected_option
            country = country_select.text

            shipping_address = Address(
                address, country, postal_code, first_name, last_name)

        # if billing not same as shipping, get the billing address details

        if not (driver.find_element(By.ID, 'sameAsShipping').is_selected()):

            billing_field = driver.find_element(
                By.CSS_SELECTOR, '.billing.box-address')

            first_name = billing_field.find_element(
                By.ID, 'c291_firstName').get_attribute('value')
            last_name = billing_field.find_element(
                By.ID, 'c291_lastName').get_attribute('value')
            address = billing_field.find_element(
                By.ID, 'c291_address').get_attribute('value')
            postal_code = billing_field.find_element(
                By.ID, 'c291_postalCode').get_attribute('value')
            country_select = Select(billing_field.find_element(
                By.ID, 'c291_countryID')).first_selected_option
            country = country_select.text

            billing_address = Address(
                address, country, postal_code, first_name, last_name)

        # determine if it is a paypal, applepay, or cc order and get the appropriate info

        table = driver.find_element(
            By.CSS_SELECTOR, 'table[style="display: table;"]')
        pmt_type = table.get_attribute('id')

        if (pmt_type == 'table_payment_cc'):

            cc_full_name = table.find_element(
                By.CSS_SELECTOR, 'tr:nth-child(2) > td:nth-child(5)').text
            seperated = cc_full_name.split(' ')
            if (len(seperated) >= 2):
                cc_f_name = seperated[0]
                cc_l_name = seperated[len(seperated) - 1]
            else:
                cc_f_name = 'name_parse_fail'
                cc_l_name = 'name_parse_fail'

        if (pmt_type == 'payment_paypal_tr'):

            paypal_email = table.find_element(
                By.CSS_SELECTOR, 'tr:last-of-type > td:nth-child(3)').text

        # return an order object with all of the info we got :)))

        return Order(member_email, shipping_address, billing_address=billing_address, paypal_email=paypal_email, cc_f_name=cc_f_name, cc_l_name=cc_l_name)

       # if anything goes wrong and is uncaught, return false and print a message
    except:
        print(
            f'Uh oh, get_hqm_details function failed for order {id}, order is likely loading too slowly, or unable to locate some details in DOM')
        return False


initialize_webdriver()


list = ['217054771', '225981941', '219487021', '225199831', '225463951', '224319711',
        '224347801',
        '224523151',
        '224574961',
        '224637791',
        '224644051',
        '224657871',
        '224736641',
        '224739111',
        '224780081',
        '224840551',
        '224861401',
        '224875011',
        '224890801',
        '224904691',
        '224950841',
        '224953941',
        '224979861',
        '224982011',
        '224990091',
        '225004121',
        '225010051',
        '225014611',
        '225040541',
        '225041721',
        '225074601',
        '225112821']

for order in list:
    print(get_hqm_details(order))


driver.quit()
