import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'

duckdb.sql(f"""
                        SELECT match_id, id, index_num, period, timestamp, duration, location_x, location_y, possession, possession_team_id, team_id, 
                         player_id, duel_type, duel_outcome
                        FROM read_parquet('{project_location}/data/Statsbomb/events.parquet')
                        WHERE duel_type IS NOT NULL
                                """).write_parquet('duel.parquet')

