# FastAPI Model Deployment

## Contents

- [Introduction](#introduction)
- [Codebase](#codebase)

## Introduction

In the machine learning engineering part for a data science project, the most important work is to deploy the trained ML or DL models. Then in production or in real-time prediction, the predictions can be requested from the deployed models via endpoints or something else. There are 2 reasons to deploy trained models, 

* In production, with the larger training set, the trained model size can be larger accordingly(e.g. Tree-based models), which could use a lot of memory resource and influence the system running if it is ingrated with the main system.
* For stable development, it is better to keep systems/environments independent and clean, for model deployment environments and other systems.

Note that there are already different cloud-based pipelines that can help us deploy models, e.g. Vertex AI on GCP, but there are still limitations, 

* For classification problems, the pipelines there can only output a final predicted class, not the probability(except TensorFlow classification models). Man can also define some customized models to output probabilities but more services or machines need to bought there, which could lead to more cost. 
* For those cloud-based model deployment pipelines, the model structure objects are limited, normally only for scikit-learn model, xgboost model and TensorFlow model, which could limit the work possibilities in production.

Thus, in production the trained model needs to be deployed, and better in a customized way.

In this repo, a model deployment method by `FastAPI`, working with docker container and k8s,  is introduced, which can give us an endpoint url where the prediction can be requested. Since this method has to work with k8s, this can be depolyed on any cloud platforms that have cloud k8s clusters, or locally with `minikube`.

This repo is compatible with all customized or predefined models, including PyTorch models. And currently this repo is designed only for GCP, since the similarity between different cloud platforms, this method can be modified easily for other platforms.

## Codebase

The model depolyment process can be referred from the codebase in `model_deployment_app` by `FastAPI`, 

* `model_deployment_app.main`: This is the main process about how to depolyment models by `FastAPI`.
* `model_deployment_app.model`: This module is used for converting PyTorch models into scikit-learn-based models, which can be deployed then.

## Usage

Since this repo is designed for GCP, here is the workflow example when using GCP,

1. Train a ML or DL model.
2. Pickle the model and upload to GCS.
3. Local test by the commandline, 
   ```
   python model_deployment_app/main.py
   ```
4. Build the base image and push to the cloud container registry by the commandline, 
   ```
   make docker-base
   ```
   Please note that to replace the `CONTAINER_REGISTRY` with your container registry url. If the functionalities in codebase are modified, please update the app version by,
   ```
   poetry version ...
   ```
   which can be referred from here, https://python-poetry.org/docs/cli/#version.