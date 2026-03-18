import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'

possession_tl = duckdb.sql(f"""
                           LOAD spatial;

                           with match_events as (
                                SELECT id, index_num, period, minute, second, timestamp, duration, location_x, location_y, possession, possession_team_id, type, 
                                    match_id, player_id, position_id, play_pattern, pass_length,
                                CASE WHEN type = 'Carry' THEN 1 ELSE 0 END AS CARRY_IND,
                                CASE WHEN type = 'Pass' THEN 1 ELSE 0 END AS PASS_IND,
                                CASE WHEN type = 'Pressure' THEN 1 ELSE 0 END AS PRESSURE_IND,
                                CASE WHEN type = 'Shot' THEN 1 ELSE 0 END AS SHOT_IND,
                                CASE WHEN type = 'Dribble' THEN 1 ELSE 0 END AS DRIBBLE_IND,
                                CASE WHEN type = 'Dribble Past' THEN 1 ELSE 0 END AS DRIBBLE_PAST_IND,
                                CASE WHEN type = 'Dispossessed' THEN 1 ELSE 0 END AS DISPOSSESS_IND,
                                CASE WHEN type = 'Miscontrol' THEN 1 ELSE 0 END AS MISCONTROL_IND,
                                CASE WHEN type = 'Interception' THEN 1 ELSE 0 END AS INTERCEPTION_IND,
                                CASE WHEN possession_team_id = team_id THEN player_id ELSE NULL END AS possessing_player,
                                CASE WHEN pass_length is NOT NULL THEN 1 ELSE 0 END as pass_attempt_ind,
                                CASE WHEN pass_height = 'High Pass' THEN 1 ELSE 0 END as high_pass_ind,
                                CASE WHEN pass_height = 'Ground Pass' THEN 1 ELSE 0 END as ground_pass_ind,
                                CASE WHEN pass_height = 'Low Pass' THEN 1 ELSE 0 END as low_pass_ind,
                                CASE WHEN pass_body_part = 'Drop Kick' THEN 1 ELSE 0 END as drop_kick_pass_ind,
                                CASE WHEN pass_body_part = 'Head' THEN 1 ELSE 0 END as head_pass_ind,
                                CASE WHEN pass_body_part = 'Keeper Arm' THEN 1 ELSE 0 END as keeper_arm_pass_ind,
                                CASE WHEN pass_body_part = 'Left Foot' THEN 1 ELSE 0 END as left_foot_pass_ind,
                                CASE WHEN pass_body_part = 'Right Foot' THEN 1 ELSE 0 END as right_foot_pass_ind,
                                CASE WHEN pass_body_part = 'Other' THEN 1 ELSE 0 END as other_pass_ind,
                                CASE WHEN pass_technique = 'Inswinging' THEN 1 ELSE 0 END as inswinging_pass_ind,
                                CASE WHEN pass_technique = 'Straight' THEN 1 ELSE 0 END as straight_pass_ind,
                                CASE WHEN pass_technique = 'Through Ball' THEN 1 ELSE 0 END as through_ball_pass_ind



                                FROM read_parquet('{project_location}/Statsbomb/events.parquet') 
                                WHERE --match_id = 15973 AND 
                                type NOT IN ('Starting XI','Half Start', 'Half End','Ball Receipt*', 'Ball Recovery')
                                AND possession_team_id = team_id
                                AND location_x IS NOT NULL
                                AND location_y IS NOT NULL
                                ),
                                get_next as (
                                SELECT match_events.*, LEAD(location_x,1) OVER (PARTITION BY match_id ORDER BY match_id, index_num) next_location_x, LEAD(location_y,1) OVER (PARTITION BY match_id ORDER BY match_id, index_num) next_location_y
                                FROM match_events
                                ),
                                calc_event_dist as (
                                SELECT get_next.*, ST_Distance(ST_Point(location_x, location_y), ST_Point(next_location_x, next_location_y)) euclidean_distance
                                FROM get_next
                                ),
                                possession_metrics as (
                                SELECT match_id, period, possession, possession_team_id, play_pattern, 
                                    MIN(index_num) min_index, MAX(index_num) max_index,
                                    SUM(IFNULL(duration,0)) total_possession_time, 
                                    SUM(CARRY_IND) carries, 
                                    SUM(PASS_IND) passes, 
                                    SUM(PRESSURE_IND) pressures, 
                                    SUM(SHOT_IND) shots, 
                                    SUM(DRIBBLE_IND) dribbles, 
                                    SUM(DRIBBLE_PAST_IND) dribble_pasts, 
                                    SUM(DISPOSSESS_IND) dispossessions, 
                                    SUM(MISCONTROL_IND) miscontrols,
                                    SUM(INTERCEPTION_IND) interceptions,
                                    SUM(euclidean_distance) total_distance,
                                    COUNT(distinct possessing_player) possessing_players,
                                    SUM(pass_length) pass_distance,
                                    SUM(pass_attempt_ind) pass_attempts,
                                    SUM(high_pass_ind) high_passes,
                                    SUM(ground_pass_ind) ground_passes,
                                    SUM(low_pass_ind) low_passes,
                                    SUM(drop_kick_pass_ind) drop_kick_passes,
                                    SUM(head_pass_ind) head_passes,
                                    SUM(keeper_arm_pass_ind) keeper_arm_passes,
                                    SUM(left_foot_pass_ind) left_foot_passes,
                                    SUM(right_foot_pass_ind) right_foot_passes,
                                    SUM(other_pass_ind) other_passes,
                                    SUM(inswinging_pass_ind) inswinging_passes,
                                    SUM(straight_pass_ind) straight_passes,
                                    SUM(through_ball_pass_ind) through_ball_passes
                                    
                                FROM calc_event_dist

                                GROUP BY match_id, period, possession, possession_team_id, play_pattern
                                ),
                                start_stop_coordinates as (
                                SELECT pm.*, iso_events.location_x poss_start_x, iso_events.location_y poss_start_y, iso_events2.location_x poss_end_x, iso_events2.location_y poss_end_y
                                FROM possession_metrics pm 

                                LEFT JOIN (SELECT id, index_num, location_x, location_y, possession, possession_team_id, match_id
                                            FROM match_events) iso_events
                                    ON pm.match_id = iso_events.match_id
                                    AND pm.possession = iso_events.possession
                                    AND pm.possession_team_id = iso_events.possession_team_id
                                    AND pm.min_index = iso_events.index_num
                                LEFT JOIN (SELECT id, index_num, location_x, location_y, possession, possession_team_id, match_id
                                            FROM match_events) iso_events2
                                    ON pm.match_id = iso_events2.match_id
                                    AND pm.possession = iso_events2.possession
                                    AND pm.possession_team_id = iso_events2.possession_team_id
                                    AND pm.max_index = iso_events2.index_num
                                )

                                SELECT start_stop_coordinates.match_id, start_stop_coordinates.period, start_stop_coordinates.possession, start_stop_coordinates.possession_team_id, play_pattern,
                                    total_possession_time, carries,  passes, pressures, shots, dribbles, dribble_pasts, dispossessions, miscontrols, interceptions, total_distance, possessing_players,
                                    pass_distance, pass_attempts, high_passes, ground_passes, low_passes, drop_kick_passes, head_passes, keeper_arm_passes, left_foot_passes, right_foot_passes, other_passes,
                                    inswinging_passes, straight_passes, through_ball_passes, 

                                ST_Distance(ST_Point(poss_start_x, poss_start_y), ST_Point(poss_end_x, poss_end_y)) relative_distance
                                FROM start_stop_coordinates 
                                ORDER BY possession
                                """).write_parquet('possession_metrics.parquet')
print(possession_tl)
