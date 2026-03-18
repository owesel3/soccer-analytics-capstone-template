import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'
#'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'
#'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/eda'

all_lineups = duckdb.sql(f"""
                  with get_player_type as (
                  SELECT distinct match_id, team_id, player_id, country_id, position_side, position_type, period, interval_start
                         --match_id, team_id
                  FROM read_parquet('{project_location}/eda/period_lineups.parquet')  pl
                  LEFT JOIN read_parquet('{project_location}/eda/position_type.parquet') pt
                        ON pl.position_name = pt.position_name
                        )
                  
                              PIVOT (
                              SELECT unq_players.*,'position_slot_' || CAST(RANK() OVER (PARTITION BY match_id, period, interval_start, team_id, position_type ORDER BY match_id, period, interval_start, team_id, position_type, player_id) as varchar) PLAYER_ID_RANK
                              FROM (SELECT *
                                    FROM get_player_type
                                    WHERE IFNULL(position_type,'N/A') NOT IN ('N/A','GK')) unq_players
                              )
                              ON PLAYER_ID_RANK
                              USING MIN(player_id)
                              GROUP BY team_id, position_type

                    """)#.write_parquet('lineup_players.parquet')

print(all_lineups)