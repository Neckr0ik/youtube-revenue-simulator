"""
YouTube Revenue Simulator

    python main.py                                   # default Finance & Business scenario
    python main.py --niche Gaming --growth 0.12 --videos 12
    python main.py --months 48 --monetized-share 0.6 --no-charts --csv

Models channel growth, YPP eligibility, ad/sponsorship/membership revenue,
and compares the same channel across content niches. All inputs are assumptions.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import replace

from src.models import NICHE_CPMS, ChannelConfig, compare_niches, monetization_milestone, simulate

MY_CHANNEL = ChannelConfig(
    name="Finance & Business",
    niche="Finance & Business",
    initial_subscribers=500,
    monthly_sub_growth_rate=0.09,
    videos_per_month=8,
    avg_video_length_min=14.0,
    views_per_sub_ratio=0.18,
    organic_view_multiplier=1.4,
    sponsorship_start_month=14,
    sponsorship_fee_usd=800.0,
    memberships_start_month=24,
    membership_price_usd=4.99,
    membership_rate=0.006,
)


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simulate YouTube channel growth and revenue")
    p.add_argument("--niche", choices=sorted(NICHE_CPMS), help="content niche (sets the CPM)")
    p.add_argument("--subs", type=int, help="starting subscribers")
    p.add_argument("--growth", type=float, help="monthly subscriber growth rate, e.g. 0.09")
    p.add_argument("--videos", type=int, help="videos per month")
    p.add_argument("--length", type=float, help="average view duration in minutes")
    p.add_argument("--months", type=int, help="simulation horizon (default 36)")
    p.add_argument("--monetized-share", type=float, help="share of views that carry ads (default 1.0)")
    p.add_argument("--out", default="output")
    p.add_argument("--csv", action="store_true", help="export monthly results and niche comparison")
    p.add_argument("--no-charts", action="store_true")
    return p.parse_args(argv)


def build_config(args) -> ChannelConfig:
    overrides = {k: v for k, v in {
        "niche": args.niche, "initial_subscribers": args.subs, "monthly_sub_growth_rate": args.growth,
        "videos_per_month": args.videos, "avg_video_length_min": args.length, "months": args.months,
        "monetized_view_share": args.monetized_share,
    }.items() if v is not None}
    if "niche" in overrides:
        overrides["name"] = overrides["niche"]
    return replace(MY_CHANNEL, **overrides)


def main(argv=None) -> int:
    args = parse_args(argv)
    cfg = build_config(args)

    print("YouTube Revenue Simulator")
    print("=" * 55)
    print(f"Channel niche : {cfg.niche}")
    print(f"CPM           : ${cfg.cpm:.2f}  |  RPM: ${cfg.rpm:.2f}")
    print(f"Starting subs : {cfg.initial_subscribers:,}  |  growth {cfg.monthly_sub_growth_rate:.0%}/month")
    print(f"Videos/month  : {cfg.videos_per_month}")

    print("\n[1/3] Simulating channel growth...")
    df = simulate(cfg)
    ms = monetization_milestone(df)

    print("\nMILESTONES")
    print("-" * 35)
    for label, month in [("YPP monetization", ms["monetization_month"]),
                         ("10K subscribers", ms["10k_subs_month"]),
                         ("100K subscribers", ms["100k_subs_month"]),
                         ("1M subscribers", ms["1M_subs_month"]),
                         ("1M views/month", ms["1M_views_month"])]:
        val = f"Month {month}" if month else f"Not reached in {cfg.months} months"
        print(f"  {label:<22} {val}")

    print(f"\n  {cfg.months}-month total revenue  : ${ms['total_revenue']:>10,.2f}")
    print(f"    of which ad revenue   : ${ms['total_ad_revenue']:>10,.2f}")
    print(f"  Peak monthly revenue    : ${ms['peak_monthly_revenue']:>10,.2f}")

    print("\n[2/3] Comparing all niches (same channel settings, only CPM changes)...")
    comparison = compare_niches(list(NICHE_CPMS), cfg)
    print(comparison[["niche", "cpm_usd", "rpm_usd", "ad_revenue_usd", "total_revenue_usd",
                      "monetization_month"]].to_string(index=False))

    if args.csv:
        os.makedirs(args.out, exist_ok=True)
        df.to_csv(os.path.join(args.out, "monthly_results.csv"), index=False)
        comparison.to_csv(os.path.join(args.out, "niche_comparison.csv"), index=False)
        print(f"\n  CSV exports -> {args.out}/")

    if not args.no_charts:
        print("\n[3/3] Generating charts...")
        from src.charts import plot_growth_and_revenue, plot_niche_comparison, plot_revenue_vs_views
        plot_growth_and_revenue(df, cfg.name, ms, args.out)
        plot_niche_comparison(comparison, cfg.months, args.out)
        plot_revenue_vs_views(df, cfg.name, args.out)

    print(f"\nOutputs saved to {args.out}/")
    print("\nTIP: python main.py --help  lists the scenario flags; edit MY_CHANNEL for the rest.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
