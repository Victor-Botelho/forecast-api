# Building a Time Series Forecasting RESTful API with Flask and StatsForecast on Google Cloud Platform
In the ever-evolving landscape of data science, time series forecasting stands as a pivotal skill, applied across diverse sectors like finance and meteorology. Our project streamlines this process, offering a Python-based API that leverages Flask for its lightweight framework and StatsForecast for robust predictive modeling. This article will guide you through building and deploying this API, both locally and on Google Cloud Platform, demonstrating a practical approach to harnessing the power of forecasting in your data-driven endeavors.

To check out the full code of the project introduced in this article, visit the [GitHub repository](), where you will find a detailed README with instructions on how to build and deploy the API, locally or on Google Cloud Platform.

## Why Flask and StatsForecast
Flask was chosen for its simplicity and lightweight nature, making it ideal for small-scale applications and quick deployments. It's a microframework in Python, meaning it provides just the essentials to build a web application, ensuring a low learning curve and flexibility. This simplicity allows for faster development and easier maintenance of the API. Some more popular alternatives to Flask would be FastAPI and Django.

StatsForecast, on the other hand, is selected for its specialized focus on time series forecasting. It's built on top of StatsModels, a Python module renowned for its extensive range of algorithms and tools for statistical analysis. StatsForecast simplifies the forecasting process by offering an intuitive interface to apply various models, making it accessible even to those with limited statistical background. While it's possible to use a variety of other libraries or even custom solutions, the simplicity and effectiveness of StatsForecast make it an ideal choice for this project.

Together, Flask's streamlined web development capabilities and StatsForecast's comprehensive forecasting tools create a potent combination for building an efficient, user-friendly API for time series analysis. This choice ensures that the project remains focused on its core functionality - delivering accurate forecasts and maintaining a simple, intuitive interface - while being easy to set up, use, and extend.

## Setting Up the API
Getting a Flask API up and running is extremely easy. The following code snippet contains code relating to the following:
- Necessary imports;
- Initialization of the app;
- Creation of endpoints;
- Running the app.

```python
# app.py

# Importing the Flask class from the flask module
from flask import Flask

# Creating an instance of the Flask class
app = Flask(__name__)

# Creating an endpoint for the root route
@app.route('/')
def index():
    return 'Hello World!'

# Running the app
if __name__ == '__main__':
    app.run(debug=True)
```

Simply run the file from the command line using `python app.py` and you should see the following output:

```
 * Serving Flask app '0_app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 123-456-789
```

This means that the app is running on localhost (127.0.0.1), on port 5000! For now, it only has one endpoint (the root route, or "/"), which returns "Hello World!". To try it out, you can open your browser and go to http://127.0.0.1:5000, and you should see the message "Hello World!".

Quite simple, right? What if we wanted to do something more complex, like sending some data to the endpoint, having the API process it, and returning a response? For that, we'll need to:
- Import the `request` object from the `flask` module (TODO 1);
- Create a new endpoint using the POST method (TODO 2);
- Use the `request` object to get the data sent to the endpoint (TODO 3);
- Define and implement a custom function to process the data (TODO 4);

For a more simpler example, the payload (the data that you, the user, sends to the server) will include two "variables" (or parameters): `a` and `b`. The API will then return the product of these two variables.

```python
# app.py

# Importing the Flask class from the flask module
from flask import Flask

# TODO 1: Importing the request object from the flask module
from flask import request


# Creating an instance of the Flask class
app = Flask(__name__)

# Creating an endpoint for the root route
@app.route('/')
def index():
    return 'Hello World!'

# TODO 2: Creating a new endpoint
@app.route('/multiply', methods=['POST'])
def multiply():
    # TODO 3: Getting the data sent to the endpoint
    a = request.json.get('a')
    b = request.json.get('b')

    # TODO 4: Defining and implementing a custom function to process the data
    def multiply_numbers(a, b):
        return int(a) * int(b)

    product = multiply_numbers(a, b)

    response = {
        'product': product
    }

    return response

# Running the app
if __name__ == '__main__':
    app.run(debug=True)
```

To test this endpoint, simply using the browser won't work, since a payload is required. Choose the best command line tool for you, according to your OS, and run the appropriate command. Using more complete tools like Postman or Thunder Client is also an option.

```
# Linux / Mac
curl -X POST -H "Content-Type: application/json" -d '{"a": 2, "b": 3}' http://localhost:5000/multiply

# Windows (PowerShell)
Invoke-WebRequest -Method POST -ContentType "application/json" -Body '{"a": 2, "b": 3}' http://localhost:5000/multiply
```

This sends the JSON payload `{"a": 2, "b": 3}` to the endpoint `/multiply`, on the localhost, on port 5000. The response should also be a JSON payload `{"product": 6}`.

Now one important thing: did you notice the warning message when you ran the app? It says that the development server should not be used in production. There are many reasons for that, but the most important one is that the development server is not optimized for performance. Because of that, instead of simply running the app from Flask, we'll use a WSGI server, which is a production-ready server. For this example, we'll use Gunicorn, but there are many other options. To run the app using Gunicorn, instead of running `python app.py`, run `gunicorn app:app -p 5000`. The `-p 5000` part specifies the port that the app will run on. It is optional, but since our previous runs were on port 5000, it's better to keep it that way, otherwise, it would be deployed to the default port 8000. Other than that, the app should run the same way as before.

That's it! You now deployed your first Flask API! 🎉

