# import OS to access system files
import os

# import the classes defined in the classes file
from scripts.classes import *

# import function to update sheet with script status
from scripts.google_sheets import update_status

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

# import regular expressions module
import re

# import dotenv module to use env variables
from dotenv import load_dotenv
load_dotenv()

# set driver options
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-notifications')

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
        print('Ekata login failed, may be failing captcha test (try logging in manually in chrome before trying again), script quitting')
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
def get_ekata_info(order, zendesk):

    try:
        # switch to correct window/tab and use the HTML base of the application as element to navigate
        driver.switch_to.window(ekata_window)
        app = driver.find_element(
            By.CLASS_NAME, 'css-1fe9b2j-ApplicationContainer')

        # run check on member email (should always be present)
        member_email_check = perform_email_check(order.member_email, app)
        paypal_email_check = None

        # if there is a paypal email, check it as well
        if order.paypal_email and not order.mb_equals_pp():
            paypal_email_check = perform_email_check(order.paypal_email, app)

        if order.paypal_email and order.mb_equals_pp():
            paypal_email_check = "MB = PP"

        if not paypal_email_check:
            paypal_email_check = ""

        sa_f_name = order.shipping_address.first_name
        sa_l_name = order.shipping_address.last_name
        cc_f_name = order.cc_f_name
        cc_l_name = order.cc_l_name
        ba_f_name = None
        ba_l_name = None

        if order.billing_address and (order.billing_address != 'error') and not order.sa_equals_ba():
            ba_f_name = order.billing_address.first_name
            ba_l_name = order.billing_address.last_name

        # perform check of shipping address

        sa_check = perform_address_check(
            order.shipping_address, app, sa_f_name, sa_l_name, ba_f_name, ba_l_name, cc_f_name, cc_l_name)

        sa_multi_unit = sa_check[1]
        sa_street_view = sa_check[2]
        shipping_check = sa_check[0]

        ba_multi_unit = ""
        ba_street_view = ""
        billing_check = "SA = BA"

        if order.billing_address and (order.billing_address != 'error') and not order.sa_equals_ba():
            ba_check = perform_address_check(
                order.billing_address, app, sa_f_name, sa_l_name, ba_f_name, ba_l_name, cc_f_name, cc_l_name)

            ba_multi_unit = ba_check[1]
            ba_street_view = ba_check[2]
            billing_check = ba_check[0]

        if order.billing_address == 'error':
            billing_check = 'Error - Review Manually'

        zillow_query_sa = "🔎"
        zillow_ss_sa = "🔎"
        zillow_query_ba = ''
        zillow_ss_ba = ''

        # if the SA is us or canada, generate a zillow link

        if order.shipping_address.country == 'United States' or order.shipping_address.country == 'Canada':

            zillow_query_sa = make_zillow_link(
                order.shipping_address.address, order.shipping_address.postal_code)
            zillow_ss_sa = f'=HYPERLINK("{zillow_query_sa}", "💸")'

        # if theres a seperate BA, generate a zillow link if the BA is in US or Canada

        if order.billing_address and (order.billing_address != 'error') and not order.sa_equals_ba():

            if order.billing_address.country == 'United States' or order.billing_address.country == 'Canada':

                zillow_query_ba = make_zillow_link(
                    order.billing_address.address, order.billing_address.postal_code)
                zillow_ss_ba = f'=HYPERLINK("{zillow_query_ba}", "💸")'

            else:
                zillow_query_ba = '🔎'
                zillow_ss_ba = '🔎'

        if zendesk:

            return [member_email_check, paypal_email_check, shipping_check, sa_street_view, sa_multi_unit, zillow_query_sa, billing_check, ba_street_view, ba_multi_unit, zillow_query_ba]

        else:

            return [member_email_check, paypal_email_check, shipping_check, sa_street_view, sa_multi_unit, zillow_ss_sa, billing_check, ba_street_view, ba_multi_unit, zillow_ss_ba]

    except Exception as e:
        print(e)
        return False

# helper function to make a zillow search link from address line and postal code (put address and postal code together with hyphens, try to remove special characters, and add it to the url)


