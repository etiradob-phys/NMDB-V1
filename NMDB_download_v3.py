# Author: E. Tirado-Bueno (etirado@inaoe.mx)
# Last Update: 25 / 02 / 2025
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
import matplotlib.pyplot as plt
import matplotlib
import scipy
import smplotlib

# --------------------------------------------------------------------------------------------------------------------------------------

def nmdb_get(startdate, enddate, station="JUNG"):
    sy,sm,sd = str(startdate).split("-")
    ey,em,ed = str(enddate).split("-")
    url = "http://nest.nmdb.eu/draw_graph.php?formchk=1&stations[]={station}&tabchoice=1m&dtype=corr_for_efficiency&tresolution=1&force=best&yunits=0&date_choice=bydate&start_day={sd}&start_month={sm}&start_year={sy}&start_hour=0&start_min=0&end_day={ed}&end_month={em}&end_year={ey}&end_hour=23&end_min=59&output=ascii&display_null=1"
#   url = "http://nest.nmdb.eu/draw_graph.php?formchk=1&stations[]={station}&tabchoice=1h&dtype=corr_for_efficiency&tresolution=60&force=1&yunits=0&date_choice=bydate&start_day={sd}&start_month={sm}&start_year={sy}&start_hour=0&start_min=0&end_day={ed}&end_month={em}&end_year={ey}&end_hour=23&end_min=59&output=ascii&display_null=1"
    url = url.format(station=station, sd=sd, sm=sm, sy=sy, ed=ed, em=em, ey=ey)
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, features="html.parser")
    pre = soup.find_all('pre')
    pre = pre[0].text
    pre = pre[pre.find('start_date_time'):]
    pre = pre.replace("start_date_time   1HCOR_E", "")
    f = open("tmpV1.txt", "w")
    f.write(pre)
    f.close()
    df = open("tmpV1.txt", "r")
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

ti_nmdb = "2008-01-01"
tf_nmdb = "2008-02-29"

# --------------------------------------------------------------------------------------------------------------------------------------

data_MCMU = nmdb_get(ti_nmdb, tf_nmdb, "MCMU")     # R = 0.30 GV - STATION 0
data_THUL = nmdb_get(ti_nmdb, tf_nmdb, "THUL")     # R = 0.30 GV - STATION 1
data_INVK = nmdb_get(ti_nmdb, tf_nmdb, "INVK")     # R = 0.30 GV - STATION 2
data_NAIN = nmdb_get(ti_nmdb, tf_nmdb, "NAIN")     # R = 0.30 GV - STATION 3
data_FSMT = nmdb_get(ti_nmdb, tf_nmdb, "FSMT")     # R = 0.30 GV - STATION 4
data_OULU = nmdb_get(ti_nmdb, tf_nmdb, "OULU")     # R = 0.81 GV - STATION 5

dataMCMU = list(data_MCMU.items())
dataTHUL = list(data_THUL.items())
dataINVK = list(data_INVK.items())
dataNAIN = list(data_NAIN.items())
dataFSMT = list(data_FSMT.items())
dataOULU = list(data_OULU.items())

data_array_MCMU = np.array(dataMCMU)
data_array_THUL = np.array(dataTHUL)
data_array_INVK = np.array(dataINVK)
data_array_NAIN = np.array(dataNAIN)
data_array_FSMT = np.array(dataFSMT)
data_array_OULU = np.array(dataOULU)

# List of NMs and corresponding data arrays
stations = {
    'MCMU': data_array_MCMU,
    'THUL': data_array_THUL,
    'INVK': data_array_INVK,
    'NAIN': data_array_NAIN,
    'FSMT': data_array_FSMT,
    'OULU': data_array_OULU
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
#    dfs[name] = df - df[name].mean()
    dfs[name] = df

# Concatenate all DataFrames along the columns
dataset_nm = pd.concat(dfs.values(), axis=1)

print(dataset_nm)

# Extract various components of Datetime:

# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------
