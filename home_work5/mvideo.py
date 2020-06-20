from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from pprint import pprint
import time
from pymongo import MongoClient
from datetime import datetime
import re

chr_opt = Options()
chr_opt.add_argument('start-maximized')
# chr_opt.add_argument('--headless')
driver = webdriver.Chrome(options=chr_opt)

driver.get('https://www.mvideo.ru/')
# подтверждение  текущего региона
btn_city = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-approve-city')))
btn_city.click()


# переключение на выпадающее меню если оно появилось и его закрытие
try:
    WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.ID, 'fl-296421')))
    driver.switch_to.frame(driver.find_element_by_id('fl-296421'))
    btn_close = driver.find_element_by_class_name('close')
    btn_close.click()
    driver.switch_to.default_content()
except:
    pass
# прокрутка для подгрузки хитов
driver.execute_script('window.scrollTo(0, 1600)')
hits = driver.find_elements_by_xpath("//div[@class='gallery-layout sel-hits-block ']")
# нажатие на кнопку next, пока не обновим весь ряд хитов
# выход из цикла осуществляется, когда количество хитов не перестанет изменятся
count = 0
while True:
    # btn_next = WebDriverWait(hits[1], 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'sel-hits-button-next')))
    items = hits[1].find_elements_by_class_name('gallery-list-item')
    # print(len(items))
    new_count = len(items)
    if new_count == count:
        break
    btn_next = hits[1].find_element_by_class_name('sel-hits-button-next')
    actions = ActionChains(driver)
    actions.move_to_element(btn_next)
    actions.click()
    actions.perform()
    time.sleep(1)
    count = new_count

# сохранение необходимых данных
products_hit = []
for item in items:
    pos = item.find_element_by_xpath("./div/div[2]/div[1]/h4/a")
    txt = re.sub(r'&#034;', '', pos.get_attribute('data-product-info'))
    products_hit.append(eval(txt))

# pprint(products_hit)
driver.quit()

# сложить в БД монго
client = MongoClient('localhost', 27017)
db = client['hh_db']
db_mvideo = db.mvideo
# db_news.delete_many({})

for pos in products_hit:
    product_id = pos['productId']
    pos['update_at'] = datetime.now().strftime("%d.%m.%Y %H:%M")
    db_mvideo.update_one({'productId': product_id}, {'$set': pos}, upsert=True)

for pos in db_mvideo.find({}):
    pprint(pos)
