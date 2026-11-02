# CLAUDE.md — youtube-revenue-simulator

Portfolio project (Neckr0ik / Giovanni Oliveira, "Hybrid Intelligence" portfolio). Month-by-month scenario simulator for a YouTube channel: subscriber growth, YouTube Partner Program (YPP) eligibility, and three revenue streams (ads, sponsorships, memberships); reruns the same channel across 8 niches where only the CPM changes. All values are editable assumptions, not YouTube data — a scenario tool, not a forecast.

## Stack

Python 3.11+, pandas, numpy, matplotlib, seaborn, pytest (`requirements.txt`). No API keys, no network.

## Structure

```
main.py          # CLI + default scenario MY_CHANNEL (ChannelConfig); flags override via dataclasses.replace
src/models.py    # ChannelConfig, NICHE_CPMS, simulate(), milestones, compare_niches()
src/charts.py    # overview, niche comparison, revenue-vs-views charts
tests/           # test_models.py, test_cli.py
```

## Commands

```bash
pip install -r requirements.txt
python main.py                                         # default scenario + charts in output/
python main.py --niche Gaming --growth 0.12 --videos 12
python main.py --months 48 --monetized-share 0.6
python main.py --length 10 --retention 0.5
python main.py --no-charts --csv                       # monthly table + niche comparison as CSV
python main.py --help                                  # also: --subs N, --out DIR
pytest -q                                              # 31 tests, offline
```

## Model (keep README "Model" section, code and tests in sync)

- `RPM = CPM × 0.55 × monetized_view_share`; ad revenue = views/1000 × RPM, only after YPP.
- YPP: ≥ 1,000 subs AND ≥ 4,000 watch hours in the **trailing 12 months**; watch hours = views × length × `avg_view_retention` (default 0.40) / 60.
- Sponsorships: flat fee × `max(1, videos_per_month // 4)`, from `sponsorship_start_month` and only once monetized.
- Memberships: from `memberships_start_month` and only if subs ≥ `memberships_min_subs` (30,000, a modelling choice).
- Niche CPMs in `src/models.py` are illustrative mid-range assumptions.

## Gotchas

- Flags are range-checked (`_ranged`): e.g. `--monetized-share 1.5`, `--retention 0`, `--months 0` must error. Keep this for new flags.
- Parameters without a flag are edited in `MY_CHANNEL` in `main.py`.
- README sample output/niche table come from the default scenario; re-run and update them if defaults or formulas change.
- Under defaults, sponsorships dominate revenue, so niche changes total revenue only ~8% — that's an assumption-driven result, not a finding.

## Conventions (shared across the owner's portfolio repos)

- Plain Python 3.11+ CLI: `main.py` (argparse) at the root, logic in `src/`, tests in `tests/`. No package build, no lint/format config.
- `pytest.ini` sets `testpaths = tests` and `pythonpath = .`, so run `pytest` from the repo root.
- CI (`.github/workflows/tests.yml`): `pip install -r requirements.txt` + `pytest -q` on Python 3.11 and 3.12, on every push and PR. Tests must stay offline (no network, no API keys).
- Generated files go to `output/` (gitignored). Never commit them.
- README is English with a Spanish `> **Resumen:**` blurb at the top; it documents formulas and limitations precisely. When you change behaviour, update the README in the same change (tests often pin the documented formulas).
- Be honest about scope: the README's "Limitations" section is part of the product. Don't add claims the code doesn't support.

## Memoria persistente (Graphiti MCP)
Este proyecto usa el connector **Graphiti** (memoria en grafo compartida entre sesiones).
- `group_id` de este repo: `youtube-revenue-simulator`. Datos del usuario y transversales: `neckr0ik-global`.
- Al empezar una tarea: busca contexto con `search_memory_facts` y `search_nodes` usando `group_ids: ["youtube-revenue-simulator", "neckr0ik-global"]`.
- Al terminar algo relevante (decisión de arquitectura, convención nueva, bug resuelto y su causa, preferencia del usuario, estado de un despliegue): guárdalo con `add_memory` (`group_id: "youtube-revenue-simulator"`, `source: "text"`) con un nombre descriptivo.
- Nunca guardes secretos, API keys, tokens, contraseñas ni datos personales sensibles.
- Si Graphiti no está disponible en la sesión, continúa normalmente.
