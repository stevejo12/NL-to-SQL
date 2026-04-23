few_shots = [
  # --- GDP (no sex/age dimensions) ---
  {
    'Question': "What was the GDP of Albania in 2021?",
    'SQLQuery': "SELECT `OBS_VALUE` FROM GDP WHERE `geo` = 'AL' AND `TIME_PERIOD` = 2021 AND `region_type` = 'Country'",
    'SQLResult': "Result of the SQL query",
    'Answer': "15243.1"
  },
  {
    'Question': "List the top 5 NUTS 2 regions by GDP in 2020.",
    'SQLQuery': "SELECT `geo`, `Geopolitical entity (reporting)`, `OBS_VALUE` FROM GDP WHERE `TIME_PERIOD` = 2020 AND `region_type` = 'NUTS 2' AND `OBS_VALUE` IS NOT NULL ORDER BY `OBS_VALUE` DESC LIMIT 5",
    'SQLResult': "Result of the SQL query",
    'Answer': "Top 5 NUTS 2 regions by GDP"
  },
  {
    'Question': "How did Albania's GDP change from 2019 to 2021 at the country level?",
    'SQLQuery': "SELECT `TIME_PERIOD`, `OBS_VALUE` FROM GDP WHERE `geo` = 'AL' AND `region_type` = 'Country' AND `TIME_PERIOD` BETWEEN 2019 AND 2021 ORDER BY `TIME_PERIOD`",
    'SQLResult': "Result of the SQL query",
    'Answer': "2019: 13917.9, 2020: 13379.5, 2021: 15243.1"
  },

  # --- Employed (has sex + age; always filter both) ---
  {
    'Question': "How many people aged 15 and over were employed in Austria in 2021?",
    'SQLQuery': "SELECT `OBS_VALUE` FROM Employed WHERE `geo` = 'AT' AND `TIME_PERIOD` = 2021 AND `region_type` = 'Country' AND `sex` = 'T' AND `age` = 'Y_GE15'",
    'SQLResult': "Result of the SQL query",
    'Answer': "Total employed persons aged 15+ in Austria, 2021"
  },
  {
    'Question': "How many young women (aged 15-24) were employed in Austria in 2021?",
    'SQLQuery': "SELECT `OBS_VALUE` FROM Employed WHERE `geo` = 'AT' AND `TIME_PERIOD` = 2021 AND `region_type` = 'Country' AND `sex` = 'F' AND `age` = 'Y15-24'",
    'SQLResult': "Result of the SQL query",
    'Answer': "203.9"
  },
  {
    'Question': "Which NUTS 2 region in Austria had the most employed men aged 20-64 in 2021?",
    'SQLQuery': "SELECT `geo`, `Geopolitical entity (reporting)`, `OBS_VALUE` FROM Employed WHERE `geo` LIKE 'AT%' AND `region_type` = 'NUTS 2' AND `TIME_PERIOD` = 2021 AND `sex` = 'M' AND `age` = 'Y20-64' AND `OBS_VALUE` IS NOT NULL ORDER BY `OBS_VALUE` DESC LIMIT 1",
    'SQLResult': "Result of the SQL query",
    'Answer': "NUTS 2 region with highest male employment"
  },

  # --- Unemployed (only T / Y15-74 exists) ---
  {
    'Question': "What was the total unemployment in Austria in 2021?",
    'SQLQuery': "SELECT `OBS_VALUE` FROM Unemployed WHERE `geo` = 'AT' AND `TIME_PERIOD` = 2021 AND `region_type` = 'Country' AND `sex` = 'T' AND `age` = 'Y15-74'",
    'SQLResult': "Result of the SQL query",
    'Answer': "283.7"
  },
  {
    'Question': "Which NUTS 2 region in Austria had the highest unemployment in 2020?",
    'SQLQuery': "SELECT `geo`, `Geopolitical entity (reporting)`, `OBS_VALUE` FROM Unemployed WHERE `geo` LIKE 'AT%' AND `region_type` = 'NUTS 2' AND `TIME_PERIOD` = 2020 AND `sex` = 'T' AND `age` = 'Y15-74' AND `OBS_VALUE` IS NOT NULL ORDER BY `OBS_VALUE` DESC LIMIT 1",
    'SQLResult': "Result of the SQL query",
    'Answer': "NUTS 2 region with highest unemployment"
  },

  # --- Employed_by_Education (sex, age, ISCED) ---
  {
    'Question': "How many people aged 25-64 with tertiary education were employed in Austria in 2021?",
    'SQLQuery': "SELECT `OBS_VALUE` FROM Employed_by_Education WHERE `geo` = 'AT' AND `TIME_PERIOD` = 2021 AND `region_type` = 'Country' AND `sex` = 'T' AND `age` = 'Y25-64' AND `International Standard Classification of Education (ISCED 2011)` = 'Tertiary education (levels 5-8)'",
    'SQLResult': "Result of the SQL query",
    'Answer': "Employed tertiary-educated persons aged 25-64"
  },
  {
    'Question': "Compare employment of men vs women with upper secondary education aged 25-64 in Austria in 2021.",
    'SQLQuery': "SELECT `sex`, `OBS_VALUE` FROM Employed_by_Education WHERE `geo` = 'AT' AND `TIME_PERIOD` = 2021 AND `region_type` = 'Country' AND `age` = 'Y25-64' AND `sex` IN ('F', 'M') AND `International Standard Classification of Education (ISCED 2011)` = 'Upper secondary and post-secondary non-tertiary education (levels 3 and 4)'",
    'SQLResult': "Result of the SQL query",
    'Answer': "Employment by sex at upper-secondary level"
  },

  # --- Population_by_Education (note: unit is PC = percent, age ranges are narrower) ---
  {
    'Question': "What percentage of women aged 25-34 in Austria had tertiary education in 2021?",
    'SQLQuery': "SELECT `OBS_VALUE` FROM Population_by_Education WHERE `geo` = 'AT' AND `TIME_PERIOD` = 2021 AND `region_type` = 'Country' AND `sex` = 'F' AND `age` = 'Y25-34' AND `International Standard Classification of Education (ISCED 2011)` = 'Tertiary education (levels 5-8)'",
    'SQLResult': "Result of the SQL query",
    'Answer': "Share of tertiary-educated women aged 25-34 (percent)"
  },
  {
    'Question': "Which Austrian NUTS 2 region had the highest share of tertiary-educated women aged 30-34 in 2021?",
    'SQLQuery': "SELECT `geo`, `Geopolitical entity (reporting)`, `OBS_VALUE` FROM Population_by_Education WHERE `geo` LIKE 'AT%' AND `region_type` = 'NUTS 2' AND `TIME_PERIOD` = 2021 AND `sex` = 'F' AND `age` = 'Y30-34' AND `International Standard Classification of Education (ISCED 2011)` = 'Tertiary education (levels 5-8)' AND `OBS_VALUE` IS NOT NULL ORDER BY `OBS_VALUE` DESC LIMIT 1",
    'SQLResult': "Result of the SQL query",
    'Answer': "Region with highest tertiary share"
  },

  # --- Cross-table join: productivity proxy ---
  {
    'Question': "What is GDP per employed person (aged 15+) for each country in 2021?",
    'SQLQuery': 
    """
      SELECT g.`geo`, g.`Geopolitical entity (reporting)`,
      g.`OBS_VALUE` / e.`OBS_VALUE` AS gdp_per_worker
      FROM GDP g
      JOIN Employed e
      ON g.`geo` = e.`geo` AND g.`TIME_PERIOD` = e.`TIME_PERIOD`
      WHERE g.`TIME_PERIOD` = 2021
      AND g.`region_type` = 'Country' AND e.`region_type` = 'Country'
      AND e.`sex` = 'T' AND e.`age` = 'Y_GE15'
      AND e.`OBS_VALUE` IS NOT NULL AND e.`OBS_VALUE` > 0
      ORDER BY gdp_per_worker DESC
    """,
    'SQLResult': "Result of the SQL query",
    'Answer': "GDP per employed person by country, 2021"
  },

  # --- Cross-table: unemployment rate proxy (unemployed / (unemployed + employed)) ---
  {
    'Question': "What is the unemployment rate for each Austrian NUTS 2 region in 2021?",
    'SQLQuery': 
    """
      SELECT u.`geo`, u.`Geopolitical entity (reporting)`,
      (u.`OBS_VALUE` / (u.`OBS_VALUE` + e.`OBS_VALUE`)) * 100 AS unemployment_rate_pct
      FROM Unemployed u
      JOIN Employed e
      ON u.`geo` = e.`geo` AND u.`TIME_PERIOD` = e.`TIME_PERIOD`
      WHERE u.`TIME_PERIOD` = 2021
      AND u.`region_type` = 'NUTS 2' AND e.`region_type` = 'NUTS 2'
      AND u.`geo` LIKE 'AT%'
      AND u.`sex` = 'T' AND u.`age` = 'Y15-74'
      AND e.`sex` = 'T' AND e.`age` = 'Y15-74'
      AND u.`OBS_VALUE` IS NOT NULL AND e.`OBS_VALUE` IS NOT NULL
      ORDER BY unemployment_rate_pct DESC
    """,
    'SQLResult': "Result of the SQL query",
    'Answer': "Unemployment rates across Austrian NUTS 2 regions"
  }
]