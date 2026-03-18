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
                      with shot_percentiles as (
                      SELECT PERCENTILE_DISC([0.25,0.5,0.75]) WITHIN GROUP (ORDER BY shot_statsbomb_xg) percentiles
                      FROM read_parquet('{project_location}/eda/gk_stats.parquet')
                      ),
                      apply_shot_percentile as (
                      SELECT gk.*,
                      CASE 
                      WHEN shot_statsbomb_xg <= (SELECT percentiles[1] FROM shot_percentiles ) THEN 'Q1' 
                      WHEN shot_statsbomb_xg <= (SELECT percentiles[2] FROM shot_percentiles ) THEN 'Q2' 
                      WHEN shot_statsbomb_xg <= (SELECT percentiles[3] FROM shot_percentiles ) THEN 'Q3' 
                      ELSE 'Q4' END AS shot_xg_range
                      FROM read_parquet('{project_location}/eda/gk_stats.parquet') gk
                      ),
                      categorize_shots as (
                      SELECT match_id, gk_player_id, gk_save, gk_collected, gk_keeper_sweeper, gk_goal_conceded, gk_smother, gk_punch, gk_shot_faced, 
                      gk_penalty_faced, gk_penalty_saved, gk_standing, gk_diving, gk_moving, gk_set, gk_prone, 
                      CASE WHEN shot_zone LIKE '%L%' AND (IFNULL(gk_shot_faced,0) > 0 OR IFNULL(gk_save,0) > 0 ) THEN 1 ELSE 0 END as shot_faced_gk_right_side,
                      CASE WHEN shot_zone LIKE '%R%' AND (IFNULL(gk_shot_faced,0) > 0 OR IFNULL(gk_save,0) > 0 )THEN 1 ELSE 0 END as shot_faced_gk_left_side, 
                      CASE WHEN IFNULL(shot_zone,'-') = '-' AND (IFNULL(gk_shot_faced,0) > 0 OR IFNULL(gk_save,0) > 0 )THEN 1 ELSE 0 END as shot_faced_gk_unk_side,
                      --CASE WHEN shot_zone LIKE '%L%' AND (IFNULL(gk_save,0) > 0 ) THEN 1 ELSE 0 END as save_gk_right_side,
                      --CASE WHEN shot_zone LIKE '%R%' AND (IFNULL(gk_save,0) > 0 ) THEN 1 ELSE 0 END as save_gk_left_side,  
                      CASE WHEN shot_xg_range = 'Q1' AND (IFNULL(gk_save,0) > 0 ) THEN 1 ELSE 0 END AS q1_shot_xg,
                      CASE WHEN shot_xg_range = 'Q2' AND (IFNULL(gk_save,0) > 0 ) THEN 1 ELSE 0 END AS q2_shot_xg,
                      CASE WHEN shot_xg_range = 'Q3' AND (IFNULL(gk_save,0) > 0 ) THEN 1 ELSE 0 END AS q3_shot_xg,
                      CASE WHEN shot_xg_range = 'Q4' AND (IFNULL(gk_save,0) > 0 ) THEN 1 ELSE 0 END AS q4_shot_xg
                      
                      FROM apply_shot_percentile
                      ),
                      match_level as (
                      SELECT match_id, gk_player_id, 
                      SUM(gk_save) gk_save, SUM(gk_collected) gk_collected, SUM(gk_keeper_sweeper) gk_keeper_sweeper, SUM(gk_goal_conceded) gk_goal_conceded, 
                      SUM(gk_smother) gk_smother, SUM(gk_punch) gk_punch, SUM(gk_shot_faced) gk_shot_faced, 
                      SUM(gk_penalty_faced) gk_penalty_faced, SUM(gk_penalty_saved) gk_penalty_saved, SUM(gk_standing) gk_standing, 
                      SUM(gk_diving) gk_diving, SUM(gk_moving) gk_moving, SUM(gk_set) gk_set, SUM(gk_prone) gk_prone, 
                      SUM(shot_faced_gk_right_side) shot_faced_gk_right_side, 
                      SUM(shot_faced_gk_left_side) shot_faced_gk_left_side,
                      SUM(shot_faced_gk_unk_side) shot_faced_gk_unk_side, 
                      --SUM(save_gk_right_side) save_gk_right_side, SUM(save_gk_left_side) save_gk_left_side, 
                      SUM(q1_shot_xg) q1_shot_xg, SUM(q2_shot_xg) q2_shot_xg, SUM(q3_shot_xg) q3_shot_xg, SUM(q4_shot_xg) q4_shot_xg
                      FROM categorize_shots
                      GROUP BY match_id, gk_player_id
                      ),
                      get_time as (
                      SELECT match_level.*, MINUTES_ON_PITCH
                      FROM match_level
                      LEFT JOIN read_parquet('{project_location}/eda/player_match_on_pitch.parquet') pt
                        ON match_level.match_id - pt.match_id
                        AND gk_player_id = player_id
                      WHERE IFNULL(MINUTES_ON_PITCH,0) > 0
                      )
                      SELECT gk_player_id, 
                      SUM(gk_save) / SUM(gk_shot_faced) gk_shot_save_pct,
                      CASE 
                      WHEN SUM(gk_penalty_saved) = 0 THEN 0
                      WHEN SUM(gk_penalty_faced) = 0 THEN 0
                      ELSE SUM(gk_penalty_saved) / SUM(gk_penalty_faced) 
                      END AS gk_penalty_save_pct,
                      SUM(q1_shot_xg) / SUM(gk_shot_faced) pct_q1_shot_xg, 
                      SUM(q2_shot_xg) / SUM(gk_shot_faced) pct_q2_shot_xg, 
                      SUM(q3_shot_xg) / SUM(gk_shot_faced) pct_q3_shot_xg, 
                      SUM(q4_shot_xg) / SUM(gk_shot_faced) pct_q4_shot_xg, 
                      SUM(gk_collected) / SUM(MINUTES_ON_PITCH) gk_collected_per_minute, 
                      SUM(gk_keeper_sweeper) / SUM(MINUTES_ON_PITCH) gk_keeper_sweeper_per_minute, 
                      SUM(gk_smother) / SUM(MINUTES_ON_PITCH) gk_smother_per_minute, 
                      SUM(gk_punch) / SUM(MINUTES_ON_PITCH) gk_punch_per_minute, 
                      SUM(gk_shot_faced) / SUM(MINUTES_ON_PITCH) gk_shot_faced_per_minute, 
                      SUM(gk_penalty_faced) / SUM(MINUTES_ON_PITCH) gk_penalty_faced_per_minute,
                      SUM(shot_faced_gk_right_side) / SUM(gk_shot_faced) pct_shot_from_gk_right,
                      SUM(shot_faced_gk_left_side) / SUM(gk_shot_faced) pct_shot_from_gk_left,
                      SUM(shot_faced_gk_unk_side) / SUM(gk_shot_faced) pct_shot_from_gk_unk
                      
                      FROM get_time
                      GROUP BY gk_player_id
                    """).write_csv('gk_k_means.csv')
