# YouTube Revenue Simulator

> **Resumen:** Simula 36 meses de un canal de YouTube: crecimiento de suscriptores, elegibilidad al Programa de Socios (YPP), ingresos por anuncios, patrocinios y membresías, y compara el mismo canal en distintos nichos (solo cambia el CPM). Todos los valores son supuestos editables, no datos de YouTube: sirve para explorar escenarios, no para pronosticar ingresos.

*Part of Giovanni Oliveira's Hybrid Intelligence portfolio — see https://github.com/Neckr0ik*

**Business questions:** how long until a new channel monetizes? How much does the niche (advertiser CPM) matter for the same posting effort? How much of the revenue comes from ads and how much from sponsorships?

The simulator models subscriber growth, YouTube Partner Program (YPP) eligibility and three revenue streams (ads, sponsorships, memberships) month by month, and reruns the same channel in eight niches.

---

## Sample output (default scenario, first lines of `python main.py --no-charts`)

```
Channel niche : Finance & Business
CPM           : $22.00  |  RPM: $12.10
Starting subs : 500  |  growth 9%/month
Videos/month  : 8  |  14 min, 40% watched on average

[1/3] Simulating channel growth...

MILESTONES
-----------------------------------
  YPP monetization       Month 20
  10K subscribers        Month 35
  100K subscribers       Not reached in 36 months
  1M subscribers         Not reached in 36 months
  1M views/month         Not reached in 36 months

  36-month total revenue  : $ 29,727.28
    of which ad revenue   : $  2,527.27
  Peak monthly revenue    : $  1,871.39
```

Niche comparison (same channel settings, only the CPM changes; rounded from the console table):

| Niche | CPM | Ad revenue (36 mo) | Total revenue (36 mo) |
|---|---:|---:|---:|
| Finance & Business | $22.00 | $2,527 | $29,727 |
| Digital Marketing | $17.00 | $1,953 | $29,153 |
| Technology | $12.00 | $1,379 | $28,579 |
| Entertainment | $4.50 | $517 | $27,717 |
| Gaming | $3.50 | $402 | $27,602 |

**How to read it:** under these assumptions the channel reaches YPP in month 20 (watch hours are the bottleneck) and stays under 10K subscribers for most of the period. Sponsorships, a flat $800 per deal for 2 deals a month once the channel is monetized, then outweigh ad revenue, so the niche changes ad revenue about 6× (the CPM ratio) but total revenue by only about 8%. Changing the assumptions changes this conclusion.

---

## Model

```python
RPM = CPM * 0.55 * monetized_view_share   # creator share of long-form ads; share of views with ads
ad_revenue = monthly_views / 1000 * RPM   # only after YPP acceptance
monthly_views = subs * views_per_sub_ratio * organic_view_multiplier * videos_per_month
watch_hours   = monthly_views * avg_video_length_min * avg_view_retention / 60
YPP: >= 1,000 subscribers AND >= 4,000 watch hours in the trailing 12 months
sponsorships  = fee * max(1, videos_per_month // 4)   # from sponsorship_start_month, once monetized
memberships   = subs * membership_rate * price        # from memberships_start_month, if subs >= memberships_min_subs
```

Assumptions behind the revenue streams (all editable):

- **Watch time.** Average view duration = video length × `avg_view_retention`. The default retention is **0.40** (viewers watch 40% of a video on average), an illustrative assumption; use your own analytics if you have them. The default channel posts 14-minute videos, so an average view lasts 5.6 minutes.
- **Sponsorships.** A flat fee per deal (default channel: $800), with one deal per 4 videos a month and **at least one deal a month**, so a channel posting 1–3 videos still books one. Deals start at `sponsorship_start_month` (default channel: 14) but only once the channel is in YPP. Real deals are priced on views and audience fit.
- **Memberships.** From `memberships_start_month` (default channel: 24), and only once subscribers reach `memberships_min_subs` (30,000, a modelling choice for "memberships matter at scale", not a YouTube rule), `membership_rate` of subscribers (default channel: 0.6%) pay `membership_price_usd` ($4.99) a month. The default channel never reaches 30,000 subscribers in 36 months, so it earns no membership revenue.

The per-niche CPMs in `src/models.py` are **illustrative mid-range assumptions**. Real CPMs vary a lot by country (LATAM CPMs are usually far below US ones), season and audience.

## Install, run, test

```bash
git clone https://github.com/Neckr0ik/youtube-revenue-simulator.git
cd youtube-revenue-simulator
pip install -r requirements.txt

python main.py                                         # default scenario + charts in output/
python main.py --niche Gaming --growth 0.12 --videos 12
python main.py --months 48 --monetized-share 0.6       # more conservative ad assumptions
python main.py --length 10 --retention 0.5             # shorter videos, higher retention
python main.py --no-charts --csv                       # monthly table + niche comparison as CSV

pytest -q                                              # offline test suite
```

Python 3.11+. CI runs the tests on Python 3.11 and 3.12 (`.github/workflows/tests.yml`). Any parameter without a flag can be changed in `MY_CHANNEL` in `main.py`.

| Parameter | Description |
|---|---|
| `niche` | Content category; sets the CPM |
| `monthly_sub_growth_rate` | Month-over-month subscriber growth |
| `videos_per_month` | Upload cadence (`--videos`, at least 1) |
| `avg_video_length_min` | Average video length in minutes (`--length`) |
| `avg_view_retention` | Share of each video watched on average, 0–1 (`--retention`, default 0.40) |
| `views_per_sub_ratio` | Share of subscribers who watch each video |
| `organic_view_multiplier` | Extra views from search and suggested |
| `monetized_view_share` | Share of views that carry ads, 0–1 (`--monetized-share`, default 1.0, the optimistic case) |
| `months` | Simulation horizon (`--months`, at least 1) |
| `sponsorship_start_month` / `sponsorship_fee_usd` | When brand deals start, and the fee per deal |
| `memberships_start_month` / `memberships_min_subs` / `membership_rate` / `membership_price_usd` | When memberships can start, the subscriber threshold, the join rate and the monthly price |

Flags are range-checked: for example `--monetized-share 1.5`, `--retention 0` or `--months 0` stop with an error.

## Project structure

```
youtube-revenue-simulator/
├── main.py         # CLI + default channel scenario
├── src/
│   ├── models.py   # ChannelConfig, simulate(), milestones, compare_niches()
│   └── charts.py   # overview, niche comparison, revenue-vs-views charts
└── tests/
```

## Limitations

- **A scenario tool, not a forecast.** Growth is compound and constant; real channels grow unevenly and depend on the algorithm.
- **Simplified YPP.** Only the long-form path is modelled (1,000 subscribers + 4,000 watch hours). The Shorts path, the lower fan-funding tier, demonetization and policy changes are not.
- **Simplified ads.** Ad revenue ignores Shorts revenue sharing, ad-blocking, seasonality and geography unless you lower `monetized_view_share` or edit the CPMs.
- **Simplified sponsorships and memberships.** Both are flat rules. Real deals scale with views and audience fit.

## License

MIT © 2026 Giovanni Oliveira
