import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'

duckdb.sql(f"""
                        SELECT match_id, id, index_num, period, timestamp, duration, location_x, location_y, possession, possession_team_id, team_id, 
                         player_id, carry_end_location_x, carry_end_location_y
                        FROM read_parquet('{project_location}/data/Statsbomb/events.parquet')
                        WHERE carry_end_location_x IS NOT NULL
                                """).write_parquet('carry.parquet')

