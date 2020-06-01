#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import io
import json
import os
import time
from datetime import date, timedelta
from pathlib import Path

import xlrd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from Parse_Leumi import parse_leumi_data
from Parse_Max import parse_max_data
from post_transactions import convert_csv_line_to_transaction, post_transaction, get_init_data


def get_config_file():
    config = configparser.ConfigParser()

    config.read('../payload_data.ini')

    return config


def create_csv_files(path, file_name):
    labels = ["Date", "Payee", "Outflow", "Memo", "Inflow"]
    csv_output = io.open(os.getcwd() + "\\" + path + "\\out\\" + file_name + ".csv", 'w', encoding="utf-8")
    for label in labels:
        csv_output.write(label + ",")
    csv_output.write("\n\r")
    return csv_output


def make_new_dir():
    last_month = date.today().replace(day=1) - timedelta(days=1)
    dir_path = str(last_month.month) + "." + str(date.today().year)
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    return dir_path


def chrome_driver(download_path):
    """ Helper function that creates a new Selenium browser """
    chrome_options = webdriver.ChromeOptions()
    os.makedirs(download_path, exist_ok=True)
    prefs = {"profile.default_content_settings.popups": 0, "download.default_directory": download_path}
    chrome_options.add_experimental_option('prefs', prefs)
    browser = webdriver.Chrome(options=chrome_options)
    return browser


def scrape_data_from_max(config, dir_path):

    driver = chrome_driver(os.getcwd() + os.sep + dir_path + os.sep + "max")

    driver.get(config['max']['login_url'])

    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "login-registered")))

    driver.find_element_by_id('PlaceHolderMain_CardHoldersLogin1_txtUserName').send_keys(config['max']['username'])
    driver.find_element_by_id("txtPassword").send_keys(config['max']['password'])
    driver.find_element_by_id("PlaceHolderMain_CardHoldersLogin1_btnLogin").click()

    after_login_url = config['max']['after_login_url']

    cards = ["-1_1_1_", "-1_0_1_"]

    curr_date = str(date.today().year) + "-" + str(date.today().month) + "-01"

    sort_val = "&sort=1a_1a_1a_1a_1a"

    for card in cards:
        driver.get(after_login_url + card + curr_date + sort_val)
        WebDriverWait(driver, 25).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "print-excel")))
        driver.implicitly_wait(15)
        driver.find_element_by_class_name("download-excel").click()
        time.sleep(10)

    driver.close()


def scrape_data_from_leumi(config, dir_path):

    driver = chrome_driver(os.getcwd() + os.sep + dir_path + os.sep + "leumi")

    driver.get(config['leumi']['login_url'])

    driver.find_element_by_id('uid').send_keys(config['leumi']['username'])
    driver.find_element_by_id("password").send_keys(config['leumi']['password'])
    driver.find_element_by_id("enter").click()

    after_login_url = config['leumi']['after_login_url']

    driver.get(after_login_url)

    select = Select(driver.find_element_by_id('ddlTransactionPeriod'))
    select.select_by_value("004")

    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.ID, "dtFromDate_textBox")))

    last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)

    start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

    start_date = "01/" + str(start_day_of_prev_month.month) + "/" + str(start_day_of_prev_month.year - 2000)

    end_date = str(last_day_of_prev_month.day) + "/" + str(last_day_of_prev_month.month) + "/" + str(
        last_day_of_prev_month.year - 2000)

    driver.find_element_by_id("dtFromDate_textBox").clear()

    driver.find_element_by_id("dtFromDate_textBox").send_keys(start_date)

    driver.find_element_by_id("dtToDate_textBox").clear()

    driver.find_element_by_id("dtToDate_textBox").send_keys(end_date)

    driver.find_element_by_id("btnDisplayDates").click()

    time.sleep(10)

    window_before = driver.window_handles[0]

    driver.find_element_by_id("BTNSAVE").click()

    window_after = driver.window_handles[1]

    driver.switch_to.window(window_after)

    time.sleep(10)

    driver.find_element_by_css_selector("input[type='radio'][value='radioHashavshevet']").click()

    driver.find_element_by_id("ImgContinue").click()

    time.sleep(10)

    driver.switch_to.window(window_before)


def csv_from_excel(path):

    data = get_init_data()

    for subdir, dirs, files in os.walk(path):
        for file_name in files:
            if "out" in subdir:
                continue
            Path(subdir + "\\out").mkdir(parents=True, exist_ok=True)
            file_path = subdir + os.sep + file_name
            if "max" in subdir:
                wb = xlrd.open_workbook(file_path)
                for sheet in wb.sheets():
                    if "עסקאות שאושרו וטרם נקלטו" in sheet.name:
                        continue
                    clean_sheet_name = sheet.name.replace('"', '')
                    clean_sheet_name += " - " + sheet.row(1)[0].value + " - " + sheet.row(2)[0].value.replace("/",
                                                                                                              "-")
                    tx_data = {"transactions": []}
                    if "4725" in clean_sheet_name:
                        account = data["data_cache"]["ohad_credit_card"]
                    else:
                        account = data["data_cache"]["shlomit_credit_card"]
                    csv_output = create_csv_files(subdir, clean_sheet_name)
                    for row in range(4, sheet.nrows):
                        if sheet.row(row)[0].value != "":
                            line_buff = parse_max_data(sheet.row(row))
                            csv_output.write(line_buff + "\n\r")
                            tx_data["transactions"] = convert_csv_line_to_transaction(tx_data["transactions"],
                                                                                      line_buff, account)
                    post_transaction(tx_data)

            else:
                with open(file_path, "r", encoding='cp862') as dat_file:
                    lines_list = dat_file.readlines()
                    split_lines = [x.split(",") for x in lines_list]
                    csv_output = create_csv_files(subdir, "leumi")
                    tx_data = {"transactions": []}
                    account = data["data_cache"]["leumi_account_id"]
                    for row in split_lines:
                        line_buff = parse_leumi_data(row)
                        csv_output.write(line_buff + "\n\r")
                        tx_data["transactions"] = convert_csv_line_to_transaction(
                            tx_data["transactions"], line_buff, account)
                    post_transaction(tx_data)


def main():
    dir_path = make_new_dir()
    config = get_config_file()
    scrape_data_from_max(config, dir_path)
    scrape_data_from_leumi(config, dir_path)
    csv_from_excel(dir_path)


if __name__ == "__main__":
    main()
