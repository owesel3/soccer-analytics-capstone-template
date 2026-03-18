import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'
#'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'
#'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/eda'

# test_query = duckdb.sql(f"""
#                         SELECT *
#                         FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet') 

#                         """
#                         )#.write_csv('match_investigate.csv')
# print(test_query.columns)

# test_query2 = duckdb.sql(f"""
                        # SELECT FULL_SQUAD_GROUPING_ID, OFFENSE_DEFENSE, AVG(shot_statsbomb_xg) avg_shot_statsbomb_xg, COUNT(id) number_of_shots, COUNT(match_id) number_of_matches
                        # FROM get_shot_xg
                        # GROUP BY FULL_SQUAD_GROUPING_ID, OFFENSE_DEFENSE
                        # ORDER BY AVG(shot_statsbomb_xg) DESC
#                     """)

# print(test_query2)

test_query3 = duckdb.sql(f"""
                        with get_shot_xg as (
                        SELECT e.id, e.match_id, shot_statsbomb_xg, possession_team_id, HOME_AWAY, l.team_id, FULL_SQUAD_GROUPING_ID, OVERALL_FORMATION, PLAYERS_ON_PITCH,
                         CASE 
                         WHEN l.team_id IS NULL THEN NULL 
                         WHEN possession_team_id = l.team_id THEN 'Offense' 
                         WHEN possession_team_id != l.team_id THEN 'Defense'
                         ELSE NULL
                         END AS OFFENSE_DEFENSE
                        FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
                        LEFT JOIN read_parquet('{project_location}/eda/find_event_players_on_pitch.parquet')  l
                           ON e.id = l.id
                           AND e.match_id = l.match_id
                        WHERE IFNULL(shot_statsbomb_xg,0) > 0
                        ),
                        get_avgs as (
                        SELECT team_id, FULL_SQUAD_GROUPING_ID, OFFENSE_DEFENSE, OVERALL_FORMATION, PLAYERS_ON_PITCH, AVG(shot_statsbomb_xg) avg_shot_statsbomb_xg, COUNT(id) number_of_shots, COUNT(distinct match_id) number_of_matches, COUNT(id)  / COUNT(distinct match_id) avg_shots_per_match
                        FROM get_shot_xg
                        GROUP BY team_id, FULL_SQUAD_GROUPING_ID, OFFENSE_DEFENSE, OVERALL_FORMATION, PLAYERS_ON_PITCH 
                        )
                        SELECT team_id, FULL_SQUAD_GROUPING_ID, OFFENSE_DEFENSE, OVERALL_FORMATION, PLAYERS_ON_PITCH, avg_shot_statsbomb_xg, number_of_matches, avg_shots_per_match, avg_shot_statsbomb_xg * avg_shots_per_match xg_match
                        FROM get_avgs
                        WHERE team_id = 781
                        ORDER BY number_of_matches DESC, avg_shot_statsbomb_xg * avg_shots_per_match DESC
                        
 
                    """)#.write_csv('player_composition.csv')

print(test_query3)