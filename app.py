#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tkinter import ttk  # Normal Tkinter.* widgets are not themed!
from ttkthemes import ThemedTk
from tkinter import *

from post_transactions import Transactions
from scrapers import Scrapers
from utils import Utils


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

    def create_widgets(self):
        self.master.geometry("400x400")
        self.master.title("YNAB automatic parser")
        self.master.iconbitmap(Utils.resource_path("YNAB.ico"))
        self.start = ttk.Button(self, width=50)
        self.start["text"] = "Start Operation"
        self.start["command"] = self.start_cmd

        self.start.grid(row=0, column=0, ipady=30, ipadx=30)

        self.quit = ttk.Button(self, text="Quit", command=self.master.destroy, width=50)
        self.quit.grid(row=4, column=0, pady=4, sticky=NE, ipady=30, ipadx=30)

    def start_cmd(self):
        transactions = Transactions()
        data = transactions.get_init_data()
        utils = Utils(transactions)
        scraper = Scrapers(dir_path=utils.dir_path, config=utils.config)
        scraper.scrape_data_from_isracard()
        scraper.scrape_data_from_leumi()
        scraper.scrape_data_from_max()
        utils.csv_from_excel(data)
        transactions.post_transaction(utils.get_tx_data(), data)


def main():
    app = Application(master=ThemedTk(theme="Arc"))
    app.mainloop()


if __name__ == "__main__":
    main()
