
from amlb.utils import call_script_in_same_dir
from amlb.benchmark import TaskConfig
from amlb.data import Dataset, DatasetType
from copy import deepcopy

import statsmodels as sm
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from statsmodels.tsa.forecasting.theta import ThetaModel
from statsmodels.tsa.api import STLForecast
from statsmodels.tsa.statespace.exponential_smoothing import ExponentialSmoothing
from frameworks.shared.utils import Timer, zip_path


def setup(*args, **kwargs):
    call_script_in_same_dir(__file__, "setup.sh", *args, **kwargs)

def run(dataset: Dataset, config: TaskConfig):

    if dataset.type is not DatasetType.timeseries:
        raise ValueError("Framework `GluonTS` does exepct timeseries tasks.")

    from frameworks.shared.caller import run_in_venv
    dataset = deepcopy(dataset)
    if not hasattr(dataset, 'timestamp_column'):
        dataset.timestamp_column = None
    if not hasattr(dataset, 'id_column'):
        dataset.id_column = None
    if not hasattr(dataset, 'forecast_range_in_steps'):
        raise AttributeError("Unspecified `forecast_range_in_steps`.")

    data = dict(
        # train=dict(path=dataset.train.data_path('parquet')),
        # test=dict(path=dataset.test.data_path('parquet')),
        train=dict(X=dataset.train.X, y=dataset.train.y, path=dataset.train.path),
        test=dict(X=dataset.test.X, y=dataset.test.y, path=dataset.test.path),
        target=dict(
            name=dataset.target.name,
            classes=dataset.target.values
        ),
        problem_type=dataset.type.name,  # AutoGluon problem_type is using same names as amlb.data.DatasetType
        timestamp_column=dataset.timestamp_column,
        id_column=dataset.id_column,
        forecast_range_in_steps=dataset.forecast_range_in_steps
    )

    return run_in_venv(__file__, "exec.py",
                       input_data=data, dataset=dataset, config=config)
