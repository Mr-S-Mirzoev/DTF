# Markowitz Portfolio Optimization

## Introduction

This project is a Python implementation of the Markowitz Portfolio Optimization algorithm. The algorithm is used to find the optimal allocation of assets in a portfolio to maximise the expected inflation-adjusted return. The algorithm is based on the work of Harry Markowitz, who won the Nobel Prize in Economics in 1990 for his work on portfolio theory.

## Results

### Key Findings

- **Inflation-Resilient Asset Classes Identified:** The analysis identified several asset classes that strongly correlate with inflation. For that, we explored treasury bonds, crude oil prices, the SPX index, real estate, gold futures, and bitcoin.

- **Optimised Portfolio Performance:** The optimised portfolio, constructed using the Markowitz framework and adjusted for inflation, outperforms a CPI-adjusted, equally weighted portfolio.

- **Diversification and Constraints:** The final portfolio includes a diversified mix of assets, each with specified weights, adhering to constraints like the sum of asset weights equaling 1 and individual asset weight upper and lower bounds.

- **Performance Metrics:** The optimized portfolio shows an expected annual return of **9.82%**, a risk (annual standard deviation) of **19.96%**, and a Sharpe ratio of **0.4922**.

### Conclusion: Effective Inflation-Resilient Strategy

Portfolios optimised for inflation resilience can significantly outperform traditional portfolios.

### Optimised Portfolio Composition

| Asset Class                                       | Weight |
| ------------------------------------------------- | ------ |
| GS10: 10-Year Treasury Constant Maturity Rate     | 5%     |
| GS30: 30-Year Treasury Constant Maturity Rate     | 5%     |
| DCOILWTICO: Crude Oil Prices: West Texas Intermediate (WTI) | 5% |
| XLE: Energy Stocks (Energy Select Sector SPDR Fund) | 15%    |
| GC=F: Gold Futures                                | 30%    |
| FXE: Foreign Currencies (CurrencyShares Euro Trust) | 5%    |
| DBC: Commodities (Invesco DB Commodity Index Tracking Fund) | 5% |
| BTC-USD: Cryptocurrencies (Bitcoin)               | 30%    |


## Usage Instructions

To run the program, you must first install the required dependencies. This can be done by running the following commands in the terminal:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Once the dependencies are installed, you can run the program by running the following command in the terminal:

```bash
python3 code/src/processing/downloader.py [-h] [-d DATA_FOLDER]
```

The program will then download the data from Yahoo Finance and save it to the specified folder. The default folder is `data/`.

The `code/src/main.ipynb` notebook explores the optimisation algorithm. The notebook can be run by running the following command in the terminal:

```bash
jupyter notebook code/src/main.ipynb
```

This can also be explored in Docker. To do so, run the following commands in the terminal:

```bash
[sudo] docker build --build-arg CACHEBUST=$(date +%s) -t markowitz .
[sudo] docker run -p 8888:8888 markowitz
```

## Development

### Installation

To install the dependencies, run the following commands in the terminal:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```
