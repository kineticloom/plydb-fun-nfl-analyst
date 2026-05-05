# NFL Data Dictionary

Column-level reference for all 17 tables in the nflverse NFL dataset.

---

## Table of Contents

1. [pbp — Play-by-Play](#pbp--play-by-play)
2. [player_stats_reg — Player Stats (Regular Season)](#player_stats_reg--player-stats-regular-season)
3. [player_stats_week — Player Stats (Weekly)](#player_stats_week--player-stats-weekly)
4. [player_stats_post — Player Stats (Postseason)](#player_stats_post--player-stats-postseason)
5. [rosters — Weekly Rosters](#rosters--weekly-rosters)
6. [snap_counts — Snap Counts](#snap_counts--snap-counts)
7. [schedules — Game Schedules and Results](#schedules--game-schedules-and-results)
8. [ngs_passing — NextGen Stats Passing](#ngs_passing--nextgen-stats-passing)
9. [ngs_receiving — NextGen Stats Receiving](#ngs_receiving--nextgen-stats-receiving)
10. [ngs_rushing — NextGen Stats Rushing](#ngs_rushing--nextgen-stats-rushing)
11. [pfr_advstats_pass — PFR Advanced Passing](#pfr_advstats_pass--pfr-advanced-passing)
12. [pfr_advstats_rush — PFR Advanced Rushing](#pfr_advstats_rush--pfr-advanced-rushing)
13. [pfr_advstats_rec — PFR Advanced Receiving](#pfr_advstats_rec--pfr-advanced-receiving)
14. [pfr_advstats_def — PFR Advanced Defense](#pfr_advstats_def--pfr-advanced-defense)
15. [combine — NFL Combine](#combine--nfl-combine)
16. [draft_picks — NFL Draft Picks](#draft_picks--nfl-draft-picks)
17. [players — Player ID Register](#players--player-id-register)

---

## pbp — Play-by-Play

**Source:** nflverse-data `pbp` release  
**Granularity:** One row per play  
**Coverage:** 1999–present  
**Primary key:** `game_id`, `play_id`  
**Size:** ~20 MB per season; ~400+ columns

The richest table. Every scrimmage play in the NFL with game state, player IDs,
outcomes, and advanced metrics. EPA and WPA are available from 1999; NextGen-style
fields (cpoe, xpass) are available from approximately 2006+.

### Identity and Game Context

| Column | Type | Description |
|---|---|---|
| `game_id` | string | Unique game identifier: `{season}_{week:02d}_{away}_{home}` (e.g. `2024_01_KC_BAL`). Joins to `schedules.game_id`. |
| `play_id` | integer | Unique play identifier within the game. |
| `season` | integer | NFL season year (e.g. 2024). |
| `week` | integer | Week number (1–18 regular season; 19–22 playoffs). |
| `season_type` | string | `'REG'` = regular season; `'POST'` = playoffs. |
| `game_type` | string | `'REG'`, `'WC'`, `'DIV'`, `'CON'`, `'SB'`. |
| `game_date` | date | Date the game was played. |
| `home_team` | string | Home team 3-letter abbreviation. |
| `away_team` | string | Away team 3-letter abbreviation. |
| `posteam` | string | Team with possession (offense). |
| `defteam` | string | Defending team. |
| `posteam_type` | string | `'home'` or `'away'`. |

### Game State

| Column | Type | Description |
|---|---|---|
| `down` | integer | Down number (1–4). NULL on kickoffs, extra points. |
| `ydstogo` | integer | Yards needed for a first down. |
| `yardline_100` | integer | Yards from the offensive end zone (1–99). |
| `quarter_seconds_remaining` | integer | Seconds left in the current quarter. |
| `half_seconds_remaining` | integer | Seconds left in the current half. |
| `game_seconds_remaining` | integer | Seconds left in the game (including OT). |
| `score_differential` | integer | `posteam_score - defteam_score` at play start. |
| `posteam_score` | integer | Offensive team's score before the play. |
| `defteam_score` | integer | Defensive team's score before the play. |

### Play Type and Outcome

| Column | Type | Description |
|---|---|---|
| `play_type` | string | `'pass'`, `'run'`, `'punt'`, `'field_goal'`, `'kickoff'`, `'extra_point'`, `'two_point_attempt'`, `'no_play'`, `'qb_kneel'`, `'qb_spike'`. |
| `qb_scramble` | integer | 1 if the QB scrambled (coded as a run but initiated as a pass). |
| `yards_gained` | integer | Net yards gained on the play. |
| `passing_yards` | integer | Yards credited to the QB (completed passes only). |
| `rushing_yards` | integer | Rushing yards on the play. |
| `receiving_yards` | integer | Receiving yards on the play. |
| `return_yards` | integer | Return yards on punts/kickoffs. |
| `complete_pass` | integer | 1 = completed pass. |
| `incomplete_pass` | integer | 1 = incomplete pass. |
| `interception` | integer | 1 = interception. |
| `touchdown` | integer | 1 = any touchdown scored. |
| `pass_touchdown` | integer | 1 = passing touchdown. |
| `rush_touchdown` | integer | 1 = rushing touchdown. |
| `return_touchdown` | integer | 1 = return touchdown. |
| `fumble` | integer | 1 = fumble occurred. |
| `fumble_lost` | integer | 1 = fumble lost to the defense. |
| `sack` | integer | 1 = QB sack. |
| `field_goal_result` | string | `'made'`, `'missed'`, `'blocked'`, or NULL. |
| `extra_point_result` | string | `'good'`, `'failed'`, `'blocked'`, or NULL. |
| `two_point_conv_result` | string | `'success'`, `'failure'`, or NULL. |
| `fourth_down_converted` | integer | 1 = converted on 4th down. |
| `fourth_down_failed` | integer | 1 = failed to convert on 4th down. |
| `third_down_converted` | integer | 1 = converted on 3rd down. |

### Player Identity

| Column | Type | Description |
|---|---|---|
| `passer_id` | string | `gsis_id` of the QB on pass plays. Join to `players.gsis_id`. |
| `passer_player_name` | string | Short display name of the passer (e.g. `"P.Mahomes"`). |
| `rusher_id` | string | `gsis_id` of the ball carrier on run plays. |
| `rusher_player_name` | string | Short display name of the rusher. |
| `receiver_id` | string | `gsis_id` of the intended receiver on pass plays. |
| `receiver_player_name` | string | Short display name of the receiver. |
| `id` | string | `gsis_id` of the primary player on the play. |
| `name` | string | Short name of the primary player. |
| `fantasy_player_id` | string | `gsis_id` used for fantasy scoring (= `passer_id` for passes, `rusher_id` for runs, `receiver_id` for catches). |

### Advanced Metrics

| Column | Type | Description |
|---|---|---|
| `epa` | float | Expected Points Added. The key play efficiency metric. |
| `qb_epa` | float | EPA adjusted to remove receiver YAC; isolates passer contribution. |
| `success` | integer | 1 if `epa > 0` (successful play), 0 otherwise. |
| `wpa` | float | Win Probability Added. |
| `vegas_wpa` | float | WPA using a spread-adjusted win probability model. |
| `wp` | float | Win probability for the possession team at play start. |
| `vegas_wp` | float | Spread-adjusted win probability at play start. |
| `xpass` | float | Predicted pass probability given game state (down, distance, score, time). |
| `pass_oe` | float | Pass rate over expected: `actual_pass - xpass`. Positive = more aggressive. |
| `cpoe` | float | Completion Percentage Over Expected on this play. |
| `xyac_epa` | float | Expected EPA from yards after catch based on catch location. |
| `xyac_success` | float | Probability the YAC contributes a successful EPA. |

### Passing Detail

| Column | Type | Description |
|---|---|---|
| `air_yards` | float | Distance from line of scrimmage to target location. Negative = behind LOS (screens). |
| `yards_after_catch` | float | Yards gained after the catch. |
| `pass_location` | string | `'left'`, `'middle'`, `'right'` — horizontal field zone. |
| `pass_length` | string | `'short'` (< 15 air yards) or `'deep'` (15+ air yards). |
| `qb_dropback` | integer | 1 if the QB dropped back (pass, scramble, or sack). |
| `no_huddle` | integer | 1 if the offense used a no-huddle snap. |
| `shotgun` | integer | 1 if the QB was in shotgun formation. |
| `out_of_pocket_pass` | integer | 1 if the QB threw from outside the pocket. |

### Game Context

| Column | Type | Description |
|---|---|---|
| `spread_line` | float | Pre-game Vegas point spread (negative = home favored). |
| `total_line` | float | Pre-game Vegas over/under total. |
| `roof` | string | Stadium roof: `'outdoors'`, `'dome'`, `'closed'`, `'open'`, `'retractable'`. |
| `surface` | string | Playing surface (e.g. `'grass'`, `'astroturf'`, `'fieldturf'`). |
| `temp` | float | Game-time temperature in °F. NULL for dome games. |
| `wind` | float | Wind speed in mph. NULL for dome games. |

---

## player_stats_reg — Player Stats (Regular Season)

**Source:** nflverse-data `stats_player` release (`stats_player_reg_{year}.parquet`)  
**Granularity:** One row per player per season  
**Coverage:** 2023–present  
**Primary key:** `player_id`, `season`

Regular-season cumulative stats for all positions (QB, RB, WR, TE, K, defense) in one table. For weekly granularity see `player_stats_week`; for postseason see `player_stats_post`.

### Identity

| Column | Type | Description |
|---|---|---|
| `player_id` | string | Player's `gsis_id`. Join to `players.gsis_id`. |
| `player_name` | string | Short player name. |
| `player_display_name` | string | Full display name (preferred). |
| `position` | string | Primary position (QB, RB, WR, TE, etc.). |
| `position_group` | string | Broader position group. |
| `recent_team` | string | Team at end of season. |
| `season` | integer | NFL season year. |
| `season_type` | string | `'REG'` or `'POST'`. |
| `week` | integer | Week number (NULL or 0 for season totals). |

### Passing

| Column | Type | Description |
|---|---|---|
| `completions` | integer | Completed passes. |
| `attempts` | integer | Pass attempts. |
| `passing_yards` | float | Total passing yards. |
| `passing_tds` | integer | Passing touchdowns. |
| `interceptions` | integer | Interceptions thrown. |
| `sacks` | float | Times sacked. |
| `sack_yards` | float | Yards lost to sacks. |
| `sack_fumbles` | integer | Fumbles on sack plays. |
| `sack_fumbles_lost` | integer | Fumbles lost on sack plays. |
| `passing_air_yards` | float | Total air yards on all pass attempts. |
| `passing_yards_after_catch` | float | Total YAC on completed passes. |
| `passing_first_downs` | integer | First downs generated by passing. |
| `passing_epa` | float | Total EPA added on passing plays. |
| `passing_2pt_conversions` | integer | Successful 2-point conversion passes. |
| `pacr` | float | Passing Air Conversion Ratio: `passing_yards / air_yards`. |
| `dakota` | float | Adjusted passing + rushing EPA; the best single QB efficiency metric. |
| `cpoe` | float | Average Completion Percentage Over Expected across all pass attempts. |

### Rushing

| Column | Type | Description |
|---|---|---|
| `carries` | integer | Rush attempts. |
| `rushing_yards` | float | Total rushing yards. |
| `rushing_tds` | integer | Rushing touchdowns. |
| `rushing_fumbles` | integer | Fumbles on rush plays. |
| `rushing_fumbles_lost` | integer | Fumbles lost on rush plays. |
| `rushing_first_downs` | integer | First downs gained rushing. |
| `rushing_epa` | float | Total EPA added on rushing plays. |
| `rushing_2pt_conversions` | integer | Successful 2-point conversion runs. |

### Receiving

| Column | Type | Description |
|---|---|---|
| `receptions` | integer | Passes caught. |
| `targets` | integer | Times targeted (caught + dropped + incomplete + TD + INT). |
| `receiving_yards` | float | Total receiving yards. |
| `receiving_tds` | integer | Receiving touchdowns. |
| `receiving_fumbles` | integer | Fumbles on receiving plays. |
| `receiving_fumbles_lost` | integer | Fumbles lost after receptions. |
| `receiving_air_yards` | float | Air yards on all targets. |
| `receiving_yards_after_catch` | float | Total YAC on receptions. |
| `receiving_first_downs` | integer | First downs gained receiving. |
| `receiving_epa` | float | Total EPA added on receiving plays. |
| `receiving_2pt_conversions` | integer | Successful 2-point receiving conversions. |
| `target_share` | float | Fraction of team targets (0–1). |
| `air_yards_share` | float | Fraction of team air yards (0–1). |
| `wopr` | float | Weighted Opportunity Rating: `0.7 × target_share + 0.5 × air_yards_share`. |
| `racr` | float | Receiver Air Conversion Ratio: `receiving_yards / air_yards`. |

### Special Teams and Fantasy

| Column | Type | Description |
|---|---|---|
| `special_teams_tds` | integer | Special teams touchdowns (returns, etc.). |
| `fantasy_points` | float | Standard scoring fantasy points. |
| `fantasy_points_ppr` | float | PPR (Points Per Reception) fantasy points. |

---

## player_stats_week — Player Stats (Weekly)

**Source:** nflverse-data `stats_player` release (`stats_player_week_{year}.parquet`)  
**Granularity:** One row per player per week  
**Coverage:** 2023–present  
**Primary key:** `player_id`, `season`, `week`

Same columns as `player_stats_reg` but at weekly granularity. Includes a `week` column for time filtering. Useful for weekly trend analysis, injury-impact studies, and matchup breakdowns.

---

## player_stats_post — Player Stats (Postseason)

**Source:** nflverse-data `stats_player` release (`stats_player_post_{year}.parquet`)  
**Granularity:** One row per player per season  
**Coverage:** 2023–present  
**Primary key:** `player_id`, `season`

Same columns as `player_stats_reg` but covering only postseason (playoff) games. Useful for comparing regular-season vs. playoff performance.

---

## rosters — Weekly Rosters

**Source:** nflverse-data `rosters` release  
**Granularity:** One row per player per week per season  
**Coverage:** 1920–present  
**Primary key:** `gsis_id`, `season`, `week`, `team`

| Column | Type | Description |
|---|---|---|
| `season` | integer | NFL season year. |
| `team` | string | Team abbreviation. |
| `position` | string | Position (QB, RB, WR, TE, OL, DL, LB, CB, S, K, P, etc.). |
| `depth_chart_position` | string | More specific position (e.g. `'EDGE'`, `'SAF'`). |
| `jersey_number` | integer | Jersey number. |
| `status` | string | Roster status (see `players` table for values). |
| `full_name` | string | Player's full name. |
| `first_name` | string | First name. |
| `last_name` | string | Last name. |
| `birth_date` | date | Date of birth. |
| `height` | integer | Height in inches. |
| `weight` | integer | Weight in pounds. |
| `college` | string | College attended. |
| `gsis_id` | string | `gsis_id`. Join to `players.gsis_id`. |
| `espn_id` | integer | ESPN player ID. |
| `sportradar_id` | string | Sportradar player ID. |
| `yahoo_id` | integer | Yahoo fantasy ID. |
| `week` | integer | Roster week snapshot. |
| `game_type` | string | `'REG'`, `'POST'`, etc. |
| `headshot_url` | string | URL to player headshot image. |
| `years_exp` | integer | Years of NFL experience. |

---

## snap_counts — Snap Counts

**Source:** nflverse-data `snap_counts` release  
**Granularity:** One row per player per week  
**Coverage:** 2012–present  
**Primary key:** `pfr_player_id`, `season`, `week`, `team`

| Column | Type | Description |
|---|---|---|
| `player` | string | Player name. |
| `pfr_player_id` | string | Pro Football Reference player ID. Join to `players.pfr_id`. |
| `position` | string | Player position. |
| `team` | string | Team abbreviation. |
| `season` | integer | NFL season year. |
| `week` | integer | Week number. |
| `game_id` | string | Game identifier (matches `pbp.game_id` and `schedules.game_id`). |
| `offense_snaps` | integer | Raw count of offensive snaps on the field. |
| `offense_pct` | float | Percentage of team's offensive snaps (0–100). |
| `defense_snaps` | integer | Raw count of defensive snaps on the field. |
| `defense_pct` | float | Percentage of team's defensive snaps (0–100). |
| `st_snaps` | integer | Special teams snaps. |
| `st_pct` | float | Percentage of team's special teams snaps (0–100). |

---

## schedules — Game Schedules and Results

**Source:** nflverse-data `schedules` release  
**Granularity:** One row per game  
**Coverage:** 1999–present  
**Primary key:** `game_id`

| Column | Type | Description |
|---|---|---|
| `game_id` | string | Unique game identifier: `{season}_{week:02d}_{away}_{home}`. |
| `season` | integer | NFL season year. |
| `game_type` | string | `'REG'`, `'WC'`, `'DIV'`, `'CON'`, `'SB'`. |
| `week` | integer | Week number (1–22). |
| `gameday` | date | Game date (YYYY-MM-DD). |
| `weekday` | string | Day of week (e.g. `'Sunday'`). |
| `gametime` | string | Kickoff time (local). |
| `away_team` | string | Away team abbreviation. |
| `home_team` | string | Home team abbreviation. |
| `away_score` | integer | Away team final score (NULL = game not yet played). |
| `home_score` | integer | Home team final score (NULL = game not yet played). |
| `result` | integer | `home_score - away_score`. Positive = home win. |
| `total` | integer | Total points scored by both teams. |
| `overtime` | integer | 1 if the game went to overtime. |
| `spread_line` | float | Vegas point spread (negative = home favored). |
| `total_line` | float | Vegas over/under total. |
| `div_game` | integer | 1 if both teams are in the same division. |
| `roof` | string | Stadium roof type. |
| `surface` | string | Playing surface. |
| `temp` | float | Game-time temperature in °F. |
| `wind` | float | Wind speed in mph. |
| `away_coach` | string | Away team head coach. |
| `home_coach` | string | Home team head coach. |
| `away_qb_id` | string | Starting QB `gsis_id` for the away team. |
| `home_qb_id` | string | Starting QB `gsis_id` for the home team. |
| `away_qb_name` | string | Starting QB name for the away team. |
| `home_qb_name` | string | Starting QB name for the home team. |
| `stadium_id` | string | Stadium identifier. |
| `stadium` | string | Stadium name. |
| `location` | string | `'Home'` or `'Neutral'`. |
| `old_game_id` | string | Legacy game identifier format. |

---

## ngs_passing — NextGen Stats Passing

**Source:** nflverse-data `nextgen_stats` release  
**Granularity:** One row per player per week (plus season summaries where week is NULL)  
**Coverage:** 2016–present  
**Primary key:** `player_gsis_id`, `season`, `week`

| Column | Type | Description |
|---|---|---|
| `player_display_name` | string | Player display name. |
| `player_gsis_id` | string | `gsis_id`. Join to `players.gsis_id`. |
| `player_position` | string | Player position. |
| `team_abbr` | string | Team abbreviation. |
| `season` | integer | NFL season year. |
| `season_type` | string | `'REG'` or `'POST'`. |
| `week` | integer | Week number (NULL or 0 for season summary rows). |
| `attempts` | integer | Pass attempts. |
| `avg_time_to_throw` | float | Average seconds from snap to release. Typical range: 2.3–3.0s. |
| `avg_completed_air_yards` | float | Average air yards on completions. |
| `avg_intended_air_yards` | float | Average air yards on all targets (including incomplete). |
| `avg_air_yards_differential` | float | `avg_completed - avg_intended` air yards. |
| `aggressiveness` | float | % of attempts thrown into tight windows (< 1 yard separation). |
| `max_completed_air_distance` | float | Longest completed pass air distance. |
| `avg_air_yards_to_sticks` | float | Average air yards relative to the first-down marker. |
| `passer_rating` | float | Traditional NFL passer rating (0–158.3). |
| `completion_percentage` | float | Actual completion percentage. |
| `expected_completion_percentage` | float | Model-predicted completion percentage. |
| `completion_percentage_above_expectation` | float | CPAE: actual minus expected completion %. |
| `avg_air_distance` | float | Average distance of all pass attempts (including incomplete). |
| `max_air_distance` | float | Longest air throw of the season. |

---

## ngs_receiving — NextGen Stats Receiving

**Source:** nflverse-data `nextgen_stats` release  
**Granularity:** One row per player per week (plus season summaries)  
**Coverage:** 2016–present  
**Primary key:** `player_gsis_id`, `season`, `week`

| Column | Type | Description |
|---|---|---|
| `player_display_name` | string | Player display name. |
| `player_gsis_id` | string | `gsis_id`. Join to `players.gsis_id`. |
| `player_position` | string | Player position (WR, TE, RB). |
| `team_abbr` | string | Team abbreviation. |
| `season` | integer | NFL season year. |
| `week` | integer | Week number (NULL for season summaries). |
| `receptions` | integer | Receptions. |
| `targets` | integer | Targets. |
| `catch_percentage` | float | Catch rate (%). |
| `yards` | float | Receiving yards. |
| `rec_touchdowns` | integer | Receiving touchdowns. |
| `avg_cushion` | float | Average yards between receiver and nearest defender at snap. |
| `avg_separation` | float | Average yards of open space at the catch or target point. |
| `avg_intended_air_yards` | float | Average depth of target (ADOT) including incomplete passes. |
| `percent_share_of_intended_air_yards` | float | Share of team's intended air yards (0–100). |
| `avg_yac` | float | Average yards after catch per reception. |
| `avg_expected_yac` | float | Model-expected YAC based on catch location. |
| `avg_yac_above_expectation` | float | YAC vs. expectation: positive = exceeding predictions. |

---

## ngs_rushing — NextGen Stats Rushing

**Source:** nflverse-data `nextgen_stats` release  
**Granularity:** One row per player per week (plus season summaries)  
**Coverage:** 2016–present  
**Primary key:** `player_gsis_id`, `season`, `week`

| Column | Type | Description |
|---|---|---|
| `player_display_name` | string | Player display name. |
| `player_gsis_id` | string | `gsis_id`. Join to `players.gsis_id`. |
| `player_position` | string | Player position (RB, QB, WR). |
| `team_abbr` | string | Team abbreviation. |
| `season` | integer | NFL season year. |
| `week` | integer | Week number (NULL for season summaries). |
| `rush_attempts` | integer | Rush attempts. |
| `rush_yards` | float | Total rushing yards. |
| `avg_rushing_yards` | float | Average yards per carry. |
| `rush_touchdowns` | integer | Rushing touchdowns. |
| `efficiency` | float | NGS composite efficiency score. |
| `percent_attempts_gte_eight_defenders` | float | % of carries facing 8+ defenders in the box. |
| `avg_time_to_los` | float | Average seconds from snap to reaching the line of scrimmage. |
| `rush_yards_over_expected` | float | RYOE: total rushing yards above model expectation. |
| `avg_rush_yards_over_expected` | float | RYOE per carry. |
| `rush_yards_over_expected_per_att` | float | Alias for `avg_rush_yards_over_expected`. |
| `rush_pct_over_expected` | float | % of carries that exceeded expected yards. |

---

## pfr_advstats_pass — PFR Advanced Passing

**Source:** nflverse-data `pfr_advstats` release  
**Granularity:** One row per player per season  
**Coverage:** ~2018–present  
**Primary key:** `pfr_id`, `season`  
**Join:** `pfr_id` → `players.pfr_id`

| Column | Type | Description |
|---|---|---|
| `player` | string | Player name. |
| `pfr_id` | string | Pro Football Reference player ID. |
| `team` | string | Team abbreviation. |
| `season` | integer | NFL season year. |
| `attempts` | integer | Pass attempts. |
| `pass_yards` | integer | Passing yards. |
| `pass_tds` | integer | Passing touchdowns. |
| `interceptions` | integer | Interceptions. |
| `first_downs` | integer | First downs generated. |
| `intended_air_yards` | float | Total intended air yards (including incomplete). |
| `intended_air_yards_per_pass_attempt` | float | ADOT: average depth of target including incomplete. |
| `completed_air_yards` | float | Total completed air yards. |
| `completed_air_yards_per_completion` | float | Average air yards on completions. |
| `completed_air_yards_per_attempt` | float | Average completed air yards per attempt. |
| `times_sacked` | integer | Times the QB was sacked. |
| `sack_yards` | integer | Yards lost to sacks. |
| `on_tgt_throws` | integer | Number of on-target throws. |
| `on_tgt_pct` | float | On-target throw percentage. |
| `bad_throws` | integer | Number of bad/inaccurate throws. |
| `bad_throw_pct` | float | Bad throw percentage. |
| `blitzed` | integer | Dropbacks facing a blitz. |
| `hurried` | integer | Times hurried. |
| `hits` | integer | Times hit. |
| `pressured` | integer | Total pressured dropbacks. |
| `pressure_pct` | float | Percentage of dropbacks where QB was pressured. |
| `dropbacks` | integer | Total dropbacks (pass attempts + scrambles + sacks). |
| `times_hurried` | integer | Times hurried (may differ from `hurried` column depending on source version). |
| `times_hit` | integer | Times hit. |

---

## pfr_advstats_rush — PFR Advanced Rushing

**Source:** nflverse-data `pfr_advstats` release  
**Granularity:** One row per player per season  
**Coverage:** ~2018–present  
**Primary key:** `pfr_id`, `season`

| Column | Type | Description |
|---|---|---|
| `player` | string | Player name. |
| `pfr_id` | string | Pro Football Reference player ID. Join to `players.pfr_id`. |
| `team` | string | Team abbreviation. |
| `season` | integer | NFL season year. |
| `att` | integer | Rush attempts. |
| `yards` | integer | Total rushing yards. |
| `tds` | integer | Rushing touchdowns. |
| `first_downs` | integer | First downs gained rushing. |
| `ybc` | float | Yards before contact (total). |
| `ybc_att` | float | Yards before contact per attempt. |
| `yac` | float | Yards after contact (total). |
| `yac_att` | float | Yards after contact per attempt. |
| `broken_tackles` | integer | Total broken tackles on runs. |
| `broken_tackles_att` | float | Broken tackles per attempt. |

---

## pfr_advstats_rec — PFR Advanced Receiving

**Source:** nflverse-data `pfr_advstats` release  
**Granularity:** One row per player per season  
**Coverage:** ~2018–present  
**Primary key:** `pfr_id`, `season`

| Column | Type | Description |
|---|---|---|
| `player` | string | Player name. |
| `pfr_id` | string | Pro Football Reference player ID. Join to `players.pfr_id`. |
| `team` | string | Team abbreviation. |
| `season` | integer | NFL season year. |
| `tgt` | integer | Targets. |
| `rec` | integer | Receptions. |
| `yards` | integer | Receiving yards. |
| `tds` | integer | Receiving touchdowns. |
| `first_downs` | integer | First downs gained. |
| `ybc` | float | Yards before contact on receptions. |
| `ybc_r` | float | Yards before contact per reception. |
| `yac` | float | Yards after contact. |
| `yac_r` | float | Yards after contact per reception. |
| `adot` | float | Average depth of target (including incomplete). |
| `broken_tackles` | integer | Broken tackles after reception. |
| `broken_tackles_r` | float | Broken tackles per reception. |
| `drop` | integer | Drops. |
| `drop_pct` | float | Drop percentage. |
| `int` | integer | Passes that resulted in interceptions when targeted. |

---

## pfr_advstats_def — PFR Advanced Defense

**Source:** nflverse-data `pfr_advstats` release  
**Granularity:** One row per player per season  
**Coverage:** ~2018–present  
**Primary key:** `pfr_id`, `season`

| Column | Type | Description |
|---|---|---|
| `player` | string | Player name. |
| `pfr_id` | string | Pro Football Reference player ID. Join to `players.pfr_id`. |
| `team` | string | Team abbreviation. |
| `position` | string | Defensive position. |
| `season` | integer | NFL season year. |
| `int` | integer | Interceptions. |
| `tgt` | integer | Times targeted in coverage. |
| `cmp` | integer | Completions allowed in coverage. |
| `cmp_pct` | float | Completion percentage allowed in coverage. |
| `yds` | integer | Coverage yards allowed. |
| `yds_per_cmp` | float | Yards per completion allowed. |
| `yds_per_tgt` | float | Yards per target allowed. |
| `td` | integer | Touchdowns allowed in coverage. |
| `rat` | float | Passer rating when targeted. |
| `dta` | integer | Defensive tackles (solo). |
| `dtm` | integer | Missed tackles. |
| `dtm_pct` | float | Missed tackle percentage. |
| `bltz` | integer | Times the player blitzed. |
| `hrry` | integer | QB hurries. |
| `qbkd` | integer | QB knockdowns (hits). |
| `sk` | float | Sacks. |
| `prss` | integer | Total pressures (hurries + hits + sacks). |
| `prcnt` | float | Pressure percentage. |
| `sgmd` | integer | Sacks generated (may vary by version). |

---

## combine — NFL Combine

**Source:** nflverse-data `combine` release  
**Granularity:** One row per player  
**Coverage:** Historical through present  
**Primary key:** `pfr_id`, `season`

| Column | Type | Description |
|---|---|---|
| `player_name` | string | Player name. |
| `pos` | string | Position at the combine. |
| `school` | string | College. |
| `ht` | string | Height (may be stored as `"6-2"` format). |
| `wt` | integer | Weight in pounds. |
| `forty` | float | 40-yard dash time (seconds). Lower = faster. |
| `bench` | integer | 225-lb bench press repetitions. Higher = stronger. |
| `vertical` | float | Vertical leap (inches). Higher = more explosive. |
| `broad_jump` | integer | Standing broad jump (inches). |
| `cone` | float | 3-cone drill (seconds). Lower = more agile. |
| `shuttle` | float | 20-yard short shuttle (seconds). Lower = quicker laterally. |
| `season` | integer | Draft class year. |
| `pfr_id` | string | Pro Football Reference player ID. Join to `players.pfr_id` and `draft_picks.pfr_player_id`. |

**Note:** NULL in any measurement column means the drill was not performed or
not recorded — it does not imply the player is unathletic.

---

## draft_picks — NFL Draft Picks

**Source:** nflverse-data `draft_picks` release  
**Granularity:** One row per player selected  
**Coverage:** 1936–present  
**Primary key:** `pfr_player_id`, `season`

| Column | Type | Description |
|---|---|---|
| `season` | integer | Draft year (e.g. 2023 = 2023 NFL Draft). |
| `round` | integer | Draft round (1–7). |
| `pick` | integer | Overall pick number (1 = first overall). |
| `team` | string | Selecting team abbreviation. |
| `player_name` | string | Player name. |
| `pos` | string | Position the player was drafted to play. |
| `age` | float | Player age at time of draft. |
| `to` | integer | Final NFL season played. |
| `allpro` | integer | Number of All-Pro selections. |
| `probowls` | integer | Number of Pro Bowl selections. |
| `starts` | integer | Career regular season starts. |
| `w_av` | float | Weighted Approximate Value (career, recent seasons weighted more). |
| `car_av` | float | Career Approximate Value (unweighted total). |
| `dr_av` | float | Approximate Value earned with the drafting team only. |
| `g` | integer | Career games played. |
| `college_id` | string | College identifier. |
| `college` | string | College name. |
| `pfr_player_id` | string | Pro Football Reference player ID. Join to `players.pfr_id` and `combine.pfr_id`. |
| `hof` | integer | 1 if the player is in the Hall of Fame. |

---

## players — Player ID Register

**Source:** nflverse-data `players` release  
**Granularity:** One row per player  
**Coverage:** All NFL players in the nflverse database  
**Primary key:** `gsis_id`

| Column | Type | Description |
|---|---|---|
| `gsis_id` | string | Primary player identifier for most nflverse tables. |
| `display_name` | string | Full player display name (e.g. `"Patrick Mahomes"`). Preferred for names. |
| `first_name` | string | First name. |
| `last_name` | string | Last name. |
| `position` | string | Primary position (QB, RB, WR, TE, OL, DL, LB, CB, S, K, P). |
| `position_group` | string | Broader position group (e.g. `'OL'`, `'DB'`, `'SPEC'`). |
| `team_abbr` | string | Current team 3-letter abbreviation. |
| `status` | string | `'ACT'` (active), `'INA'` (inactive/retired), `'RES'` (reserve/IR), `'CUT'`, `'UFA'`. |
| `birth_date` | date | Player date of birth. |
| `height` | integer | Height in inches. |
| `weight` | integer | Weight in pounds. |
| `college` | string | College or university. |
| `draft_club` | string | Team that drafted the player. |
| `draft_number` | integer | Overall draft pick number. |
| `years_exp` | integer | Years of NFL experience. |
| `headshot_url` | string | URL to player headshot. |
| `pfr_id` | string | Pro Football Reference ID. Used in `pfr_advstats_*` and `snap_counts`. |
| `espn_id` | integer | ESPN player ID. |
| `pff_id` | integer | Pro Football Focus player ID. |
| `fantasy_data_id` | integer | FantasyData player ID. |
| `rotowire_id` | integer | RotoWire player ID. |
| `sportradar_id` | string | Sportradar player ID. |
| `yahoo_id` | integer | Yahoo Fantasy player ID. |
| `sleeper_id` | integer | Sleeper platform player ID. |
| `short_name` | string | Abbreviated name (e.g. `"P.Mahomes"`). |

### Common Join Patterns

```sql
-- Get passer name for pbp plays
SELECT p.display_name, AVG(pbp.epa) AS avg_epa
FROM pbp
JOIN players p ON pbp.passer_id = p.gsis_id
WHERE pbp.play_type = 'pass' AND pbp.season = 2024
  AND pbp.season_type = 'REG'
GROUP BY p.display_name
ORDER BY avg_epa DESC
LIMIT 10;

-- Resolve snap count player IDs (uses pfr_id, not gsis_id)
SELECT p.display_name, sc.offense_pct
FROM snap_counts sc
JOIN players p ON sc.pfr_player_id = p.pfr_id
WHERE sc.season = 2024 AND sc.week = 1;

-- Resolve pfr_advstats player IDs
SELECT p.display_name, pa.pressure_pct
FROM pfr_advstats_pass pa
JOIN players p ON pa.pfr_id = p.pfr_id
WHERE pa.season = 2024;
```
