"""
YouTube Revenue Simulator
Run:  python main.py
Models channel growth, YPP eligibility, ad/sponsorship/membership revenue,
and compares earnings across all major content niches.
"""
from src.models import ChannelConfig, simulate, monetization_milestone, compare_niches, NICHE_CPMS
from src.charts import plot_growth_and_revenue, plot_niche_comparison, plot_revenue_vs_views

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

def main():
    print("YouTube Revenue Simulator")
    print("=" * 55)
    print(f"Channel niche : {MY_CHANNEL.niche}")
    print(f"CPM           : ${MY_CHANNEL.cpm:.2f}  |  RPM: ${MY_CHANNEL.rpm:.2f}")
    print(f"Starting subs : {MY_CHANNEL.initial_subscribers:,}")
    print(f"Videos/month  : {MY_CHANNEL.videos_per_month}")

    print("\n[1/3] Simulating channel growth...")
    df = simulate(MY_CHANNEL)
    ms = monetization_milestone(df)

    print("\nMILESTONES")
    print("-" * 35)
    items = [
        ("YPP monetization",    ms["monetization_month"]),
        ("10K subscribers",     ms["10k_subs_month"]),
        ("100K subscribers",    ms["100k_subs_month"]),
        ("1M subscribers",      ms["1M_subs_month"]),
        ("1M views/month",      ms["1M_views_month"]),
    ]
    for label, month in items:
        val = f"Month {month}" if month else "Not reached in 36 months"
        print(f"  {label:<22} {val}")

    print(f"\n  36-month total revenue  : ${ms['total_36m_revenue']:>10,.2f}")
    print(f"  Peak monthly revenue    : ${ms['peak_monthly_revenue']:>10,.2f}")

    print("\n[2/3] Comparing all niches...")
    comparison = compare_niches(list(NICHE_CPMS.keys()), MY_CHANNEL)
    print(comparison[["niche", "cpm_usd", "rpm_usd", "36m_revenue_usd",
                        "monetization_month"]].to_string(index=False))

    print("\n[3/3] Generating charts...")
    plot_growth_and_revenue(df, MY_CHANNEL.name, ms)
    plot_niche_comparison(comparison)
    plot_revenue_vs_views(df, MY_CHANNEL.name)

    print("\nAll charts saved to output/")
    print("\nTIP: Edit MY_CHANNEL in main.py to model your own channel assumptions.")

if __name__ == "__main__":
    main()
