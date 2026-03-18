import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'

duckdb.sql(f"""
                      with score_info as (
                       SELECT match_id, period, start_date, end_date, home_goals, away_goals
                       FROM read_parquet('{project_location}/eda/match_score_timeline.parquet')
                       ),
                       track_times as (
                       SELECT match_id, period, interval_start
                       FROM read_parquet('{project_location}/eda/period_lineups.parquet')

                       UNION

                       SELECT match_id, period, start_date
                       FROM score_info
                       ),
                       id_changes as (
                       SELECT track_times.*, --home_goals, away_goals, 
                       player_id, country_id, POSITION_SIDE_ADJ, POSITION_TYPE, POSITION_TYPE_ALT, POSITION_BEHAVIOR, PLAYERS_SAME_COUNTRY, 
                       PLAYERS_DIFF_COUNTRY, POSITION_SAME_COUNTRY, POSITION_DIFF_COUNTRY, SIDE_SAME_COUNTRY, SIDE_DIFF_COUNTRY, team_id,
                       CASE 
                       WHEN team_id = home_team_id THEN home_goals ELSE away_goals END AS TEAM_GOALS,
                       CASE 
                       WHEN team_id = away_team_id THEN away_goals ELSE home_goals END AS OPP_GOALS,

                       CASE
                       WHEN IFNULL(LAG(track_times.period,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),-1) != track_times.period THEN 1
                       WHEN IFNULL(LAG(home_goals,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),-1) != home_goals THEN 1
                       WHEN IFNULL(LAG(away_goals,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),-1) != away_goals THEN 1
                       WHEN IFNULL(LAG(POSITION_SIDE_ADJ,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),'N/A') != POSITION_SIDE_ADJ THEN 1
                       WHEN IFNULL(LAG(POSITION_TYPE,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),'N/A') != POSITION_TYPE THEN 1
                       WHEN IFNULL(LAG(POSITION_TYPE_ALT,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),'N/A') != POSITION_TYPE_ALT THEN 1
                       WHEN IFNULL(LAG(POSITION_BEHAVIOR,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),'N/A') != POSITION_BEHAVIOR THEN 1
                       WHEN IFNULL(LAG(PLAYERS_SAME_COUNTRY,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),-1) != PLAYERS_SAME_COUNTRY THEN 1
                       WHEN IFNULL(LAG(PLAYERS_DIFF_COUNTRY,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),-1) != PLAYERS_DIFF_COUNTRY THEN 1
                       WHEN IFNULL(LAG(POSITION_SAME_COUNTRY,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),-1) != POSITION_SAME_COUNTRY THEN 1
                       WHEN IFNULL(LAG(POSITION_DIFF_COUNTRY,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),-1) != POSITION_DIFF_COUNTRY THEN 1
                       WHEN IFNULL(LAG(SIDE_SAME_COUNTRY,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),-1) != SIDE_SAME_COUNTRY THEN 1
                       WHEN IFNULL(LAG(SIDE_DIFF_COUNTRY,1) OVER (PARTITION BY track_times.match_id, track_times.period, player_id ORDER BY track_times.match_id, track_times.period, player_id, track_times.interval_start),-1) != SIDE_DIFF_COUNTRY THEN 1
                       ELSE 0
                       END AS iso_row
                       FROM track_times
                       LEFT JOIN score_info
                        ON track_times.match_id = score_info.match_id
                        AND track_times.period = score_info.period
                        AND track_times.interval_start >= score_info.start_date
                        AND track_times.interval_start < IFNULL(score_info.end_date, TODAY())
                        LEFT JOIN read_parquet('{project_location}/eda/period_lineups.parquet') pl
                        ON track_times.match_id = pl.match_id
                        AND track_times.period = pl.period
                        AND track_times.interval_start >= pl.interval_start
                        AND track_times.interval_start < IFNULL(pl.interval_end, TODAY())
                        LEFT JOIN read_parquet('{project_location}/data/Statsbomb/matches.parquet') e
                          ON track_times.match_id = e.match_id
                        )

                        SELECT iso_changes.*, IFNULL(LEAD(interval_start) OVER (PARTITION BY iso_changes.match_id, iso_changes.period, player_id ORDER BY iso_changes.match_id, iso_changes.period, player_id, interval_start), period_timestamp) interval_end
                        FROM (
                        SELECT match_id, period, team_id, TEAM_GOALS, OPP_GOALS, player_id, country_id, POSITION_SIDE_ADJ, POSITION_TYPE, POSITION_TYPE_ALT, POSITION_BEHAVIOR, PLAYERS_SAME_COUNTRY, 
                       PLAYERS_DIFF_COUNTRY, POSITION_SAME_COUNTRY, POSITION_DIFF_COUNTRY, SIDE_SAME_COUNTRY, SIDE_DIFF_COUNTRY, interval_start
                       FROM id_changes
                       WHERE iso_row = 1
                       ) iso_changes

                       LEFT JOIN (                              
                              SELECT match_id, period, start_date + TO_MINUTES(minute) + TO_SECONDS(second) period_timestamp
                              FROM (SELECT distinct match_id, team_id, period, minute, second, timestamp, strptime('2026-01-01' , '%Y-%m-%d') start_date, type
                                    FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') 
                                    WHERE type IN ('Half End')
                                    )
                                    ) half_end
                                ON iso_changes.match_id = half_end.match_id
                                AND iso_changes.period = half_end.period

                                """).write_parquet('player_match_timeline_with_score.parquet')

