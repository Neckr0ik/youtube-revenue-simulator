# YouTube Revenue Simulator

**Business problem:** How long until a new YouTube channel becomes self-sustaining? Which content niche maximizes earnings for the same posting effort? When does sponsorship revenue overtake ad revenue?

This simulator models YouTube channel growth, YouTube Partner Program (YPP) eligibility, and multi-stream revenue (ads, sponsorships, memberships) over 36 months — using publicly documented CPM rates and YouTube's 55% creator revenue share.

---

## Sample output (Finance & Business niche)

```
Channel niche : Finance & Business
CPM           : $22.00  |  RPM: $12.10

MILESTONES
  YPP monetization       Month 11
  10K subscribers        Month 35
  36-month total revenue : $39,737
  Peak monthly revenue   : $ 1,871
```

**Niche revenue comparison (same channel settings, ad revenue only):**

| Niche | CPM | 36M Revenue |
|---|---|---|
| Finance & Business | $22.00 | $21,937 |
| Digital Marketing | $17.00 | $21,270 |
| Technology | $12.00 | $20,602 |
| Entertainment | $4.50 | $19,601 |
| Gaming | $3.50 | $19,467 |

Finance earns 12.7% more than Gaming for identical content output — purely from advertiser demand for the audience.

---

## Key formulas used

```python
RPM = CPM * 0.55             # YouTube's 55% creator share
ad_revenue = (views / 1000) * RPM
# YPP requires: 1,000+ subscribers AND 4,000+ watch hours (trailing 12 months)
```

All CPM values are based on publicly reported mid-range estimates per niche.

---

## Quick start

```bash
git clone https://github.com/Neckr0ik/youtube-revenue-simulator.git
cd youtube-revenue-simulator
pip install -r requirements.txt
python main.py
```

Edit `MY_CHANNEL` in `main.py` to model your own channel assumptions. Runtime: ~5 seconds.

---

## Project structure

```
youtube-revenue-simulator/
├── main.py              # Channel config, entry point, milestone report
├── src/
│   ├── models.py        # ChannelConfig, simulate(), compare_niches(), milestone tracker
│   └── charts.py        # Growth overview, niche comparison, revenue-vs-views scatter
├── output/              # Generated charts (git-ignored)
└── requirements.txt
```

---

## Configurable parameters

| Parameter | Description |
|---|---|
| `niche` | Content category — sets CPM from documented rates |
| `monthly_sub_growth_rate` | Month-over-month subscriber growth |
| `videos_per_month` | Upload cadence |
| `views_per_sub_ratio` | % of subscribers who watch each video |
| `organic_view_multiplier` | Search/suggested traffic multiplier |
| `sponsorship_start_month` | When brand deals begin |
| `membership_rate` | % of subscribers joining channel memberships |

---

## Skills demonstrated

`Python` · `Pandas` · `NumPy` · `Matplotlib` · `Seaborn` · `Financial Modeling` · `Revenue Simulation` · `Scenario Analysis` · `Creator Economy Analytics`

---

## License

MIT © 2026 Giovanni Oliveira
