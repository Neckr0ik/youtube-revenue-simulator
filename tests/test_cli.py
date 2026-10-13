import main


def test_default_run_with_charts(tmp_path):
    assert main.main(["--out", str(tmp_path), "--csv"]) == 0
    assert (tmp_path / "02_niche_comparison.png").exists()
    assert (tmp_path / "monthly_results.csv").exists()


def test_flags_override_config(tmp_path, capsys):
    assert main.main(["--niche", "Gaming", "--months", "12", "--no-charts", "--out", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Channel niche : Gaming" in out and "12-month total revenue" in out
