import time

from flask import Flask, request, g
import numpy as np

from src.forecast import forecast, cross_validation, get_model


app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'Hello, World!'


@app.route('/forecast', methods=['POST'])
def forecast_():
    try:
        start_time = time.time()

        model_name = request.json['model'].lower()
        horizon = request.json['horizon']
        series = np.array(request.json['series'])

        print('Running model selection...')
        CV_NAMES = {'cv', 'cross_validation', 'cross validation', 'cross-validation', ''}
        FAST_MODEL = 'autoarima'
        if model_name in CV_NAMES:
            model = cross_validation(series, horizon)
        elif model_name == 'fast':
            model = get_model(FAST_MODEL)
        else:
            model = get_model(model_name)

        print('Running forecasts...')
        predictions = forecast(series, horizon, model)

        print('Preparing response...')
        response_content = {
            'model': model.__class__.__name__,
            'predictions': predictions.tolist(),
        }
        response = response_content, 200, {'Content-Type': 'application/json'}

        print(f'Time elapsed: {(time.time() - start_time):.2f} seconds')

    except Exception as e:
        print(e)
        response_content = {}
        response = response_content, 500, {'Content-Type': 'application/json'}

    return response
