import unittest
import numpy as np
import pandas as pd
from src.analysis import load_data, make_pipeline, metrics
from sklearn.linear_model import LogisticRegression

class AnalysisTests(unittest.TestCase):
    def test_missing_customers_preserved(self):
        df = load_data()
        self.assertEqual(len(df), 7043)
        self.assertEqual(df.TotalCharges.isna().sum(), 11)
        self.assertTrue(df.loc[df.TotalCharges.isna(), "tenure"].eq(0).all())

    def test_preprocessing_learns_only_training_and_unknown_categories(self):
        train = pd.DataFrame({"tenure": [1, 2, 3, 4],
            "MonthlyCharges": [10, 20, 30, 40], "TotalCharges": [10, np.nan, 30, 40],
            "Contract": ["monthly", "annual", "monthly", "annual"]})
        model = make_pipeline(train, LogisticRegression()).fit(train, [0, 1, 0, 1])
        imputer = model["prepare"].named_transformers_["numeric"]["impute"]
        self.assertEqual(imputer.statistics_[2], 30)
        unseen = train.iloc[:1].copy()
        unseen["Contract"] = "unseen"
        unseen["TotalCharges"] = 100000
        p = model.predict_proba(unseen)
        self.assertEqual(p.shape, (1, 2))
        self.assertEqual(imputer.statistics_[2], 30)

    def test_confusion_and_contact_accounting(self):
        m = metrics([0, 0, 1, 1], np.array([.1, .8, .2, .9]))
        self.assertEqual((m["tn"], m["fp"], m["fn"], m["tp"]), (1, 1, 1, 1))
        self.assertEqual(m["contacts"], m["fp"] + m["tp"])

if __name__ == "__main__":
    unittest.main()
