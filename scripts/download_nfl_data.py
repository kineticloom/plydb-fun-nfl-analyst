#!/usr/bin/env python3
"""
Download NFL data from nflverse-data GitHub releases and save as Parquet files.

Files are fetched directly from GitHub release assets (no third-party packages
needed beyond Python stdlib). Output is laid out in a Hive-partitioned structure
for use with PlyDB.

Output layout:
  data/nflverse/pbp/Season={year}/pbp.parquet
  data/nflverse/player_stats_reg/Season={year}/player_stats_reg.parquet
  data/nflverse/player_stats_week/Season={year}/player_stats_week.parquet
  data/nflverse/rosters/Season={year}/rosters.parquet
  data/nflverse/snap_counts/Season={year}/snap_counts.parquet
  data/nflverse/schedules/schedules.parquet
  data/nflverse/ngs_passing/ngs_passing.parquet
  data/nflverse/ngs_receiving/ngs_receiving.parquet
  data/nflverse/ngs_rushing/ngs_rushing.parquet
  data/nflverse/pfr_advstats_pass/pfr_advstats_pass.parquet
  data/nflverse/pfr_advstats_rush/pfr_advstats_rush.parquet
  data/nflverse/pfr_advstats_rec/pfr_advstats_rec.parquet
  data/nflverse/pfr_advstats_def/pfr_advstats_def.parquet
  data/nflverse/combine/combine.parquet
  data/nflverse/draft_picks/draft_picks.parquet
  data/nflverse/players/players.parquet

Examples:
  # Recommended starting point: core datasets for 2023–2024
  python scripts/download_nfl_data.py --start-season 2023 --end-season 2024

  # Full play-by-play for a specific season (large: ~20 MB each)
  python scripts/download_nfl_data.py --start-season 2024 --datasets pbp

  # Player stats for multiple seasons
  python scripts/download_nfl_data.py --start-season 2020 --end-season 2024 \\
      --datasets player_stats_reg

  # Static reference tables (no season needed)
  python scripts/download_nfl_data.py --datasets players schedules combine draft_picks

  # NextGen Stats and PFR advanced stats (all-seasons single files)
  python scripts/download_nfl_data.py \\
      --datasets ngs_passing ngs_receiving ngs_rushing \\
      --datasets pfr_advstats_pass pfr_advstats_rush pfr_advstats_rec pfr_advstats_def

  # List all available datasets
  python scripts/download_nfl_data.py --list-datasets
"""

import argparse
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "nflverse"
BASE_URL = "https://github.com/nflverse/nflverse-data/releases/download"

CURRENT_SEASON = 2025


# ---------------------------------------------------------------------------
# Dataset registry
# ---------------------------------------------------------------------------


@dataclass
class DatasetSpec:
    release: str        # nflverse GitHub release tag
    file_pattern: str   # remote filename; use {year} for seasonal datasets
    local_dir: str      # subdirectory under DATA_DIR
    local_file: str     # output filename
    seasonal: bool      # True = Season={year}/ Hive partition
    first_year: int     # earliest available season (0 if not seasonal)
    description: str


