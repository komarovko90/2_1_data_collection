from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
from pprint import pprint
from pymongo import MongoClient
from datetime import datetime


chr_opt = Options()
chr_opt.add_argument('start-maximized')
driver = webdriver.Chrome()

my_login = 'study.ai_172'
my_pass = 'NextPassword172'

driver.get('https://mail.ru/')

login = driver.find_element_by_id('mailbox:login')
login.send_keys(my_login)

btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'mailbox:submit')))
btn.click()

# пауза до открытия поля для ввода пароля
password = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'mailbox:password')))
password.send_keys(my_pass)

btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'mailbox:submit')))
btn.click()
WebDriverWait(driver, 9).until(EC.element_to_be_clickable((By.CLASS_NAME, 'js-letter-list-item')))
letter_id1 = set()
letters_info = []
while True:
    letter_id2 = set()  # для проверки достигли ли конца почты
    finish = True

    letters = driver.find_elements_by_class_name('js-letter-list-item')
    for letter in letters:
        uidl = letter.get_attribute('data-uidl-id')
        letter_id2.add(uidl)
        if uidl not in letter_id1:
            info = {}
            info['from'] = letter.find_element_by_class_name('ll-crpt').get_attribute('title')
            info['theme'] = letter.find_element_by_class_name('ll-sj__normal').text
            info['date'] = letter.find_element_by_class_name('llc__item_date').get_attribute('title')
            info['letter_id'] = uidl

            # открытие письма в новой вкладке для считывания текста
            link = letter.get_attribute('href')
            driver.execute_script(f"window.open('')")
            WebDriverWait(driver, 3).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link)
            # body = driver.find_element_by_class_name('letter-body')
            body = WebDriverWait(driver, 9).until(EC.visibility_of_element_located((By.CLASS_NAME, 'letter-body')))
            info['text'] = body.text
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            letters_info.append(info)
            finish = False
    # проверка флага что считали все письма
    if finish:
        break
    # перемотка для подгрузки писем
    actions = ActionChains(driver)
    actions.move_to_element(letters[-1])
    actions.perform()
    letter_id1 = letter_id2
    time.sleep(0.3)

driver.quit()

client = MongoClient('localhost', 27017)
db = client['hh_db']
db_mail = db.mail
# db_news.delete_many({})

for pos in letters_info:
    letter_id = pos['letter_id']
    pos['update_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
    db_mail.update_one({'letter_id': letter_id}, {'$set': pos}, upsert=True)

for pos in db_mail.find({}):
    pprint(pos)
