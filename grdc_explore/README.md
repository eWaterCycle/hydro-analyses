[![Build Status](https://travis-ci.com/sebranchett/hydro-analyses.svg?branch=master)](https://travis-ci.com/sebranchett/hydro-analyses)

## Running the notebook in Windows:

RUN 
```conda create --name ewatercycle python=3.6```

## Running the notebook in Linux:

RUN
```conda create -n ewatercycle```

# Windows and Linux:

RUN 
```conda activate ewatercycle```

RUN 
```conda install pytest```

Install the kernel to use this environment in a Jupyter Notebook

RUN
```python -m ipykernel install --user --name ewatercycle --display-name "Py3_eWaterCycle"```

RUN 
```jupyter notebook```
select the kernel "Py3_eWaterCycle"

## For running pytest:
RUN 
```pip install -e ./grdc_explore```
