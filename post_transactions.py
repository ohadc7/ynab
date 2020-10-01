# -*- coding: utf-8 -*-

import configparser
import datetime
import json
import requests


def convert_csv_line_to_transaction(tx_data, line_buff, account):

    line = line_buff.split(",")
    if line[2] != "":
        amount = int(1000 * float(line[2])) * - 1
    else:
        amount = int(1000 * float(line[4]))
    memo = None
    if line[3] != "":
        memo = line[3]
    tx_data.append(
            {
                "account_id": account,
                'date': line[0],
                'amount': amount,
                "payee_id": None,
                "payee_name": line[1],
                "category_id": None,
                "memo": memo,
                "cleared": "cleared",
                "approved": False,
                "flag_color": None,
                "import_id": None,
            }
        )
    return tx_data


def get_id_for_name(collection, name):
    for item in collection:
        if item['name'] == name:
            return item['id']
    raise ValueError('name not found in collection!', name, collection)


def get_init_data():
    try:
        with open("../ynab_data_file.json") as data_file:
            data = json.load(data_file)
            print('Data loaded:', data)
            return data

    except FileNotFoundError:
        print('Data file not found. Getting new data.')
        config = configparser.ConfigParser()

        config.read('../payload_data.ini')
        pa_token = config['ynab']['tokken']
        header = {'Authorization': 'Bearer ' + pa_token}

        budgets = requests.get('https://api.youneedabudget.com/v1/budgets', headers=header)
        budgets.raise_for_status()
        budgets = budgets.json()['data']['budgets']
        budget_id = get_id_for_name(budgets, config['ynab_accounts']['budget_name'])

        accounts = requests.get('https://api.youneedabudget.com/v1/budgets/' + budget_id + '/accounts', headers=header)
        accounts.raise_for_status()
        accounts = accounts.json()['data']['accounts']
        leumi_account_id = get_id_for_name(accounts, config['ynab_accounts']['leumi_account_id'])
        shlomit_credit_card = get_id_for_name(accounts, config['ynab_accounts']['shlomit_credit_card'])
        ohad_credit_card = get_id_for_name(accounts, config['ynab_accounts']['ohad_credit_card'])

        data = {
            'header': {
                'Authorization': 'Bearer ' + pa_token
            },
            'data_cache': {
                'budget_id': budget_id,
                'leumi_account_id': leumi_account_id,
                'shlomit_credit_card': shlomit_credit_card,
                'ohad_credit_card': ohad_credit_card,
                'refresh_date': datetime.datetime.now().date().isoformat()
            }
        }
        with open("../ynab_data_file.json", "w") as write_file:
            write_file.write(json.dumps(data, indent=4))

        return get_init_data()


def post_transaction(tx_data):
    init_data = get_init_data()

    tx_response = requests.post('https://api.youneedabudget.com/v1/budgets/' + init_data['data_cache']['budget_id']
                               + '/transactions', headers=init_data['header'], json=tx_data).json()
    print(json.dumps(tx_response, indent=4))
