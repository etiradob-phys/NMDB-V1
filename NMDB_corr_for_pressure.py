# Author: E. Tirado-Bueno (etirado@inaoe.mx)
# Last Update: 27 / 02 / 2025
# --------------------------------------------------------------------------------------------------------------------------------------
import subprocess
import sys
# --------------------------------------------------------------------------------------------------------------------------------------
# Function to install a package
# --------------------------------------------------------------------------------------------------------------------------------------

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------

#install_package(" ")

# --------------------------------------------------------------------------------------------------------------------------------------

import requests
import xarray as xr
import pandas as pd
import os
import zipfile
import urllib
from bs4 import BeautifulSoup
import numpy as np
import math
import scipy

# --------------------------------------------------------------------------------------------------------------------------------------

def nmdb_get(startdate, enddate, station="JUNG"):
    sy,sm,sd = str(startdate).split("-")
    ey,em,ed = str(enddate).split("-")
    url = "http://nest.nmdb.eu/draw_graph.php?formchk=1&stations[]={station}&tabchoice=1m&dtype=corr_for_pressure&tresolution=1&force=best&yunits=0&date_choice=bydate&start_day={sd}&start_month={sm}&start_year={sy}&start_hour=0&start_min=0&end_day={ed}&end_month={em}&end_year={ey}&end_hour=23&end_min=59&output=ascii&display_null=1"
#   url = "http://nest.nmdb.eu/draw_graph.php?formchk=1&stations[]={station}&tabchoice=1h&dtype=corr_for_pressure&tresolution=60&force=1&yunits=0&date_choice=bydate&start_day={sd}&start_month={sm}&start_year={sy}&start_hour=0&start_min=0&end_day={ed}&end_month={em}&end_year={ey}&end_hour=23&end_min=59&output=ascii&display_null=1"
    url = url.format(station=station, sd=sd, sm=sm, sy=sy, ed=ed, em=em, ey=ey)
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, features="html.parser")
    pre = soup.find_all('pre')
    pre = pre[0].text
    pre = pre[pre.find('start_date_time'):]
    pre = pre.replace("start_date_time   1HCOR_E", "")
    f = open("tmpV1_uncorr.txt", "w")
    f.write(pre)
    f.close()
    df = open("tmpV1_uncorr.txt", "r")
    lines = df.readlines()
    df.close()
    lines = lines[1:]
    dfneut = pd.DataFrame(lines)
    dfneut = dfneut[0].str.split(";", n = 2, expand = True)
    cols = ['DATE', 'COUNT']
    dfneut.columns = cols
    dates = pd.to_datetime(dfneut['DATE'])
    values = dfneut['COUNT']

    dfdict = dict(zip(dates,values))

    return dfdict

# --------------------------------------------------------------------------------------------------------------------------------------

year_ti = input("Enter the initial year: ")
month_ti = input("Enter the initial month (e.g., JAN -> 01): ")
day_ti = input("Enter the initial day: ")
print('---------------------------------------------------------------')
year_tf = input("Enter the final year: ")
month_tf = input("Enter the final month (e.g., JAN -> 01): ")
day_tf = input("Enter the final day: ")

ti_nmdb = f"{year_ti}-{month_ti}-{day_ti}"
tf_nmdb = f"{year_tf}-{month_tf}-{day_tf}"

ti = f"{year_ti}{month_ti}{day_ti}"
tf = f"{year_tf}{month_tf}{day_tf}"

# --------------------------------------------------------------------------------------------------------------------------------------

corr_for_pressure_MCMU = nmdb_get(ti_nmdb, tf_nmdb, "MCMU")     # R = 0.30 GV - STATION 0
corr_for_pressure_THUL = nmdb_get(ti_nmdb, tf_nmdb, "THUL")     # R = 0.30 GV - STATION 1
corr_for_pressure_INVK = nmdb_get(ti_nmdb, tf_nmdb, "INVK")     # R = 0.30 GV - STATION 2
corr_for_pressure_NAIN = nmdb_get(ti_nmdb, tf_nmdb, "NAIN")     # R = 0.30 GV - STATION 3
corr_for_pressure_FSMT = nmdb_get(ti_nmdb, tf_nmdb, "FSMT")     # R = 0.30 GV - STATION 4
corr_for_pressure_OULU = nmdb_get(ti_nmdb, tf_nmdb, "OULU")     # R = 0.81 GV - STATION 5

