# Model Deployment Application

## Contents

  - [Introduction](#introduction)
  - [Requirements](#requirements)
  - [Model Pools](#model-pools)
  - [Output](#output)
  - [Development](#development)
    - [Model update](#model-update)
    - [Model deployment](#model-deployment)
    - [Daily routine](#daily-routine)
    - [Dependency management](#dependency-management)

## Introduction

This application is used for ML/DL model deployment by `FastAPI`, `Docker` and `Kubernetes`, which can be used for classification or regression problems in production. 

## Requirements

* [Poetry](https://python-poetry.org/)
* [Helm](https://helm.sh/)
* Kubernetes cluster
* Docker registry

## Model Pools

* Scikit-Learn models
* PyTorch models

## Output

* For classification: return predicted probabilities
* For regression: return predictions

## Development

### Model update

1. Train the ML/DL model and save it with the format `joblib` or `pickle`. 

   Note that all models need to be saved in the format inheriting from 
   `sklearn.base.BaseEstimator`. And for DL models from `PyTorch`, they can be
   converted to this format by the class `model_deployment_app.model.PyTorchEstimator`.
2. Update the model on local or cloud.
3. Update the model location in Helm files with the new directory.

### Model deployment

1. If there is no already existing helm chart, to create one in the folder `k8s_dev` by `helm`, i.e.
   ```
   helm create NEWMODEL
   ```
   Then remove the useless deployment files, 
      1. `k8s_dev/NEWMODEL/templates/hpa.yaml`
      2. `k8s_dev/NEWMODEL/templates/serviceaccount.yaml`
   Note that the service account should be already created for credentials.
2. Write or modify helm chart files.
   1. Set values in `values.yaml` for k8s deployment, including the sections, 
      * replicaCount: The number of pods for the model deployment.
      * image: The docker image information.
      * service: The service configuration used to generate endpoint APIs, note that the port needs to be selected carefully for different models.
      * ingress(if in used): The ingress configuration for prediction request URL. 
        The request URL for different models should be distinguished by `ingress.hosts.paths.path`, which means that it is possible to use one host URL for multi model deployments.
      * config: The configuration for model deployment implementation by `FastAPI`, having the following structure,
         ```
         config:
            # configuration
            logLevel: # logging level from uvicorn, e.g. error, info
            modelType: # pkl or joblib
            job: # regression or classification
            model: 
               # the model on GCS
               method: # LOCAL or GCS
               projectName: # GCP project name when the model is on GCS
               bucketName: # GCS bucket name when the model is on GCS
               blobDir: # # blob name when the model is on GCS
            inputSize: # the number of input dimension
         ```
   2. Update if necessary,
      * `k8s_dev/NEWMODEL/templates/deployment.yaml`
      * `k8s_dev/NEWMODEL/service.yaml`
      * `k8s_dev/NEWMODEL/templates/ingress.yaml` (if in used)
      * (`k8s_dev/NEWMODEL/templates/NOTES.txt` if necessary)
      
      according to the values in `k8s_dev/NEWMODEL/values.yaml`
   3. Create `k8s_dev/NEWMODEL/templates/configmap.yaml` to invoke the FastAPI
      configuration values from `k8s_dev/NEWMODEL/values.yaml`.
   4. Set up helm chart version and app version in `k8s_dev/NEWMODEL/Chart.yaml`,
      * chart version needs to be increased when there are changes in k8s deployment files.
      * app version is the version of latest or specified model deployment app.
3. Update or add the corresponding commandlines in `Makefile`.
4. Deploy the model by,
   ```
   make k8s-NEWMODEL-deploy
   ```
5. Remove the model deployment by,
   ```
   make k8s-NEWMODEL-undeploy
   ```

Note that, when we implement one model deployment for some test, it is better to keep related Kubernetes files in a branch, once we decide to go live with the new model, merge the branch to master and give a formal model deployment name.

### Daily routine

When the project needs to be updated, please follow the steps below,

1. Checkout to a new branch
   ```
   $ git checkout -b DATE-BRANCHNAME
   ```
2. Modify the code,
   * When needs to update workflow, modify the code in `/model_deployment_app/`.
   * When needs to update the k8s deployment, modify the deployment files in `/k8s_dev/MODELNAME/`.
3. Update the version,
   * When the update is in workflow or dependencies, 
     * Update the app version in `./pyproject.toml` by,
       ```
       $ poetry version *
       ```
     * Then update the app version in `./daily-prediction/Chart.yaml`, and the chart version in `./daily-prediction/Chart.yaml`.
   * When the update is only in k8s deployment files, update the chart version in `./daily-prediction/Chart.yaml`.
4. Run the test,
   ```
   $ make test
   ```
5. Make sure the code complies with black and other standards,
   ```
   $ make coding_standards
   ```
6. Add the changes and create a commit by `git`.
7. Push the branch to remote and create a PR.
8. Merge the PR after passing CI/CD and obtaining the approvals from others.
9. Checkout to master branch, then rebase on the new change,
   ```
   $ git fetch origin
   $ git rebase -i origin/main
   ```
10. Update the base docker image,
    ```
    $ make docker-base
    ```

### Dependency management

* Remove a package, 
  ```
  $ poetry remove PACKAGE
  ```
* Add a package, 
  ```
  $ poetry add PACKAGE
  ```