"""The main module to do the prediction work

The workflow is,
-> Load the configuration parameters
-> Load the trained model
-> Create FastAPI instance
-> Define path function for prediction
"""

import os
import pickle
from tempfile import TemporaryFile
from typing import Dict, List

import joblib
import uvicorn
import yaml
from fastapi import Body, FastAPI
from google.cloud import storage
from sklearn import base

from model_deployment_app.model import *  # noqa: F401, F403

# read configuration file
with open("/etc/config/config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

# read model
if CONFIG["model"]["method"] == "LOCAL":
    # The model saved on local
    WORKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL: base.BaseEstimator = joblib.load(
        os.path.join(WORKDIR, CONFIG["model"]["model_dir"])
    )
elif CONFIG["model"]["method"] == "GCS":
    # The model saved on Google Cloud Storage
    # Note that when deployment, the service account selected in Kubernetes
    # files should be used for credentials
    storage_client = storage.Client(
        project=CONFIG["model"]["project_name"],
    )
    bucket = storage_client.get_bucket(CONFIG["model"]["bucket_name"])
    blob = bucket.blob(CONFIG["model"]["blob_dir"])
    with TemporaryFile() as temp_file:
        blob.download_to_file(temp_file)
        temp_file.seek(0)
        if CONFIG["model_type"] == "pkl":
            MODEL: base.BaseEstimator = pickle.load(temp_file)
        elif CONFIG["model_type"] == "joblib":
            MODEL: base.BaseEstimator = joblib.load(temp_file)
        else:
            raise NameError(f"Wrong model type name: {CONFIG['model_type']}")
else:
    raise NameError(f"Wrong method name: {CONFIG['model']['method']}")

# define prediction app
pred_app = FastAPI()


@pred_app.post(CONFIG["path"])
async def predict(
    feature_matrix: List[List[float]] = Body(..., title="The feature matrix")
) -> Dict[str, str]:
    """Predicts the optimal start price by a trained model

    Parameters
    ----------
    feature_matrix: np.ndarray
        the 1*n raw feature matrix

    Returns
    -------
    dict
        the prediction result
    """
    # feature matrix validation
    assert (
        len(feature_matrix[0]) == CONFIG["input_size"]
    ), f"{len(feature_matrix[0])} != {CONFIG['input_size']}"

    # prediction
    if CONFIG["job"] == "classification":
        # predict probabilities
        pred = MODEL.predict_proba(feature_matrix)[:, -1].tolist()
    elif CONFIG["job"] == "regression":
        # predict regressive values
        pred = MODEL.predict(feature_matrix).tolist()
    else:
        raise NameError("Unknown job name or model type.")
    return {"predictions": str(pred)}


if __name__ == "__main__":
    uvicorn.run(
        pred_app, host="0.0.0.0", port=CONFIG["port"], log_level=CONFIG["log_level"]
    )
