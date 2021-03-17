# -*- coding: utf-8 -*-
from datetime import date

from selenium import webdriver
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait


class Scrapers:

    def __init__(self, dir_path, config):
        self.dir_path = dir_path
        self.config = config
        self.driver = None

    def chrome_driver(self, module):
        download_path = os.getcwd() + os.sep + self.dir_path + os.sep + module
        """ Helper function that creates a new Selenium browser """
        chrome_options = webdriver.ChromeOptions()
        os.makedirs(download_path, exist_ok=True)
        chrome_options.add_argument("--start-maximized")
        prefs = {"profile.default_content_settings.popups": 0, "download.default_directory": download_path}
        chrome_options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape_data_from_max(self):
        self.chrome_driver("max")

        self.driver.get(self.config['max']['login_url'])

        WebDriverWait(self.driver, 10).until(ec.visibility_of_all_elements_located((By.CLASS_NAME, "login-registered")))

        self.driver.find_element_by_id('PlaceHolderMain_CardHoldersLogin1_txtUserName').send_keys(
            self.config['max']['username'])
        self.driver.find_element_by_id("txtPassword").send_keys(self.config['max']['password'])
        self.driver.find_element_by_id("PlaceHolderMain_CardHoldersLogin1_btnLogin").click()

        after_login_url = self.config['max']['after_login_url']

        cards = ["-1_0_1_"]

        curr_date = str(date.today().year) + "-" + str(date.today().month) + "-01"

        sort_val = "&sort=1a_1a_1a_1a_1a"

        for card in cards:
            self.driver.get(after_login_url + card + curr_date + sort_val)
            WebDriverWait(self.driver, 25).until(ec.visibility_of_all_elements_located((By.CLASS_NAME, "print-excel")))
            self.driver.implicitly_wait(15)
            self.driver.find_element_by_class_name("download-excel").click()
            time.sleep(10)

        self.driver.close()

    def scrape_data_from_isracard(self):
        self.chrome_driver("isracard")

        self.driver.get(self.config['isracard']['login_url'])

        self.driver.find_element_by_id('otpLoginId_ID').send_keys(self.config['isracard']['username'])
        self.driver.find_element_by_name('otpLoginLastDigits_ID').send_keys(self.config['isracard']['last_digits'])
        self.driver.find_element_by_id("otpLoginPwd").send_keys(self.config['isracard']['password'])
        self.driver.find_element_by_id("otpLobbyFormPassword").submit()

        after_login_url = self.config['isracard']['after_login_url']

        time.sleep(5)

        self.driver.get(after_login_url)

        header = WebDriverWait(self.driver, 10). \
            until(ec.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.card-box__hidden-mobile.export-list")))

        all_children_by_css = header[0].find_elements_by_css_selector("*")

        all_children_by_css[1].click()

        time.sleep(10)

        self.driver.close()

    def scrape_data_from_leumi(self):
        self.chrome_driver("leumi")

        self.driver.get(self.config['leumi']['login_url'])

        self.driver.find_element_by_id('uid').send_keys(self.config['leumi']['username'])
        self.driver.find_element_by_id("password").send_keys(self.config['leumi']['password'])
        self.driver.find_element_by_id("enter").click()

        after_login_url = self.config['leumi']['after_login_url']

        self.driver.get(after_login_url)

        select = Select(self.driver.find_element_by_id('ddlTransactionPeriod'))
        select.select_by_value("004")

        WebDriverWait(self.driver, 10).until(ec.visibility_of_all_elements_located((By.ID, "dtFromDate_textBox")))

        start_date = self.config['leumi']['last_time_used']

        end_date = str(date.today().day) + "/" + str(date.today().month) + "/" + str(date.today().year - 2000)

        self.driver.find_element_by_id("dtFromDate_textBox").clear()

        self.driver.find_element_by_id("dtFromDate_textBox").send_keys(start_date)

        self.driver.find_element_by_id("dtToDate_textBox").clear()

        self.driver.find_element_by_id("dtToDate_textBox").send_keys(end_date)

        self.driver.find_element_by_id("btnDisplayDates").click()

        time.sleep(10)

        window_before = self.driver.window_handles[0]

        self.driver.find_element_by_id("BTNSAVE").click()

        window_after = self.driver.window_handles[1]

        self.driver.switch_to.window(window_after)

        time.sleep(10)

        self.driver.find_element_by_css_selector("input[type='radio'][value='radioHashavshevet']").click()

        self.driver.find_element_by_id("ImgContinue").click()

        time.sleep(10)

        self.config['leumi']['last_time_used'] = end_date

        self.driver.switch_to.window(window_before)
