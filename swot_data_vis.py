import earthaccess 
import json 
from pathlib import Path 
import os 
import xarray as xr 
# for plot 
import matplotlib.pyplot as plt 
import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker 
import numpy as np 

# log in to earthdata (defaults to using netrc file but will ask for credentials if that doesn't work) 
earthaccess.login() 

# prompt user for date range (note: valid date range for the data product this program uses (simulated data) is 2011-11-13 to 2012-11-12) 
start = input("Please enter the date range in the following format: yyyy-mm-dd \nstart of time range: ") # for testing I'm using 2011-11-13 as start & end of time range, which has 1 matching granule)
end = input("end of time range: ") 

# find & download matching granules 
datasets = earthaccess.search_data(short_name = "SWOT_SIMULATED_L2_KARIN_SSH_ECCO_LLC4320_CALVAL_V1", temporal = (start, end)) 

folder = Path("./swot_data") # path to folder where you want to download the data 
earthaccess.download(datasets, "./swot_data/") 
for item in os.listdir(folder): 
    if item.endswith(".zip"): # check for ".zip" extension
        zip_ref = zipfile.ZipFile(f"{folder}/{item}") # create zipfile object
        zip_ref.extractall(folder) # extract file to dir
        zip_ref.close() # close file 

# create list of downloaded file names 
fns = list() 
if len(os.listdir(folder)) > 0: 
    fns = [file.name for file in folder.glob("*.nc")] 
print(f"files found: {len(fns)}") 

# prompt user for bounding box and variable name 
# bbox = input("bounding box coordinates (format: [#,#,#,#]): ") 
# bbox = json.loads(bbox) 
# vname = input("variable name: ") 

# using this for testing instead of asking for user input 
bbox = [60,-50,80,-20] 
vname = "ssha_karin_2" 

# open file (currently defaulting to first file in list) 
ds = xr.open_dataset(Path(f"./swot_data/{fns[0]}"), engine="netcdf4") 

lon0, lat0, lon1, lat1 = bbox # store bounding box coordinates as individual variables 
lon, lat = ds['longitude_nadir'], ds['latitude_nadir'] # xarray DataArrays representing lon & lat of nadir point 
msk = (lon > lon0) & (lon < lon1) & (lat > lat0) & (lat < lat1) 
dout = {}
if msk.sum() > 1:
    dout[vname] = ds[vname][msk, :] 

# subset to use for plot 
subset = xr.Dataset(dout) 

### create plot: ### 

# set plot size 
fig = plt.figure(figsize=(11,8.5))

# set axes using specified map projection
ax=plt.axes(projection=ccrs.PlateCarree())

# make filled contour plot
ax.contourf(subset['longitude'], subset['latitude'], subset['ssha_karin_2'],
            transform = ccrs.PlateCarree())

# make map global & add coastlines 
ax.set_global() 
ax.coastlines()

# define xticks for longitude
ax.set_xticks(np.arange(-180,181,60), crs=ccrs.PlateCarree())
lon_formatter = cticker.LongitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)

# define yticks for latitude
ax.set_yticks(np.arange(-90,91,30), crs=ccrs.PlateCarree())
lat_formatter = cticker.LatitudeFormatter()
ax.yaxis.set_major_formatter(lat_formatter)
