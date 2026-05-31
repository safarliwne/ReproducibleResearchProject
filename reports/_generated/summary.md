## Generated data summary

The Python pipeline uses the same filtering logic as the reference R project:
non-missing CO2 per capita, non-missing GDP, positive population, and years from 1960 onward.

- Prepared analytical rows: **9,901**
- Latest snapshot rows: **165**
- Year range after filtering: **1960-2022**
- Latest year present in the snapshot: **2022**

## Regression reproduction

The reproduced model is `co2_pc ~ gdp_pc`, fit on the latest observation for each country or region.

- Number of observations: **165**
- Intercept: **0.5640**
- GDP per capita slope: **0.00020714**
- R-squared: **0.5556**
- p-value for GDP per capita: **1.624e-30**

## Top 10 by latest CO2 per capita

| country              |   year |   co2_pc |   gdp_pc |
|:---------------------|-------:|---------:|---------:|
| Qatar                |   2022 |   37.89  | 131991   |
| Kuwait               |   2022 |   25.242 |  47709   |
| Trinidad and Tobago  |   2022 |   25.063 |  25077.1 |
| Bahrain              |   2022 |   24.668 |  38324.9 |
| Saudi Arabia         |   2022 |   20.73  |  56685.8 |
| United Arab Emirates |   2022 |   20.221 |  76127.2 |
| Oman                 |   2022 |   16.488 |  37494   |
| United States        |   2022 |   14.802 |  57075.3 |
| Australia            |   2022 |   14.659 |  51305.4 |
| Turkmenistan         |   2022 |   14.116 |  13485.5 |

## Top 10 by latest total CO2 emissions

| country       |   year |   total_co2 |   co2_pc |
|:--------------|-------:|------------:|---------:|
| World         |   2022 |   37527.8   |    4.678 |
| China         |   2022 |   11711.8   |    8.218 |
| United States |   2022 |    5055.4   |   14.802 |
| India         |   2022 |    2831.13  |    1.986 |
| Russia        |   2022 |    1675.46  |   11.509 |
| Japan         |   2022 |    1029.64  |    8.237 |
| Iran          |   2022 |     767.178 |    8.57  |
| Indonesia     |   2022 |     758.021 |    2.719 |
| Germany       |   2022 |     667.843 |    7.942 |
| Saudi Arabia  |   2022 |     666.994 |   20.73  |

## GDP quartile summary

|   gdp_q |   countries |   avg_co2_pc |   median_co2_pc |   min_gdp_pc |   max_gdp_pc |
|--------:|------------:|-------------:|----------------:|-------------:|-------------:|
|       1 |          42 |        0.48  |           0.304 |      688.913 |      4443.56 |
|       2 |          41 |        2.307 |           1.945 |     4538.22  |     12658.8  |
|       3 |          41 |        5.574 |           4.06  |    12792.1   |     27406.8  |
|       4 |          41 |        9.844 |           7.483 |    27472.1   |    131991    |

## EU27 versus non-EU latest summary

The EU extension uses country-only rows and population-weighted CO2 per capita for the aggregate comparison.

| region_group   |   countries |   latest_year |   total_co2_mt |   population |   avg_co2_pc |   median_co2_pc |   weighted_co2_pc |
|:---------------|------------:|--------------:|---------------:|-------------:|-------------:|----------------:|------------------:|
| EU27           |          27 |          2022 |        2736.94 |  4.49113e+08 |        5.985 |           5.705 |             6.094 |
| Non-EU         |         137 |          2022 |       33740.8  |  7.46145e+09 |        4.238 |           2.138 |             4.522 |
