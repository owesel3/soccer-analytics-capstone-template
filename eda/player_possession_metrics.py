import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'

possession_tl = duckdb.sql(f"""
                           LOAD spatial;

                           with match_events as (
                                SELECT id, index_num, period, minute, second, timestamp, duration, location_x, location_y, possession, possession_team_id, team_id, type, 
                                    match_id, player_id, position_id, play_pattern, pass_length,
                               (minute * 60) + second seconds_into_period,
                                CASE WHEN type = 'Carry' THEN 1 ELSE 0 END AS CARRY_IND,
                                CASE WHEN type = 'Pass' THEN 1 ELSE 0 END AS PASS_IND,
                                CASE WHEN type = 'Pressure' THEN 1 ELSE 0 END AS PRESSURE_IND,
                                CASE WHEN type = 'Shot' THEN 1 ELSE 0 END AS SHOT_IND,
                                CASE WHEN type = 'Dribble' THEN 1 ELSE 0 END AS DRIBBLE_IND,
                                CASE WHEN type = 'Dribbled Past' THEN 1 ELSE 0 END AS DRIBBLED_PAST_IND,
                                CASE WHEN type = 'Dispossessed' THEN 1 ELSE 0 END AS DISPOSSESS_IND,
                                CASE WHEN type = 'Miscontrol' THEN 1 ELSE 0 END AS MISCONTROL_IND,
                                CASE WHEN type = 'Interception' THEN 1 ELSE 0 END AS INTERCEPTION_IND,
                                CASE WHEN type = 'Ball Receipt*' THEN 1 ELSE 0 END AS BALL_RECEIPT_IND,
                                CASE WHEN type = 'Ball Recovery' THEN 1 ELSE 0 END AS BALL_RECOVERY_IND,
                                CASE WHEN type = '50/50' THEN 1 ELSE 0 END AS IS_50_50_IND,
                                CASE WHEN type = 'Bad Behaviour' THEN 1 ELSE 0 END AS BAD_BEHAVIOR_IND,
                                CASE WHEN type = 'Block' THEN 1 ELSE 0 END AS BLOCK_IND,
                                CASE WHEN type = 'Clearance' THEN 1 ELSE 0 END AS CLEARANCE_IND,
                                CASE WHEN type = 'Duel' THEN 1 ELSE 0 END AS DUEL_IND,
                                CASE WHEN type = 'Error' THEN 1 ELSE 0 END AS ERROR_IND,
                                CASE WHEN type = 'Foul Committed' THEN 1 ELSE 0 END AS FOUL_COMMITTED_IND,
                                CASE WHEN type = 'Foul Won' THEN 1 ELSE 0 END AS FOUL_WON_IND,
                                CASE WHEN type = 'Offside' THEN 1 ELSE 0 END AS OFFSIDE_IND,
                                CASE WHEN type = 'Own Goal Against' THEN 1 ELSE 0 END AS OWN_GOAL_AGAINST_IND,
                                CASE WHEN type = 'Own Goal For' THEN 1 ELSE 0 END AS OWN_GOAL_FOR_IND,
                                CASE WHEN type = 'Shield' THEN 1 ELSE 0 END AS SHIELD_IND,
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
                                WHERE match_id = 15973 AND 
                                type NOT IN ('Starting XI','Half Start', 'Half End'--,'Ball Receipt*', 'Ball Recovery'
                                )
                                --AND possession_team_id = team_id
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
                                )
                                SELECT match_id, period, possession, possession_team_id, team_id, play_pattern, player_id,
                                    MIN(index_num) min_index, MAX(index_num) max_index,
                                    SUM(CARRY_IND) carries, 
                                    SUM(PASS_IND) passes, 
                                    SUM(PRESSURE_IND) pressures, 
                                    SUM(SHOT_IND) shots, 
                                    SUM(DRIBBLE_IND) dribbles, 
                                    SUM(DRIBBLED_PAST_IND) dribbled_pasts, 
                                    SUM(DISPOSSESS_IND) dispossessions, 
                                    SUM(MISCONTROL_IND) miscontrols,
                                    SUM(INTERCEPTION_IND) interceptions,
                                    SUM(BALL_RECEIPT_IND) ball_receipts,
                                    SUM(BALL_RECOVERY_IND) ball_recoveries,
                                    SUM(IFNULL(euclidean_distance,0)) total_distance,
                                    COUNT(distinct possessing_player) possessing_players,
                                    SUM(IFNULL(pass_length,0)) pass_distance,
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
                                    SUM(through_ball_pass_ind) through_ball_passes,
                                    SUM(duration) time_of_events,
                                    MAX(duration) longest_event,
                                    COUNT(index_num) events_attributed,

                                    SUM(IS_50_50_IND) is_50_50_events,
                                    SUM(BAD_BEHAVIOR_IND) bad_behavior_events,
                                    SUM(BLOCK_IND) blocks,
                                    SUM(CLEARANCE_IND) clearances,
                                    SUM(DUEL_IND) duels,
                                    SUM(ERROR_IND) errors,
                                    SUM(FOUL_COMMITTED_IND) fouls_committed,
                                    SUM(FOUL_WON_IND) fouls_won,
                                    SUM(OFFSIDE_IND) offsides,
                                    SUM(OWN_GOAL_AGAINST_IND) own_goals_against,
                                    SUM(OWN_GOAL_FOR_IND) own_goals_for,
                                    SUM(SHIELD_IND) shields
                                    
                                FROM calc_event_dist

                                GROUP BY match_id, period, possession, possession_team_id, team_id, play_pattern, player_id
                                """).write_parquet('player_possession_metrics.parquet')
print(possession_tl)
