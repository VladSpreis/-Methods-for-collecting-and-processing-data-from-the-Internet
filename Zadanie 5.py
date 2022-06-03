from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from ordered_set import OrderedSet
from pymongo import MongoClient, database
from pymongo.errors import DuplicateKeyError
import time

s = Service("./chromedriver.exe")
options = Options()
options.add_argument('start-maximized')



driver = webdriver.Chrome(service=s, options=options)
driver.implicitly_wait(10)
driver.get("https://account.mail.ru/login?page=https%3A%2F%2Fe.mail.ru%2Fmessages%2Finbox%3Futm_source%3Dportal"
           "%26utm_medium%3Dmailbox%26utm_campaign%3De.mail.ru%26mt_click_id%3Dmt-veoz41-1654094553-3140402770"
           "&allow_external=1")

def switch(def_driver):
    global driver
    input = def_driver.find_element(By.NAME, "username")
    input.send_keys("study.ai_172@mail.ru")

    button = def_driver.find_element(By.XPATH, "//button[@data-test-id='next-button']")
    button.click()

    input_1 = def_driver.find_element(By.XPATH, "//input[@name='password']")
    input_1.send_keys("NextPassword172#")

    button_1 = def_driver.find_element(By.XPATH, "//button[@data-test-id='submit-button']")
    button_1.click()

xpath = "//div[@class='ReactVirtualized__Grid__innerScrollContainer']/a"
xpath_href = "//div[@class='ReactVirtualized__Grid__innerScrollContainer']"

switch(driver)

href_container = OrderedSet()

def href_in_container(def_container):
    global href_container
    for element in def_container:
        href_container.add(element.get_attribute("href"))


def scrolling (xpath_el):
    tag_a = driver.find_elements(By.XPATH, xpath_el)
    action = ActionChains(driver)
    action.move_to_element(tag_a[-1])
    action.perform()

check_value = 0

while True:
    try:
        container = driver.find_elements(By.XPATH, xpath)
        href_in_container(container)
        count_container = len(href_container)
        if count_container - check_value == 0:
            driver.close()
            break
        else:
            scrolling(xpath)
            check_value += (count_container - check_value)
    except:
        break
print(href_container)

full_data = []

for link in href_container:
    empty_dict = {}
    driver_1 = webdriver.Chrome(service=s, options=options)
    driver_1.implicitly_wait(10)
    driver_1.get(link)
    input = driver_1.find_element(By.NAME, "username")
    input.send_keys("study.ai_172@mail.ru")
    button = driver_1.find_element(By.XPATH, "//button[@data-test-id='next-button']")
    button.click()
    input_1 = driver_1.find_element(By.XPATH, "//input[@name='password']")
    input_1.send_keys("NextPassword172#")
    driver_1.implicitly_wait(10)
    button_1 = driver_1.find_element(By.XPATH, "//button[@data-test-id='submit-button']")
    button_1.click()
    date = driver_1.find_element(By.CLASS_NAME, "b-letter__head__date").text
    from_whom = driver_1.find_element(By.XPATH, "//div[@data-mnemo='from']/span[contains(@class,'b-contact-informer-target')]/span").text
    letter_theme = driver_1.find_element(By.CLASS_NAME, "b-letter__head__subj__text").text
    content_of_the_letter = driver_1.find_element(By.CLASS_NAME, "b-letter__body").text
    driver_1.implicitly_wait(10)
    empty_dict['letter_theme'] = letter_theme
    empty_dict['from whom'] = from_whom
    empty_dict['content'] = content_of_the_letter
    empty_dict['date'] = date
    full_data.append(empty_dict)
    driver_1.close()
    driver_1 = None



def mongo(data):
    if type(data) == list:
        return data
    else:
        return list(data)


def add_to_database(databases):
    client = MongoClient('127.0.0.1', 27017)
    db = client['home_work_database_train']
    actual_vacancy = db.actual_vacancy
    mongo_data = mongo(databases)
    for vac in range(len(mongo_data)):
        try:
            actual_vacancy.insert_one(mongo_data[vac])

        except DuplicateKeyError:
            print('please use another id')
            continue
    return actual_vacancy


view_data = add_to_database(full_data)
for i in view_data.find({}):
    print(i)