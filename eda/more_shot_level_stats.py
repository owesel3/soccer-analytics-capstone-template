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
                      with goal_zone_metrics as (
                      SELECT player_id, OFF_ZONE, 
                      SUM(shot_statsbomb_xg) shot_statsbomb_xg_sum, SUM(CASE WHEN shot_outcome = 'Goal' THEN 1 ELSE 0 END) GOALS_CONVERTED, COUNT(*) shots_taken
                      --, 
                      --AVG(shot_statsbomb_xg) shot_statsbomb_xg_avg
                      --player_id, shot_statsbomb_xg, shot_outcome, OFF_ZONE, DIST_TO_GOAL
                      FROM read_parquet('{project_location}/eda/shot_level_stats.parquet')
                      GROUP BY player_id, OFF_ZONE
                      ),
                      player_level as (
                      SELECT player_id, 
                      SUM(shot_statsbomb_xg) shot_statsbomb_xg_sum, SUM(CASE WHEN shot_outcome = 'Goal' THEN 1 ELSE 0 END) GOALS_CONVERTED, COUNT(*) shots_taken
                      FROM read_parquet('{project_location}/eda/shot_level_stats.parquet') 
                      GROUP BY player_id
                      ),
                      zone_stats as (
                      SELECT goal_zone_metrics.*, goals_converted / shot_statsbomb_xg_sum goals_over_xg, goals_converted - shot_statsbomb_xg_sum goals_minus_xg, goals_converted/shots_taken goal_shot_percentage, (goals_converted - shot_statsbomb_xg_sum) / shots_taken new_metric
                      FROM goal_zone_metrics
                      ),
                      player_max as (
                      SELECT zone_stats.player_id, OFF_ZONE
                      FROM zone_stats 
                      INNER JOIN (
                      SELECT player_id, MAX(new_metric) max_new_metric
                      FROM zone_stats
                      GROUP BY player_id) get_max 
                      ON zone_stats.player_id = get_max.player_id
                      AND zone_stats.new_metric = get_max.max_new_metric
                      ),
                      player_stats as (
                      SELECT player_level.*, goals_converted / shot_statsbomb_xg_sum goals_over_xg, goals_converted - shot_statsbomb_xg_sum goals_minus_xg, goals_converted/shots_taken goal_shot_percentage, (goals_converted - shot_statsbomb_xg_sum) / shots_taken new_metric
                      FROM player_level
                      )
                      SELECT player_stats.*, OFF_ZONE BEST_SHOT_ZONE
                      FROM player_stats
                      LEFT JOIN player_max
                        ON player_stats.player_id = player_max.player_id
                      WHERE shots_taken > 10
                      ORDER BY new_metric DESC
                    """).write_parquet('more_shot_level_stats.parquet')
