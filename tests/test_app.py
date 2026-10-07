"""Release checks. Small fixtures are test inputs, never application data."""
import ast
from pathlib import Path
import unittest

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from analytics import (
    build_edges, country_metrics, country_year_table, annual_growth,
    pair_persistence, pca_analysis, cluster_analysis,
)

ROOT = Path(__file__).resolve().parents[1]


class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.projects = pd.DataFrame({"project_id": ["p1", "p2", "p3"],
                                      "start_year": [2020, 2022, 2022]})
        self.orgs = pd.DataFrame([
            ["p1", "a", "EC", "participant", 10.0],
            ["p1", "b", "EC", "participant", 20.0],
            ["p1", "c", "ES", "coordinator", 30.0],
            ["p2", "a", "EC", "coordinator", 40.0],
            ["p2", "c", "ES", "participant", 50.0],
            ["p3", "d", "DE", "participant", np.nan],
        ], columns=["project_id", "organisation_id", "country", "role", "ec_contribution"])

    def test_bilateral_projects_not_organisation_pairs(self):
        edges = build_edges(self.orgs, self.projects)
        self.assertEqual(len(edges), 2)
        pairs = pair_persistence(edges)
        self.assertEqual(pairs.iloc[0].shared_projects, 2)
        self.assertEqual(pairs.iloc[0].active_years, 2)
        self.assertEqual(pairs.iloc[0].first_year, 2020)
        self.assertEqual(pairs.iloc[0].last_year, 2022)

    def test_country_funding_coordination_and_isolated_country(self):
        cm, graph = country_metrics(self.orgs, self.projects, build_edges(self.orgs, self.projects))
        cm = cm.set_index("country")
        self.assertEqual(cm.loc["EC", "projects"], 2)
        self.assertEqual(cm.loc["EC", "participations"], 3)
        self.assertEqual(cm.loc["EC", "ec_funding"], 70)
        self.assertEqual(cm.loc["EC", "funding_per_project"], 35)
        self.assertAlmostEqual(cm.loc["EC", "coordination_share"], 100 / 3)
        self.assertEqual(cm.loc["EC", "diversification"], 0)
        self.assertTrue(pd.isna(cm.loc["DE", "ec_funding"]))
        self.assertNotIn("DE", graph.nodes)
        self.assertTrue(pca_analysis(cm.reset_index())[0].empty)
        self.assertTrue(cluster_analysis(cm.reset_index())[0].empty)

    def test_documented_annual_country_project_counts(self):
        annual = annual_growth(country_year_table(self.orgs, self.projects)).set_index("start_year")
        self.assertEqual(annual.loc[2020, "projects"], 2)
        self.assertEqual(annual.loc[2022, "projects"], 3)
        self.assertEqual(annual.loc[2020, "ec_funding"], 60)


class InterfaceTests(unittest.TestCase):
    def test_seed_startup_and_language_switch(self):
        app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=60)
        self.assertEqual(len(app.exception), 0, str(app.exception))
        self.assertEqual(app.session_state["projects"].shape[0], 5)
        self.assertTrue(app.session_state["orgs"].empty)
        self.assertEqual(len(app.tabs), 5)
        app.sidebar.radio[0].set_value("EN").run(timeout=60)
        self.assertEqual(len(app.exception), 0, str(app.exception))
        self.assertIn("Executive HMI", app.title[0].value)

    def test_public_version(self):
        tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8-sig"))
        values = {node.targets[0].id: node.value.value for node in tree.body
                  if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                  and isinstance(node.value, ast.Constant)}
        self.assertEqual(values["APP_VERSION"], "1.0.0")
        self.assertIn("APP_VERSION=1.0.0", (ROOT / "VERSION.txt").read_text())


if __name__ == "__main__":
    unittest.main()
