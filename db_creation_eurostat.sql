CREATE DATABASE IF NOT EXISTS eurostat_econ;

USE eurostat_econ;

CREATE TABLE IF NOT EXISTS GERD_by_sector_of_performance_and_NUTS_2_region (
    `STRUCTURE` VARCHAR(255),
    `STRUCTURE_ID` VARCHAR(255),
    `STRUCTURE_NAME` VARCHAR(255),
    `freq` VARCHAR(255),
    `Time frequency` VARCHAR(255),
    `sectperf` VARCHAR(255),
    `Sector of performance` VARCHAR(255),
    `unit` VARCHAR(255),
    `Unit of measure` VARCHAR(255),
    `geo` VARCHAR(255),
    `Geopolitical entity (reporting)` VARCHAR(255),
    `TIME_PERIOD` INT,
    `Time` FLOAT,
    `OBS_VALUE` FLOAT,
    `Observation value` FLOAT,
    `OBS_FLAG` VARCHAR(255),
    `Observation status (Flag) V2 structure` VARCHAR(255),
    `CONF_STATUS` FLOAT,
    `Confidentiality status (flag)` FLOAT
);

LOAD DATA LOCAL INFILE '/var/lib/mysql-files/GERD_by_sector_of_performance_and_NUTS_2_region.csv'
INTO TABLE GERD_by_sector_of_performance_and_NUTS_2_region
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`STRUCTURE`, `STRUCTURE_ID`, `STRUCTURE_NAME`, `freq`, `Time frequency`, `sectperf`, `Sector of performance`, `unit`, `Unit of measure`, `geo`, `Geopolitical entity (reporting)`, `TIME_PERIOD`, `Time`, `OBS_VALUE`, `Observation value`, `OBS_FLAG`, `Observation status (Flag) V2 structure`, `CONF_STATUS`, `Confidentiality status (flag)`);
CREATE TABLE IF NOT EXISTS CorrespondanceTable (
    `Unnamed: 0` INT,
    `Geopolitical entity (reporting)` VARCHAR(255),
    `geo` VARCHAR(255),
    `Country` VARCHAR(255),
    `NUTS_1` VARCHAR(255),
    `NUTS_2` VARCHAR(255)
);

LOAD DATA LOCAL INFILE '/var/lib/mysql-files/CorrespondanceTable.csv'
INTO TABLE CorrespondanceTable
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`Unnamed: 0`, `Geopolitical entity (reporting)`, `geo`, `Country`, `NUTS_1`, `NUTS_2`);
CREATE TABLE IF NOT EXISTS Employed_persons_by_educational_attainment_level_and_NUTS_2_region (
    `STRUCTURE` VARCHAR(255),
    `STRUCTURE_ID` VARCHAR(255),
    `freq: Time frequency` VARCHAR(255),
    `unit: Unit of measure` VARCHAR(255),
    `sex: Sex` VARCHAR(255),
    `age: Age class` VARCHAR(255),
    `isced11: International Standard Classification of Education (ISCED 2011)` VARCHAR(255),
    `geo` VARCHAR(9),
    `geopolitical_entity` VARCHAR(255),
    `TIME_PERIOD: Time` INT,
    `OBS_VALUE: Observation value` FLOAT,
    `OBS_FLAG: Observation status (Flag) V2 structure` VARCHAR(255),
    `CONF_STATUS: Confidentiality status (flag)` FLOAT
);

LOAD DATA LOCAL INFILE '/var/lib/mysql-files/Employed_persons_by_educational_attainment_level_and_NUTS_2_region.csv'
INTO TABLE Employed_persons_by_educational_attainment_level_and_NUTS_2_region
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`STRUCTURE`, `STRUCTURE_ID`, `freq: Time frequency`, `unit: Unit of measure`, `sex: Sex`, `age: Age class`, `isced11: International Standard Classification of Education (ISCED 2011)`, @messy_geo, `TIME_PERIOD: Time`, `OBS_VALUE: Observation value`, `OBS_FLAG: Observation status (Flag) V2 structure`, `CONF_STATUS: Confidentiality status (flag)`)
SET 
    `geo` = SUBSTRING_INDEX(@messy_geo, ': ', 1),
    `geopolitical_entity` = SUBSTRING_INDEX(@messy_geo, ': ', -1);
CREATE TABLE IF NOT EXISTS Unemployed_persons_by_educational_attainment_level_and_NUTS_2_region (
    `STRUCTURE` VARCHAR(255),
    `STRUCTURE_ID` VARCHAR(255),
    `freq: Time frequency` VARCHAR(255),
    `isced11: International Standard Classification of Education (ISCED 2011)` VARCHAR(255),
    `sex: Sex` VARCHAR(255),
    `age: Age class` VARCHAR(255),
    `unit: Unit of measure` VARCHAR(255),
    `geo` VARCHAR(9),
    `geopolitical_entity` VARCHAR(255),
    `TIME_PERIOD: Time` INT,
    `OBS_VALUE: Observation value` FLOAT,
    `OBS_FLAG: Observation status (Flag) V2 structure` VARCHAR(255),
    `CONF_STATUS: Confidentiality status (flag)` FLOAT
);

