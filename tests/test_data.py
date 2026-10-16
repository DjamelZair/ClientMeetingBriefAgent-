"""loader tests on tiny hand built raw files, never the real data."""
import numpy as np
import pandas as pd
import pytest

from client_brief_agent import config
from client_brief_agent.data import load


def raw_rows(month, ids, **over):
    n = len(ids)
    df = pd.DataFrame({
        "fecha_dato": [month] * n, "ncodpers": np.array(ids, dtype=np.float32),
        "ind_empleado": ["N"] * n, "pais_residencia": ["ES"] * n, "sexo": ["V"] * n,
        "age": [" 35"] * n, "fecha_alta": ["2012-01-10"] * n, "ind_nuevo": [0.0] * n,
        "antiguedad": ["     40"] * n, "indrel": [1.0] * n, "ult_fec_cli_1t": [None] * n,
        "indrel_1mes": ["1"] * n, "tiprel_1mes": ["A"] * n, "indresi": ["S"] * n, "indext": ["N"] * n,
        "conyuemp": [None] * n, "canal_entrada": ["KHE"] * n, "indfall": ["N"] * n, "tipodom": [1.0] * n,
        "cod_prov": [28.0] * n, "nomprov": ["MADRID"] * n, "ind_actividad_cliente": [1.0] * n,
        "renta": [50000.0] * n, "segmento": ["02 - PARTICULARES"] * n,
    })
    for raw in config.PRODUCT_COLUMNS:
        df[raw] = 0.0
    for k, v in over.items():
        df[k] = v
    return df


def test_clean_chunk_handles_the_messy_fields():
    df = raw_rows("2016-05-28", [1, 2, 3, 4],
                  age=[" NA", "  164", " 2", " 40"],
                  antiguedad=["     NA", "-999999", "      3", "     12"],
                  segmento=["01 - TOP", "03 - UNIVERSITARIO", None, "02 - PARTICULARES"],
                  ind_empleado=[None, "A", "N", "N"], indrel=[1.0, 99.0, 1.0, np.nan],
                  indext=["S", "N", None, "N"], indfall=["N", "S", None, "N"],
                  ind_actividad_cliente=[np.nan, 1.0, 0.0, 1.0],
                  ind_tjcr_fin_ult1=[np.nan, 1.0, 0.0, 1.0])
    out = load._clean_chunk(df)
    assert out["month"].tolist() == ["2016-05"] * 4
    assert out["client_id"].dtype == np.int64
    assert np.isnan(out["age"].iloc[0]) and np.isnan(out["age"].iloc[1])
    assert out["age"].iloc[2] == 2 and out["age"].dtype == np.float32
    assert np.isnan(out["tenure_months"].iloc[0]) and np.isnan(out["tenure_months"].iloc[1])
    assert out["segment"].tolist()[:2] == ["top", "student"] and pd.isna(out["segment"].iloc[2])
    assert out["employee"].tolist() == [0, 1, 0, 0]
    assert out["primary"].tolist() == [1, 0, 1, 0]
    assert out["foreign_birth"].tolist() == [1, 0, 0, 0]
    assert out["deceased"].tolist() == [0, 1, 0, 0]
    assert out["active"].tolist() == [0, 1, 0, 1]
    assert out["credit_card"].tolist() == [0, 1, 0, 1] and out["credit_card"].dtype == np.int8


def test_bin_channels_keeps_top_and_missing():
    ch = pd.Series(["A"] * 20 + ["B"] * 3 + [None])
    binned = load._bin_channels(ch)
    assert binned.iloc[0] == "A" and pd.isna(binned.iloc[-1])


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    # two parts: april with clients 1,2,3 and may with 2,3,4 (client 1 left, 4 joined)
    raw_rows("2016-04-28", [1, 2, 3]).to_parquet(tmp_path / "part.0.parquet")
    raw_rows("2016-05-28", [2, 3, 4], ind_cco_fin_ult1=[1.0, 0.0, np.nan]).to_parquet(tmp_path / "part.1.parquet")
    monkeypatch.setattr(config, "RAW_DIR", tmp_path)
    return tmp_path


def test_sample_ids_come_from_last_month_and_are_deterministic(raw_dir):
    a = load.sample_client_ids(seed=1, n=2)
    b = load.sample_client_ids(seed=1, n=2)
    assert np.array_equal(a, b) and a.dtype == np.int64
    assert set(a) <= {2, 3, 4} and len(a) == 2


def test_load_panel_filters_to_ids_and_sorts(raw_dir):
    panel = load.load_panel(np.array([2, 4]))
    assert panel[["client_id", "month"]].values.tolist() == [[2, "2016-04"], [2, "2016-05"], [4, "2016-05"]]
    assert panel["current_account"].tolist() == [0, 1, 0]
    assert str(panel["segment"].dtype) == "category"
