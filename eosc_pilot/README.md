[![Build Status](https://travis-ci.com/sebranchett/hydro-analyses.svg?branch=master)](https://travis-ci.com/sebranchett/hydro-analyses)

## Running the notebook in Windows:

RUN 
```conda create --name ewatercycle python=2.7```
OR
```conda create --name ewatercycle python=3.6```

## Running the notebook in Linux:

RUN
```conda create -n ewatercycle```

# Windows and Linux:

RUN 
```conda activate ewatercycle```

RUN 
```conda install xarray dask netCDF4 bottleneck```
OR 
```conda install -c conda-forge xarray cartopy pynio pseudonetcdf``` 
currently pynio not available

RUN 
```conda install -c conda-forge cartopy```

RUN 
```conda install -c ioam holoviews bokeh```

RUN ```conda install -c pyviz geoviews```

RUN 
```pip install hydrostats```

RUN 
```pip install rank-histogram```

RUN 
```conda install pytest```

Install the kernel to use this environment in a Jupyter Notebook

RUN
```python -m ipykernel install --user --name ewatercycle --display-name "Py3_eWaterCycle"```

RUN 
```jupyter notebook```
select the kernel "Py3_eWaterCycle"

