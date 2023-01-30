import os

#import the classes defined in the classes file
from classes import *

#for debugging (printing complete objects to console)
from pprint import pprint

#selenium modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

#import dotenv module to use env variables
from dotenv import load_dotenv

load_dotenv()

#test data
shipping_address = Address('157 power line ct', 'Hamilton', 'Ontario', 'L9B1N6', 'Jeremy', 'Buist')
billing_address1 = Address('157 power line ct', 'Hamilton', 'Ontario', 'L9B1N6', 'Jeremy', 'Buist')
billing_address2 = Address('3511 Rue Ethel', 'Verdun', 'Quebec', 'H4G1R9', 'Jeremy', 'Buist')

sa_equals_ba = Order('jbuistjbuist@gmail.com', shipping_address, billing_address1)
sa_not_ba = Order('jbuistjbuist@gmail.com', shipping_address, billing_address2)
paypal_order = Order('jbuistjbuist@gmail.com', shipping_address, None, 'jeremy.j.buist@gmail.com', True)


chrome_options = Options()
chrome_options.add_argument('--start-maximized')

# add this to driver initialization later to have headless chrome
#chrome_options.add_argument('--headless')

chrome_drive = Service()
driver = webdriver.Chrome(service=chrome_drive, options=chrome_options)
driver.implicitly_wait(50)
ekata_password = os.getenv("ekata_password")
email = os.getenv("agent_email")


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


def get_ekata_info(order):
  driver.switch_to.window(driver.window_handles[0])
  app = driver.find_element(By.CLASS_NAME, 'css-1fe9b2j-ApplicationContainer')
  app.find_element(By.XPATH, "//a[text()='Email']").click()
  app.find_element(By.NAME, 'email').send_keys(order.member_email)
  app.find_element(By.CLASS_NAME, 'css-uw1vjm-StyledButton-primary').click()


  email_validity = driver.find_element(By.XPATH, '//div[2]/div[2]/div[2]').text
  online_presence = driver.find_element(By.XPATH, '//div[3]/div[2]').text
  creation = driver.find_element(By.XPATH, '//div[4]/div[2]').text
  domain_reputation = driver.find_element(By.XPATH, '//div[3]/div[4]/div[2]').text

  print(email_validity, online_presence, creation, domain_reputation)



initialize_webdriver()

get_ekata_info(sa_equals_ba)
