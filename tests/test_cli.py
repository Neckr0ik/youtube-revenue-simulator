import main


def test_default_run_with_charts(tmp_path):
    assert main.main(["--out", str(tmp_path), "--csv"]) == 0
    assert (tmp_path / "02_niche_comparison.png").exists()
    assert (tmp_path / "monthly_results.csv").exists()


def test_flags_override_config(tmp_path, capsys):
    assert main.main(["--niche", "Gaming", "--months", "12", "--no-charts", "--out", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Channel niche : Gaming" in out and "12-month total revenue" in out


import pytest


@pytest.mark.parametrize("args", [
    ["--monetized-share", "1.5"], ["--monetized-share", "-0.1"], ["--months", "0"],
    ["--retention", "0"], ["--retention", "1.2"], ["--videos", "0"], ["--subs", "-5"],
    ["--growth", "-1"], ["--length", "0"], ["--months", "abc"],
])
def test_out_of_range_flags_are_rejected(args, tmp_path, capsys):
    with pytest.raises(SystemExit) as e:
        main.main(args + ["--no-charts", "--out", str(tmp_path)])
    assert e.value.code == 2
    assert "error:" in capsys.readouterr().err


def test_retention_flag(tmp_path, capsys):
    assert main.main(["--retention", "1.0", "--no-charts", "--out", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "100% watched on average" in out and "YPP monetization       Month 11" in out
