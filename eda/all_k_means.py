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
                      SELECT every_player.player_id, pct_shot_first_time, pct_shot_follows_dribble, pct_shot_open_goal, pct_shot_dominant_foot, 
                      pct_shot_header, pct_shot_into_goal pct_shot_goal_scored, pct_shot_saved pct_shot_taken_saved, shots_per_minute, 
                      goals_over_expected, pct_shot_q1 pct_shot_from_q1_dist, pct_shot_q2 pct_shot_from_q2_dist, 
                      pct_shot_q3 pct_shot_from_q3_dist, pct_shot_q4 pct_shot_from_q4_dist, pct_shots_taken_in_arc, pct_of_goals_from_arc, pct_shots_taken_in_box, pct_of_goals_from_box, 
                      avg_progress_to_goal_shooting_on_per_carry, avg_distance_traveled_per_carry, pct_carrying_team_possession, pct_miscontrol, 
                      pct_dispossessed, carries, pct_duel_won, duels_per_minute, foul_committed_per_minute, yellow_cards_per_minute, 
                      red_cards_per_minute, pressures_applied_per_minute defensive_pressures_applied_per_minute, blocks_per_minute defensive_blocks_per_minute, 
                      interceptions_per_minute defensive_interceptions_per_minute, 
                      MINUTES_ON_PITCH, pass_attempt, pass_success_pct, pass_attempts_per_minute, percent_cross_success, percent_through_ball_success, 
                      percent_through_ball percent_pass_through_ball, percent_cross percent_pass_cross, percent_q1 percent_q1_pass_dist, 
                      percent_q2 percent_q2_pass_dist, percent_q3 percent_q3_pass_dist, percent_q4 percent_q4_pass_dist, pass_shot_assist_per_minute
                      FROM (
                      SELECT player_id
                      FROM read_parquet('{project_location}/eda/shot_k_means.parquet') 

                      UNION

                      SELECT player_id
                      FROM read_parquet('{project_location}/eda/carry_k_means.parquet') 

                      UNION

                      SELECT player_id
                      FROM read_parquet('{project_location}/eda/defense_k_means.parquet') 

                      UNION

                      SELECT player_id
                      FROM read_parquet('{project_location}/eda/pass_k_means.parquet') 
                      ) every_player
                      LEFT JOIN read_parquet('{project_location}/eda/shot_k_means.parquet') s
                        ON every_player.player_id = s.player_id
                      LEFT JOIN read_parquet('{project_location}/eda/carry_k_means.parquet') c
                        ON every_player.player_id = c.player_id
                      LEFT JOIN read_parquet('{project_location}/eda/defense_k_means.parquet') d
                        ON every_player.player_id = d.player_id
                      LEFT JOIN read_parquet('{project_location}/eda/pass_k_means.parquet') p
                        ON every_player.player_id = p.player_id
                    """).write_parquet('all_k_means.parquet')
