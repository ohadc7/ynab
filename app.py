#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from tkinter import ttk  # Normal Tkinter.* widgets are not themed!
from ttkthemes import ThemedTk
from tkinter import *
from tkinter.ttk import *
from scrapers import Scrapers
from utils import Utils
import time


class Progress:
    """ threaded progress bar for tkinter gui """

    def __init__(self, parent, row, column, columnspan):
        self.maximum = 100
        self.interval = 10
        self.progressbar = ttk.Progressbar(parent, orient=HORIZONTAL, length=100, mode='determinate',
                                           maximum=self.maximum)
        self.progressbar.grid(row=1, ipady=30, ipadx=100)
        #self.thread = threading.Thread()
        #self.thread.__init__(target=self.progressbar.start(self.interval),
        #                             args=())
        #self.thread.start()

    # def pb_stop(self):
    #     """ stops the progress bar """
    #     if not self.thread.is_alive():
    #         VALUE = self.progressbar["value"]
    #         self.progressbar.stop()
    #         self.progressbar["value"] = VALUE
    #
    # def pb_start(self):
    #     """ starts the progress bar """
    #     if not self.thread.is_alive():
    #         VALUE = self.progressbar["value"]
    #         self.progressbar.configure(mode="indeterminate",
    #                                    maximum=self.maximum,
    #                                    value=VALUE)
    #         self.progressbar.start(self.interval)
    #
    # def pb_clear(self):
    #     """ stops the progress bar """
    #     if not self.thread.is_alive():
    #         self.progressbar.stop()
    #         self.progressbar.configure(mode="determinate", value=0)
    #
    # def pb_complete(self):
    #     """ stops the progress bar and fills it """
    #     if not self.thread.is_alive():
    #         self.progressbar.stop()
    #         self.progressbar.configure(mode="determinate",
    #                                    maximum=self.maximum,
    #                                    value=self.maximum)


class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()

        self.start = None
        # self.progress_bar = Progress(master, row=0, column=0, columnspan=2)

        self._start_bar = None
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
        utils = Utils()
        scraper = Scrapers(dir_path=utils.dir_path, config=utils.config)
        scraper.scrape_data_from_isracard()
        #scraper.scrape_data_from_leumi()
        #scraper.scrape_data_from_max()
        #utils.csv_from_excel()


def main():
    app = Application(master=ThemedTk(theme="Arc"))
    app.mainloop()


if __name__ == "__main__":
    main()
