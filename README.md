# Nighttime Light (NTL) Remote Sensing Data for Urban Growth Mapping

## GIS Course Project — IIT Kharagpur

### Project Overview

This project investigates the relationship between **Nighttime Light (NTL) intensity and urban growth in India** using satellite-based remote sensing data and socioeconomic indicators.

The study covers **India as a whole** and analyzes temporal changes over the period **2000–2026**, with emphasis on:

1. **Nighttime Light (NTL)**
2. **Gross Domestic Product (GDP)**
3. **Population**
4. **Urban/territorial expansion**

The objective is to understand how changes in artificial nighttime illumination correspond to changes in economic activity, population, and the spatial expansion of urbanized areas.

---

## Objectives

The major objectives of this project are:

* Analyze the spatial and temporal variation of Nighttime Light intensity across India.
* Study the relationship between NTL intensity and India's GDP over time.
* Analyze population growth and its relationship with nighttime illumination.
* Measure changes in urbanized/expanded areas over time.
* Generate GIS-based maps showing the spatial expansion of illuminated areas.
* Identify major periods and regions of urban growth using satellite observations.

---

## Study Area

**Country:** India

---

## Study Period

**2000–2026**

The NTL analysis combines data from different satellite sensor generations:

* **DMSP-OLS:** Historical nighttime-light observations, particularly useful for the early part of the study period.
* **VIIRS:** Higher-resolution nighttime-light observations for the later period.

---

## Data Sources

### 1. Nighttime Light Data

Nighttime Light data are obtained from the **Earth Observation Group (EOG), Colorado School of Mines**.

#### DMSP-OLS

DMSP-OLS provides a long historical nighttime-light record. The annual Version 4 products cover the historical period beginning in 1992, with the standard annual series extending through 2013 and additional extension products available beyond that period.

Data characteristics:

* Spatial resolution: approximately 30 arc-seconds (~1 km)
* CRS: EPSG:4326
* Data format: GeoTIFF
* Measurement: nighttime visible-light intensity

Source:

Earth Observation Group — DMSP Nighttime Lights

#### VIIRS

VIIRS nighttime-light products provide higher spatial resolution observations for the later period.

Data characteristics:

* Spatial resolution: approximately 15 arc-seconds (~500 m at the equator)
* CRS: EPSG:4326
* Data format: GeoTIFF
* Measurement: average nighttime radiance
* Unit: nW/cm²/sr

Source:

Earth Observation Group — VIIRS Nighttime Lights

---

### 2. GDP Data

GDP data are obtained from the **World Bank World Development Indicators**.

The primary indicator used is:

**GDP (current US$)**

The World Bank provides annual GDP data for India and other countries. The dataset can be used to construct a yearly GDP time series and compare it with aggregate NTL measurements.

Source:

World Bank — World Development Indicators

---

### 3. Population Data

Population data are obtained from the **World Bank World Development Indicators**.

The primary indicator is:

**Population, total**

The annual population series is used to investigate the relationship between population growth and nighttime-light expansion.

---

## Methodology

The overall workflow is:

```text
Satellite NTL Data
        |
        v
Data Download
        |
        v
Preprocessing
        |
        +--------------------+
        |                    |
        v                    v
   DMSP-OLS               VIIRS
        |                    |
        +---------+----------+
                  |
                  v
          India Boundary
                  |
                  v
        Spatial Clipping
                  |
                  v
       NTL Statistics
                  |
        +---------+----------+
        |         |          |
        v         v          v
      GDP    Population   Urban Area
        |         |          |
        +---------+----------+
                  |
                  v
        Temporal Analysis
                  |
                  v
        Maps + Graphs + Tables
```

---

## GIS Software

The project uses:

* QGIS
* Python
* Raster processing tools
* Pandas
* NumPy
* Rasterio
* GeoPandas
* Matplotlib
---

## Authors

**Stitipragya Behera 22CS30055**
IIT Kharagpur

**Asritha Chouhan 23CS30071**
IIT Kharagpur

### Course

Geographical Information System (GIS)

### Institution

Indian Institute of Technology Kharagpur

