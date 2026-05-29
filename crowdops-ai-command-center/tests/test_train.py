"""Tests for model training, metrics output, and app-critical files."""

from __future__ import annotations

import json

from src.generate_data import save_dataset
from src.train import train_models


def test_training_creates_model_and_metrics(tmp_path, monkeypatch) -> None:
    """Train on a temp dataset and confirm artifacts + metrics are written."""
    import src.train as train_module

    # Redirect all output paths into the temporary directory.
    data_path = tmp_path / "crowd_ops.csv"
    model_path = tmp_path / "crowd_risk_model.joblib"
    metrics_path = tmp_path / "metrics.json"
    summary_path = tmp_path / "model_summary.md"

    monkeypatch.setattr(train_module, "MODEL_PATH", model_path)
    monkeypatch.setattr(train_module, "METRICS_PATH", metrics_path)
    monkeypatch.setattr(train_module, "MODEL_SUMMARY_PATH", summary_path)

    save_dataset(path=data_path, n_rows=2000, seed=21)
    result = train_models(data_path=data_path)

    assert model_path.exists(), "Model artifact should be created"
    assert metrics_path.exists(), "metrics.json should be created"
    assert summary_path.exists(), "model_summary.md should be created"

    assert result["best_model"] in {"LogisticRegression", "RandomForest"}

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    for model_metrics in metrics["all_models"].values():
        for key in ("accuracy", "precision_macro", "recall_macro", "f1_macro"):
            assert key in model_metrics
            assert 0.0 <= model_metrics[key] <= 1.0


def test_train_autogenerates_data_when_missing(tmp_path, monkeypatch) -> None:
    """If the dataset is absent, training should generate it automatically."""
    import src.train as train_module

    data_path = tmp_path / "crowd_ops.csv"
    monkeypatch.setattr(train_module, "MODEL_PATH", tmp_path / "m.joblib")
    monkeypatch.setattr(train_module, "METRICS_PATH", tmp_path / "metrics.json")
    monkeypatch.setattr(train_module, "MODEL_SUMMARY_PATH", tmp_path / "summary.md")

    assert not data_path.exists()
    train_models(data_path=data_path)
    assert data_path.exists(), "Training should auto-generate the dataset"


def test_app_critical_files_exist() -> None:
    """Sanity-check that the core project files are present in the repo."""
    from src import PROJECT_ROOT

    expected = [
        "app.py",
        "README.md",
        "requirements.txt",
        "pyproject.toml",
        "src/generate_data.py",
        "src/data.py",
        "src/features.py",
        "src/train.py",
        "src/evaluate.py",
        "src/predict.py",
        "src/monitor.py",
        "visuals/week3_visual_storytelling.md",
        "visuals/week4_multimedia_briefing.md",
        "visuals/executive_demo_talk_track.md",
        ".github/workflows/ci.yml",
    ]
    for rel in expected:
        assert (PROJECT_ROOT / rel).exists(), f"Missing critical file: {rel}"