DATASET_REGISTRY: dict[str, DatasetSpec] = {
    "pbp": DatasetSpec(
        release="pbp",
        file_pattern="play_by_play_{year}.parquet",
        local_dir="pbp",
        local_file="pbp.parquet",
        seasonal=True,
        first_year=1999,
        description="Play-by-play data (370+ cols: EPA, WPA, down/distance, player IDs, Vegas lines). ~20 MB/season.",
    ),
    "player_stats_reg": DatasetSpec(
        release="stats_player",
        file_pattern="stats_player_reg_{year}.parquet",
        local_dir="player_stats_reg",
        local_file="player_stats_reg.parquet",
        seasonal=True,
        first_year=2023,
        description="Regular-season cumulative stats per player (all positions: QB, RB, WR, TE, K, defense). ~140 KB/season.",
    ),
    "player_stats_week": DatasetSpec(
        release="stats_player",
        file_pattern="stats_player_week_{year}.parquet",
        local_dir="player_stats_week",
        local_file="player_stats_week.parquet",
        seasonal=True,
        first_year=2023,
        description="Weekly player stats (all positions). One row per player per week. ~600 KB/season.",
    ),
    "player_stats_post": DatasetSpec(
        release="stats_player",
        file_pattern="stats_player_post_{year}.parquet",
        local_dir="player_stats_post",
        local_file="player_stats_post.parquet",
        seasonal=True,
        first_year=2023,
        description="Postseason cumulative stats per player (all positions). ~40 KB/season.",
    ),
    "rosters": DatasetSpec(
        release="rosters",
        file_pattern="roster_{year}.parquet",
        local_dir="rosters",
        local_file="rosters.parquet",
        seasonal=True,
        first_year=1920,
        description="Weekly roster snapshots: player name, position, team, status, jersey number. ~34 KB/season.",
    ),
    "snap_counts": DatasetSpec(
        release="snap_counts",
        file_pattern="snap_counts_{year}.parquet",
        local_dir="snap_counts",
        local_file="snap_counts.parquet",
        seasonal=True,
        first_year=2012,
        description="Weekly offensive, defensive, and special teams snap counts and percentages per player. ~210 KB/season.",
    ),
    "schedules": DatasetSpec(
        release="schedules",
        file_pattern="games.parquet",
        local_dir="schedules",
        local_file="schedules.parquet",
        seasonal=False,
        first_year=0,
        description="All game schedules and results (1999–present). Vegas lines, weather, stadium, coaches. ~500 KB.",
    ),
    "ngs_passing": DatasetSpec(
        release="nextgen_stats",
        file_pattern="ngs_passing.parquet",
        local_dir="ngs_passing",
        local_file="ngs_passing.parquet",
        seasonal=False,
        first_year=0,
        description="NFL NextGen Stats for passers: avg time to throw, aggressiveness, completion % above expected. ~700 KB.",
    ),
    "ngs_receiving": DatasetSpec(
        release="nextgen_stats",
        file_pattern="ngs_receiving.parquet",
        local_dir="ngs_receiving",
        local_file="ngs_receiving.parquet",
        seasonal=False,
        first_year=0,
        description="NFL NextGen Stats for receivers: avg separation, YAC above expected, catch %. ~1 MB.",
    ),
    "ngs_rushing": DatasetSpec(
        release="nextgen_stats",
        file_pattern="ngs_rushing.parquet",
        local_dir="ngs_rushing",
        local_file="ngs_rushing.parquet",
        seasonal=False,
        first_year=0,
        description="NFL NextGen Stats for rushers: rush yards over expected (RYOE), efficiency rating. ~370 KB.",
    ),
    "pfr_advstats_pass": DatasetSpec(
        release="pfr_advstats",
        file_pattern="advstats_season_pass.parquet",
        local_dir="pfr_advstats_pass",
        local_file="pfr_advstats_pass.parquet",
        seasonal=False,
        first_year=0,
        description="PFR advanced passing stats: pressure rate, time in pocket, ADOT, bad throw %, on-target %. ~400 KB.",
    ),
    "pfr_advstats_rush": DatasetSpec(
        release="pfr_advstats",
        file_pattern="advstats_season_rush.parquet",
        local_dir="pfr_advstats_rush",
        local_file="pfr_advstats_rush.parquet",
        seasonal=False,
        first_year=0,
        description="PFR advanced rushing stats: broken tackles, yards before/after first contact. ~300 KB.",
    ),
    "pfr_advstats_rec": DatasetSpec(
        release="pfr_advstats",
        file_pattern="advstats_season_rec.parquet",
        local_dir="pfr_advstats_rec",
        local_file="pfr_advstats_rec.parquet",
        seasonal=False,
        first_year=0,
        description="PFR advanced receiving stats: drop rate, target separation, yards after catch. ~350 KB.",
    ),
    "pfr_advstats_def": DatasetSpec(
        release="pfr_advstats",
        file_pattern="advstats_season_def.parquet",
        local_dir="pfr_advstats_def",
        local_file="pfr_advstats_def.parquet",
        seasonal=False,
        first_year=0,
        description="PFR advanced defensive stats: missed tackle rate, pressures, blitz rate, coverage. ~300 KB.",
    ),
    "combine": DatasetSpec(
        release="combine",
        file_pattern="combine.parquet",
        local_dir="combine",
        local_file="combine.parquet",
        seasonal=False,
        first_year=0,
        description="NFL Combine measurements: 40-yard dash, bench press, vertical leap, broad jump, 3-cone, shuttle. ~365 KB.",
    ),
    "draft_picks": DatasetSpec(
        release="draft_picks",
        file_pattern="draft_picks.parquet",
        local_dir="draft_picks",
        local_file="draft_picks.parquet",
        seasonal=False,
        first_year=0,
        description="NFL Draft picks with career approximate value (w_av), drafting team, and position. ~680 KB.",
    ),
    "players": DatasetSpec(
        release="players",
        file_pattern="players.parquet",
        local_dir="players",
        local_file="players.parquet",
        seasonal=False,
        first_year=0,
        description="Player ID register: gsis_id (primary), pfr_id, espn_id, pff_id, name, position, status. ~3 MB.",
    ),
}

