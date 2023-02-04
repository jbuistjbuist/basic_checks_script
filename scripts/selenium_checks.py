# import OS to access system files
import os

# import the classes defined in the classes file
from classes import *

# import function to update sheet with script status
from google_sheets import update_status

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

# set driver options
chrome_options = Options()
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-notifications')

# disable image loading to increase speed
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

# initialize chrome driver and env variables
chrome_drive = Service()
driver = webdriver.Chrome(service=chrome_drive, options=chrome_options)
driver.implicitly_wait(30)

# fetch env variables
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
        update_status('Failed')
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
        update_status('Failed')
        quit()


# function to get info from Ekata, based on provided order details
def get_ekata_info(order):

    try:
        # switch to correct window/tab and use the HTML base of the application as element to navigate
        driver.switch_to.window(ekata_window)
        app = driver.find_element(
            By.CLASS_NAME, 'css-1fe9b2j-ApplicationContainer')

        # run check on member email (should always be present)
        member_email_check = perform_email_check(order.member_email, app)
        paypal_email_check = None

        # if there is a paypal email, check it as well
        if order.paypal_email:
            paypal_email_check = 'PayPal ' + \
                perform_email_check(order.paypal_email, app)
            member_email_check = 'Member ' + member_email_check

        if not paypal_email_check:
            paypal_email_check = 'N/A'

        sa_f_name = order.shipping_address.first_name
        sa_l_name = order.shipping_address.last_name
        cc_f_name = order.cc_f_name
        cc_l_name = order.cc_l_name
        ba_f_name = None
        ba_l_name = None

        if order.billing_address:
            ba_f_name = order.billing_address.first_name
            ba_l_name = order.billing_address.last_name

        # perform check of shipping address

        sa_check = perform_address_check(
            order.shipping_address, app, sa_f_name, sa_l_name, ba_f_name, ba_l_name, cc_f_name, cc_l_name)

        multi_unit = sa_check[1]
        shipping_check = sa_check[0]

        billing_check = 'N/A'

        if order.billing_address and not order.sa_equals_ba():
            billing_check = perform_address_check(
                order.billing_address, app, sa_f_name, sa_l_name, ba_f_name, ba_l_name, cc_f_name, cc_l_name)[0]

        return [member_email_check, paypal_email_check, shipping_check, multi_unit, billing_check]

    except Exception as e:
        print(e)
        return False