## Implementing Forecasting with StatsForecast
Now that we have a working API, we can start implementing the forecasting functionality. This functionality could be called from some of our endpoints, for example! For this example, we'll two main forecasting functions.

The first one, `forecast`, will take a time series, a specified model, and a number of steps (or horizon) to forecast, and return the forecasted values.

The second one, `cross_validation`, will also take a time series and a horizon, but intead of fitting a single model, it will split the time series into a training and testing set, fit multiple models, forecast the testing set, find the best model given a metric (MSE, MAE, etc.), train the best model on the entire time series, and return the forecasted values.

The models chosen are AutoARIMA and WindowAverage, but you can choose any model from StatsForecast. Also, since StatsForecast can't process lists, we'll use NumPy arrays instead. Besides that, calling `predict` on models returns a dictionary with a single key named `mean` and as its value an array with the forecasted values. To make it easier to work with, we'll extract the array and return it directly.

```python
# forecast.py

import numpy as np
from statsforecast.models import AutoARIMA, WindowAverage


def forecast(model_name, series, horizon):
    # Initialize model based on model name
    if model_name == 'autoarima':
        model = AutoARIMA()
    elif model_name == 'windowaverage':
        model = WindowAverage(window_size=7)
    else:
        raise ValueError(f'Invalid model name: {model_name}')

    # Convert series to array
    series = np.array(series)

    # Fit model and predict
    model.fit(series)
    predictions = model.predict(horizon)
    predictions = np.array(predictions['mean'])

    return predictions


def cross_validation(series, horizon):
    # List of models to be evaluated
    models = {
        'autoarima': AutoARIMA(),
        'windowaverage': WindowAverage(window_size=7),
    }

    # Convert series to array and split into train and test based on horizon
    series = np.array(series)
    train = series[:len(series) - horizon]
    test = series[len(series) - horizon:]

    # Initialize dictionary to keep track of MSE for each model
    mse_dict = {}

    # Fit, predict and evaluate each model
    for model_name, model in models.items():
        # Fit model on train data
        model.fit(train)

        # Predict on horizon equivalent to test data
        test_predictions = model.predict(horizon)
        test_predictions = np.array(test_predictions['mean'])

        # Evaluate predictions based on mean squared error (MSE)
        mse = np.mean(np.square(test_predictions - test))

        # Store MSE for model
        mse_dict[model_name] = mse

    # Select the best model based on minimum MSE
    champion = min(mse_dict, key=lambda x: mse_dict[x])

    return champion


data = [54,23,65,87,34,56,23,12,76,94]
horizon = 3

arima_predictions = forecast(model_name='autoarima', series=data, horizon=horizon)
window_average_predictions = forecast(model_name='windowaverage', series=data, horizon=horizon)

best_model_name = cross_validation(series=data, horizon=3)
best_model_predictions = forecast(model_name=best_model_name, series=data, horizon=horizon)

print('PREDICTIONS')
print(f'ARIMA: {arima_predictions}')
print(f'Window Average: {window_average_predictions}')
print(f'Best model ({best_model_name}): {best_model_predictions}')
```

You can add as many models you want, from StatsForecast or not, and even change the metric used to evaluate the models!

Congratulations! You now have a working forecasting module that can be integrated into your API! 🎉

## Containerization with Docker
From the knowledge you acquired in the previous sections, you can now build a Flask API with forecasting capabilities. Suppose you do it, and try it out on you computer. But what happens when your friend also wants to try it out? You would have to send them the code, and they would have to install all the dependencies, and run it on their computer. Or what if you want to deploy it to a server on the cloud, and when you try to run your code there, it suddenly raises some never-before-seen error? To avoid all of that, we can use Docker!

Docker allows us to create containers, which are isolated environments that contain all the dependencies and configurations needed to run our code. This way, we can create a container with our API, and send it to our friend, who can run it on their computer without having to install anything. We can also deploy it to a server on the cloud, and it will run the same way as it did on our computer. This is called containerization, and it's one of the main reasons why Docker is so popular.

To create a container, you will need all the files that are necessary to run your code, including scripts and configuration files. Besides that, a Dockerfile is also required, which is a file that contains instructions on how to build the container. Then, from the Dockerfile, you can build and run the container.

For more information about Docker generally, check out the [official documentation](https://docs.docker.com/). Also check out the README of the [GitHub repository]() to see how a project like the one introduced in this article can be containerized.

## Deploying to Google Cloud Platform
Google Cloud Platform (GCP) is a suite of cloud computing services offered by Google. It allows you to build, test, and deploy applications on Google's highly-scalable and reliable infrastructure. It also offers free tiers for many of its services, and hundreds of dollars in credits for new users, making it a great option for deploying your applications. Keep in mind that there are many other cloud providers, like AWS and Azure, which will most probably offer similar enough services to deploy your application there as well.

To deploy our API to GCP, you will need to create a project, enable all the necessary services (APIs), such as Artifact Registry and Cloud Run, and then build and deploy the container to Cloud Run. For more information about how to do that, check out the README of the [GitHub repository]().

## Conclusion
In this article, you learned how to build a Flask API with forecasting capabilities, containerize it with Docker, and deploy it to Google Cloud Platform. This project can be used as a starting point for your own projects, and can be extended in many ways. For example, you can add more forecasting models, or even add a database to store the forecasts. You can also add authentication, so that only authorized users can access the API. The possibilities are endless!
