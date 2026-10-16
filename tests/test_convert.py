"""the csv converter has to give the loader exactly what the parquet re-upload gives it."""
import pandas as pd
import pyarrow.parquet as pq
import pytest

from client_brief_agent import config
from client_brief_agent.data import convert, load

pytestmark = pytest.mark.skipif(not any(config.RAW_DIR.glob("part.*.parquet")), reason="raw data not downloaded")


def test_csv_round_trip_matches_parquet(tmp_path):
    raw = pq.read_table(load.raw_files()[-1], columns=convert.columns()).slice(0, 3000).to_pandas()
    csv = tmp_path / "train_ver2.csv"
    raw.to_csv(csv, index=False)
    out = tmp_path / "parts"
    assert convert.convert(csv, out, chunk_rows=1000) == len(raw)

    parts = sorted(out.glob("part.*.parquet"), key=lambda p: int(p.stem.split(".")[1]))
    via_csv = pd.concat([load._clean_chunk(pd.read_parquet(p)) for p in parts], ignore_index=True)
    direct = load._clean_chunk(raw).reset_index(drop=True)
    pd.testing.assert_frame_equal(direct, via_csv, check_dtype=False)
