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
#    dfs[name] = ((df - df[name].mean())/(df[name].mean())) * 100
    dfs[name] = df

# Concatenate all DataFrames along the columns
dataset_nm = pd.concat(dfs.values(), axis=1)

print(dataset_nm)
print('---------------------------------------------------------------')

dataset_nm_resample = dataset_nm.resample('60min').mean()

# --------------------------------------------------------------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rc('xtick', labelsize=15) 
matplotlib.rc('ytick', labelsize=15)

fig, b = plt.subplots(6, 1, sharex=True, figsize=(10,8), tight_layout=False)
fig.suptitle('Neutron Monitor Data', fontsize=16)
fig.tight_layout()
dataset_nm.plot(ax=b, subplots=True, rot=20, legend=False, color='gray')
dataset_nm_resample.plot(ax=b, subplots=True, rot=20, legend=False, color='black')
b[0].set_ylabel('$I_{Obs}$', fontsize=10)
b[1].set_ylabel('$I_{Obs}$', fontsize=10)
b[2].set_ylabel('$I_{Obs}$', fontsize=10)
b[3].set_ylabel('$I_{Obs}$', fontsize=10)
b[4].set_ylabel('$I_{Obs}$', fontsize=10)
b[5].set_ylabel('$I_{Obs}$', fontsize=10)

b[0].legend(['McMurdo $R_{C}=0.30$ GV'], loc='lower left', fontsize=5)
b[1].legend(['Thule $R_{C}=0.30$ GV'], loc='lower left', fontsize=5)
b[2].legend(['Inuvik $R_{C}=0.30$ GV'], loc='lower left', fontsize=5)
b[3].legend(['Nain $R_{C}=0.30$ GV'], loc='lower left', fontsize=5)
b[4].legend(['Fort Smith $R_{C}=0.81$ GV'], loc='lower left', fontsize=5)
b[5].legend(['Oulu $R_{C}=0.81$ GV'], loc='lower left', fontsize=5)

#b[0].axhline(y = 0.0, color = 'black', linestyle = '--', linewidth=0.5)
#b[1].axhline(y = 0.0, color = 'black', linestyle = '--', linewidth=0.5)
#b[2].axhline(y = 0.0, color = 'black', linestyle = '--', linewidth=0.5)
#b[3].axhline(y = 0.0, color = 'black', linestyle = '--', linewidth=0.5)
#b[4].axhline(y = 0.0, color = 'black', linestyle = '--', linewidth=0.5)
#b[5].axhline(y = 0.0, color = 'black', linestyle = '--', linewidth=0.5)

plt.subplots_adjust(wspace=0, hspace=0)
plt.show()

# --------------------------------------------------------------------------------------------------------------------------------------

# Extract various components of Datetime:

dataset_nm_txt = dataset_nm
dataset_nm_txt = dataset_nm.reset_index()

dataset_nm_txt['Year'] = dataset_nm_txt['Datetime'].dt.year
dataset_nm_txt['Month'] = dataset_nm_txt['Datetime'].dt.month
dataset_nm_txt['Day'] = dataset_nm_txt['Datetime'].dt.day
dataset_nm_txt['Hour'] = dataset_nm_txt['Datetime'].dt.hour
dataset_nm_txt['Minute'] = dataset_nm_txt['Datetime'].dt.minute
dataset_nm_txt['Second'] = dataset_nm_txt['Datetime'].dt.second

dataset_nm_resample_txt = dataset_nm_resample
dataset_nm_resample_txt = dataset_nm_resample.reset_index()

dataset_nm_resample_txt['Year'] = dataset_nm_resample_txt['Datetime'].dt.year
dataset_nm_resample_txt['Month'] = dataset_nm_resample_txt['Datetime'].dt.month
dataset_nm_resample_txt['Day'] = dataset_nm_resample_txt['Datetime'].dt.day
dataset_nm_resample_txt['Hour'] = dataset_nm_resample_txt['Datetime'].dt.hour
dataset_nm_resample_txt['Minute'] = dataset_nm_resample_txt['Datetime'].dt.minute
dataset_nm_resample_txt['Second'] = dataset_nm_resample_txt['Datetime'].dt.second

# --------------------------------------------------------------------------------------------------------------------------------------

dataset_nm_txt = dataset_nm_txt[['Datetime', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second', 'MCMU', 'THUL', 'INVK', 'NAIN', 'FSMT', 'OULU']]
dataset_nm_txt.set_index('Datetime', inplace=True)

dataset_nm_resample_txt = dataset_nm_resample_txt[['Datetime', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second', 'MCMU', 'THUL', 'INVK', 'NAIN', 'FSMT', 'OULU']]
dataset_nm_resample_txt.set_index('Datetime', inplace=True)

dataset_nm_txt.to_csv(f'/Users/eduardotiradobueno/Downloads/{ti}to{tf}.txt', header=True, index=None, sep='\t', mode='w')
dataset_nm_resample_txt.to_csv(f'/Users/eduardotiradobueno/Downloads/{ti}to{tf}_resample.txt', header=True, index=None, sep='\t', mode='w')

# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------
