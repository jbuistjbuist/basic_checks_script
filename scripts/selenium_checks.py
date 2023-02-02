import os

# import the classes defined in the classes file
from classes import *

# for debugging (printing complete objects to console)
from pprint import pprint

# selenium modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

# import dotenv module to use env variables
from dotenv import load_dotenv

load_dotenv()

# test data
shipping_address = Address(
    '157 power line ct', 'Hamilton', 'Ontario', 'L9B1N6', 'Jeremy', 'Buist')
billing_address1 = Address(
    '157 power line ct', 'Hamilton', 'Ontario', 'L9B1N6', 'Jeremy', 'Buist')
billing_address2 = Address('3511 Rue Ethel', 'Verdun',
                           'Quebec', 'H4G1R9', 'Jeremy', 'Buist')

sa_equals_ba = Order('jjbuist@gmail.com',
                     shipping_address, billing_address1)
sa_not_ba = Order('jbuistjbuist@gmail.com', shipping_address, billing_address2)
paypal_order = Order('jbuistjbuist@gmail.com', shipping_address,
                     None, 'jeremy.j.buist@gmail.com', True)


chrome_options = Options()
chrome_options.add_argument('--start-maximized')

# add this to driver initialization later to have headless chrome
#chrome_options.add_argument('--headless')

chrome_drive = Service()
driver = webdriver.Chrome(service=chrome_drive, options=chrome_options)
driver.implicitly_wait(30)
ekata_password = os.getenv("ekata_password")
hqm_password = os.getenv("hqm_password")
email = os.getenv("agent_email")
hqm_username = os.getenv("hqm_username")


def initialize_webdriver():
  driver.get('https://app.ekata.com/sign_in')

  form = driver.find_element(By.CLASS_NAME, 'simple_form')
  form.find_element(By.ID, 'profile_password').send_keys(ekata_password)
  form.find_element(By.ID, 'profile_email').send_keys(email)
  form.find_element(By.CLASS_NAME, 'btn-primary').click()

  global ekata_window
  ekata_window = driver.current_window_handle

  time.sleep(5)

  if driver.current_url == 'https://app.ekata.com/search':
    print('Ekata login OK')
  else:
    print('Ekata login failed, may be failing captcha test, script quitting')
    quit()
  
  driver.switch_to.new_window('tab')
  global hqm_window
  hqm_window = driver.current_window_handle

  driver.get('https://hqm.ssense.com/core/auth/login')

  form = driver.find_element(By.ID, 'formAuthentication')
  form.find_element(By.ID, 'username').send_keys(hqm_username)
  form.find_element(By.ID, 'password').send_keys(hqm_password)
  form.find_element(By.ID, 'connexion_btn').click()

  time.sleep(3)

  if driver.current_url == 'https://hqm.ssense.com/core/':
    print('HQM login OK')
  else: 
    print('HQM login failed, script quitting')
    quit()


def get_ekata_info(order):
  driver.switch_to.window(ekata_window)
  app = driver.find_element(By.CLASS_NAME, 'css-1fe9b2j-ApplicationContainer')

  member_email_check = perform_email_checks(order.member_email, app)

  if (order.paypal_email):
    paypal_email_check = 'PayPal ' + perform_email_checks(order.paypal_email, app)
    member_email_check = 'Member ' + member_email_check

  else:
    paypal_email_check = None


  print(member_email_check, paypal_email_check)


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
    email_validity = dom_section.find_element(By.XPATH, '//div[2]/div[2]/div[2]').text
    online_presence_html = dom_section.find_element(By.XPATH, '//div[2]/div[3]')
    online_presence = online_presence_html.find_element(By.CLASS_NAME, 'e8160634').text

    try:
      driver.implicitly_wait(0)
      time_ago = online_presence_html.find_element(By.CLASS_NAME, 'e8160633').text
      online_presence = online_presence + f' ({time_ago})'
      driver.implicitly_wait(5)
    except NoSuchElementException:
      driver.implicitly_wait(5)
    
    creation = dom_section.find_element(By.XPATH, '//div[4]/div[2]').text
    domain_reputation = dom_section.find_element(By.XPATH, '//div[3]/div[4]/div[2]').text

    return f'Email - Validity: {email_validity}, Online Presence: {online_presence}, Creation: {creation}, Domain: {domain_reputation}'

  except NoSuchElementException:
    return 'Email - check Failed, please review manually'



def get_hqm_details(id):
  driver.switch_to.window(hqm_window)
  driver.get(f'https://hqm.ssense.com/customer-support/master-order/edit/{id}')

  print(driver.find_element(By.ID, 'c292_firstName').text)
  return


initialize_webdriver()

get_hqm_details('188087741')

get_ekata_info(sa_equals_ba)
get_ekata_info(sa_not_ba)
get_ekata_info(paypal_order)