corr_for_pressureMCMU = list(corr_for_pressure_MCMU.items())
corr_for_pressureTHUL = list(corr_for_pressure_THUL.items())
corr_for_pressureINVK = list(corr_for_pressure_INVK.items())
corr_for_pressureNAIN = list(corr_for_pressure_NAIN.items())
corr_for_pressureFSMT = list(corr_for_pressure_FSMT.items())
corr_for_pressureOULU = list(corr_for_pressure_OULU.items())

corr_for_pressure_array_MCMU = np.array(corr_for_pressureMCMU)
corr_for_pressure_array_THUL = np.array(corr_for_pressureTHUL)
corr_for_pressure_array_INVK = np.array(corr_for_pressureINVK)
corr_for_pressure_array_NAIN = np.array(corr_for_pressureNAIN)
corr_for_pressure_array_FSMT = np.array(corr_for_pressureFSMT)
corr_for_pressure_array_OULU = np.array(corr_for_pressureOULU)

# List of NMs and corresponding data arrays
stations = {
    'MCMU': corr_for_pressure_array_MCMU,
    'THUL': corr_for_pressure_array_THUL,
    'INVK': corr_for_pressure_array_INVK,
    'NAIN': corr_for_pressure_array_NAIN,
    'FSMT': corr_for_pressure_array_FSMT,
    'OULU': corr_for_pressure_array_OULU
}

# Dictionary to store DataFrames
dfs = {}

# Loop through each station and process the data
for name, data in stations.items():
    df = pd.DataFrame(data)
    df.columns = ['Datetime', name]
    df = df.replace('   null\n', np.nan, regex=True)
    df = df.replace('\n', '', regex=True)
    df[name] = df[name].astype(float)
    df.set_index('Datetime', inplace=True)
#    dfs[name] = ((df - df[name].mean())/(df[name].mean())) * 100
    dfs[name] = df

# Concatenate all DataFrames along the columns
dataset_nm_corr_for_pressure = pd.concat(dfs.values(), axis=1)

print(dataset_nm_corr_for_pressure)
print('---------------------------------------------------------------')

# Extract various components of Datetime:

dataset_nm_corr_for_pressure_txt = dataset_nm_corr_for_pressure
dataset_nm_corr_for_pressure_txt = dataset_nm_corr_for_pressure.reset_index()

dataset_nm_corr_for_pressure_txt['Year'] = dataset_nm_corr_for_pressure_txt['Datetime'].dt.year
dataset_nm_corr_for_pressure_txt['Month'] = dataset_nm_corr_for_pressure_txt['Datetime'].dt.month
dataset_nm_corr_for_pressure_txt['Day'] = dataset_nm_corr_for_pressure_txt['Datetime'].dt.day
dataset_nm_corr_for_pressure_txt['Hour'] = dataset_nm_corr_for_pressure_txt['Datetime'].dt.hour
dataset_nm_corr_for_pressure_txt['Minute'] = dataset_nm_corr_for_pressure_txt['Datetime'].dt.minute
dataset_nm_corr_for_pressure_txt['Second'] = dataset_nm_corr_for_pressure_txt['Datetime'].dt.second

# --------------------------------------------------------------------------------------------------------------------------------------

dataset_nm_corr_for_pressure_txt = dataset_nm_corr_for_pressure_txt[['Datetime', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second', 'MCMU', 'THUL', 'INVK', 'NAIN', 'FSMT', 'OULU']]
dataset_nm_corr_for_pressure_txt.set_index('Datetime', inplace=True)

dataset_nm_corr_for_pressure_txt.to_csv(f'/Users/eduardotiradobueno/Downloads/corr_for_pressure_{ti}to{tf}.txt', header=True, index=None, sep='\t', mode='w')

