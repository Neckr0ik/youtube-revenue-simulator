"""Visualizations for the YouTube Revenue Simulator."""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd

sns.set_theme(style="darkgrid", palette="muted")
RED    = "#FF0000"
DARK   = "#282828"
GOLD   = "#FFD700"
GREEN  = "#2E8B57"
OUT    = os.path.join(os.path.dirname(__file__), "..", "output")

def _save(name: str):
    os.makedirs(OUT, exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  saved -> output/{name}")

def plot_growth_and_revenue(df: pd.DataFrame, label: str, milestones: dict):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(f"YouTube Channel Simulation: {label}", fontsize=13, fontweight="bold")

    # Subscribers
    ax = axes[0, 0]
    ax.plot(df["month"], df["subscribers"] / 1e3, color=RED, lw=2.5)
    ax.fill_between(df["month"], df["subscribers"] / 1e3, alpha=0.1, color=RED)
    for threshold, color, text in [(1, "orange", "1K"), (10, "gold", "10K"), (100, "green", "100K")]:
        ax.axhline(threshold, color=color, lw=0.8, linestyle="--", alpha=0.6)
        ax.text(1, threshold * 1.05, text, fontsize=7, color=color)
    ax.set_ylabel("Subscribers (thousands)")
    ax.set_title("Subscriber Growth")

    # Monthly views
    ax = axes[0, 1]
    ax.plot(df["month"], df["monthly_views"] / 1e3, color=DARK, lw=2)
    ax.fill_between(df["month"], df["monthly_views"] / 1e3, alpha=0.1, color=DARK)
    ax.set_ylabel("Monthly Views (thousands)")
    ax.set_title("Monthly Views")

    # Revenue stack
    ax = axes[1, 0]
    ax.bar(df["month"], df["ad_revenue"],          label="Ad Revenue",          color=RED,   alpha=0.75)
    ax.bar(df["month"], df["sponsorship_revenue"], label="Sponsorships",         color=DARK,  alpha=0.75,
           bottom=df["ad_revenue"])
    ax.bar(df["month"], df["membership_revenue"],  label="Memberships",          color=GOLD,  alpha=0.85,
           bottom=df["ad_revenue"] + df["sponsorship_revenue"])
    ax.set_ylabel("Monthly Revenue (USD)")
    ax.set_title("Revenue Breakdown by Stream")
    ax.legend(fontsize=8)

    # Cumulative revenue
    ax = axes[1, 1]
    ax.plot(df["month"], df["cumulative_revenue"], color=GREEN, lw=2.5)
    ax.fill_between(df["month"], df["cumulative_revenue"], alpha=0.12, color=GREEN)
    if milestones.get("monetization_month"):
        ax.axvline(milestones["monetization_month"], color="orange", lw=1.2,
                   linestyle=":", label=f"Monetized: Month {milestones['monetization_month']}")
        ax.legend(fontsize=8)
    ax.set_ylabel("Cumulative Revenue (USD)")
    ax.set_title("Cumulative Earnings")

    for ax_row in axes:
        for ax in ax_row:
            ax.set_xlabel("Month")

    _save(f"01_channel_overview_{label.lower().replace(' ', '_').replace('&','and')}.png")

def plot_niche_comparison(comparison: pd.DataFrame):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("YouTube Niche Comparison (Same Channel Settings)", fontsize=12, fontweight="bold")

    comp_sorted = comparison.sort_values("36m_revenue_usd")
    bars = axes[0].barh(comp_sorted["niche"], comp_sorted["36m_revenue_usd"],
                        color=[RED if n == comp_sorted["niche"].iloc[-1] else "#888" for n in comp_sorted["niche"]])
    axes[0].set_xlabel("36-Month Total Revenue (USD)")
    axes[0].set_title("Total 36-Month Revenue by Niche")

    comp_cpm = comparison.sort_values("cpm_usd")
    axes[1].barh(comp_cpm["niche"], comp_cpm["cpm_usd"], color=DARK, alpha=0.8)
    axes[1].set_xlabel("CPM (USD)")
    axes[1].set_title("Advertiser CPM by Niche")

    comp_subs = comparison.sort_values("month36_subscribers")
    axes[2].barh(comp_subs["niche"], comp_subs["month36_subscribers"] / 1e3, color="#1a73e8", alpha=0.8)
    axes[2].set_xlabel("Month-36 Subscribers (thousands)")
    axes[2].set_title("Final Subscriber Count (Same Growth Rate)")

    _save("02_niche_comparison.png")

def plot_revenue_vs_views(df: pd.DataFrame, label: str):
    monetized = df[df["is_monetized"]]
    if monetized.empty:
        return
    plt.figure(figsize=(9, 5))
    sc = plt.scatter(monetized["monthly_views"] / 1e3,
                     monetized["total_revenue"],
                     c=monetized["month"], cmap="YlOrRd", s=60, alpha=0.8)
    plt.colorbar(sc, label="Month")
    plt.xlabel("Monthly Views (thousands)")
    plt.ylabel("Monthly Revenue (USD)")
    plt.title(f"Revenue vs Views After Monetization — {label}", fontweight="bold")
    _save(f"03_revenue_vs_views_{label.lower().replace(' ', '_').replace('&','and')}.png")
