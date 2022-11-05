import pandas as pd
import shap


def get_shap_explanations(X, model, prefix="SHAP_"):
    explainer = shap.Explainer(model)
    shap_values = explainer(X)
    return pd.DataFrame(data=shap_values.values, columns=[f"{prefix}{s}" for s in X.columns])
