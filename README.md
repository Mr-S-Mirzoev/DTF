# Markowitz Portfolio Optimization

## Introduction

This project is a Python implementation of the Markowitz Portfolio Optimization algorithm. The algorithm is used to find the optimal allocation of assets in a portfolio to maximize the expected return given a certain level of risk. The algorithm is based on the work of Harry Markowitz, who won the Nobel Prize in Economics in 1990 for his work on portfolio theory.

## Usage Instructions

In order to run the program, you must first install the required dependencies. This can be done by running the following commands in the terminal:

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

The optimisation algorithm is explored in the `code/src/main.ipynb` notebook. The notebook can be run by running the following command in the terminal:

```bash
jupyter notebook code/src/main.ipynb
```

This can be also explored in Docker. To do so, run the following commands in the terminal:

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