DEFAULT_DATASETS = ["pbp", "player_stats_reg", "schedules", "players"]
SEASON_REQUIRED = {k for k, v in DATASET_REGISTRY.items() if v.seasonal}


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------


def _fetch(url: str, dest: Path, label: str) -> bool:
    """Download url to dest atomically via a temp file. Returns True on success."""
    tmp = dest.with_suffix(".tmp.parquet")
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, 4):
        try:
            print(f"  Fetching {label} …", end=" ", flush=True)
            urllib.request.urlretrieve(url, tmp)
            size_kb = tmp.stat().st_size // 1024
            tmp.rename(dest)
            print(f"{size_kb:,} KB → {dest.relative_to(ROOT)}")
            return True
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                print(f"not found (404) — skipping")
                tmp.unlink(missing_ok=True)
                return False
            print(f"HTTP {exc.code} (attempt {attempt}/3)")
        except Exception as exc:  # noqa: BLE001
            print(f"error: {exc} (attempt {attempt}/3)")
        tmp.unlink(missing_ok=True)
        if attempt < 3:
            time.sleep(2**attempt)
    print(f"  [error] failed after 3 attempts: {url}", file=sys.stderr)
    return False


def download_static(key: str) -> None:
    spec = DATASET_REGISTRY[key]
    dest = DATA_DIR / spec.local_dir / spec.local_file
    if dest.exists():
        print(f"  [skip] {dest.relative_to(ROOT)} — already exists")
        return
    url = f"{BASE_URL}/{spec.release}/{spec.file_pattern}"
    _fetch(url, dest, key)


def download_seasonal(key: str, year: int, force: bool = False) -> None:
    spec = DATASET_REGISTRY[key]
    dest = DATA_DIR / spec.local_dir / f"Season={year}" / spec.local_file
    if dest.exists() and not force:
        print(f"  [skip] {dest.relative_to(ROOT)} — already exists")
        return
    filename = spec.file_pattern.format(year=year)
    url = f"{BASE_URL}/{spec.release}/{filename}"
    _fetch(url, dest, f"{key} {year}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download NFL data from nflverse-data GitHub releases to Parquet files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--start-season",
        type=int,
        metavar="YEAR",
        help="First season to download, e.g. 2024. Required for season-partitioned datasets.",
    )
    parser.add_argument(
        "--end-season",
        type=int,
        metavar="YEAR",
        help="Last season to download inclusive (default: same as --start-season).",
    )
    parser.add_argument(
        "--datasets",
        nargs="+",
        default=DEFAULT_DATASETS,
        choices=sorted(DATASET_REGISTRY.keys()),
        metavar="DATASET",
        help=(
            f"Dataset(s) to download (default: {' '.join(DEFAULT_DATASETS)}). "
            f"Choices: {', '.join(sorted(DATASET_REGISTRY.keys()))}"
        ),
    )
    parser.add_argument(
        "--list-datasets",
        action="store_true",
        help="Print available datasets with descriptions and exit.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download files that already exist.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_datasets:
        print("\nAvailable datasets:\n")
        width = max(len(k) for k in DATASET_REGISTRY)
        for key, spec in sorted(DATASET_REGISTRY.items()):
            tag = f"seasonal {spec.first_year}+" if spec.seasonal else "static"
            print(f"  {key:<{width}}  [{tag:<14}]  {spec.description}")
        print()
        return

    datasets = args.datasets
    seasonal = [d for d in datasets if DATASET_REGISTRY[d].seasonal]
    static = [d for d in datasets if not DATASET_REGISTRY[d].seasonal]

    if seasonal and args.start_season is None:
        names = ", ".join(seasonal)
        print(
            f"ERROR: --start-season YEAR is required for: {names}\n"
            "       (Non-seasonal datasets can be downloaded without it.)",
            file=sys.stderr,
        )
        sys.exit(1)

    start = args.start_season
    end = args.end_season if args.end_season is not None else start
    if start and end and end < start:
        print("ERROR: --end-season must be >= --start-season.", file=sys.stderr)
        sys.exit(1)

    if static:
        print("\nDownloading static datasets …")
        for key in static:
            download_static(key)

    if seasonal:
        for year in range(start, end + 1):
            print(f"\n{'=' * 60}\nSeason {year}\n{'=' * 60}")
            for key in seasonal:
                download_seasonal(key, year, force=args.force)

    print("\nDone.")


if __name__ == "__main__":
    main()
