import logging
import os
import sqlite3
import time
from copy import deepcopy
from datetime import datetime
from queue import Queue
from threading import Lock, Thread

import pandas as pd
import pandas_datareader.data as web
import yfinance as yf


class DataDownloader:
    expected_source = [
        "yahoo",
        "iex",
        "iex-tops",
        "iex-last",
        "iex-last",
        "bankofcanada",
        "stooq",
        "iex-book",
        "enigma",
        "fred",
        "famafrench",
        "oecd",
        "eurostat",
        "nasdaq",
        "quandl",
        "moex",
        "tiingo",
        "yahoo-actions",
        "yahoo-dividends",
        "av-forex",
        "av-forex-daily",
        "av-daily",
        "av-daily-adjusted",
        "av-weekly",
        "av-weekly-adjusted",
        "av-monthly",
        "av-monthly-adjusted",
        "av-intraday",
        "econdb",
        "naver",
    ]

    def __init__(
        self,
        lst_tickers: list = None,
        start_date: datetime = datetime(1970, 1, 1),
        end_date: datetime = datetime(2023, 12, 1),
        concurrency: int = 5,
        save=True,
        base_path="./data",
    ):
        self.lst_tickers = (
            lst_tickers if lst_tickers else [{"fred": "CPIAUCSL"}]
        )
        self.start_date = start_date
        self.end_date = end_date
        self.base_path = base_path
        self.concurrency = min(concurrency, len(lst_tickers))
        self.dw_queue = Queue()
        self.logger = logging.getLogger("DataDownloader")
        self.set_up_logging()
        self.create_folder()
        self.dw_results_lock = Lock()
        self.save = save
        self.db_path = f"{self.base_path}/prices.db"
        self.initialize_database()
        self.tickers = [list(x.values())[0] for x in self.lst_tickers]

    def set_up_logging(self):
        self.logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def validate_data_source(self, source):
        assert source in self.expected_source, self.logger.error(
            f"Data source {source} is not supported."
            + f"Please use one of the following: {self.expected_source}"
        )

    def create_folder(self):
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)
            self.logger.info("Created folder for data %s", self.base_path)
        else:
            self.logger.info(
                "Folder for data already exists: %s", self.base_path
            )

    def initialize_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS prices (
                              date TEXT,
                              ticker TEXT,
                              value REAL,
                              PRIMARY KEY (date, ticker))"""
            )
            conn.commit()

    def delete_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""DROP TABLE IF EXISTS prices""")
            conn.commit()

    def download_data_worker(self):
        while True:
            ticker_info = self.dw_queue.get()
            if ticker_info is None:
                self.dw_queue.task_done()
                break

            try:
                copy_ticker_info = deepcopy(ticker_info)  # Ensure a deep copy
                data_source = list(copy_ticker_info.keys())[0]
                ticker = copy_ticker_info[data_source]

                # self.validate_data_source(data_source)
                if data_source == "yahoo":
                    df = yf.download(
                        ticker,
                        start=self.start_date,
                        end=self.end_date,
                        progress=False,
                        threads=False,
                    )
                else:
                    df = web.DataReader(
                        ticker,
                        data_source,
                        start=self.start_date,
                        end=self.end_date,
                    )
                df = self.extract_data(df).rename(ticker).dropna()
                df.index.name = "date"
                if len(df) > 0:
                    with self.dw_results_lock:
                        self.dw_results.append(df)
                else:
                    raise LookupError(f"No data for {ticker}")
            except Exception as e:
                self.logger.error("Error downloading %s: %s", ticker, e)
                self.dw_queue.task_done()

            else:
                self.logger.info("Downloaded %s", ticker)
                self.dw_queue.task_done()

    def queue_download_data(self):
        threads = []
        self.logger.info("Starting %d threads", self.concurrency)
        # Clear the data workers results
        self.dw_results = []

        for _ in range(self.concurrency):
            thread = Thread(target=self.download_data_worker)
            thread.start()
            threads.append(thread)

        for ticker_info in deepcopy(self.lst_tickers):
            self.dw_queue.put(ticker_info)

        # Add sentinel values for each thread
        for _ in range(self.concurrency):
            self.dw_queue.put(None)

        self.dw_queue.join()

        for thread in threads:
            thread.join()

        self.logger.info("Done downloading data")

    def extract_data(self, df):
        if isinstance(df, pd.Series):
            return df

        cols = df.columns
        if len(cols) == 1:
            return df[cols[0]]

        open_col = next((x for x in cols if "open" in x.lower()), None)
        return df[open_col]

    def resample_data(self, freq="D"):
        self.resampled_data = []
        for df in self.dw_results:
            self.resampled_data.append(df.resample(freq).ffill().dropna())
        self.logger.info("Done resampling data")

    def concat_data(self):
        if len(self.resampled_data) == 0:
            self.logger.error(
                "No data to save. Please run resample_data() first."
            )
        return pd.concat(self.resampled_data, axis=1)

    def save_data(self, df):
        with sqlite3.connect(self.db_path) as conn:
            df.index = df.index.strftime("%Y-%m-%d %H:%M:%S")
            self.logger.info(df)
            time.sleep(10)
            insert_values = df.stack().reset_index().values.tolist()
            try:
                cur = conn.cursor()
                cur.executemany(
                    "INSERT OR IGNORE INTO prices (date, ticker, value)"
                    + "VALUES (?, ?, ?)",
                    insert_values,
                )
                conn.commit()
            except Exception as excpt:
                self.logger.error("Error saving data: %s", excpt)
                conn.rollback()
            self.logger.info("Done saving data")

    def load_data(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            tickers = ",".join(["?"] * len(self.tickers))
            sql = f"SELECT * FROM prices WHERE ticker in ({tickers})"
            db_data = cursor.execute(sql, self.tickers).fetchall()
            df = pd.DataFrame(db_data, columns=["date", "ticker", "value"])
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index(["date", "ticker"]).unstack()
            df.columns = df.columns.droplevel(0)
            return df

    def download_data(self):
        self.queue_download_data()

        self.resample_data(freq="D")

        df = self.concat_data()
        if self.save:
            self.save_data(df)

        return df


if __name__ == "__main__":
    data_downloader = DataDownloader(
        lst_tickers=[
            {"yahoo": "XHB"},
            {"fred": "CPIAUCSL"},
            {"fred": "DCOILWTICO"},
            {"yahoo": "^GSPC"},
            {"yahoo": "GC=F"},
            {"fred": "GS10"},
            {"fred": "GS30"},
            {"yahoo": "VNQ"},
            {"yahoo": "DBC"},
            {"yahoo": "FXE"},
            {"yahoo": "BTC-USD"},
            {"yahoo": "IGF"},
            {"yahoo": "XLE"},
        ],
        concurrency=10,
        save=True,
    )
    data_downloader.download_data()
    data = data_downloader.load_data()
