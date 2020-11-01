# -*- coding: utf-8 -*-

import configparser
import datetime
import json
import requests
import time


class Transactions:

    @staticmethod
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

    @staticmethod
    def get_id_for_name(collection, name):
        for item in collection:
            if item['name'] == name:
                return item['id']
        raise ValueError('name not found in collection!', name, collection)

    def get_init_data(self):
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
            budget_id = self.get_id_for_name(budgets, config['ynab_accounts']['budget_name'])

            accounts = requests.get('https://api.youneedabudget.com/v1/budgets/' + budget_id + '/accounts',
                                    headers=header)
            accounts.raise_for_status()
            accounts = accounts.json()['data']['accounts']
            leumi_account_id = self.get_id_for_name(accounts, config['ynab_accounts']['leumi_account_id'])
            shlomit_credit_card = self.get_id_for_name(accounts, config['ynab_accounts']['shlomit_credit_card'])
            ohad_credit_card = self.get_id_for_name(accounts, config['ynab_accounts']['ohad_credit_card'])

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

            return self.get_init_data()

    @staticmethod
    def post_transaction(tx_data, data):

        # chunks_size = int(len(tx_data["transactions"]) / 10)

        if len(tx_data["transactions"]) >= 200:
            print("over 200 transactions, will send first 200 right now, rest will be sent in next hour")

        chunk_tx_data = {"transactions": []}

        for i, transaction in enumerate(tx_data["transactions"]):

            chunk_tx_data["transactions"].append(transaction)
            # if len(chunk_tx_data["transactions"]) == chunks_size:
            tx_response = requests.post(
                'https://api.youneedabudget.com/v1/budgets/' + data['data_cache']['budget_id']
                + '/transactions', headers=data['header'], json=chunk_tx_data).json()
            chunk_tx_data = {"transactions": []}

            # TODO: check tx_response for success post or for fail, and act accordingly.
            print(json.dumps(tx_response, indent=4))
            if i == 199:
                delta = datetime.timedelta(hours=1)
                now = datetime.datetime.now()
                next_hour = (now + delta).replace(microsecond=0, second=0, minute=2)
                time.sleep((next_hour - now).seconds)
