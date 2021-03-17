#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tkinter import ttk  # Normal Tkinter.* widgets are not themed!
from ttkthemes import ThemedTk
from tkinter import *

from post_transactions import Transactions
from scrapers import Scrapers
from utils import Utils
from Naked.toolshed.shell import execute_js

class Progress:
    """ threaded progress bar for tkinter gui """

    def __init__(self, parent):
        self.maximum = 100
        self.interval = 10
        self.progressbar = ttk.Progressbar(parent, orient=HORIZONTAL, length=100, mode='determinate',
                                           maximum=self.maximum)
        self.progressbar.grid(row=1, ipady=30, ipadx=100)


class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()

        self.start = None
        self.quit = None
        self.create_widgets()
        self.transactions = Transactions()
        self.utils = None


    def create_widgets(self):
        self.master.geometry("400x400")
        self.master.title("YNAB automatic parser")
        self.master.iconbitmap(Utils.resource_path("YNAB.ico"))
        self.start = ttk.Button(self, width=50)
        self.start["text"] = "Download Data"
        self.start["command"] = self.download_transactions_data

        self.start.grid(row=0, column=0, ipady=30, ipadx=30)

        self.start = ttk.Button(self, width=50)
        self.start["text"] = "Parse data and upload to YNAB"
        self.start["command"] = self.parse_and_upload_cmd

        self.start.grid(row=2, column=0, ipady=30, ipadx=30)

        self.quit = ttk.Button(self, text="Quit", command=self.master.destroy, width=50)
        self.quit.grid(row=3, column=0, ipady=30, ipadx=30)

    def download_transactions_data(self):
        self.utils = Utils(self.transactions)
        #
        scraper = Scrapers(dir_path=self.utils.dir_path, config=self.utils.config)
        # # scraper.scrape_data_from_isracard()
       # scraper.scrape_data_from_leumi()
        # # scraper.scrape_data_from_max()
        # success = execute_js('../scrape.js')
        # if success:
        #     print("success")
        # else:
        #     print("failed")


    def parse_and_upload_cmd(self):
        data = self.transactions.get_init_data()

        self.utils.csv_from_excel(data)
        self.transactions.post_transaction(self.utils.get_tx_data(), data)


def main():
    app = Application(master=ThemedTk(theme="Arc"))
    app.mainloop()


if __name__ == "__main__":
    main()
