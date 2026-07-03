#!/usr/bin/env python3
"""
explainability.py
=================
Generates SHAP feature-importance plots for both trained XGBoost models.
Called via `python main.py --explain`.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_MODELS_DIR  = os.path.join(_ROOT, "models")
_PLOTS_DIR   = os.path.join(_ROOT, "plots")
_TRAINING_CSV = os.path.join(
    "/media/atharva/WD Gen3 SSD/Atomberg/xgboost_train",
    "cad_training_data.csv"
)


def _patch_model_json(model_path: str) -> str:
    """Rewrite base_score to float to avoid XGBoost 2.x parser bug."""
    with open(model_path, "r") as f:
        data = json.load(f)
    learner = data.get("learner", {})
    attrs   = learner.get("attributes", {})
    if "base_score" in attrs and not isinstance(attrs["base_score"], (int, float)):
        try:
            attrs["base_score"] = float(attrs["base_score"])
        except (ValueError, TypeError):
            attrs["base_score"] = 0.5
    patched_path = model_path.replace(".json", "_patched.json")
    with open(patched_path, "w") as f:
        json.dump(data, f)
    return patched_path


def run_shap_explanation():
    import xgboost as xgb

    os.makedirs(_PLOTS_DIR, exist_ok=True)
    df = pd.read_csv(_TRAINING_CSV)

    # ── Stage 2 Component Model ─────────────────────────────────────────────
    comp_features = ["face_count","aspect_ratio","vol_ratio","dia_ratio",
                     "thick_ratio","radial_dist","z_dist_to_stator",
                     "touches_top_bearing","touches_bot_bearing","is_wider_than_stator"]

    df_comp = df.dropna(subset=comp_features + ["label"])
    X_comp  = df_comp[comp_features]

    model_path = _patch_model_json(os.path.join(_MODELS_DIR, "xgboost_model.json"))
    xgb_comp   = xgb.XGBClassifier()
    xgb_comp.load_model(model_path)

    print("⚡ Computing SHAP values for Stage 2 Component Model (this may take a minute)...")
    explainer_comp  = shap.PermutationExplainer(xgb_comp.predict_proba, X_comp.sample(min(100, len(X_comp)), random_state=42))
    shap_vals_comp  = explainer_comp(X_comp.sample(min(200, len(X_comp)), random_state=42))

    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_vals_comp.values[..., 0], X_comp.sample(min(200, len(X_comp)), random_state=42),
                      plot_type="bar", show=False)
    plt.title("Stage 2 Component Model — SHAP Feature Importance", fontsize=13)
    plt.tight_layout()
    out = os.path.join(_PLOTS_DIR, "shap_component_model.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  Saved → {out}")

    # ── Stage 1 Anchor Model ────────────────────────────────────────────────
    anchor_features = ["face_count", "aspect_ratio"]
    df_anc = df.dropna(subset=anchor_features + ["label"])
    X_anc  = df_anc[anchor_features]

    model_path_anc = _patch_model_json(os.path.join(_MODELS_DIR, "xgb_anchors.json"))
    xgb_anc        = xgb.XGBClassifier()
    xgb_anc.load_model(model_path_anc)

    print("⚡ Computing SHAP values for Stage 1 Anchor Model...")
    explainer_anc = shap.PermutationExplainer(xgb_anc.predict_proba, X_anc.sample(min(100, len(X_anc)), random_state=42))
    shap_vals_anc = explainer_anc(X_anc.sample(min(200, len(X_anc)), random_state=42))

    plt.figure(figsize=(8, 4))
    shap.summary_plot(shap_vals_anc.values[..., 0], X_anc.sample(min(200, len(X_anc)), random_state=42),
                      plot_type="bar", show=False)
    plt.title("Stage 1 Anchor Model — SHAP Feature Importance", fontsize=13)
    plt.tight_layout()
    out_anc = os.path.join(_PLOTS_DIR, "shap_anchor_model.png")
    plt.savefig(out_anc, dpi=150)
    plt.close()
    print(f"  Saved → {out_anc}")

    print("\n SHAP explanation complete. Plots saved to:", _PLOTS_DIR)
