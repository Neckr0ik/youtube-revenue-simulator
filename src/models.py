"""
YouTube Channel Revenue Simulator
Models growth, ad revenue, and monetization milestones using
publicly documented YouTube Partner Program economics.

Key formulas:
  RPM (per 1,000 views) = CPM * 0.55 * monetized_view_share
      (creators keep 55% of long-form ad revenue; only some views show ads)
  Ad revenue           = (views / 1000) * RPM
  Watch time (hours)   = views * avg_video_length_min * avg_view_retention / 60
                         (average view duration = video length x share of it watched)
  YPP eligibility      = >= 1,000 subscribers AND >= 4,000 public watch hours
                         in the trailing 12 months (the Shorts-views path is not modelled)

All CPMs and rates are illustrative assumptions, not YouTube data.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace

import pandas as pd

# Illustrative mid-range CPM assumptions by niche (USD). Real CPMs vary widely by
# country, season and audience; edit these to match your own analytics.
NICHE_CPMS = {
    "Finance & Business":   22.0,
    "Technology":           12.0,
    "Education":             9.0,
    "Digital Marketing":    17.0,
    "Entertainment":         4.5,
    "Gaming":                3.5,
    "Lifestyle & Travel":    5.0,
    "Health & Fitness":      8.0,
}
DEFAULT_CPM = 8.0

YOUTUBE_REVENUE_SHARE = 0.55          # creator keeps 55% of long-form ad revenue
MONETIZATION_MIN_SUBS = 1_000
MONETIZATION_MIN_WATCH_HOURS = 4_000  # trailing 12 months
DEFAULT_VIEW_RETENTION = 0.40         # assumption: viewers watch 40% of a video on average


@dataclass
class ChannelConfig:
    name: str
    niche: str
    initial_subscribers: int = 500
    monthly_sub_growth_rate: float = 0.08
    videos_per_month: int = 8
    avg_video_length_min: float = 12.0    # average video length (minutes)
    avg_view_retention: float = DEFAULT_VIEW_RETENTION  # share of each video watched on average
    views_per_sub_ratio: float = 0.18     # avg share of subs who watch each video
    organic_view_multiplier: float = 1.3  # search/suggested views on top of sub views
    months: int = 36
    monetized_view_share: float = 1.0     # share of views that carry ads (1.0 = optimistic)
    # Sponsorships (assumption): from sponsorship_start_month, and only once the channel is in
    # YPP, it books a flat fee per deal; deals per month = videos_per_month // 4, but at least 1.
    sponsorship_start_month: int | None = 18
    sponsorship_fee_usd: float = 500.0
    # Memberships (assumption): from memberships_start_month, once subscribers reach
    # memberships_min_subs, a fixed share of subscribers pays a fixed monthly price.
    # The threshold is a modelling choice for "memberships matter at scale", not a YouTube rule.
    memberships_start_month: int | None = 24
    memberships_min_subs: int = 30_000
    membership_price_usd: float = 4.99
    membership_rate: float = 0.005        # share of subs who join memberships

    @property
    def cpm(self) -> float:
        return NICHE_CPMS.get(self.niche, DEFAULT_CPM)

    @property
    def rpm(self) -> float:
        return self.cpm * YOUTUBE_REVENUE_SHARE * self.monetized_view_share


def sponsorship_deals(videos_per_month: int) -> int:
    """Deals per month: one per 4 videos, but at least one (a channel posting 1-3 videos
    a month still books one deal)."""
    return max(1, videos_per_month // 4)


def simulate(cfg: ChannelConfig) -> pd.DataFrame:
    rows = []
    subs = float(cfg.initial_subscribers)
    last_12_watch_hours: deque[float] = deque(maxlen=12)
    cumulative_watch_hours = 0.0
    cumulative_revenue = 0.0
    monetized = False

    for m in range(1, cfg.months + 1):
        subs *= 1 + cfg.monthly_sub_growth_rate

        monthly_views = int(subs * cfg.views_per_sub_ratio * cfg.organic_view_multiplier
                            * cfg.videos_per_month)
        watch_hours_month = monthly_views * cfg.avg_video_length_min * cfg.avg_view_retention / 60
        cumulative_watch_hours += watch_hours_month
        last_12_watch_hours.append(watch_hours_month)
        rolling_watch_hours = sum(last_12_watch_hours)

        # Once accepted into YPP the channel stays monetized (no demonetization modelled).
        if (not monetized and int(subs) >= MONETIZATION_MIN_SUBS
                and rolling_watch_hours >= MONETIZATION_MIN_WATCH_HOURS):
            monetized = True

        ad_rev = (monthly_views / 1000) * cfg.rpm if monetized else 0.0

        sponsor_rev = 0.0
        if cfg.sponsorship_start_month and m >= cfg.sponsorship_start_month and monetized:
            sponsor_rev = cfg.sponsorship_fee_usd * sponsorship_deals(cfg.videos_per_month)

        member_rev = 0.0
        if (cfg.memberships_start_month and m >= cfg.memberships_start_month
                and int(subs) >= cfg.memberships_min_subs):
            member_rev = int(subs) * cfg.membership_rate * cfg.membership_price_usd

        total_rev = ad_rev + sponsor_rev + member_rev
        cumulative_revenue += total_rev

        rows.append({
            "month":                m,
            "subscribers":          int(subs),
            "monthly_views":        monthly_views,
            "watch_hours_month":    round(watch_hours_month, 1),
            "watch_hours_12m":      round(rolling_watch_hours, 1),
            "watch_hours_total":    round(cumulative_watch_hours, 1),
            "ad_revenue":           round(ad_rev, 2),
            "sponsorship_revenue":  round(sponsor_rev, 2),
            "membership_revenue":   round(member_rev, 2),
            "total_revenue":        round(total_rev, 2),
            "is_monetized":         monetized,
            "cumulative_revenue":   round(cumulative_revenue, 2),
        })

    return pd.DataFrame(rows)


def _first_month(df: pd.DataFrame, mask) -> int | None:
    hit = df[mask]
    return int(hit["month"].iloc[0]) if not hit.empty else None


def monetization_milestone(df: pd.DataFrame) -> dict:
    return {
        "months":               int(df["month"].iloc[-1]),
        "monetization_month":   _first_month(df, df["is_monetized"]),
        "10k_subs_month":       _first_month(df, df["subscribers"] >= 10_000),
        "100k_subs_month":      _first_month(df, df["subscribers"] >= 100_000),
        "1M_subs_month":        _first_month(df, df["subscribers"] >= 1_000_000),
        "1M_views_month":       _first_month(df, df["monthly_views"] >= 1_000_000),
        "total_revenue":        float(df["cumulative_revenue"].iloc[-1]),
        "total_ad_revenue":     float(df["ad_revenue"].sum().round(2)),
        "peak_monthly_revenue": float(df["total_revenue"].max()),
    }


def compare_niches(niches: list[str], base_cfg: ChannelConfig) -> pd.DataFrame:
    """Run the *same* channel settings in each niche; only the CPM changes."""
    rows = []
    for niche in niches:
        cfg = replace(base_cfg, name=niche, niche=niche)
        df = simulate(cfg)
        ms = monetization_milestone(df)
        rows.append({
            "niche":               niche,
            "cpm_usd":             cfg.cpm,
            "rpm_usd":             round(cfg.rpm, 2),
            "ad_revenue_usd":      round(ms["total_ad_revenue"], 2),
            "total_revenue_usd":   round(ms["total_revenue"], 2),
            "peak_monthly_usd":    ms["peak_monthly_revenue"],
            "monetization_month":  ms["monetization_month"] or f">{cfg.months}",
            "final_subscribers":   int(df["subscribers"].iloc[-1]),
        })
    return pd.DataFrame(rows).sort_values("total_revenue_usd", ascending=False).reset_index(drop=True)
