import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/'

possession_tl = duckdb.sql(f"""
                        SELECT player_id, match_id, SUM(date_diff('second', interval_start, interval_end)) / 60 MINUTES_ON_PITCH
                        FROM read_parquet('{project_location}/eda/period_lineups.parquet')
                        GROUP BY player_id, match_id
                                """).write_parquet('player_match_on_pitch.parquet')
print(possession_tl)
