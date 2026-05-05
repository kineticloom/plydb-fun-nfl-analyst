# NFL Analyst

Accompanying [blog post](https://www.plydb.com/blog/plydb-fun-nfl-analyst/).

---

Bring your own AI agent and ask questions about NFL data in plain English — no
SQL required.

```
> Which quarterbacks perform best in close games in the fourth quarter?
> Do teams that invest heavily in offensive line draft picks win more?
> Which wide receivers generate the most separation but are chronically undertargeted?
```

Under the hood: [nflverse](https://github.com/nflverse/nflverse-data) provides
the data as Parquet files, [PlyDB](https://www.plydb.com/) gives your agent
unified SQL access to local files, and your agent handles the rest — no
warehouse, no ETL, no cloud.

---

## Workflow

1. [Install prerequisites](#step-1--install-prerequisites)
2. [Download NFL data](#step-2--download-nfl-data)
3. [Configure PlyDB](#step-3--configure-plydb)
4. [Start analyzing](#step-4--start-analyzing)

---

## Step 1 — Install prerequisites

### PlyDB

PlyDB is the database gateway that gives your AI agent unified SQL access to
local data files. Your agent translates your questions into SQL; PlyDB executes
them.

**New to PlyDB?** The [PlyDB quickstart](https://www.plydb.com/docs/quickstart/)
walks through installation, config, and your first queries end-to-end.

### Python

The download script requires Python 3.9+ with `pyarrow`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install pyarrow
```

> `pyarrow` is needed only to read back file sizes and verify downloads. The
> script uses only Python's built-in `urllib.request` to fetch files — no
> third-party HTTP clients required.

---

## Step 2 — Download NFL data

`scripts/download_nfl_data.py` fetches Parquet files directly from
[nflverse-data](https://github.com/nflverse/nflverse-data) GitHub releases and
writes them to `data/nflverse/`.

### Output layout

```
data/nflverse/
├── pbp/
│   └── Season={year}/
│       └── pbp.parquet
├── player_stats_offense/
│   └── Season={year}/
│       └── player_stats_offense.parquet
├── player_stats_defense/
│   └── Season={year}/
│       └── player_stats_defense.parquet
├── player_stats_kicking/
│   └── Season={year}/
│       └── player_stats_kicking.parquet
├── rosters/
│   └── Season={year}/
│       └── rosters.parquet
├── snap_counts/
│   └── Season={year}/
│       └── snap_counts.parquet
├── schedules/
│   └── schedules.parquet
├── ngs_passing/
│   └── ngs_passing.parquet
├── ngs_receiving/
│   └── ngs_receiving.parquet
├── ngs_rushing/
│   └── ngs_rushing.parquet
├── pfr_advstats_pass/
│   └── pfr_advstats_pass.parquet
├── pfr_advstats_rush/
│   └── pfr_advstats_rush.parquet
├── pfr_advstats_rec/
│   └── pfr_advstats_rec.parquet
├── pfr_advstats_def/
│   └── pfr_advstats_def.parquet
├── combine/
│   └── combine.parquet
├── draft_picks/
│   └── draft_picks.parquet
└── players/
    └── players.parquet
```

Re-running the script skips files that already exist, so downloads are
resumable.

### Quick start

```bash
# List available datasets
python scripts/download_nfl_data.py --list-datasets

# Download core datasets: play-by-play + offensive stats + schedule + player IDs (2023–2024)
python scripts/download_nfl_data.py --start-season 2023 --end-season 2024

# Play-by-play only for one season (~20 MB)
python scripts/download_nfl_data.py --start-season 2024 --datasets pbp

# Player stats for multiple seasons
python scripts/download_nfl_data.py --start-season 2023 --end-season 2024 \
    --datasets player_stats_reg player_stats_week

# Static reference tables (no season needed)
python scripts/download_nfl_data.py --datasets players schedules combine draft_picks

# NextGen Stats and PFR advanced stats (all-seasons single files)
python scripts/download_nfl_data.py \
    --datasets ngs_passing ngs_receiving ngs_rushing \
    pfr_advstats_pass pfr_advstats_rush pfr_advstats_rec pfr_advstats_def
```

### All options

| Flag              | Description                                            | Default                                              |
| ----------------- | ------------------------------------------------------ | ---------------------------------------------------- |
| `--start-season`  | First season to download (required for seasonal data)  | —                                                    |
| `--end-season`    | Last season to download inclusive                      | same as `--start-season`                             |
| `--datasets`      | Dataset(s) to download (see below)                     | `pbp player_stats_offense schedules players`         |
| `--list-datasets` | Print available datasets and exit                      | —                                                    |
| `--force`         | Re-download files that already exist                   | off                                                  |

### Datasets

| Dataset | Partition | Source | Description |
| --- | --- | --- | --- |
| `pbp` | Season | nflverse-data | One row per play; EPA, WPA, down/distance, player IDs (1999+). ~20 MB/season |
| `player_stats_reg` | Season | nflverse-data | Regular-season cumulative stats, all positions (QB/RB/WR/TE/K/DEF). ~140 KB/season (2023+) |
| `player_stats_week` | Season | nflverse-data | Weekly player stats, all positions. ~600 KB/season (2023+) |
| `player_stats_post` | Season | nflverse-data | Postseason cumulative stats, all positions. ~40 KB/season (2023+) |
| `rosters` | Season | nflverse-data | Weekly roster snapshots: name, position, status (1920+) |
| `snap_counts` | Season | nflverse-data | Weekly offensive/defensive/ST snap counts and percentages (2012+) |
| `schedules` | (none) | nflverse-data | All game schedules and results; Vegas lines, weather, coaches (1999+) |
| `ngs_passing` | (none) | nflverse-data | NextGen Stats: time to throw, aggressiveness, CPAE (2016+) |
| `ngs_receiving` | (none) | nflverse-data | NextGen Stats: receiver separation, YAC above expected (2016+) |
| `ngs_rushing` | (none) | nflverse-data | NextGen Stats: rush yards over expected (RYOE), efficiency (2016+) |
| `pfr_advstats_pass` | (none) | nflverse-data | PFR: pressure rate, on-target %, bad throw %, ADOT (2018+) |
| `pfr_advstats_rush` | (none) | nflverse-data | PFR: broken tackles, yards before/after contact (2018+) |
| `pfr_advstats_rec` | (none) | nflverse-data | PFR: drop rate, target separation, YAC (2018+) |
| `pfr_advstats_def` | (none) | nflverse-data | PFR: pressures, missed tackle rate, coverage stats (2018+) |
| `combine` | (none) | nflverse-data | NFL Combine: 40-yard dash, bench press, vertical, cone, shuttle |
| `draft_picks` | (none) | nflverse-data | NFL Draft picks with career approximate value (w_av) (1936+) |
| `players` | (none) | nflverse-data | Player ID register: gsis_id, pfr_id, espn_id, name, position |

> **Note on play-by-play size:** Each season of `pbp` is roughly 15–25 MB.
> Downloading 10+ seasons requires 150–250 MB of disk space for this table alone.

---

## Step 3 — Configure PlyDB

`plydb-config-example.json` contains a ready-to-use PlyDB config that registers
all 17 datasets. Copy it and comment out or remove any tables for datasets you
haven't downloaded yet.

```bash
cp plydb-config-example.json plydb-config.json
```

---

## Step 4 — Start analyzing

Open Claude Code (or any PlyDB-compatible agent) in this directory and start
asking questions. The agent will translate your questions into SQL, run them
against the local Parquet files via PlyDB, and return results.

### Sample prompts

**Who are the clutch quarterbacks?** Compare each QB's EPA/play and win
probability added in close games (score within 7) vs. blowouts over the last
three seasons. Which QBs actually elevate when the game is on the line — and
which ones pad stats in garbage time?

**The fourth-down revolution:** Track fourth-down conversion attempt rates by
head coach and season. Which coaches are leading the analytics-driven movement
away from punting, and does going for it more actually translate to more wins?

**Does home-field advantage still exist?** Using game schedules, compare home
win percentage before 2020, during the empty-stadium 2020 season, and from
2021 onward by team and venue type (dome vs. outdoor). Did crowds actually
matter?

**Open but underutilized receivers:** Join NextGen Stats receiving
(avg_separation) with player offensive stats (target_share, wopr) and snap
counts. Which wide receivers consistently create the most separation from
defenders yet see a below-average share of their team's targets?

**Pressure and QB performance:** Which QBs maintain the highest EPA per play
under pressure? Join PFR advanced passing stats (pressure_pct) with pbp EPA
and offensive stats. Does a QB's ability to handle pressure predict breakouts
or breakdowns in the following season?

**The draft value curve:** Using draft picks, chart career approximate value
(w_av) by overall pick number and position. Join combine results to find which
athletic testing metrics (40 time, vertical, etc.) best predict NFL success at
each position — and which combine workouts are just noise.

**Snap efficiency: hidden breakout candidates:** Identify skill players who
produce high EPA per snap on limited playing time. Join snap_counts with pbp
and player stats to find receivers and backs who could break out if given more
opportunity.

**EPA by play type, down, and distance:** Which teams deviate most from
league-average pass/run balance on early downs? Does running more on first down
actually help — or do the teams that pass more consistently generate better EPA?

---

## Data sources

| Source | Description |
| --- | --- |
| [nflverse-data](https://github.com/nflverse/nflverse-data) | Primary data repository for all tables |
| [nflfastR](https://www.nflfastr.com/) | Play-by-play model documentation (EPA, WPA, win probability) |
| [nflreadr](https://nflreadr.nflverse.com/) | R package with full dataset documentation |

---

## Reference

- [nflverse-data releases](https://github.com/nflverse/nflverse-data/releases) —
  raw data files and release notes
- [nflfastR field definitions](https://www.nflfastr.com/articles/field_descriptions.html) —
  column-level reference for the pbp dataset
- [PlyDB documentation](https://www.plydb.com/docs/) — full PlyDB reference
