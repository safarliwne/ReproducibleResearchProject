# Reproducible CO2 Emissions Analysis

## Project Description

This project reproduces and translates an R-based global CO2 emissions analysis into Python.

Original project:
https://github.com/hoangsonww/CO2-Global-Emissions-Analysis

Dataset:
https://github.com/owid/co2-data

The objective is to reproduce the visualizations and analytical workflow of the original R project while ensuring full reproducibility using Python and Docker.

---

## Repository Structure

data/raw/          Dataset (OWID CO2 data)

reference/         Original R project and reference plots

reports/           Generated outputs and visualizations

src/co2_repro/     Python source code

---

## Python Files

data.py
- Loads and prepares the dataset.

analysis.py
- Performs analytical operations on CO2 emissions data.

visualization.py
- Creates charts and visualizations.

main.py
- Runs the complete workflow.

---

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Run the Project

Execute:

```bash
python src/co2_repro/main.py
```

Generated plots will be saved in the `reports` directory.

---

## Docker

Build Docker image:

```bash
docker build -t co2-analysis .
```

Run container:

```bash
docker run co2-analysis
```

---

## Dataset Source

Our World in Data CO2 Dataset:

https://github.com/owid/co2-data

---

## Original Reference Project

https://github.com/hoangsonww/CO2-Global-Emissions-Analysis

---

## Authors

Said Mahmud

Sabir Mammadov

Aykhan Safarli

Nural Mammadov

---

## Course Goal

The goal of this project is to reproduce an existing R-based CO2 emissions analysis in Python and demonstrate a reproducible workflow using:

- Python
- GitHub
- Docker
- Structured project organization
- Reproducible data analysis