def make_zillow_link(address, postal_code):
    zillow_base_link = 'https://www.zillow.com/homes/'
    zillow_search_raw = address + ' ' + postal_code
    zillow_search_raw = re.sub(r"[,.#]", "", zillow_search_raw).strip()
    zillow_search_term = zillow_search_raw.split(" ")
    zillow_search_term = "-".join(zillow_search_term)
    return zillow_base_link + zillow_search_term


# function to perform Ekata email check, for a given email and HTML section
def perform_email_check(email, dom_section):

    driver.implicitly_wait(8)
    dom_section.find_element(By.XPATH, "//a[text()='Email']").click()

    try:

        form = dom_section.find_element(By.TAG_NAME, 'form')
        email_input = form.find_element(By.ID, 'email')
        email_input.send_keys(Keys.COMMAND, 'a')
        email_input.send_keys(Keys.DELETE)
        email_input.send_keys(email)
        form.find_element(
            By.CLASS_NAME, 'css-uw1vjm-StyledButton-primary').click()

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
            driver.implicitly_wait(8)
        except NoSuchElementException:
            driver.implicitly_wait(8)

        creation = dom_section.find_element(By.XPATH, '//div[4]/div[2]').text
        domain_reputation = dom_section.find_element(
            By.XPATH, '//div[3]/div[4]/div[2]').text

        return f'{email_validity}, {online_presence}, {creation}, {domain_reputation}'

    except NoSuchElementException:
        return 'Error - Please review manually'

# function to check one address for multiunit, streetview link, and name matches


