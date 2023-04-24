# Model Deployment Application

## Contents

  - [Introduction](#introduction)
  - [Requirements](#requirements)
  - [Method](#method)
  - [Output](#output)
  - [Usage](#usage)
    - [Update test image](#update-test-image)
    - [Update base image](#update-base-image)
    - [Model deployment](#model-deployment)

## Introduction

This application is used for ML/DL model deployment in k8s cluster, which can be used for classification or regression problems in production. 

## Requirements

* Cloud based k8s cluster
* Cloud based storage
* Cloud based container registry

## Method

Use `FastAPI` to deploy model in k8s pod, which will give us an api that can be requested from internal environment. 

## Output

* For classification: return predicted probabilities
* For regression: return predictions

## Usage

### Update test image

Once the dependencies are updated in the app, the test image needs to be updated by,
```
make docker-ci-test
```

### Update base image

1. Checkout to the new branch and make the change.
2. Update the app version in `pyproject.toml` by the commandline
   ```
   poetry version NAME
   ```
   where can be refered from here, https://python-poetry.org/docs/cli/#version.
3. Push the branch to remote and create the MR.
4. Merge the MR and rebase on the new change.
5. Push the new base image to GCR, by the commandline
   ```
   make docker-base
   ```

### Model deployment

1. Train the ML model and save it with `joblib` or `pickle`. 
   
   Note that all models need to be saved in the format inheriting from 
   `sklearn.base.BaseEstimator`. And for DL models from `PyTorch`, they can be
   converted to this model format by the class `model_deployment_app.model.PyTorchEstimator`.
2. Upload model to the cloud based storage.
3. Create new helm chart in the folder `k8s_dev` by `helm`, e.g.
   ```
   helm create NEWMODEL
   ```
4. Remove the useless deployment files, 
   1. `k8s_dev/NEWMODEL/templates/hpa.yaml`
   2. `k8s_dev/NEWMODEL/templates/serviceaccount.yaml`
5. Overwrite helm chart files.
   1. Set values in `values.yaml` for k8s deployment, including the sections, 
      * replicaCount: The number of pods for the model deployment.
      * image: The image location.
      * service: The service configuration, note that the port needs to be selected carefully.
      * ingress: The ingress configuration for request url. 
         1. The request url of different models for different projects should be distinguished by `ingress.hosts.paths.path`.
      * config: The configuration for model deployment implementation by `FastAPI`, having the following structure,
         ```
         config:
            # configuration
            modelType: # pkl or joblib
            job: # regression or classification
            model: 
               # the model on GCS
               method: GCS
               projectName: PROJECT
               bucketName: BUCKET
               blobDir: BLOB
            inputSize: INPUT_DIM
         ```
   2. Update 
      * `k8s_dev/NEWMODEL/templates/deployment.yaml`
      * `k8s_dev/NEWMODEL/service.yaml`
      * `k8s_dev/NEWMODEL/templates/ingress.yaml`
      * (`k8s_dev/NEWMODEL/templates/NOTES.txt` if necessary)
      
      according to the values in `k8s_dev/NEWMODEL/values.yaml`
   3. Create `k8s_dev/NEWMODEL/templates/configmap.yaml` to invoke the FastAPI
      configuration values.
   4. Set up helm chart version and app version in `k8s_dev/NEWMODEL/Chart.yaml`,
      * chart version needs to be increased when there are changes in k8s deployment files.
      * app version is the version of latest or specified model deployment app.
6. Update or add the corresponding commandlines in `Makefile`.
7. Deploy the model by,
   ```
   make k8s-deploy
   ```
8. Remove the model deployment by,
   ```
   make k8s-undeploy
   ```

Note that, 
* When we implement one model deployment for some test, it is better to keep 
  related k8s files in a branch, once we decide to go live with the new model,
  merge the branch to master and give a formal model deployment name.
* DL models from `PyTorch` are also available with this model deployment tool, but the models need to be pickled in the format, `model_deployment_app.model.PyTorchEstimator`.