LOAD DATA LOCAL INFILE '/var/lib/mysql-files/Unemployed_persons_by_educational_attainment_level_and_NUTS_2_region.csv'
INTO TABLE Unemployed_persons_by_educational_attainment_level_and_NUTS_2_region
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`STRUCTURE`, `STRUCTURE_ID`, `freq: Time frequency`, `isced11: International Standard Classification of Education (ISCED 2011)`, `sex: Sex`, `age: Age class`, `unit: Unit of measure`, @messy_geo, `TIME_PERIOD: Time`, `OBS_VALUE: Observation value`, `OBS_FLAG: Observation status (Flag) V2 structure`, `CONF_STATUS: Confidentiality status (flag)`)
SET 
    `geo` = SUBSTRING_INDEX(@messy_geo, ': ', 1),
    `geopolitical_entity` = SUBSTRING_INDEX(@messy_geo, ': ', -1);
CREATE TABLE IF NOT EXISTS Population_in_private_households_by_educational_attainment_level_and_NUTS_2_region (
    `STRUCTURE` VARCHAR(255),
    `STRUCTURE_ID` VARCHAR(255),
    `STRUCTURE_NAME` VARCHAR(255),
    `freq` VARCHAR(255),
    `Time frequency` VARCHAR(255),
    `sex` VARCHAR(255),
    `Sex` VARCHAR(255),
    `isced11` VARCHAR(255),
    `International Standard Classification of Education (ISCED 2011)` VARCHAR(255),
    `age` VARCHAR(255),
    `Age class` VARCHAR(255),
    `unit` VARCHAR(255),
    `Unit of measure` VARCHAR(255),
    `geo` VARCHAR(255),
    `Geopolitical entity (reporting)` VARCHAR(255),
    `TIME_PERIOD` INT,
    `Time` FLOAT,
    `OBS_VALUE` FLOAT,
    `Observation value` FLOAT,
    `OBS_FLAG` VARCHAR(255),
    `Observation status (Flag) V2 structure` VARCHAR(255),
    `CONF_STATUS` FLOAT,
    `Confidentiality status (flag)` FLOAT
);

LOAD DATA LOCAL INFILE '/var/lib/mysql-files/Population_in_private_households_by_educational_attainment_level_and_NUTS_2_region.csv'
INTO TABLE Population_in_private_households_by_educational_attainment_level_and_NUTS_2_region
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`STRUCTURE`, `STRUCTURE_ID`, `STRUCTURE_NAME`, `freq`, `Time frequency`, `sex`, `Sex`, `isced11`, `International Standard Classification of Education (ISCED 2011)`, `age`, `Age class`, `unit`, `Unit of measure`, `geo`, `Geopolitical entity (reporting)`, `TIME_PERIOD`, `Time`, `OBS_VALUE`, `Observation value`, `OBS_FLAG`, `Observation status (Flag) V2 structure`, `CONF_STATUS`, `Confidentiality status (flag)`);
CREATE TABLE IF NOT EXISTS GDP_at_current_market_prices_by_NUTS_2_region (
    `STRUCTURE` VARCHAR(255),
    `STRUCTURE_ID` VARCHAR(255),
    `STRUCTURE_NAME` VARCHAR(255),
    `freq` VARCHAR(255),
    `Time frequency` VARCHAR(255),
    `unit` VARCHAR(255),
    `Unit of measure` VARCHAR(255),
    `geo` VARCHAR(255),
    `Geopolitical entity (reporting)` VARCHAR(255),
    `TIME_PERIOD` INT,
    `Time` FLOAT,
    `OBS_VALUE` FLOAT,
    `Observation value` FLOAT,
    `OBS_FLAG` FLOAT,
    `Observation status (Flag) V2 structure` FLOAT,
    `CONF_STATUS` FLOAT,
    `Confidentiality status (flag)` FLOAT
);

LOAD DATA LOCAL INFILE '/var/lib/mysql-files/GDP_at_current_market_prices_by_NUTS_2_region.csv'
INTO TABLE GDP_at_current_market_prices_by_NUTS_2_region
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`STRUCTURE`, `STRUCTURE_ID`, `STRUCTURE_NAME`, `freq`, `Time frequency`, `unit`, `Unit of measure`, `geo`, `Geopolitical entity (reporting)`, `TIME_PERIOD`, `Time`, `OBS_VALUE`, `Observation value`, `OBS_FLAG`, `Observation status (Flag) V2 structure`, `CONF_STATUS`, `Confidentiality status (flag)`);
CREATE TABLE IF NOT EXISTS Employed_persons_by_NUTS_2_region (
    `STRUCTURE` VARCHAR(255),
    `STRUCTURE_ID` VARCHAR(255),
    `freq: Time frequency` VARCHAR(255),
    `unit: Unit of measure` VARCHAR(255),
    `sex: Sex` VARCHAR(255),
    `age: Age class` VARCHAR(255),
    `geo` VARCHAR(9),
    `geopolitical_entity` VARCHAR(255),
    `TIME_PERIOD: Time` INT,
    `OBS_VALUE: Observation value` FLOAT,
    `OBS_FLAG: Observation status (Flag) V2 structure` VARCHAR(255),
    `CONF_STATUS: Confidentiality status (flag)` FLOAT
);

LOAD DATA LOCAL INFILE '/var/lib/mysql-files/Employed_persons_by_NUTS_2_region.csv'
INTO TABLE Employed_persons_by_NUTS_2_region
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(`STRUCTURE`, `STRUCTURE_ID`, `freq: Time frequency`, `unit: Unit of measure`, `sex: Sex`, `age: Age class`, @messy_geo, `TIME_PERIOD: Time`, `OBS_VALUE: Observation value`, `OBS_FLAG: Observation status (Flag) V2 structure`, `CONF_STATUS: Confidentiality status (flag)`)
SET 
    `geo` = SUBSTRING_INDEX(@messy_geo, ': ', 1),
    `geopolitical_entity` = SUBSTRING_INDEX(@messy_geo, ': ', -1);