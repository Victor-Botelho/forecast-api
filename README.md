# forecast-api
This project is a simple API to make forecasts on time series data. It is built using Python, with some focus on the libraries Flask and StatsForecast. A tutorial is included on how to also deploy the application to Google Cloud Platform (GCP) for free, although it is also possible to run it locally.

From the contents of this repository, the reader my learn different things, such as:
- How to build a simple API using Flask;
- How to make forecasts using StatsForecast;
- How to build a Docker image and run a container locally;
- How to deploy a Docker image to GCP using Artifact Registry and Cloud Run.

For a more concise version of this project, see the branch [concise]. For a more complete version, see the branch [main].

## Flask
Flask is a Python microframework for web development. It is lightweight and easy to use, and it is a good choice for small applications. Therefore, it is used here to build the API. For more information and simple demonstrations, refer to the [official documentation](https://flask.palletsprojects.com/en/3.0.x/quickstart/).

To deploy the application locally, there are 3 main options:
1) Using the Flask development server: simply run `flask -app src.main run --debug -p 8000` from the project root directory. This is the simplest option, but it is not recommended for production, as it is not optimized for performance and security;
2) Using a WSGI server: this is the recommended option for production. There are many WSGI servers available, such as Gunicorn, uWSGI, and Waitress. Here, Gunicorn is used. To run the application using Gunicorn, simply run `gunicorn --config gunicorn_config.py src.main:app`.
3) Using Docker: this is also a good option for production, as it is easy to deploy and manage. To run the application using Docker, simply build the image and run a container, as described in the [Docker](#docker) section.
4) Using Google Cloud Platform (GCP): this is also a good option for production, as it is easy to deploy and manage. To run the application using GCP, simply build the image and deploy it to Cloud Run, as described in the [GCP](#google-cloud-platform-gcp) section.

To test the application, 2 endpoints are available: `/` and `/forecast`. The first one is a simple endpoint that returns the message "Hello, world!". The second one is the main endpoint, which makes a forecast on the time series data sent by the user. The data must be sent as a JSON object, with the following format:

```json
// Request body
{
    "model": "cross validation",
    "horizon": 2,
    "series": [34, 54, 23, 45, 67, 87, 34, 64, 12, 65, 23, 65, 12]
}

// Response body
{
    "model": "AutoARIMA",
    "predictions": [
        52.00152848651413,
        17.060870982272373
    ]
}
```

The current version supports specifying the model to be used, or allowing the program to choose the best model. The supported models can be found in the [src/forecast.py](src/forecast.py) file, in the `MODELS` list. The supported models are:
- `cross validation`: uses cross validation to select the best model. Other accepted values are `cv`, `cross_validation`, `cross-validation` or `` (an empty string);
- `fast`: for users that do not wish to specify a model and do not desire to wait for the cross validation to finish. This is simply translated to AutoARIMA, which although is not the fastest model, it is faster than the cross validation, and usually performs well;
- `AutoARIMA`;
- `SimpleExponentialSmoothing`;
- `Theta`;
- `AutoETS`;
- `AutoCES`;
- `AutoTheta`;
- `Naive`;
- `SeasonalNaive`;
- `WindowAverage`;
- `ADIDA`.

To test the API locally using cURL, run the following command:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"model": "cross validation", "horizon": 2, "series": [34, 54, 23, 45, 67, 87, 34, 64, 12, 65, 23, 65, 12]}' http://localhost:8000/forecast
```

## StatsForecast
StatsForecast is a Python library for time series forecasting. It is built on top of the StatsModels library, and it provides a simple interface to make forecasts using different models. For more information, refer to the [official documentation](https://nixtlaverse.nixtla.io/statsforecast/index.html).

In this project, the logic implemented goes as follows:
1) The user sends a request to the API with the time series data and the desired forecast horizon;
2) From the time series data, the API extracts the last `horizon` values, which will be used as the test set. The remaining values are used as the training set;
3) Many StatsForecast models are trained using the training set, and the best one is selected based on the MSE metric on the test set;
4) The best model (or algorithm) is then trained again using the entire series, and a forecast is made for the next `horizon` values;
5) The forecasted values, along with the chosen model, are returned to the user.

It is also possible for the user to specify the model to be used, instead of letting the API choose the best one. In this case, the API will simply train the chosen model using the entire series and make a forecast for the next `horizon` values, which will most likel result in faster execution time.

## Docker
Build the image by running the following command from the project root directory:

```bash
docker build -t forecast-api .
```

Run the Docker container using the command below:

```bash
docker run -p 8000:8000 -d --name forecast-api-container forecast-api
```

If there is already a container running with that name, delete it first:

```bash
docker rm forecast-api-container
```

To delete an image by its ID:

```bash
docker rmi <image_id>
```

To access the container's shell:

```bash
docker exec -it forecast-api-container /bin/bash
```

## Google Cloud Platform (GCP)
NOTE: If you are already properly authenticated, you can skip to the [Permissions](#permissions) section.

To deploy the application to GCP, you must have a GCP account and a project. If you don't have one, you can create a free account [here](https://cloud.google.com/free). After creating the account, you can create a project by following the instructions [here](https://cloud.google.com/resource-manager/docs/creating-managing-projects). Finally, install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) to interact with GCP from your own machine, either through the command line or through the Python APIs.

### Authentication
To authenticate you GCP account locally, simply run the command `gcloud auth login` and follow the instructions. For more information, simply access the official [documentation](https://cloud.google.com/sdk/gcloud/reference/auth/login).

Make sure the desired GCP account and project are selected by running `gcloud config get-value account` and `gcloud config get-value project` respectively. If they are not, set them by running `gcloud config set account <account>` and `gcloud config set project <project-id>` respectively.

If you get a warning message like this after setting the project, you may have specified the project name instead of its ID:

```
WARNING: You do not appear to have access to project [<project>] or it does not exist.
Are you sure you wish to set property [core/project] to <project>?

