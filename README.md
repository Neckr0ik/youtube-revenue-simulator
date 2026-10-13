# YouTube Revenue Simulator

> **Resumen:** Simula 36 meses de un canal de YouTube: crecimiento de suscriptores, elegibilidad al Programa de Socios (YPP), ingresos por anuncios, patrocinios y membresías, y compara el mismo canal en distintos nichos (solo cambia el CPM). Todos los valores son supuestos editables, no datos de YouTube: sirve para explorar escenarios, no para pronosticar ingresos.

*Part of Giovanni Oliveira's Hybrid Intelligence portfolio — see https://github.com/Neckr0ik*

**Business questions:** how long until a new channel monetizes? How much does the niche (advertiser CPM) matter for the same posting effort? How much of the revenue comes from ads and how much from sponsorships?

The simulator models subscriber growth, YouTube Partner Program (YPP) eligibility and three revenue streams (ads, sponsorships, memberships) month by month, and reruns the same channel in eight niches.

---

## Sample output (default scenario, `python main.py`)

```
Channel niche : Finance & Business
CPM           : $22.00  |  RPM: $12.10

MILESTONES
  YPP monetization       Month 11
  10K subscribers        Month 35
  100K subscribers       Not reached in 36 months

  36-month total revenue  : $ 39,737.05
    of which ad revenue   : $  2,937.02
  Peak monthly revenue    : $  1,871.39
```

Niche comparison (same channel settings, only the CPM changes):

| Niche | CPM | Ad revenue (36 mo) | Total revenue (36 mo) |
|---|---:|---:|---:|
| Finance & Business | $22.00 | $2,937 | $39,737 |
| Digital Marketing | $17.00 | $2,270 | $39,070 |
| Technology | $12.00 | $1,602 | $38,402 |
| Entertainment | $4.50 | $601 | $37,401 |
| Gaming | $3.50 | $467 | $37,267 |

**How to read it:** under these assumptions the channel stays under 10K subscribers for most of the period. Sponsorships, a flat $800 per deal for 2 deals a month from month 14, then outweigh ad revenue, so the niche changes ad revenue about 6× (the CPM ratio) but total revenue by only about 7%. Changing the assumptions changes this conclusion.

---

## Model

```python
RPM = CPM * 0.55 * monetized_view_share   # creator share of long-form ads; share of views with ads
ad_revenue = monthly_views / 1000 * RPM   # only after YPP acceptance
monthly_views = subs * views_per_sub_ratio * organic_view_multiplier * videos_per_month
watch_hours   = monthly_views * avg_video_length_min / 60
YPP: >= 1,000 subscribers AND >= 4,000 watch hours in the trailing 12 months
sponsorships  = fee * max(1, videos_per_month // 4)   # from sponsorship_start_month, once monetized
memberships   = subs * membership_rate * price        # from memberships_start_month, if subs >= memberships_min_subs
```

The per-niche CPMs in `src/models.py` are **illustrative mid-range assumptions**. Real CPMs vary a lot by country (LATAM CPMs are usually far below US ones), season and audience.

## Install, run, test

```bash
git clone https://github.com/Neckr0ik/youtube-revenue-simulator.git
cd youtube-revenue-simulator
pip install -r requirements.txt

python main.py                                         # default scenario + charts in output/
python main.py --niche Gaming --growth 0.12 --videos 12
python main.py --months 48 --monetized-share 0.6       # more conservative ad assumptions
python main.py --no-charts --csv                       # monthly table + niche comparison as CSV

pytest -q                                              # offline test suite
```

Python 3.11+. CI runs the tests on Python 3.11 and 3.12 (`.github/workflows/tests.yml`). Any parameter without a flag can be changed in `MY_CHANNEL` in `main.py`.

| Parameter | Description |
|---|---|
| `niche` | Content category; sets the CPM |
| `monthly_sub_growth_rate` | Month-over-month subscriber growth |
| `videos_per_month` | Upload cadence |
| `views_per_sub_ratio` | Share of subscribers who watch each video |
| `organic_view_multiplier` | Extra views from search and suggested |
| `monetized_view_share` | Share of views that carry ads (default 1.0, the optimistic case) |
| `sponsorship_start_month` / `sponsorship_fee_usd` | When brand deals start, and the fee per deal |
| `memberships_min_subs` / `membership_rate` | Subscriber threshold and join rate for memberships |

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
