import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gridbalance"))

from prediction import predict_demand


class PredictDemandTests(unittest.TestCase):
    @patch("prediction.clean_series")
    @patch("prediction.load_data")
    @patch("prediction.forecast")
    @patch("prediction.train_models")
    def test_auto_uses_best_model_for_selected_region(
        self,
        train_models_mock,
        forecast_mock,
        load_data_mock,
        clean_series_mock,
    ):
        train_models_mock.return_value = {"best_model": "Random Forest"}
        forecast_mock.return_value = [
            {
                "timestamp": "2026-01-01 01:00",
                "hour": "01:00",
                "predicted_demand": 120.0,
            }
        ]
        clean_series_mock.return_value = (
            pd.DataFrame({"Demand_MW": [100.0, 110.0]}),
            {},
        )

        result = predict_demand(
            {"region": "AEP_hourly", "horizon": "6", "model": "Auto"}
        )

        train_models_mock.assert_called_once_with("AEP_hourly")
        forecast_mock.assert_called_once_with(
            "AEP_hourly", 6, "Random Forest"
        )
        load_data_mock.assert_called_once_with("AEP_hourly")
        self.assertEqual(result["model"], "Random Forest")
        self.assertEqual(result["horizon"], 6)


if __name__ == "__main__":
    unittest.main()
