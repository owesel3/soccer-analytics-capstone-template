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

y_coords = duckdb.sql(f"""
                     LOAD spatial;
                      

                      with shot_side as (
                     SELECT distinct match_id, period, team_id, possession_team_id, 
                      CASE WHEN location_x >= 60 THEN 'R'
                      ELSE 'L'
                      END AS SHOOTING_SIDE
                        FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
                        WHERE type = 'Shot'
                        ),
                        bad_matches_shot_side as (
                        SELECT match_id
                        FROM shot_side
                        GROUP BY match_id, period, possession_team_id
                        HAVING IFNULL(COUNT(distinct SHOOTING_SIDE),0) != 1
                        ),
                    
                    label_zones as (
                        SELECT match_id, id, index_num, period, minute, second, timestamp, duration, player_id, team_id, possession_team_id, type, location_x, location_y,
                        CASE WHEN location_x <= 40 THEN 'L'
                        ELSE 'R'
                        END AS PITCH_ORIENTATION,
                      CASE 
                      WHEN location_x <= 18 AND location_y >= 19.885 AND  location_y <= 60.115 THEN 'Box'
                      WHEN location_x <= 18 AND location_y > 60.115 THEN '1'
                      WHEN location_x > 18 AND location_x <= 60 AND location_y > 60.115 THEN '2'
                      WHEN location_x > 18 AND location_x <= 60 AND location_y <= 60.115 AND location_y >= 19.885 THEN '3'
                     WHEN location_x > 18 AND location_x <= 60 AND location_y < 19.885 THEN '4'
                     WHEN location_x <= 18 AND location_y < 60.885 THEN '5'
                      
                      WHEN location_x >= 102 AND location_y >= 19.885 AND  location_y <= 60.115 THEN 'Box'
                      WHEN location_x >= 102 AND location_y > 60.115 THEN '6'
                      WHEN location_x < 102 AND location_x > 60 AND location_y > 60.115 THEN '7'
                      WHEN location_x < 102 AND location_x > 60 AND location_y <= 60.115 AND location_y >= 19.885 THEN '8'
                     WHEN location_x < 102 AND location_x > 60 AND location_y < 19.885 THEN '9'
                     WHEN location_x >= 102 AND location_y < 60.885 THEN '10'
                      ELSE NULL 
                      END AS ZONE_LOCATION,


                      CASE 
                      WHEN location_x <= 6 AND location_y >= 30.855 AND  location_y <= 49.125 THEN 'Goal Area'
                      WHEN location_x <= 6 AND location_y > 49.125 THEN '1'
                      WHEN location_x > 6 AND location_x <= 60 AND location_y > 49.125 THEN '2'
                      WHEN location_x > 6 AND location_x <= 60 AND location_y <= 49.125 AND location_y >= 30.855 THEN '3'
                     WHEN location_x > 6 AND location_x <= 60 AND location_y < 30.855 THEN '4'
                     WHEN location_x <= 6 AND location_y < 60.885 THEN '5'
                      
                      WHEN location_x >= 114 AND location_y >= 30.855 AND  location_y <= 49.125 THEN 'Goal Area'
                      WHEN location_x >= 114 AND location_y > 49.125 THEN '6'
                      WHEN location_x < 114 AND location_x > 60 AND location_y > 49.125 THEN '7'
                      WHEN location_x < 114 AND location_x > 60 AND location_y <= 49.125 AND location_y >= 30.855 THEN '8'
                     WHEN location_x < 114 AND location_x > 60 AND location_y < 30.855 THEN '9'
                     WHEN location_x >= 114 AND location_y < 60.885 THEN '10'
                      ELSE NULL 
                      END AS ZONE_LOCATION_2,

                      CASE
                      WHEN location_x <= 60 AND location_y > 43.66 THEN '1'
                      WHEN location_x <= 60 AND location_y <= 43.66 AND location_y >= 36.34 THEN '2'
                      WHEN location_x <= 60 AND location_y < 36.34 THEN '3'

                      WHEN location_x > 60 AND location_y > 43.66 THEN '4'
                      WHEN location_x > 60 AND location_y <= 43.66 AND location_y >= 36.34 THEN '5'
                      WHEN location_x > 60 AND location_y < 36.34 THEN '6'
                      ELSE NULL
                      END AS ZONE_LOCATION_3



                        FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
                        WHERE location_y IS NOT NULL AND match_id = 7542
                        ),
                        add_prox_box as (

                        SELECT label_zones.*, 
                        CASE
                        WHEN ZONE_LOCATION = 'Box' THEN 0
                        WHEN ZONE_LOCATION = '1' THEN location_y - 60.115
                        WHEN ZONE_LOCATION = '2' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(12, 60.115)) 
                        WHEN ZONE_LOCATION = '3' THEN location_x - 18
                        WHEN ZONE_LOCATION = '4' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(12, 19.885)) 
                        WHEN ZONE_LOCATION = '5' THEN 19.885 - location_y
                        WHEN ZONE_LOCATION = '6' THEN location_y - 60.115
                        WHEN ZONE_LOCATION = '7' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(102, 60.115))  
                        WHEN ZONE_LOCATION = '8' THEN 102 - location_x
                        WHEN ZONE_LOCATION = '9' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(102, 19.885)) 
                        WHEN ZONE_LOCATION = '10' THEN 19.885 - location_y
                        ELSE NULL 
                        END AS PROX_BOX, 
                        CASE
                        WHEN ZONE_LOCATION_2 = 'Goal Area' THEN 0
                        WHEN ZONE_LOCATION_2 = '1' THEN location_y - 49.125
                        WHEN ZONE_LOCATION_2 = '2' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(6, 49.125)) 
                        WHEN ZONE_LOCATION_2 = '3' THEN location_x - 6
                        WHEN ZONE_LOCATION_2 = '4' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(6, 30.855)) 
                        WHEN ZONE_LOCATION_2 = '5' THEN 30.855 - location_y
                        WHEN ZONE_LOCATION_2 = '6' THEN location_y - 49.125
                        WHEN ZONE_LOCATION_2 = '7' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(114, 49.125)) 
                        WHEN ZONE_LOCATION_2 = '8' THEN 114 - location_x
                        WHEN ZONE_LOCATION_2 = '9' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(114, 30.855)) 
                        WHEN ZONE_LOCATION_2 = '10' THEN 30.855 - location_y
                        ELSE NULL 
                        END AS GOAL_AREA_DIST, 

                        CASE
                        WHEN ZONE_LOCATION_3 = '1' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(0, 43.66)) 
                        WHEN ZONE_LOCATION_3 = '2' THEN location_x
                        WHEN ZONE_LOCATION_3 = '3' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(0, 36.34)) 

                        WHEN ZONE_LOCATION_3 = '4' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(120, 43.66)) 
                        WHEN ZONE_LOCATION_3 = '5' THEN 120 - location_x
                        WHEN ZONE_LOCATION_3 = '6' THEN ST_Distance(ST_Point(location_x, location_y), ST_Point(120, 36.34)) 

                        ELSE NULL
                        END AS DIST_TO_GOAL,

                        CASE
                        WHEN location_x <= 40 OR location_x > 80 THEN 'Outer'
                        ELSE 'Middle'
                        END AS PITCH_THIRD

                        FROM label_zones

                        ),
                        check_shooting_side as (
                        SELECT add_prox_box.match_id, id, player_id, add_prox_box.period, duration, add_prox_box.team_id, add_prox_box.possession_team_id, type, 
                        pitch_orientation, DIST_TO_GOAL, GOAL_AREA_DIST, prox_box, pitch_third, SHOOTING_SIDE
                        FROM add_prox_box
                        LEFT JOIN (SELECT * 
                                    FROM shot_side 
                                    WHERE match_id NOT IN (SELECT match_id FROM bad_matches_shot_side) 
                                    ) get_shot_side

                            ON add_prox_box.match_id = get_shot_side.match_id
                            AND add_prox_box.period = get_shot_side.period
                            AND add_prox_box.team_id = get_shot_side.team_id
                        --WHERE duration IS NOT NULL
                        )

                        SELECT match_id, id, period, team_id, 
                        possession_team_id, DIST_TO_GOAL, 
                        GOAL_AREA_DIST, PROX_BOX, PITCH_THIRD,
                        CASE 
                        WHEN PITCH_ORIENTATION = 'R' AND PITCH_THIRD = 'Outer' AND SHOOTING_SIDE = 'R' THEN 'Offensive Third'
                        WHEN PITCH_ORIENTATION = 'R' AND PITCH_THIRD = 'Outer' AND SHOOTING_SIDE = 'L' THEN 'Defensive Third'
                        WHEN PITCH_ORIENTATION = 'L' AND PITCH_THIRD = 'Outer' AND SHOOTING_SIDE = 'R' THEN 'Defensive Third'
                        WHEN PITCH_ORIENTATION = 'L' AND PITCH_THIRD = 'Outer' AND SHOOTING_SIDE = 'L' THEN 'Offensive Third'

                        WHEN PITCH_ORIENTATION = 'R' AND PITCH_THIRD = 'Middle' AND SHOOTING_SIDE = 'R' THEN 'Offensive Middle'
                        WHEN PITCH_ORIENTATION = 'R' AND PITCH_THIRD = 'Middle' AND SHOOTING_SIDE = 'L' THEN 'Defensive Middle'
                        WHEN PITCH_ORIENTATION = 'L' AND PITCH_THIRD = 'Middle' AND SHOOTING_SIDE = 'R' THEN 'Defensive Middle'
                        WHEN PITCH_ORIENTATION = 'L' AND PITCH_THIRD = 'Middle' AND SHOOTING_SIDE = 'L' THEN 'Offensive Middle'

                        ELSE NULL

                        END AS PITCH_THIRD_ADJ
                        


                        FROM check_shooting_side
                    """)
print(y_coords)