import duckdb
import math
import matplotlib.pyplot as plt
import numpy as np

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

# x_coords = duckdb.sql(f"""
#                         SELECT location_x
#                         FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
#                         WHERE location_x IS NOT NULL --AND match_id = 7542
 
#                     """).df()

# y_coords = duckdb.sql(f"""
#                         SELECT location_y
#                         FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
#                         WHERE location_y IS NOT NULL --AND match_id = 7542
 
#                     """).df()
#x_coords, y_coords = np.array(xy_coords).T


#print(x_coords)

#plt.scatter(x_coords, y_coords)
#plt.savefig('another_test.png')


# y_coords = duckdb.sql(f"""
                      
#                       SELECT distinct min_x, max_x, min_y, max_y
#                       FROM (
#                         SELECT match_id, MIN(round(location_x)) min_x, MAX(round(location_x)) max_x, MIN(round(location_y)) min_y, MAX(round(location_y)) max_y
#                         FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
#                         WHERE location_y IS NOT NULL --AND match_id = 7542
#                         GROUP BY match_id)
 
#                     """)
# print(y_coords)

#x coords
#0-18 left box
#102-120 right box

#y coords
#40 +- (20.115)
#60.115
#19.885


#left box

#top left
#(60.115, 0)
#top right
#(60.115, 18)
#bottom left
#(19.885, 0)
#bottom right
#(19.885, 18)


#right box

#top left
#(60.115, 102)
#top right
#(60.115, 120)
#bottom left
#(19.885, 102)
#bottom right
#(19.885, 120)

#halfway 60

duckdb.sql(f"""
                      with gk_events as (
                      SELECT match_id, id, possession, index_num, team_id, player_id, type,
                      --goalkeeper_outcome, 
                      --goalkeeper_body_part,
                      CASE 
                      WHEN goalkeeper_outcome = 'Saved Twice' THEN 2
                      WHEN goalkeeper_type LIKE '%Save%' THEN 1
                      ELSE 0
                      END AS gk_save,
                      CASE 
                      WHEN goalkeeper_outcome = 'Collected Twice' THEN 2
                      WHEN goalkeeper_type = 'Collected' THEN 1
                      ELSE 0
                      END AS gk_collected,
                      CASE 
                      WHEN goalkeeper_type = 'Keeper Sweeper' THEN 1
                      ELSE 0
                      END AS gk_keeper_sweeper,
                      CASE 
                      WHEN goalkeeper_type = 'Goal Conceded' THEN 1
                      WHEN goalkeeper_type = 'Penalty Conceded' THEN 1
                      ELSE 0
                      END AS gk_goal_conceded,
                      CASE 
                      WHEN goalkeeper_type = 'Smother' THEN 1
                      ELSE 0
                      END AS gk_smother,
                      CASE 
                      WHEN goalkeeper_type = 'Punch' THEN 1
                      ELSE 0
                      END AS gk_punch,
                      CASE 
                      WHEN goalkeeper_type = 'Goal Conceded' THEN 1
                      WHEN goalkeeper_type = 'Penalty Conceded' THEN 1
                      WHEN goalkeeper_type LIKE '%Save%' THEN 1
                      ELSE 0
                      END AS gk_shot_faced,
                      CASE 
                      WHEN goalkeeper_type LIKE '&Penalty%' THEN 1
                      ELSE 0
                      END AS gk_penalty_faced,
                      CASE 
                      WHEN goalkeeper_type = 'Penalty Saved' THEN 1
                      ELSE 0
                      END AS gk_penalty_saved,
                      CASE WHEN goalkeeper_technique = 'Standing' THEN 1 ELSE 0 END AS gk_standing,
                      CASE WHEN goalkeeper_technique = 'Diving' THEN 1 ELSE 0 END AS gk_diving,
                      CASE WHEN goalkeeper_position = 'Moving' THEN 1 ELSE 0 END AS gk_moving,
                      CASE WHEN goalkeeper_position = 'Set' THEN 1 ELSE 0 END AS gk_set,
                      CASE WHEN goalkeeper_position = 'Prone' THEN 1 ELSE 0 END AS gk_prone

                      FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
                      WHERE type = 'Goal Keeper' 
                      ),
                      shot_events as (
                      SELECT s.match_id, possession, index_num, s.id, s.team_id, s.player_id, EVENT_ZONE_START, STARTING_DISTANCE_TO_GOAL_SHOOTING_ON, type, 
                      shot_end_location_x, shot_end_location_y, shot_end_location_z, shot_statsbomb_xg
                      FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') s
                      LEFT JOIN read_parquet('{project_location}/eda/event_proximity.parquet') ep
                        ON s.match_id = ep.match_id
                        AND s.id = ep.id
                      WHERE type = 'Shot'
                      ),
                      stack_event as (
                      SELECT match_id, id, possession, index_num, team_id, player_id, type
                      FROM shot_events

                      UNION

                      SELECT match_id, id, possession, index_num, team_id, player_id, type
                      FROM gk_events
                      ),
                      id_shot as (
                      SELECT stack_event.*, 
                      CASE 
                      WHEN type = 'Shot' THEN 1
                      ELSE 0
                      END AS shot_tracker
                      FROM stack_event
                      ),
                      rt_shot as (
                      SELECT id_shot.*, SUM(shot_tracker) OVER (PARTITION BY match_id, possession ORDER BY match_id, possession, index_num) RT_shot_event
                      FROM id_shot
                      ),
                      combine_shot_gk as (
                      SELECT iso_shot_event.match_id, iso_shot_event.possession, shot_event_id, gk_react_event_id
                      FROM (SELECT match_id, possession, RT_shot_event, id shot_event_id
                            FROM rt_shot
                            WHERE type= 'Shot') iso_shot_event
                      INNER JOIN (SELECT match_id, possession, RT_shot_event, id gk_react_event_id
                            FROM rt_shot
                            WHERE type= 'Goal Keeper') gk_react
                      ON iso_shot_event.match_id = gk_react.match_id
                      AND iso_shot_event.possession = gk_react.possession
                      AND iso_shot_event.RT_shot_event = gk_react.RT_shot_event
                      )

                      SELECT gk_events.match_id, gk_react_event_id, gk_events.player_id gk_player_id, gk_save, gk_collected, gk_keeper_sweeper, 
                      gk_goal_conceded, gk_smother, gk_punch, gk_shot_faced, gk_penalty_faced, gk_penalty_saved, 
                      gk_standing, gk_diving, gk_moving, gk_set, gk_prone, shot_events.team_id shooting_team_id, 
                      shot_event_id, shot_events.player_id shot_player_id, EVENT_ZONE_START shot_zone, STARTING_DISTANCE_TO_GOAL_SHOOTING_ON shot_distance_center_goal_line,
                      shot_end_location_x, shot_end_location_y, shot_end_location_z, shot_statsbomb_xg
                      FROM gk_events
                      LEFT JOIN combine_shot_gk
                        ON gk_events.match_id = combine_shot_gk.match_id
                        AND gk_events.id = combine_shot_gk.gk_react_event_id
                      LEFT JOIN shot_events
                        ON combine_shot_gk.match_id = shot_events.match_id
                        AND combine_shot_gk.shot_event_id = shot_events.id
                    """).write_parquet('gk_stats.parquet')
