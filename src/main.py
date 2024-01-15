import time
import logging

from flask import Flask, request, Response, g
import numpy as np

from src.forecast import forecast, cross_validation, get_model


app = Flask(__name__)

# Setup logging
logging.basicConfig(filename="./logs/access.log", level=logging.INFO)

@app.route('/', methods=['GET'])
def index():
    return 'Hello, World!'


@app.before_request
def before_request():
    g.start_time = time.time()


@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        end_time = time.time()
        elapsed_time = end_time - g.start_time

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        method = request.method
        endpoint = request.endpoint

        log_message = (
            f"Timestamp: {timestamp} - Method: {method} - Endpoint: {endpoint} - "
            f"Duration (s) {elapsed_time:.6f}"
        )

        if method == 'POST' and endpoint == 'forecast_':
            try:
                data_length = len(request.json.get('series', []))
                horizon = request.json.get('horizon', 'Not provided')
                request_model = request.json.get('model', 'Not provided')
                response_model = response.json.get('model', 'Not provided')
                log_message += (
                    f" - Data Length: {data_length} - Horizon: {horizon} - Model: {request_model} -> {response_model}"
                )
            except Exception as e:
                log_message += f" - Error parsing JSON: {str(e)}"

        app.logger.info(log_message)

    return response

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
