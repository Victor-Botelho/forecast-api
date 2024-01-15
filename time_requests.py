import aiohttp
import json
import asyncio
import time
import numpy as np
import pandas as pd


# Generate some data of the form y = a + x + noise, of length n
def generate_linear(n: int, a: float, std: float = 1):
    x = np.arange(n)
    noise = np.random.normal(0, std, n)
    y = a + x + noise
    return x, y


# Generate some data of the form y = a + x**2 + noise, of length n
def generate_exponential(n: int, a: float, std: float = 1):
    x = np.arange(n)
    noise = np.random.normal(0, std, n)
    y = a + x**2 + noise
    return x, y


# Generate some data of the form y = a + sin(x) + noise, of length n
def generate_sin(n: int, a: float, std: float = 1):
    FREQUENCY = 0.2
    x = np.arange(n)
    noise = np.random.normal(0, std, n)
    y = a + np.sin(FREQUENCY * x) + noise
    return x, y


# Generate some data of the form y = a + log(x) + noise, of length n
def generate_log(n: int, a: float, std: float = 1):
    x = np.arange(n)
    x = np.where(x == 0, 1, x)  # Replace all 0s in x with 1s
    noise = np.random.normal(0, std, n)
    y = a + np.log(x) + noise
    return x, y


async def make_post_request(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.text(), response.status


async def run_requests(
    data_generator: callable,
    data_params: dict,
    server_url: str,
    horizon: int,
    n_requests: int,
    sleep: float = 0,
):
    """

    Args:
        data_generator (callable): A function that generates data of the form
            (x, y).
        data_params (dict) : A dictionary of parameters to be passed to the
            data_generator function.
        server_url (str): The URL of the server to which to make the POST
            request.
        horizon (int) : The forecast horizon.
        n_requests (int) : The number of requests to make.
        sleep (float, optional): The number of seconds to sleep between each
            request. Defaults to 0.

    Returns:
        list: A list of dictionaries containing the results of each request.
    """
    results = []

    for i in range(n_requests):
        start_time = time.time()

        # Generate data using the specified data generator and parameters
        x, y = data_generator(**data_params)

        # Prepare the payload for the POST request
        payload = {
            'model': 'cv',
            'horizon': horizon,
            'series': y.round(2).tolist()
        }

        # Make the asynchronous POST request
        print(f'Request {i+1}/{n_requests}...')
        response_text, status_code = await make_post_request(server_url, payload)
        elapsed_time = time.time() - start_time

        result = {
            'status_code': status_code,
            'elapsed_time': elapsed_time,
            'parameters': data_params,
        }

        results.append(result)
        time.sleep(sleep)

    return results


# Example usage:
data_params = {'n': 100, 'a': 1, 'std': 0.1}
# server_url = 'https://forecast-api-fm46betxta-uc.a.run.app/forecast'
server_url = 'http://localhost:8000/forecast'
horizon = 10
n_requests = 100
data_generator = generate_sin


print('Starting requests...')
results = asyncio.run(run_requests(
    data_generator, data_params, server_url, horizon, n_requests, sleep=0))
print('Done!')
df_results = pd.DataFrame(results).drop(columns=['parameters'])
print(df_results)
df_results.to_csv('results.csv', index=False)
