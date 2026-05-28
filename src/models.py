"""
YouTube Channel Revenue Simulator
Models growth, ad revenue, and monetization milestones using
publicly documented YouTube Partner Program economics.

Key formulas:
  Ad revenue = (views / 1000) * RPM
  RPM = CPM * 0.45  (YouTube's 55% creator share applied to advertiser CPM)
  Watch time (hours) = views * avg_video_length_min / 60
"""
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

# Publicly documented CPM ranges by niche (USD, mid-range estimates)
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

YOUTUBE_REVENUE_SHARE = 0.55   # creator keeps 55% of gross ad revenue
MONETIZATION_MIN_SUBS = 1_000
MONETIZATION_MIN_WATCH_HOURS = 4_000   # trailing 12 months

@dataclass
class ChannelConfig:
    name: str
    niche: str
    initial_subscribers: int = 500
    monthly_sub_growth_rate: float = 0.08
    videos_per_month: int = 8
    avg_video_length_min: float = 12.0
    views_per_sub_ratio: float = 0.18    # avg % of subs who watch each video
    organic_view_multiplier: float = 1.3  # search/suggested views on top of sub views
    months: int = 36
    sponsorship_start_month: int | None = 18
    sponsorship_fee_usd: float = 500.0
    memberships_start_month: int | None = 24
    membership_price_usd: float = 4.99
    membership_rate: float = 0.005        # % of subs who join memberships

    @property
    def cpm(self) -> float:
        return NICHE_CPMS.get(self.niche, 8.0)

    @property
    def rpm(self) -> float:
        return self.cpm * YOUTUBE_REVENUE_SHARE

@dataclass
class MonthResult:
    month: int
    subscribers: int
    monthly_views: int
    watch_hours_ytd: float
    ad_revenue: float
    sponsorship_revenue: float
    membership_revenue: float
    total_revenue: float
    is_monetized: bool
    cumulative_revenue: float

def simulate(cfg: ChannelConfig) -> pd.DataFrame:
    rows = []
    subs = float(cfg.initial_subscribers)
    cumulative_views = 0
    cumulative_watch_hours = 0.0
    cumulative_revenue = 0.0
    monetized = False

    for m in range(1, cfg.months + 1):
        subs = subs * (1 + cfg.monthly_sub_growth_rate)

        # View calculation: subscribers * ratio * organic multiplier * videos
        monthly_views = int(
            subs * cfg.views_per_sub_ratio
            * cfg.organic_view_multiplier
            * cfg.videos_per_month
        )
        watch_hours_month = monthly_views * cfg.avg_video_length_min / 60

        cumulative_views      += monthly_views
        cumulative_watch_hours += watch_hours_month

        # Monetization eligibility check (rolling 12-month watch hours simplified)
        rolling_watch_hours = min(cumulative_watch_hours, watch_hours_month * 12)
        if not monetized and int(subs) >= MONETIZATION_MIN_SUBS and rolling_watch_hours >= MONETIZATION_MIN_WATCH_HOURS:
            monetized = True

        ad_rev = (monthly_views / 1000) * cfg.rpm if monetized else 0.0

        sponsor_rev = 0.0
        if cfg.sponsorship_start_month and m >= cfg.sponsorship_start_month and monetized:
            sponsor_rev = cfg.sponsorship_fee_usd * max(1, cfg.videos_per_month // 4)

        member_rev = 0.0
        if cfg.memberships_start_month and m >= cfg.memberships_start_month and int(subs) >= 30_000:
            member_rev = int(subs) * cfg.membership_rate * cfg.membership_price_usd

        total_rev = ad_rev + sponsor_rev + member_rev
        cumulative_revenue += total_rev

        rows.append({
            "month":                m,
            "subscribers":          int(subs),
            "monthly_views":        monthly_views,
            "watch_hours_ytd":      round(cumulative_watch_hours, 1),
            "ad_revenue":           round(ad_rev, 2),
            "sponsorship_revenue":  round(sponsor_rev, 2),
            "membership_revenue":   round(member_rev, 2),
            "total_revenue":        round(total_rev, 2),
            "is_monetized":         monetized,
            "cumulative_revenue":   round(cumulative_revenue, 2),
        })

    return pd.DataFrame(rows)

def monetization_milestone(df: pd.DataFrame) -> dict:
    mon_row = df[df["is_monetized"]].head(1)
    k10     = df[df["subscribers"] >= 10_000].head(1)
    k100    = df[df["subscribers"] >= 100_000].head(1)
    k1000   = df[df["subscribers"] >= 1_000_000].head(1)
    first_k = df[df["monthly_views"] >= 1_000_000].head(1)
    return {
        "monetization_month":  int(mon_row["month"].iloc[0]) if not mon_row.empty else None,
        "10k_subs_month":      int(k10["month"].iloc[0])     if not k10.empty else None,
        "100k_subs_month":     int(k100["month"].iloc[0])    if not k100.empty else None,
        "1M_subs_month":       int(k1000["month"].iloc[0])   if not k1000.empty else None,
        "1M_views_month":      int(first_k["month"].iloc[0]) if not first_k.empty else None,
        "total_36m_revenue":   df["cumulative_revenue"].iloc[-1],
        "peak_monthly_revenue": df["total_revenue"].max(),
    }

def compare_niches(niches: list[str], base_cfg: ChannelConfig) -> pd.DataFrame:
    rows = []
    for niche in niches:
        cfg = ChannelConfig(
            name=niche, niche=niche,
            initial_subscribers=base_cfg.initial_subscribers,
            monthly_sub_growth_rate=base_cfg.monthly_sub_growth_rate,
            videos_per_month=base_cfg.videos_per_month,
            avg_video_length_min=base_cfg.avg_video_length_min,
            views_per_sub_ratio=base_cfg.views_per_sub_ratio,
            organic_view_multiplier=base_cfg.organic_view_multiplier,
        )
        df = simulate(cfg)
        ms = monetization_milestone(df)
        rows.append({
            "niche":                niche,
            "cpm_usd":              cfg.cpm,
            "rpm_usd":              round(cfg.rpm, 2),
            "36m_revenue_usd":      ms["total_36m_revenue"],
            "peak_monthly_usd":     ms["peak_monthly_revenue"],
            "monetization_month":   ms["monetization_month"] or ">36",
            "month36_subscribers":  df["subscribers"].iloc[-1],
        })
    return pd.DataFrame(rows).sort_values("36m_revenue_usd", ascending=False)