Do you want to continue (Y/n)?
```

If that is the case, then run the command again, this time specifying the project ID, and then check if the project was authenticated correctly by running `gcloud projects list` and seeing if it is listed.

### Permissions
To deploy the application, 2 GCP services are required: (i) Artifact Registry, to store the Docker image, and (ii) Cloud Run, to deploy the application. So firstly, check if these services are enabled by running the following commands:

```bash
gcloud services list --enabled | grep artifactregistry --ignore-case
gcloud services list --enabled | grep run --ignore-case
```

They should return something like this:

```bash
# Artifact Registry
artifactregistry.googleapis.com  Artifact Registry API

# Cloud Run
run.googleapis.com               Serverless Integrations API
```

If you do not get any output, then enable the services by running the following commands and check again:

```bash
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com
```

You can also use your browser to enable the services, or check if they are enabled. Simply access the Google Cloud Console, search for each service, and enable them if they are not already enabled.

### Docker image
Now it is time to build the Docker image and push it to Artifact Registry. To do so, run the following commands. Note that you may choose to use a different image name and tag. In this tutorial, the image name is `forecast-api` and the tag is `latest`. Also, for consistency, the container is always named `forecast-api-container`. The repository name is `forecast-api-repository` and the region used is `us-central1`. You may choose different names and regions, but make sure to change the commands accordingly. You may also refer to the [official documentation](https://cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling) for more information.

First, a Docker repository is needed. To see all existing repositories, run `gcloud artifacts repositories list`. If you already have a proper repository you wish to use, then skip this step. Otherwise, create a new repository by running the following command. Then check if it was created correctly, either from the terminal or from the Google Cloud Console.

```bash
gcloud artifacts repositories create forecast-api-repo --repository-format=docker --location=us-central1 --description="Forecast API repository"
```

Now, it is necessary to authenticate to the desired region:

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

Then, build the Docker image locally:

```bash
docker build -t forecast-api .
```

Tag the image with the repository name and region. Remember to change the following command to reference your own project ID:

```bash
docker tag forecast-api us-central1-docker.pkg.dev/<project-id>/forecast-api-repo/forecast-api:latest
```

Finally, push the image to the remote repository:

```bash
docker push us-central1-docker.pkg.dev/<project-id>/forecast-api-repo/forecast-api
```

### Cloud Run
Now that the Docker image is ready, it is time to deploy the application to Cloud Run. There are many ways to do that, as described in the [official documentation](https://cloud.google.com/run/docs/deploying). Here, the command line interface is used. To do so, replicate the following commands, remembering to change the project ID, region, image name, etc accordingly. Since the flag `--allow-unauthenticated` is used, the application will be publicly available. This means that anyone with the deployed service URL will be able to call it. So be careful when using or publishing it, as it may incur in costs. Since Cloud Run has a free tier, it should be fine for few requests.

```bash
gcloud run deploy forecast-api --image us-central1-docker.pkg.dev/<project-id>/forecast-api-repo/forecast-api --allow-unauthenticated --region us-central1 --port 8000 --memory 1500Mi --cpu 1
```

## Troubleshooting
## Response time
Performing some manual tests, it was observed that the response time of the API using cross-validation, 100 samples and 10 forecast horizon was about ~1 second. However, initial requests may take up to a minute to complete. This behaviour was observed when running the application locally and when running it on Cloud Run. This might be related to some initial procesing when the worker is started, but it is not clear why it happens. If you have any idea, please let me know. Feel free to open an issue or a pull request.

### Google Cloud SDK (gcloud)
If you encounter any issues with some gcloud components, try updating them with `gcloud components update`. However, if you - like me - installed the SDK through a package manager, as the official documentation recommends for Ubuntu users, you might get the following error when trying to update the components:

```
ERROR: (gcloud.components.update)
You cannot perform this action because the Google Cloud CLI component manager
is disabled for this installation.
```

If that is the case, then uninstall the SDK and install it again from the Linux archive files, as described in this [separate documentation page](https://cloud.google.com/knowledge/kb/cloud-sdk-shows-error-sdk-component-manager-is-disabled-000004810) or in the [original documentation page](https://cloud.google.com/sdk/docs/install-sdk#linux) (note the "Linux archive" tab). After doing so, remember to use a new terminal window to run the commands, as the changes will NOT be applied to previously opened terminals.

## Possible improvements
If you wish to contribute to this project, or deepen your knowledge on the topics covered here, you may try to implement some of the following improvements:
- Add more models to the API: this could be done using standard models from StatsModels, or even using custom models from other libraries, such as Prophet, LightGBM, TensorFlow, etc;
- Implement more endpoints to the API: for example, an endpoint to return run batch forecasts, instead of just one forecast at a time;
- Introduce tests: unit tests, integration tests, etc;
- Create a CI/CD pipeline: for example, using GitHub Actions to automatically build and deploy the application to GCP;
- Connect to a database: for example, using Cloud SQL to store the time series data and the forecasts;
- Require authentication: for example, using Cloud IAM to authenticate users and restrict access to the API;
- Add a front-end: for example, using React to create a simple web application to interact with the API;
- Refactor the back-end: for example, using FastAPI instead of Flask, or using a different language, such as Go or Rust;
- Document the API: for example, using OpenAPI.
