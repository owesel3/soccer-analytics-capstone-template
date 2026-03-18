import duckdb

project_location = 'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'

possession_tl = duckdb.sql(f"""SELECT id, index_num, period, minute, second, timestamp,duration, location_x, location_y, possession, possession_team_id, type, 
                                    match_id, player_id, position_id, play_pattern
                                FROM read_parquet('{project_location}/Statsbomb/events.parquet') 
                                WHERE match_id = 15973 AND type NOT IN ('Starting XI','Half Start')
                                AND possession_team_id = team_id
                                
                                """)

#print(possession_tl)


possession_check = duckdb.sql(f"""SELECT id, index_num, period, minute, second, timestamp,duration, location_x, location_y, possession, possession_team_id, type, 
                                    match_id, player_id, position_id, play_pattern
                                FROM read_parquet('{project_location}/Statsbomb/events.parquet') 
                                WHERE match_id = 15973 
                                AND type NOT IN ('Starting XI','Half Start')
                                AND possession_team_id != team_id 
                                AND type != 'Pressure'


                                
                                """)


#print(possession_check)

possession_check2 = duckdb.sql(f"""
                               with subset_records as (
                               SELECT id, index_num, period, minute, second, timestamp,duration, location_x, location_y, possession, possession_team_id, type, 
                                    match_id, player_id, position_id, play_pattern, team_id
                                FROM read_parquet('{project_location}/Statsbomb/events.parquet') 
                                WHERE match_id = 15973 
                                AND type NOT IN ('Starting XI','Half Start')
                                AND type NOT IN ('Pressure', 'Foul Committed')

                                ),

                                multi_team as (

                                SELECT player_id, COUNT(distinct possession_team_id) 
                                FROM subset_records
                                WHERE match_id = 15973 
                                AND player_id IS NOT NULL
                                GROUP BY player_id
                                HAVING COUNT(distinct possession_team_id) > 1
                                )
                                SELECT *
                                FROM subset_records
                                WHERE player_id IN (SELECT player_id FROM multi_team)
                                AND possession_team_id != team_id
                                """)

#print(possession_check2)

duckdb.sql(f"""
                               SELECT is_international, season_name, country_name, count(distinct match_id)
                                FROM read_parquet('{project_location}/Statsbomb/matches.parquet') 
                                GROUP BY is_international, season_name, country_name
                                ORDER BY is_international, season_name, country_name
                                """)