def perform_address_check(address, dom_section, sa_f_name=None, sa_l_name=None, ba_f_name=None, ba_l_name=None, cc_f_name=None, cc_l_name=None):

    driver.implicitly_wait(2.6)
    # navigate to the address page
    dom_section.find_element(By.XPATH, "//a[text()='Address']").click()

    # find the form and enter the information
    form = dom_section.find_element(By.TAG_NAME, 'form')
    form.find_element(By.CSS_SELECTOR, 'button[type="reset"]').click()
    form.find_element(By.ID, 'street').send_keys(address.address)
    form.find_element(By.ID, 'where').send_keys(address.postal_code)
    form.find_element(By.ID, 'countryCode').send_keys(address.country)
    form.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    # initialize variables to be returned
    street_view = ''
    sa_name_check = None
    ba_name_check = None
    cc_name_check = None
    multi_unit = ''

    # try to get street view and multi unit information first
    try:
        street_view = driver.find_element(
            By.PARTIAL_LINK_TEXT, 'Street view').get_attribute('href')
        street_view = f'=HYPERLINK("{street_view}", "📍")'

    except:
        street_view = "🔎"

    try:
        driver.implicitly_wait(0)
        multi_unit = driver.find_element(
            By.CSS_SELECTOR, '.e81606331 .e81606327 > .e81606326:last-of-type > span:last-of-type').text

        if multi_unit == "Multi-unit":
            multi_unit = '🏬'

        elif multi_unit == "Single-unit":
            multi_unit = '🏠'

        else:
            multi_unit = "🔎"

    except:
        multi_unit = "🔎"

    # return an error if error message appears
    try:
        driver.implicitly_wait(0.5)
        error = form.find_element(
            By.CLASS_NAME, 'css-1cxasnz-StyledErrorMessage').text

        if error:
            return [error, multi_unit, street_view]

     # if no error message, proceed with getting streetview url, multi unit information, and match information
    except:

        result = None

        # try to get the container element of the results section, else return an error

        try:

            result = dom_section.find_element(By.CLASS_NAME, 'e81606332')

        except:

            return ['Error - Review Manually', multi_unit, street_view]

        # get results section as a variable
        matches = dom_section.find_element(
            By.CSS_SELECTOR, '.e81606331:nth-of-type(2)')

        # just in case anything has not completely loaded
        driver.implicitly_wait(2.4)

        # in this try block, we try to get a list of all the names matched by ekata for the address,
        # if these elements dont exist we say there is no subscriber info
        try:
            matches.find_element(
                By.CSS_SELECTOR, '.css-1o61uci-PanelTitleContainer')
            names = []
            driver.implicitly_wait(0.5)

            # see if there are any alternate names listed and save them to list of names
            try:
                alt_names = matches.find_elements(
                    By.CSS_SELECTOR, '.css-unmwr4-AlternateNames')
                for name in alt_names:
                    try:
                        raw_names = name.text
                        raw_names = raw_names.split(", ")
                        for raw_name in raw_names:
                            names.append(raw_name)
                    except:
                        continue
            except:
                'nothing'

            # check all the matches and save them to list of names
            try:
                match_names = matches.find_elements(
                    By.CSS_SELECTOR, '.e81606329')

                for name in match_names:
                    try:
                        raw_name = name.text
                        names.append(raw_name)
                    except:
                        continue
            except:
                'nothing'

            try:
                associated_names = matches.find_elements(
                    By.CSS_SELECTOR, 'li')

                for name in associated_names:
                    try:
                        raw_name = name.text
                        names.append(raw_name)
                    except:
                        continue

            except Exception as e:
                print(e)

            # for all the names gathered, check them against the shipping address name, credit card name, and billing address names to find matches.
            # matching on last name only is considered partial, and both first and last name is a full match.
            # matching on first name only is not considered a match
            sa_done = False
            ba_done = False
            cc_done = False

            for name in names:

                if not sa_done:
                    result = search_match(sa_f_name, sa_l_name, name)
                    if result:
                        sa_name_check = f'SA Name: {result}'
                        if result == 'F':
                            sa_done = True

                if ba_l_name and not ba_done:
                    result = search_match(ba_f_name, ba_l_name, name)
                    if result:
                        ba_name_check = f'BA Name: {result}'
                        if result == 'F':
                            ba_done = True

                if cc_l_name and (cc_l_name != 'name_parse_fail') and not cc_done:
                    result = search_match(cc_f_name, cc_l_name, name)
                    if result:
                        cc_name_check = f'CC Name: {result}'
                        if result == 'F':
                            cc_done = True

            # if a billing address name was not provided it is N/A
            if not ba_l_name:
                ba_name_check = 'BA Name: X'

             # if a credit card name was not provided it is N/A
            if not cc_l_name:
                cc_name_check = 'CC Name: X'

            # if the credit card name is 'name_parse_fail' this means that there is a credit card name, but it was not parsed successfully.
            # will need to review manually
            if (cc_l_name == 'name_parse_fail'):
                cc_name_check = 'CC Name: M'

            # finally, if any of these still do not have a value, it means there was no match and no exceptions/exclusions apply
            if not ba_name_check:
                ba_name_check = 'BA Name: N'

            if not cc_name_check:
                cc_name_check = 'CC Name: N'

            if not sa_name_check:
                sa_name_check = 'SA Name: N'

            # return all da info

            return [f'{sa_name_check} | {cc_name_check} | {ba_name_check}', multi_unit, street_view]

        # if there were no results at all, return the below
        except:

            return ["No Subscriber Info", multi_unit, street_view]


# function that uses regular expressions to match names from HQM to names from ekata
def search_match(first_name, last_name, string_to_search):
    last_name_match = re.search(
        f'(\ |\-){last_name}($|\ |,|\-)', string_to_search, re.I)
    full_name_match = re.search(
        f'(^|\ ){first_name}\ {last_name}($|\ |,|\-)', string_to_search, re.I)
    if not full_name_match:
        full_name_match = re.search(
            f'(^|\ ){first_name}(\ |\-|,).*(\ |\-){last_name}($|\ |,|\-)', string_to_search, re.I)

    if full_name_match:
        return 'F'
    elif last_name_match:
        return 'P'
    else:
        return None


