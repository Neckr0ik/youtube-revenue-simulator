from dataclasses import replace

import pytest

from main import MY_CHANNEL
from src.models import (MONETIZATION_MIN_WATCH_HOURS, NICHE_CPMS, YOUTUBE_REVENUE_SHARE, ChannelConfig,
                        compare_niches, monetization_milestone, simulate)


def test_rpm_formula():
    cfg = ChannelConfig(name="x", niche="Gaming")
    assert cfg.rpm == pytest.approx(NICHE_CPMS["Gaming"] * YOUTUBE_REVENUE_SHARE)
    assert replace(cfg, monetized_view_share=0.5).rpm == pytest.approx(cfg.rpm / 2)
    assert ChannelConfig(name="x", niche="Unknown").cpm == 8.0


def test_no_revenue_before_monetization():
    df = simulate(MY_CHANNEL)
    pre = df[~df["is_monetized"]]
    assert not pre.empty and (pre["ad_revenue"] == 0).all() and (pre["sponsorship_revenue"] == 0).all()


def test_ypp_uses_trailing_12_month_watch_hours():
    df = simulate(MY_CHANNEL)
    first = df[df["is_monetized"]].iloc[0]
    assert first["subscribers"] >= 1_000 and first["watch_hours_12m"] >= MONETIZATION_MIN_WATCH_HOURS
    # rolling window equals the sum of the last 12 monthly watch-hour values
    monthly = df["watch_hours_total"].diff().fillna(df["watch_hours_total"])
    assert df["watch_hours_12m"].iloc[-1] == pytest.approx(monthly.tail(12).sum(), rel=1e-3)


def test_never_monetizes_when_too_small():
    cfg = ChannelConfig(name="tiny", niche="Gaming", initial_subscribers=50, monthly_sub_growth_rate=0.0)
    df = simulate(cfg)
    assert not df["is_monetized"].any() and df["total_revenue"].sum() == 0
    assert monetization_milestone(df)["monetization_month"] is None


def test_cumulative_revenue_consistent():
    df = simulate(MY_CHANNEL)
    parts = df["ad_revenue"] + df["sponsorship_revenue"] + df["membership_revenue"]
    assert (abs(parts - df["total_revenue"]) < 0.02).all()
    assert df["cumulative_revenue"].iloc[-1] == pytest.approx(df["total_revenue"].sum(), abs=0.5)


def test_months_parameter():
    df = simulate(replace(MY_CHANNEL, months=12))
    assert len(df) == 12 and monetization_milestone(df)["months"] == 12


def test_niche_comparison_keeps_all_channel_settings():
    # Regression: comparison used to drop sponsorship/membership settings, so the
    # channel's own niche showed a different total than simulate() did.
    own = monetization_milestone(simulate(MY_CHANNEL))
    comp = compare_niches(list(NICHE_CPMS), MY_CHANNEL).set_index("niche")
    assert comp.loc[MY_CHANNEL.niche, "total_revenue_usd"] == pytest.approx(own["total_revenue"], abs=0.01)
    assert comp.loc[MY_CHANNEL.niche, "ad_revenue_usd"] == pytest.approx(own["total_ad_revenue"], abs=0.01)


def test_ad_revenue_scales_with_cpm_only():
    comp = compare_niches(["Finance & Business", "Gaming"], MY_CHANNEL).set_index("niche")
    ratio = comp.loc["Finance & Business", "ad_revenue_usd"] / comp.loc["Gaming", "ad_revenue_usd"]
    assert ratio == pytest.approx(NICHE_CPMS["Finance & Business"] / NICHE_CPMS["Gaming"], rel=1e-3)
    # same growth settings -> same subscribers in every niche
    assert comp["final_subscribers"].nunique() == 1


def test_watch_hours_use_view_retention():
    cfg = replace(MY_CHANNEL, months=3)
    full = simulate(replace(cfg, avg_view_retention=1.0))
    part = simulate(replace(cfg, avg_view_retention=0.4))
    assert (part["monthly_views"] == full["monthly_views"]).all()
    row = part.iloc[0]
    assert row["watch_hours_month"] == pytest.approx(
        row["monthly_views"] * cfg.avg_video_length_min * 0.4 / 60, abs=0.1)
    assert part["watch_hours_12m"].iloc[-1] == pytest.approx(full["watch_hours_12m"].iloc[-1] * 0.4, rel=1e-3)


def test_default_retention_is_documented_value():
    from src.models import DEFAULT_VIEW_RETENTION
    assert ChannelConfig(name="x", niche="Gaming").avg_view_retention == DEFAULT_VIEW_RETENTION == 0.40


def test_lower_retention_delays_monetization():
    early = monetization_milestone(simulate(replace(MY_CHANNEL, avg_view_retention=1.0)))["monetization_month"]
    late = monetization_milestone(simulate(MY_CHANNEL))["monetization_month"]
    assert early < late


@pytest.mark.parametrize("videos,deals", [(1, 1), (3, 1), (4, 1), (7, 1), (8, 2), (12, 3)])
def test_sponsorship_deals_rule(videos, deals):
    from src.models import sponsorship_deals
    assert sponsorship_deals(videos) == deals
    df = simulate(replace(MY_CHANNEL, videos_per_month=videos, months=36, avg_view_retention=1.0,
                          initial_subscribers=5_000))
    paid = df[df["sponsorship_revenue"] > 0]["sponsorship_revenue"]
    assert not paid.empty and (paid == MY_CHANNEL.sponsorship_fee_usd * deals).all()


def test_memberships_need_threshold_and_start_month():
    cfg = replace(MY_CHANNEL, initial_subscribers=40_000, monthly_sub_growth_rate=0.0, months=30)
    df = simulate(cfg)
    assert (df.loc[df["month"] < cfg.memberships_start_month, "membership_revenue"] == 0).all()
    expected = 40_000 * cfg.membership_rate * cfg.membership_price_usd
    assert df.loc[df["month"] >= cfg.memberships_start_month, "membership_revenue"].tolist() == \
        [pytest.approx(expected, abs=0.01)] * (cfg.months - cfg.memberships_start_month + 1)
    assert simulate(replace(cfg, initial_subscribers=29_000))["membership_revenue"].sum() == 0
