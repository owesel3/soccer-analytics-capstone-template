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
                      SELECT PERCENTILE_DISC([0.25,0.5,0.75]) WITHIN GROUP (ORDER BY DIST_TO_GOAL) shot_dist_percentiles
                      FROM read_parquet('{project_location}/eda/shot_level_stats.parquet') 
                      ),
                        get_percentile as (
                        SELECT shot_dist_percentiles[1] percentile_25, shot_dist_percentiles[2] percentile_50, shot_dist_percentiles[3] percentile_75 
                        FROM shot_percentiles
                        ),
                      
                      iso_stats as (
                      SELECT match_id, player_id, shot_first_time, shot_follows_dribble, shot_open_goal, 
                      CASE WHEN shot_body_part = 'Right Foot' THEN 1 ELSE 0 END AS shot_right_foot,
                      CASE WHEN shot_body_part = 'Left Foot' THEN 1 ELSE 0 END AS shot_left_foot,
                      CASE WHEN shot_body_part = 'Head' THEN 1 ELSE 0 END AS shot_header,
                      CASE WHEN shot_outcome = 'Goal' THEN 1 ELSE 0 END AS shot_into_goal,
                      shot_saved_off_target + shot_saved_to_post shot_saved, OFF_ZONE, DIST_TO_GOAL, player_advantage, goal_diff, shot_statsbomb_xg,
                      CASE 
                      WHEN DIST_TO_GOAL <= (SELECT MIN(percentile_25) FROM get_percentile) THEN 'Q1' 
                      WHEN DIST_TO_GOAL <= (SELECT MIN(percentile_50) FROM get_percentile) THEN 'Q2'
                      WHEN DIST_TO_GOAL <= (SELECT MIN(percentile_75) FROM get_percentile) THEN 'Q3'
                      ELSE 'Q4'
                      END AS shot_q
                      
                      FROM read_parquet('{project_location}/eda/shot_level_stats.parquet') s
                      ),
                      agg_match_shots as (
                      SELECT player_id, match_id, SUM(shot_first_time) shot_first_time, SUM(shot_follows_dribble) shot_follows_dribble, SUM(shot_open_goal) shot_open_goal, 
                      SUM(shot_right_foot) shot_right_foot, SUM(shot_left_foot) shot_left_foot, SUM(shot_header) shot_header, SUM(shot_into_goal) shot_into_goal, SUM(shot_saved) shot_saved, COUNT(*) shots_taken,
                      SUM(shot_statsbomb_xg) shot_statsbomb_xg_total,
                      SUM(CASE WHEN shot_q = 'Q1' THEN 1 ELSE 0 END) shot_q1,
                      SUM(CASE WHEN shot_q = 'Q2' THEN 1 ELSE 0 END) shot_q2,
                      SUM(CASE WHEN shot_q = 'Q3' THEN 1 ELSE 0 END) shot_q3,
                      SUM(CASE WHEN shot_q = 'Q4' THEN 1 ELSE 0 END) shot_q4
                      FROM iso_stats
                      GROUP BY player_id, match_id
                      ),
                      get_time_on_pitch as (
                      SELECT agg_match_shots.*, MINUTES_ON_PITCH
                      FROM agg_match_shots
                      LEFT JOIN read_parquet('{project_location}/eda/player_match_on_pitch.parquet') player_min
                        ON agg_match_shots.player_id = player_min.player_id
                        AND agg_match_shots.match_id = player_min.match_id
                      ),
                      player_level as (
                      SELECT player_id, SUM(shot_first_time) shot_first_time, SUM(shot_follows_dribble) shot_follows_dribble, SUM(shot_open_goal) shot_open_goal, 
                      SUM(shot_right_foot) shot_right_foot, SUM(shot_left_foot) shot_left_foot, SUM(shot_header) shot_header, SUM(shot_into_goal) shot_into_goal, 
                      SUM(shot_saved) shot_saved, SUM(shots_taken) shots_taken, SUM(MINUTES_ON_PITCH) MINUTES_ON_PITCH, SUM(shot_statsbomb_xg_total) shot_statsbomb_xg_total,
                      SUM(shot_q1) shot_q1, SUM(shot_q2) shot_q2, SUM(shot_q3) shot_q3, SUM(shot_q4) shot_q4
                      FROM get_time_on_pitch
                      GROUP BY player_id
                      ),
                      stg_pct as (
                      SELECT player_id, shot_first_time / shots_taken pct_shot_first_time, shot_follows_dribble / shots_taken pct_shot_follows_dribble, shot_open_goal / shots_taken pct_shot_open_goal,
                      GREATEST(shot_right_foot / shots_taken , shot_left_foot / shots_taken) pct_shot_dominant_foot, shot_header / shots_taken pct_shot_header, shot_into_goal / shots_taken pct_shot_into_goal,
                      shot_saved / shots_taken pct_shot_saved, shots_taken / MINUTES_ON_PITCH shots_per_minute, shot_into_goal - shot_statsbomb_xg_total goals_over_expected,
                      shot_q1 / shots_taken pct_shot_q1, shot_q2 / shots_taken pct_shot_q2, shot_q3 / shots_taken pct_shot_q3, shot_q4 / shots_taken pct_shot_q4
                      FROM player_level
                      ),
                      zone_total as (
                      SELECT player_id, OFF_ZONE, SUM(shot_into_goal) shot_into_goal, COUNT(*) shots_taken 
                      FROM iso_stats
                      GROUP BY player_id, OFF_ZONE
                      ),
                      zone_adj_total as (
                      SELECT player_id, OFF_ZONE_ADJ, SUM(shot_into_goal) shot_into_goal, SUM(shots_taken) shots_taken
                      FROM (
                      SELECT player_id, shot_into_goal, shots_taken, CASE WHEN OFF_ZONE LIKE 'OBI%' OR OFF_ZONE LIKE 'OAI%' THEN OFF_ZONE ELSE 'Other' END AS OFF_ZONE_ADJ
                      FROM zone_total
                      )
                      GROUP BY player_id, OFF_ZONE_ADJ
                      ),

                      pivot_totals as (

                      SELECT player_id, 
                      --SUM(CASE WHEN OFF_ZONE_ADJ = 'OAIR' THEN shot_into_goal ELSE 0 END) shot_into_goal_OAIR, 
                      --SUM(CASE WHEN OFF_ZONE_ADJ = 'OAIR' THEN shots_taken ELSE 0 END) shots_taken_OAIR,  
                      --SUM(CASE WHEN OFF_ZONE_ADJ = 'OAIL' THEN shot_into_goal ELSE 0 END) shot_into_goal_OAIL, 
                      --SUM(CASE WHEN OFF_ZONE_ADJ = 'OAIL' THEN shots_taken ELSE 0 END) shots_taken_OAIL, 
                      --SUM(CASE WHEN OFF_ZONE_ADJ = 'OBIL' THEN shot_into_goal ELSE 0 END) shot_into_goal_OBIL, 
                      --SUM(CASE WHEN OFF_ZONE_ADJ = 'OBIL' THEN shots_taken ELSE 0 END) shots_taken_OBIL, 
                      --SUM(CASE WHEN OFF_ZONE_ADJ = 'OBIR' THEN shot_into_goal ELSE 0 END) shot_into_goal_OBIR, 
                      --SUM(CASE WHEN OFF_ZONE_ADJ = 'OBIR' THEN shots_taken ELSE 0 END) shots_taken_OBIR, 
                      --SUM(CASE WHEN OFF_ZONE_ADJ = 'Other' THEN shot_into_goal ELSE 0 END) shot_into_goal_Other, 
                      --SUM(CASE WHEN OFF_ZONE_ADJ = 'Other' THEN shots_taken ELSE 0 END) shots_taken_Other,

                      SUM(CASE WHEN OFF_ZONE LIKE 'OA%' THEN shot_into_goal ELSE 0 END) shot_into_goal_OA,
                      SUM(CASE WHEN OFF_ZONE LIKE 'OA%' THEN shots_taken ELSE 0 END) shots_taken_OA,

                      SUM(CASE WHEN OFF_ZONE LIKE 'OB%' THEN shot_into_goal ELSE 0 END) shot_into_goal_OB,
                      SUM(CASE WHEN OFF_ZONE LIKE 'OB%' THEN shots_taken ELSE 0 END) shots_taken_OB,
                      SUM(shots_taken) shots_taken,
                      SUM(shot_into_goal) shot_into_goal
                      FROM zone_total --zone_adj_total
                      GROUP BY player_id

                      ),
                      final_zone as (
                      SELECT player_id, 
                      --shots_taken_OAIR / shots_taken pct_shots_taken_OAIR, 
                      --shots_taken_OAIL / shots_taken pct_shots_taken_OAIL, 
                      --shots_taken_OBIL / shots_taken pct_shots_taken_OBIL, 
                      --shots_taken_OBIR / shots_taken pct_shots_taken_OBIR, 
                      --shots_taken_Other / shots_taken pct_shots_taken_Other,
                      --CASE
                      --WHEN shot_into_goal_OAIR = 0 OR shot_into_goal = 0 THEN 0
                      --ELSE shot_into_goal_OAIR / shot_into_goal 
                      --END AS pct_goal_OAIR,
                      --CASE
                      --WHEN shot_into_goal_OAIL = 0 OR shot_into_goal = 0 THEN 0
                      --ELSE shot_into_goal_OAIL / shot_into_goal 
                      --END AS pct_goal_OAIL,
                      --CASE
                      --WHEN shot_into_goal_OBIL = 0 OR shot_into_goal = 0 THEN 0
                      --ELSE shot_into_goal_OBIL / shot_into_goal 
                      --END AS pct_goal_OBIL,
                      --CASE
                      --WHEN shot_into_goal_OBIR = 0 OR shot_into_goal = 0 THEN 0
                      --ELSE shot_into_goal_OBIR / shot_into_goal 
                      --END AS pct_goal_OBIR,
                      --CASE
                      --WHEN shot_into_goal_Other = 0 OR shot_into_goal = 0 THEN 0
                      --ELSE shot_into_goal_Other / shot_into_goal 
                      --END AS pct_goal_Other,

                      shots_taken_OA / shots_taken pct_shots_taken_OA,
                      CASE
                      WHEN shot_into_goal_OA = 0 OR shot_into_goal = 0 THEN 0
                      ELSE shot_into_goal_OA / shot_into_goal 
                      END AS pct_goal_OA,

                      shots_taken_OB / shots_taken pct_shots_taken_OB,
                      CASE
                      WHEN shot_into_goal_OB = 0 OR shot_into_goal = 0 THEN 0
                      ELSE shot_into_goal_OB / shot_into_goal 
                      END AS pct_goal_OB


                      FROM pivot_totals
                      )

                      SELECT stg_pct.*, 
                      --pct_shots_taken_OAIR, pct_shots_taken_OAIL, pct_shots_taken_OBIL, pct_shots_taken_OBIR, pct_shots_taken_Other,
                      --pct_goal_OAIR, pct_goal_OAIL, pct_goal_OBIL, pct_goal_OBIR, pct_goal_Other
                      pct_shots_taken_OA pct_shots_taken_in_arc, pct_goal_OA pct_of_goals_from_arc, pct_shots_taken_OB pct_shots_taken_in_box, pct_goal_OB pct_of_goals_from_box
                      FROM stg_pct
                      LEFT JOIN final_zone
                        ON stg_pct.player_id = final_zone.player_id
                    """).write_parquet('shot_k_means.parquet')