# function to remove honorifics etc. from names, takes in name and boolean of whether it is a full name (first and last), or one name
def format_name(name, last_name=True):
    name = name.replace('Mr. ', '')
    name = name.replace('M. ', '')
    name = name.replace('Mrs. ', '')
    name = name.replace('Rev. ', '')
    name = name.replace('Ms. ', '')
    name = name.replace('Dr. ', '')
    name = name.replace(' Jr.', '')
    name = name.replace(' II', '')
    name = name.replace(' I', '')
    name = name.replace(' III', '')
    name = name.replace(' Sr.', '')

    name = name.strip()
    name = re.split('\-|\ ', name)
    if last_name:
        name = name[len(name) - 1]
    else:
        name = name[0]

    return name.strip().lower()


# function which takes in an order id, and retrieves the order details for a provided order
def get_hqm_details(id):

    try:

        # switch to already opened HQM tab and navigate to the URL
        driver.switch_to.window(hqm_window)
        driver.get(
            f'https://hqm.ssense.com/customer-support/master-order/edit/{id}')
        driver.implicitly_wait(25)

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

            driver.implicitly_wait(0.2)
            shipping_address = get_hqm_address(shipping_field, 'c292')
            driver.implicitly_wait(15)

        except NoSuchElementException:

            driver.implicitly_wait(15)
            shipping_address = get_hqm_address(shipping_field, 'c293')

        # if billing not same as shipping, get the billing address details
        if not (driver.find_element(By.ID, 'sameAsShipping').is_selected()):

            # find this to make sure its loaded first
            driver.find_element(By.ID, 'shipping-address-book-btn')

            billing_field = driver.find_element(
                By.CSS_SELECTOR, '.billing.box-address')

            # try to get billing details, billing fields can have c291 or c292 classes so check both
            driver.implicitly_wait(0.2)

            try:

                billing_address = get_hqm_address(billing_field, 'c293')
                driver.implicitly_wait(15)

            except NoSuchElementException:

                driver.implicitly_wait(15)
                billing_address = get_hqm_address(billing_field, 'c292')

        # determine if it is a paypal, applepay, or cc order and get the appropriate info from the payments table
        table = driver.find_element(
            By.CSS_SELECTOR, 'table[style="display: table;"]')
        pmt_type = table.get_attribute('id')

        if (pmt_type == 'table_payment_cc'):

            cc_full_name = table.find_element(
                By.CSS_SELECTOR, 'tr:nth-of-type(2) > td:nth-child(5)').text

            seperated = cc_full_name.split(' ')
            if (len(seperated) >= 2):

                cc_f_name = seperated[0]
                cc_l_name = seperated[len(seperated) - 1]
                cc_f_name = format_name(cc_f_name, False)
                cc_l_name = format_name(cc_l_name, True)
            else:
                cc_f_name = 'name_parse_fail'
                cc_l_name = 'name_parse_fail'

        if (pmt_type == 'payment_paypal_tr'):

            paypal_email = table.find_element(
                By.CSS_SELECTOR, 'tr:last-of-type > td:nth-child(3)').text

        # return an order object with all of the info we got :)))
        return Order(member_email, shipping_address, billing_address=billing_address, paypal_email=paypal_email, cc_f_name=cc_f_name, cc_l_name=cc_l_name)

       # if anything goes wrong and is uncaught, return false and print a message
    except Exception as e:
        print("getting order " + id +
              " details fail, will try up to three times and output a blank row if not done")
        return False


def get_hqm_address(field, css_id):

    first_name_html = field.find_element(
        By.ID, f'{css_id}_firstName')
    first_name = first_name_html.get_attribute('value')
    first_name = format_name(first_name, last_name=False)
    last_name = field.find_element(
        By.ID, f'{css_id}_lastName').get_attribute('value')
    last_name = format_name(last_name, last_name=True)
    address = field.find_element(
        By.ID, f'{css_id}_address').get_attribute('value')
    postal_code = field.find_element(
        By.ID, f'{css_id}_postalCode').get_attribute('value')
    country_select = Select(field.find_element(
        By.ID, f'{css_id}_countryID')).first_selected_option
    country = country_select.text

    return Address(
        address, country, postal_code, first_name, last_name)


def quit_webdriver():
    driver.quit()
