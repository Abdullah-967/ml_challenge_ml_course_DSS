"""Editable experiment file for the auto-mae skill.

Copy this to the project root as `experiment.py` and edit freely. The harness
(`.claude/skills/auto-mae/eval.py`) and submission builder
(`.claude/skills/auto-mae/predict.py`) both import the function below.

Required interface:
    fit_predict(train_records: list[dict], test_records: list[dict]) -> list[float]

`train_records` are dicts with all 47 columns plus `property_value`.
`test_records` are dicts with the same columns minus `property_value`.
Return predictions in the same order as `test_records`.

Starter implementation: reproduces baseline/baseline.py (Ridge on 3 features
with MinMaxScaler) so the very first eval run lands at the baseline number.
"""

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import MinMaxScaler

FEATURE_KEYS = ["built_area", "num_lots", "num_commercial"]
TARGET_KEY = "property_value"


def to_matrix(records, keys):
    return np.array(
        [[float(r.get(k, 0.0) or 0.0) for k in keys] for r in records],
        dtype=np.float64,
    )


def fit_predict(train_records, test_records):
    X_train = to_matrix(train_records, FEATURE_KEYS)
    y_train = np.array(
        [float(r[TARGET_KEY]) for r in train_records], dtype=np.float64
    )
    X_test = to_matrix(test_records, FEATURE_KEYS)

    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = Ridge(alpha=10.0)
    model.fit(X_train, y_train)
    return model.predict(X_test).tolist()
