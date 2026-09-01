"""
Core, transparent (non-AI) logic for CineMatch:
loading data, ranking titles, and (in later phases) grounding checks and feedback.
"""
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_members() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "members.csv"))


def load_catalog() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "catalog.csv"))


def load_availability() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "availability.csv"))


def load_policy_text() -> str:
    with open(os.path.join(DATA_DIR, "policy.txt")) as f:
        return f.read()
