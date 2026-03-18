import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'

duckdb.sql(f"""
                      with player_level as (
                      SELECT --match_id, 
                      team_id, player_id, SUM(duration) player_carry_time
                      FROM read_parquet('{project_location}/eda/carry_level_stats.parquet')
                      GROUP BY --match_id, 
                      team_id, player_id
                      ),
                      team_level as (
                      SELECT --match_id, 
                      team_id, SUM(duration) team_carry_time
                      FROM read_parquet('{project_location}/eda/carry_level_stats.parquet')
                      GROUP BY --match_id, 
                      team_id
                      ),
                      seconds_on_pitch as (
                      SELECT team_id, player_id, SUM(DATE_DIFF('seconds', interval_start, interval_end)) seconds_on_pitch
                     FROM read_parquet('{project_location}/eda/player_match_timeline_with_score.parquet')
                     GROUP BY team_id, player_id
                     ),
                      get_percent as (
                      SELECT pl.*, team_carry_time, seconds_on_pitch, player_carry_time / seconds_on_pitch player_carry_time_percentage
                      FROM player_level pl
                      LEFT JOIN team_level tl
                        ON pl.team_id = tl.team_id
                      LEFT JOIN seconds_on_pitch
                        ON pl.team_id = seconds_on_pitch.team_id
                        AND pl.player_id = seconds_on_pitch.player_id
                      )
                      SELECT *
                      FROM get_percent
                      ORDER BY player_carry_time_percentage DESC

                                """).write_parquet('more_carry_level_metrics.parquet')

