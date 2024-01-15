from statsforecast.models import (
    AutoARIMA, SimpleExponentialSmoothing, Theta, AutoETS, AutoCES, AutoTheta,
    Naive, SeasonalNaive, WindowAverage, ADIDA
)
from statsforecast.models import _TS
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error

from src.utils import ram_stats


StatsForecastModel = _TS

MODELS = [
    # (Model, {hyperparameters})
    (AutoARIMA, {}),
    (SimpleExponentialSmoothing, {'alpha': 0.5}),
    (Theta, {}),
    (AutoETS, {}),
    (AutoCES, {}),
    (AutoTheta, {}),
    (Naive, {}),
    (SeasonalNaive, {'season_length': 7}),
    (WindowAverage, {'window_size': 7}),
    (ADIDA, {}),
]


def series_to_df(series: np.array) -> pd.DataFrame:
    """Converts a series to a dataframe with columns 'unique_id', 'ds' and 'y'.
    This is the format expected by the StatsForecastModel class.

    Args:
        series (np.array): A series of values to be forecasted.

    Returns:
        pd.DataFrame: A dataframe with columns 'unique_id', 'ds' and 'y'.
    """
    data = {
        'unique_id': 'unique_id',
        'ds': range(len(series)),
        'y': series,
    }
    return pd.DataFrame(data)


def forecast(
    series: np.array,
    horizon: int,
    model: StatsForecastModel
    ) -> np.array:
    """Forecasts a series using the specified model.

    Args:
        series (np.array): A series of values to be forecasted.
        horizon (int): The forecast horizon.
        model (StatsForecastModel): The model to use for forecasting.

    Returns:
        np.array: An array of forecasted values.
    """
    model.fit(series)
    predictions = np.array(model.predict(horizon)['mean'])
    return predictions


def cross_validation(series: np.array, horizon: int) -> StatsForecastModel:
    """Selects the best model from a list of models using cross-validation.

    Args:
        series (np.array): A series of values to be forecasted.
        horizon (int): The forecast horizon.

    Returns:
        StatsForecastModel: The best model.
    """
    # Split series into train and test
    train = series[:len(series) - horizon]
    test = series[len(series) - horizon:]

    # Fit and predict using each model
    history = {}
    for model, hyperparameters in MODELS:
        # Load model, fit, predict and evaluate
        model = model(**hyperparameters)
        predictions = forecast(train, horizon, model)
        mse = mean_squared_error(test, predictions)

        # Save model and mse
        model_name = model.__class__.__name__
        history[model_name] = {'model': model, 'mse': mse}

        mem_used, mem_total, mem_percent = ram_stats()
        print(f'{model_name} - {mem_used}/{mem_total} {mem_percent}% - {mse:.2f}')

    # Select the best model based on minimum mse
    champion = min(history, key=lambda x: history[x]['mse'])
    print(f'Best model: {champion} ({history[champion]["mse"]:.2f})')

    return history[champion]['model']


def get_model(model_name: str) -> StatsForecastModel:
    """Returns a model based on its name.

    Args:
        model_name (str): The name of the model. Must match one of the
            following criteria:
            - Have the same name as the class (case insensitive). Accepted
            names can be found in the `MODELS` variable defined in this file.
            - Be named 'fast'. In this case, the model returned will be the
            model defined in the `FAST_MODEL` variable defined in the main.py
            file.

    Returns:
        StatsForecastModel: The instantiated model.
    """
    model_name = model_name.lower()

    for model, hyperparameters in MODELS:
        if model.__name__.lower() == model_name:
            return model(**hyperparameters)