# function to perform Ekata email check, for a given email and HTML section
def perform_email_check(email, dom_section):

    driver.implicitly_wait(5)
    dom_section.find_element(By.XPATH, "//a[text()='Email']").click()

    form = dom_section.find_element(By.TAG_NAME, 'form')
    email_input = form.find_element(By.ID, 'email')
    email_input.send_keys(Keys.COMMAND, 'a')
    email_input.send_keys(Keys.DELETE)
    email_input.send_keys(email)
    form.find_element(
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

        return f'Validity: {email_validity}, Online Presence: {online_presence}, Creation: {creation}, Domain: {domain_reputation}'

    except NoSuchElementException:
        return 'Err/Manual'

# function to check one address for multiunit, streetview link, and name matches


def perform_address_check(address, dom_section, sa_f_name=None, sa_l_name=None, ba_f_name=None, ba_l_name=None, cc_f_name=None, cc_l_name=None):

    driver.implicitly_wait(1)
    # navigate to the address page
    dom_section.find_element(
        By.CSS_SELECTOR, '.css-17zawny-MenuItem:nth-child(4) > a').click()

    # find the form and enter the information
    form = dom_section.find_element(By.TAG_NAME, 'form')
    form.find_element(By.CSS_SELECTOR, 'button[type="reset"]').click()
    form.find_element(By.ID, 'street').send_keys(address.address)
    form.find_element(By.ID, 'where').send_keys(address.postal_code)
    form.find_element(By.ID, 'countryCode').send_keys(address.country)
    form.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    # initialize variables to be returned
    street_view = None
    sa_name_check = None
    ba_name_check = None
    cc_name_check = None
    multi_unit = 'Err/Manual'

    # return an error if error message appears
    try:
        error = form.find_element(By.CLASS_NAME, 'e1u7f1f03').text
        if error:
            return [f'Error: {error}', multi_unit]

     # if no error message, proceed with getting streetview url, multi unit information, and match information
    except:

        result = dom_section.find_element(By.CLASS_NAME, 'e81606332')

        # try to get street view info, if failed skip it
        try:
            street_view = result.find_element(
                By.PARTIAL_LINK_TEXT, 'Street').get_attribute('href')
        except:
            street_view = street_view

        # page should be loaded by now, so change the wait time to increase speed of execution
        driver.implicitly_wait(0)

        # see if the page confirms whether the SA is multi-unit
        try:
            multi_unit = result.find_element(
                By.CSS_SELECTOR, '.e81606327 > .e81606326:last-of-type > span:last-of-type').text
        except:
            multi_unit = multi_unit

        # get results section as a variable
        matches = dom_section.find_element(
            By.CSS_SELECTOR, '.e81606331:nth-of-type(2)')

        # just in case anything has not completely loaded
        driver.implicitly_wait(1)

        # in this try block, we try to get a list of all the names matched by ekata for the address,
        # if these elements dont exist we say there is no subscriber info
        try:
            matches.find_element(By.TAG_NAME, 'a')
            names = []
            driver.implicitly_wait(0)

            # see if there are any alternate names listed and save them to list of names
            try:
                alt_names = matches.find_elements(
                    By.CSS_SELECTOR, '.css-unmwr4-AlternateNames')
                for name in alt_names:
                    try:
                        raw_name = name.text
                        formatted_name = format_name(raw_name, full_name=True)
                        names.append(formatted_name)
                    except:
                        continue
            except:
                'nothing'

            # check all the matches and save them to list of names
            try:
                match_names = matches.find_elements(
                    By.CSS_SELECTOR, 'a[href^="/entity?id=Person"]')

                for name in match_names:
                    try:
                        raw_name = name.text
                        formatted_name = format_name(raw_name, full_name=True)
                        names.append(formatted_name)
                    except:
                        continue

            except:
                'nothing'

            # for all the names gathered, check them against the shipping address name, credit card name, and billing address names to find matches.
            # matching on last name only is considered partial, and both first and last name is a full match.
            # matching on first name only is not considered a match
            for name in names:
                if (name[1] == sa_l_name):
                    sa_name_check = 'Shipping Name: Partial Match'
                    if (name[0] == sa_f_name):
                        sa_name_check = 'Shipping Name: Full Match'

                if ba_l_name:
                    if (name[1] == ba_l_name):
                        ba_name_check = 'Billing Name: Partial Match'
                        if (name[0] == ba_f_name):
                            ba_name_check = 'Billing Name: Full Match'

                if cc_l_name and (cc_l_name != 'name_parse_fail'):
                    if (name[1] == cc_l_name):
                        ba_name_check = 'Credit Card Name: Partial Match'
                        if (name[0] == cc_f_name):
                            cc_name_check = 'Credit Card Name: Full Match'

            # if a billing address name was not provided it is N/A
            if not ba_l_name:
                ba_name_check = 'Billing Name: N/A'

             # if a credit card name was not provided it is N/A
            if not cc_l_name:
                cc_name_check = 'Credit Card Name: N/A'

            # if the credit card name is 'name_parse_fail' this means that there is a credit card name, but it was not parsed successfully.
            # will need to review manually
            if (cc_l_name == 'name_parse_fail'):
                cc_name_check = 'Credit Card Name: Review Manually'

            # finally, if any of these still do not have a value, it means there was no match and no exceptions/exclusions apply
            if not ba_name_check:
                ba_name_check = 'Billing Name: No Match'

            if not cc_name_check:
                cc_name_check = 'Credit Card Name: No Match'

            if not sa_name_check:
                sa_name_check = 'Shipping Address Name: No Match'

            # if a streetview link was successfully retrieved, format the output so it will produce linked text in google sheets
            # otherwise, return the text without a link
            if not street_view:
                return [f'{sa_name_check}, {cc_name_check}, {ba_name_check}', multi_unit]
            else:
                return [f'=HYPERLINK("{street_view}", "{sa_name_check}, {cc_name_check}, {ba_name_check}")', multi_unit]

        # if there were no results at all, return the below
        except:
            return ['No Subscriber Info', multi_unit]


# function to remove honorifics etc. from names, takes in name and boolean of whether it is a full name (first and last), or one name
def format_name(name, full_name):
    name = name.replace('Mr. ', '')
    name = name.replace('M. ', '')
    name = name.replace('Mrs. ', '')
    name = name.replace('Ms. ', '')
    name = name.replace('Dr. ', '')
    name = name.replace(' Jr.', '')
    name = name.replace(' II', '')

    # if it is a full name, return a list with two elements. list[0] is the first name, list[1] is the last name.
    # middle names / initials are not returned
    if (full_name):
        name = name.split(' ')
        return [name[0].strip().lower(), name[len(name) - 1].strip().lower()]
    else:
        return name.strip().lower()


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
            first_name = format_name(first_name, full_name=False)
            last_name = shipping_field.find_element(
                By.ID, 'c292_lastName').get_attribute('value')
            last_name = format_name(last_name, full_name=False)
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
            first_name = format_name(first_name, full_name=False)
            last_name = shipping_field.find_element(
                By.ID, 'c293_lastName').get_attribute('value')
            last_name = format_name(last_name, full_name=False)
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
            first_name = format_name(first_name, full_name=False)
            last_name = billing_field.find_element(
                By.ID, 'c291_lastName').get_attribute('value')
            last_name = format_name(last_name, full_name=False)
            address = billing_field.find_element(
                By.ID, 'c291_address').get_attribute('value')
            postal_code = billing_field.find_element(
                By.ID, 'c291_postalCode').get_attribute('value')
            country_select = Select(billing_field.find_element(
                By.ID, 'c291_countryID')).first_selected_option
            country = country_select.text

            billing_address = Address(
                address, country, postal_code, first_name, last_name)

        # determine if it is a paypal, applepay, or cc order and get the appropriate info from the payments table
        table = driver.find_element(
            By.CSS_SELECTOR, 'table[style="display: table;"]')
        pmt_type = table.get_attribute('id')

        if (pmt_type == 'table_payment_cc'):

            cc_full_name = table.find_element(
                By.CSS_SELECTOR, 'tr:nth-child(2) > td:nth-child(5)').text
            seperated = cc_full_name.split(' ')
            if (len(seperated) >= 2):
                cc_name = format_name(cc_full_name, full_name=True)
                cc_f_name = cc_name[0]
                cc_l_name = cc_name[1]
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
            f'get_hqm_details function failed for order {id}, order is likely loading too slowly, or unable to locate some details in DOM')
        return False


def quit_webdriver():
    driver.quit()
