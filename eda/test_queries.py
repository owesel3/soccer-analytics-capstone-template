import duckdb
#import math
#import matplotlib.pyplot as plt
#import numpy as np
#from sklearn.cluster import KMeans
#import polars as pl

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'
#'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'
#'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/eda'



#print(x_coords)

#plt.scatter(x_coords, y_coords)
#plt.savefig('another_test.png')



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
                     """)

print(y_coords)






# y_coords = duckdb.sql(f"""

#                       with match_stats as (
#                       SELECT c.player_id, c.match_id, c.possession_team_id,
#                       SUM(IFNULL(duration,0)) total_seconds_carrying, 
#                       --AVG(IFNULL(duration,0)) avg_seconds_carry, 
#                       SUM(IFNULL(DISTANCE_TRAVELED,0)) total_distance_traveled_carry, 
#                       --AVG(IFNULL(DISTANCE_TRAVELED,0)) avg_distance_traveled_carry, 
#                       SUM(IFNULL(PROGRESS_TO_GOAL_SHOOTING_ON,0)) total_progress_to_goal_shooting_on_carry,
#                       --AVG(IFNULL(PROGRESS_TO_GOAL_SHOOTING_ON,0)) avg_progress_to_goal_shooting_on_carry, 
#                       COUNT(*) carries
#                       FROM read_parquet('{project_location}/eda/carry.parquet') c
#                       LEFT JOIN read_parquet('{project_location}/eda/event_proximity.parquet') ep
#                         ON c.id = ep.id
#                       GROUP BY c.player_id, c.match_id, c.possession_team_id
#                       ),
#                       agg_player as (

#                       SELECT match_stats.player_id, 
#                        SUM(total_seconds_carrying) total_seconds_carrying, 
#                        SUM(total_distance_traveled_carry) total_distance_traveled_carry,
#                        SUM(team_seconds_possession_when_player_on_pitch) total_team_seconds_possession_when_player_on_pitch, 
#                        SUM(total_progress_to_goal_shooting_on_carry) total_progress_to_goal_shooting_on_carry, 
#                        SUM(carries) carries
#                       FROM match_stats

#                       LEFT JOIN (
#                                   SELECT possession_team_id, pt.player_id, e.match_id, SUM(IFNULL(duration,0)) team_seconds_possession_when_player_on_pitch 
#                                   FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
#                                   LEFT JOIN read_parquet('{project_location}/eda/player_match_timeline_with_score.parquet') pt
#                                     ON e.match_id = pt.match_id
#                                     AND e.period = pt.period
#                                     AND possession_team_id = pt.team_id
#                                     AND strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(minute) + TO_SECONDS(second) >= interval_start
#                                     AND strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(minute) + TO_SECONDS(second) < interval_end
#                                   GROUP BY possession_team_id, pt.player_id, e.match_id
#                                   HAVING SUM(IFNULL(duration,0)) > 0
#                                 ) team_possession

#                         ON match_stats.match_id = team_possession.match_id
#                         AND match_stats.possession_team_id = team_possession.possession_team_id
#                         AND match_stats.player_id = team_possession.player_id


#                       GROUP BY match_stats.player_id

#                       )
#                       SELECT agg_player.player_id, 
#                        CASE
#                        WHEN IFNULL(total_progress_to_goal_shooting_on_carry,0) <= 0 OR IFNULL(carries,0) <= 0 THEN 0
#                        ELSE IFNULL(total_progress_to_goal_shooting_on_carry,0) / IFNULL(carries,0)
#                        END AS avg_progress_to_goal_shooting_on_per_carry, 
#                        CASE
#                        WHEN IFNULL(total_distance_traveled_carry,0) <= 0 OR IFNULL(carries,0) <= 0 THEN 0
#                        ELSE IFNULL(total_distance_traveled_carry,0) / IFNULL(carries,0)
#                        END AS avg_distance_traveled_per_carry, 
#                        (total_seconds_carrying + other_possession_time) / total_team_seconds_possession_when_player_on_pitch pct_carrying_team_possession,
#                        miscontrols / carries pct_miscontrol, dispossessed / carries pct_dispossessed,
#                        carries
#                        --, other_possession_time, dispossessed, bad_possession_time, miscontrols

#                        FROM agg_player
#                        LEFT JOIN (SELECT player_id, SUM(duration) bad_possession_time, 
#                                     SUM(CASE WHEN type = 'Dispossessed' THEN 1 ELSE 0 END) dispossessed,
#                                     SUM(CASE WHEN type = 'Miscontrol' THEN 1 ELSE 0 END) miscontrols
#                                     FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') 
#                                     WHERE type IN ('Dispossessed', 'Miscontrol') 
#                                     GROUP BY player_id) bad_poss
#                           ON agg_player.player_id = bad_poss.player_id
#                         LEFT JOIN (SELECT player_id, SUM(duration) other_possession_time FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') WHERE type IN ('Dribble') GROUP BY player_id) other_poss
#                           ON agg_player.player_id = other_poss.player_id
#                        ORDER BY carries DESC
#                      """)

# print(y_coords)

# y_coords = duckdb.sql(f"""

#                       SELECT --player_id, team_id, match_id, goalkeeper_type, 
#                       --goalkeeper_outcome, 
#                       distinct goalkeeper_technique, 
#                       goalkeeper_position--, goalkeeper_body_part
#                       FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
#                       WHERE type = 'Goal Keeper' AND goalkeeper_outcome IN ('Saved Twice','Collected Twice ')
#                      """)

# print(y_coords)


# y_coords = duckdb.sql(f"""

#                       with match_stats as (
#                       SELECT c.player_id, c.match_id, c.possession_team_id,
#                       SUM(IFNULL(duration,0)) total_seconds_carrying, 
#                       --AVG(IFNULL(duration,0)) avg_seconds_carry, 
#                       SUM(IFNULL(DISTANCE_TRAVELED,0)) total_distance_traveled_carry, 
#                       --AVG(IFNULL(DISTANCE_TRAVELED,0)) avg_distance_traveled_carry, 
#                       SUM(IFNULL(PROGRESS_TO_GOAL_SHOOTING_ON,0)) total_progress_to_goal_shooting_on_carry,
#                       --AVG(IFNULL(PROGRESS_TO_GOAL_SHOOTING_ON,0)) avg_progress_to_goal_shooting_on_carry, 
#                       COUNT(*) carries
#                       FROM read_parquet('{project_location}/eda/carry.parquet') c
#                       LEFT JOIN read_parquet('{project_location}/eda/event_proximity.parquet') ep
#                         ON c.id = ep.id
#                       GROUP BY c.player_id, c.match_id, c.possession_team_id
#                       ),
#                       agg_player as (
#                       SELECT match_stats.player_id, 
#                       SUM(total_seconds_carrying) total_seconds_carrying, 
#                       SUM(total_distance_traveled_carry) total_distance_traveled_carry, 
#                       SUM(total_progress_to_goal_shooting_on_carry) total_progress_to_goal_shooting_on_carry, 
#                       SUM(carries) carries,

#                       SUM(MINUTES_ON_PITCH * 60) player_seconds_on_pitch,
#                       SUM(team_possession_duration) team_possession_seconds
#                       --avg_seconds_carry, avg_progress_to_goal_shooting_on_carry, avg_distance_traveled_carry, 
#                       --total_seconds_carrying / (MINUTES_ON_PITCH * 60) pct_carrying_player_time,
#                       --total_seconds_carrying / team_possession_duration pct_carrying_team_possession
#                       FROM match_stats
#                       LEFT JOIN (SELECT possession_team_id, match_id, SUM(duration) team_possession_duration
#                                   FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
#                                   GROUP BY possession_team_id, match_id) team_possession
#                         ON match_stats.match_id = team_possession.match_id
#                         AND match_stats.possession_team_id = team_possession.possession_team_id
#                       LEFT JOIN read_parquet('{project_location}/eda/player_match_on_pitch.parquet') player_time
#                         ON match_stats.match_id = player_time.match_id
#                         AND match_stats.player_id = player_time.player_id

#                       GROUP BY match_stats.player_id
#                       )

#                       SELECT player_id, 
#                       CASE
#                       WHEN IFNULL(total_progress_to_goal_shooting_on_carry,0) <= 0 OR IFNULL(carries,0) <= 0 THEN 0
#                       ELSE IFNULL(total_progress_to_goal_shooting_on_carry,0) / IFNULL(carries,0)
#                       END AS avg_progress_to_goal_shooting_on_per_carry, 
#                       CASE
#                       WHEN IFNULL(total_distance_traveled_carry,0) <= 0 OR IFNULL(carries,0) <= 0 THEN 0
#                       ELSE IFNULL(total_distance_traveled_carry,0) / IFNULL(carries,0)
#                       END AS avg_distance_traveled_per_carry, 

#                       total_seconds_carrying / player_seconds_on_pitch pct_carrying_player_time,
#                       total_seconds_carrying / team_possession_seconds pct_carrying_team_possession

#                       FROM agg_player

#                       LEFT JOIN (
#                                   SELECT possession_team_id, pt.player_id, e.match_id, SUM(IFNULL(duration,0)) team_seconds_possession_when_player_on_pitch 
#                                   FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
#                                   LEFT JOIN read_parquet('{project_location}/eda/player_match_timeline_with_score.parquet') pt
#                                     ON e.match_id = pt.match_id
#                                     AND e.period = pt.period
#                                     AND possession_team_id = pt.team_id
#                                     AND strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(minute) + TO_SECONDS(second) >= interval_start
#                                     AND strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(minute) + TO_SECONDS(second) < interval_end
#                                   GROUP BY possession_team_id, pt.player_id, e.match_id
#                                   HAVING SUM(IFNULL(duration,0)) > 0
#                                 ) team_possession


#                      """)

# print(y_coords)

# y_coords = duckdb.sql(f"""

#                       SELECT *
#                         FROM read_parquet('{project_location}/eda/pass_k_means.parquet') 
#                         WHERE pass_attempt <> 'NaN'::FLOAT
#                         AND pass_success_pct <> 'NaN'::FLOAT
#                         AND pass_attempts_per_minute <> 'NaN'::FLOAT
#                         AND percent_cross_success <> 'NaN'::FLOAT
#                         AND percent_through_ball_success <> 'NaN'::FLOAT
#                         AND percent_through_ball <> 'NaN'::FLOAT
#                         AND percent_cross <> 'NaN'::FLOAT
#                         AND percent_q1 <> 'NaN'::FLOAT
#                         AND percent_q2 <> 'NaN'::FLOAT
#                         AND percent_q3 <> 'NaN'::FLOAT
#                         AND percent_q4 <> 'NaN'::FLOAT
#                         AND pass_shot_assist_per_minute <> 'NaN'::FLOAT
#                      """)

# #print(y_coords.columns)

# df = pl.DataFrame(y_coords)

# km_df = df.select(
#     pl.all().exclude(['player_id', 'MINUTES_ON_PITCH', 'pass_attempt'])
# )

# kmeans_m = KMeans(n_clusters=10, random_state=0, n_init='auto')

# km_df = km_df.with_columns(pl.Series(name='cluster', values=kmeans_m.fit_predict(km_df)))

# print(km_df.group_by('cluster').agg(
#     pl.col('cluster').count().alias('num_players')
# ))



































# y_coords = duckdb.sql(f"""

#                         --SELECT PERCENTILE_DISC([0.25,0.5,0.75]) WITHIN GROUP (ORDER BY pass_length)
#                         --FROM read_parquet('{project_location}/eda/pass.parquet') p
#                         --LEFT JOIN 
#                         --WHERE pass_length > 0

                     
#                      """)
# print(y_coords)

# y_coords = duckdb.sql(f"""
#                   with pass_events as (
#                         SELECT match_id, id, 
#                         --index_num, 
#                       period, --timestamp, duration, --location_x, location_y, 
#                         possession, possession_team_id, team_id, 
#                          player_id, --pass_end_location_x, pass_end_location_y, 
#                         pass_recipient_id, pass_length, pass_angle, pass_height, pass_body_part, pass_type, pass_outcome,
#                          pass_technique, pass_assisted_shot_id, 
#                          CASE WHEN pass_goal_assist = TRUE THEN 1 ELSE 0 END AS pass_goal_assist, 
#                          CASE WHEN pass_shot_assist = TRUE THEN 1 ELSE 0 END AS pass_shot_assist, 
#                          CASE WHEN pass_cross = TRUE THEN 1 ELSE 0 END AS pass_cross, 
#                          CASE WHEN pass_switch = TRUE THEN 1 ELSE 0 END AS pass_switch, 
#                          CASE WHEN pass_through_ball = TRUE THEN 1 ELSE 0 END AS pass_through_ball, 
#                          CASE WHEN pass_aerial_won = TRUE THEN 1 ELSE 0 END AS pass_aerial_won, 
#                          CASE WHEN pass_deflected = TRUE THEN 1 ELSE 0 END AS pass_deflected,
#                          CASE WHEN pass_inswinging = TRUE THEN 1 ELSE 0 END AS pass_inswinging, 
#                          CASE WHEN pass_outswinging = TRUE THEN 1 ELSE 0 END AS pass_outswinging, 
#                          CASE WHEN pass_no_touch = TRUE THEN 1 ELSE 0 END AS pass_no_touch, 
#                          CASE WHEN pass_cut_back = TRUE THEN 1 ELSE 0 END AS pass_cut_back, 
#                          CASE WHEN pass_straight = TRUE THEN 1 ELSE 0 END AS pass_straight, 
#                          CASE WHEN pass_miscommunication = TRUE THEN 1 ELSE 0 END AS pass_miscommunication,
#                       strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(minute) + TO_SECONDS(second) event_date
#                         FROM read_parquet('{project_location}/data/Statsbomb/events.parquet')
#                         WHERE pass_length IS NOT NULL
#                       ),
#                         get_score as (
#                         SELECT pass_events.*, POSITION_TYPE, EVENT_ZONE_START, EVENT_ZONE_END, off_team.TEAM_COMPOSITION_PK OFF_TEAM_COMPOSITION_PK, def_team.TEAM_COMPOSITION_PK DEF_TEAM_COMPOSITION_PK,
#                         home_away.HOME_AWAY OFF_HOME_AWAY, home_away2.team_id DEF_TEAM_ID, home_away2.HOME_AWAY DEF_HOME_AWAY,
#                         score_check1.home_score,
#                         score_check1.away_score,
#                         off_team.PLAYERS_ON_PITCH - def_team.PLAYERS_ON_PITCH player_advantage,
#                         CASE
#                         WHEN POSITION_TYPE = 'F' THEN off_team.FORWARDS_GROUPING_ID
#                         WHEN POSITION_TYPE = 'M' THEN off_team.MIDFIELDERS_GROUPING_ID
#                         WHEN POSITION_TYPE = 'B' THEN off_team.BACKS_GROUPING_ID
#                         ELSE NULL
#                         END AS PLAYER_GROUPING_ID
#                         FROM pass_events
#                         LEFT JOIN read_parquet('{project_location}/eda/event_proximity.parquet') ep
#                               ON pass_events.match_id = ep.match_id
#                               AND pass_events.id = ep.id
#                         LEFT JOIN read_parquet('{project_location}/eda/team_composition.parquet') off_team
#                           ON pass_events.match_id = off_team.match_id
#                           AND pass_events.team_id = off_team.team_id
#                           AND pass_events.period = off_team.period
#                           AND pass_events.event_date >= off_team.interval_start
#                           AND pass_events.event_date < off_team.interval_end
#                         LEFT JOIN read_parquet('{project_location}/eda/team_composition.parquet') def_team
#                           ON pass_events.match_id = def_team.match_id
#                           AND pass_events.team_id != def_team.team_id
#                           AND pass_events.period = def_team.period
#                           AND pass_events.event_date >= def_team.interval_start
#                           AND pass_events.event_date < def_team.interval_end
#                         LEFT JOIN (                        
#                                     SELECT match_id, home_team_id team_id, 'H' HOME_AWAY
#                                     FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')

#                                     UNION

#                                     SELECT match_id, away_team_id team_id, 'A' HOME_AWAY
#                                     FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')
#                                     ) home_away
#                            ON pass_events.match_id = home_away.match_id 
#                            AND pass_events.team_id = home_away.team_id 
#                           LEFT JOIN (                        
#                                     SELECT match_id, home_team_id team_id, 'H' HOME_AWAY
#                                     FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')

#                                     UNION

#                                     SELECT match_id, away_team_id team_id, 'A' HOME_AWAY
#                                     FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')
#                                     ) home_away2
#                            ON pass_events.match_id = home_away2.match_id 
#                            AND pass_events.team_id != home_away2.team_id 

#                            LEFT JOIN (
#                                     SELECT match_id, period, home_goals home_score, away_goals away_score, 
#                                     start_date,
#                                     end_date
#                                     FROM read_parquet('{project_location}/eda/match_score_timeline.parquet')
#                                     ) score_check1
#                             ON pass_events.match_id = score_check1.match_id
#                             AND pass_events.period = score_check1.period
#                             AND pass_events.event_date >= score_check1.start_date
#                             AND pass_events.event_date < score_check1.end_date
#                           LEFT JOIN read_parquet('{project_location}/eda/period_lineups.parquet') pl
#                             ON pass_events.match_id = pl.match_id
#                             AND pass_events.period = pl.period
#                             AND pass_events.player_id = pl.player_id
#                             AND pass_events.event_date >= pl.interval_start
#                             AND pass_events.event_date < pl.interval_end

#                         ),
#                         goal_diff_calc as (
#                         SELECT get_score.*, 
#                         CASE WHEN OFF_HOME_AWAY = 'H' THEN home_score - away_score ELSE away_score - home_score END AS goal_diff,
#                         FROM get_score
#                         ),
#                         calc_pct as (
#                         SELECT POSITION_TYPE, PERCENTILE_DISC([0.25,0.5,0.75]) WITHIN GROUP (ORDER BY pass_length) percentiles
#                         FROM read_parquet('{project_location}/eda/pass.parquet') p
#                         LEFT JOIN read_parquet('{project_location}/eda/player_match_timeline_with_score.parquet') pt
#                           ON p.player_id = pt.player_id
#                           AND p.match_id = pt.match_id
#                           AND p.period = pt.period
#                           AND event_date >= interval_start
#                           AND event_date < interval_end
#                         GROUP BY POSITION_TYPE
#                         ),
#                         position_percentile as (
#                         SELECT POSITION_TYPE, percentiles[1] percentile_25, percentiles[2] percentile_50, percentiles[3] percentile_75 
#                         FROM calc_pct
#                         ),
#                         apply_position_pct as (

#                         SELECT goal_diff_calc.*,
#                         CASE 
#                         WHEN pass_length <= percentile_25 THEN 'Q1'
#                         WHEN pass_length <= percentile_50 THEN 'Q2'
#                         WHEN pass_length <= percentile_50 THEN 'Q3'
#                         ELSE 'Q4'
#                         END AS position_pass_quartile
#                         FROM goal_diff_calc
#                         LEFT JOIN position_percentile
#                           ON goal_diff_calc.POSITION_TYPE = position_percentile.POSITION_TYPE
#                         WHERE pass_length >= 0
#                         )

#                         SELECT match_id, period, possession, possession_team_id, team_id, player_id, pass_recipient_id, EVENT_ZONE_START, EVENT_ZONE_END, OFF_TEAM_COMPOSITION_PK, 
#                         DEF_TEAM_COMPOSITION_PK, OFF_HOME_AWAY, DEF_TEAM_ID, DEF_HOME_AWAY, home_score, away_score, player_advantage, PLAYER_GROUPING_ID, goal_diff, pass_height,
#                         --'pass_angle', 'pass_type', 'pass_outcome', 'pass_technique', 'pass_length',
                         
#                         SUM(pass_goal_assist) pass_goal_assist, SUM(pass_shot_assist) pass_shot_assist, 
#                         SUM(CASE WHEN pass_outcome IS NULL THEN pass_cross ELSE 0 END) pass_cross_success, 
#                         SUM(CASE WHEN pass_outcome IS NOT NULL THEN pass_cross ELSE 0 END) pass_cross_fail,
#                         SUM(pass_switch) pass_switch, 
#                         SUM(CASE WHEN pass_outcome IS NULL THEN pass_through_ball ELSE 0 END) pass_through_ball_success, 
#                         SUM(CASE WHEN pass_outcome IS NOT NULL THEN pass_through_ball ELSE 0 END) pass_through_ball_fail, 
#                         SUM(pass_aerial_won) pass_aerial_won, 
#                         SUM(pass_deflected) pass_deflected, 
#                         SUM(pass_inswinging) pass_inswinging, 
#                         SUM(pass_outswinging) pass_outswinging, 
#                         SUM(pass_no_touch) pass_no_touch, SUM(pass_cut_back) pass_cut_back, SUM(pass_straight) pass_straight, SUM(pass_miscommunication) pass_miscommunication,
#                         SUM(CASE WHEN pass_outcome IS NOT NULL THEN 1 ELSE 0 END) pass_success,
#                         SUM(CASE WHEN position_pass_quartile = 'Q1' THEN 1 ELSE 0 END) pos_pct_q1,
#                         SUM(CASE WHEN position_pass_quartile = 'Q2' THEN 1 ELSE 0 END) pos_pct_q2,
#                         SUM(CASE WHEN position_pass_quartile = 'Q3' THEN 1 ELSE 0 END) pos_pct_q3,
#                         SUM(CASE WHEN position_pass_quartile = 'Q4' THEN 1 ELSE 0 END) pos_pct_q4,
#                         COUNT(*) pass_attempt
                        
#                         FROM apply_position_pct

#                         GROUP BY match_id, period, possession, possession_team_id, team_id, player_id, pass_recipient_id, EVENT_ZONE_START, EVENT_ZONE_END, OFF_TEAM_COMPOSITION_PK, 
#                         DEF_TEAM_COMPOSITION_PK, OFF_HOME_AWAY, DEF_TEAM_ID, DEF_HOME_AWAY, home_score, away_score, player_advantage, PLAYER_GROUPING_ID, goal_diff, pass_height
#                      """)
# print(y_coords)

# y_coords = duckdb.sql(f"""
#                       SELECT MIDFIELDERS_ATTACKING_GROUP_ID, FORWARDS_ATTACKING_GROUP_ID, team_id,
#                       --player_id, 
#                       EVENT_ZONE_END ,
#                       --MAX(completed_pass_length) max_completed_pass_length, AVG(completed_pass_length) avg_completed_pass_length,
#                       SUM(pass_goal_assist) pass_goal_assist, SUM(pass_shot_assist) pass_shot_assist, COUNT(completed_pass_length) completed_passes, COUNT(*) pass_attempts, 
#                       --BACKS_DEFENDING_GROUP_ID, MIDFIELDERS_DEFENDING_GROUP_ID, 
#                       --FORWARDS_ATTACKING_GROUP_ID, MIDFIELDERS_ATTACKING_GROUP_ID, 
#                       MIDFIELDERS_DEFENDING,  BACKS_DEFENDING, MIDFIELDERS_ATTACKING, FORWARDS_ATTACKING,
#                       FROM (
#                           SELECT 
#                           pl.team_id, player_id, EVENT_ZONE_END, --pass_length, 
#                           CASE WHEN pass_outcome IS NULL THEN pass_length ELSE NULL END AS completed_pass_length,
#                           --CASE WHEN EVENT_ZONE_END = EVENT_ZONE_START THEN 'Within' ELSE 'Outside' END AS PASS_WITHIN_ZONE,
#                       dtc.BACKS_GROUPING_ID BACKS_DEFENDING_GROUP_ID, dtc.MIDFIELDERS_GROUPING_ID MIDFIELDERS_DEFENDING_GROUP_ID,
#                       otc.FORWARDS_GROUPING_ID FORWARDS_ATTACKING_GROUP_ID, otc.MIDFIELDERS_GROUPING_ID MIDFIELDERS_ATTACKING_GROUP_ID,
#                           pass_goal_assist, pass_shot_assist, dtc.MIDFIELDERS MIDFIELDERS_DEFENDING, dtc.BACKS BACKS_DEFENDING, otc.MIDFIELDERS MIDFIELDERS_ATTACKING, otc.FORWARDS FORWARDS_ATTACKING
#                           FROM read_parquet('{project_location}/eda/pass_level_stats.parquet') pl
#                           LEFT JOIN read_parquet('{project_location}/eda/team_composition.parquet') dtc
#                             ON DEF_TEAM_COMPOSITION_PK = dtc.TEAM_COMPOSITION_PK 
#                           LEFT JOIN read_parquet('{project_location}/eda/team_composition.parquet') otc
#                             ON DEF_TEAM_COMPOSITION_PK = otc.TEAM_COMPOSITION_PK 
#                           )
#                       WHERE EVENT_ZONE_END LIKE 'O%'
#                       AND MIDFIELDERS_ATTACKING_GROUP_ID IS NOT NULL
#                       AND MIDFIELDERS_DEFENDING_GROUP_ID IS NOT NULL
#                       GROUP BY MIDFIELDERS_ATTACKING_GROUP_ID, FORWARDS_ATTACKING_GROUP_ID,
#                       --player_id, 
#                       EVENT_ZONE_END, team_id,
#                       --BACKS_DEFENDING_GROUP_ID, MIDFIELDERS_DEFENDING_GROUP_ID, 
#                       --FORWARDS_ATTACKING_GROUP_ID, MIDFIELDERS_ATTACKING_GROUP_ID, 
#                       MIDFIELDERS_DEFENDING,  BACKS_DEFENDING, MIDFIELDERS_ATTACKING, FORWARDS_ATTACKING
#                       ORDER BY pass_goal_assist DESC
#                      """)
# print(y_coords)


# y_coords = duckdb.sql(f"""
                      
#                       SELECT match_id, --period, --possession, 
#                       possession_team_id, --team_id, --OFF_TEAM_COMPOSITION_PK, DEF_TEAM_COMPOSITION_PK, 
#                       --player_advantage, goal_diff,
#                       --COUNT(distinct player_id) players_passing, COUNT(distinct player_id) players_receiving_passes, 
#                       AVG(pass_length) avg_pass_length, MAX(pass_length) max_pass_length,
#                       SUM(pass_goal_assist) pass_goal_assist, SUM(pass_shot_assist) pass_shot_assist, SUM(pass_cross) pass_cross, SUM(pass_switch) pass_switch,
#                       SUM(pass_through_ball) pass_through_ball, SUM(pass_aerial_won) pass_aerial_won, SUM(pass_deflected) pass_deflected,  SUM(pass_inswinging) pass_inswinging,
#                       SUM(pass_outswinging) pass_outswinging, SUM(pass_no_touch) pass_no_touch, SUM(pass_cut_back) pass_cut_back, SUM(pass_straight) pass_straight, 
#                       SUM(pass_miscommunication) pass_miscommunication
#                       FROM read_parquet('{project_location}/eda/pass_level_stats.parquet')
#                       WHERE possession_team_id = team_id
#                       GROUP BY match_id, --period, --possession, 
#                       possession_team_id--, --team_id, 
#                       --OFF_TEAM_COMPOSITION_PK, DEF_TEAM_COMPOSITION_PK--, 
#                       --player_advantage, goal_diff
#                      """)
# print(y_coords)

# y_coords = duckdb.sql(f"""
#                         with half_timestamps as (
#                               SELECT match_id, team_id, period, minute, second, timestamp, start_date + TO_MINUTES(minute) + TO_SECONDS(second) period_timestamp, type
#                               FROM (SELECT distinct match_id, team_id, period, minute, second, timestamp, strptime('2026-01-01' , '%Y-%m-%d') start_date, type
#                                     FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') 
#                                     WHERE type IN ('Half End', 'Half Start')
#                                     ),
#                         iso_goals as (
#                         SELECT e.match_id, id, index_num, period, timestamp, minute, second, duration,
#                          CASE WHEN team_id = home_team_id THEN 1 ELSE 0 END AS home_goal,
#                          CASE WHEN team_id = away_team_id THEN 1 ELSE 0 END AS away_goal

#                         FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
#                         LEFT JOIN read_parquet('{project_location}/data/Statsbomb/matches.parquet') m
#                            ON e.match_id = m.match_id
#                         WHERE shot_outcome = 'Goal'
#                         ),
#                         rt_goals as (
#                         SELECT match_id, period, timestamp, minute, second, 
#                         SUM(home_goal) OVER (PARTITION BY match_id ORDER BY match_id, period, minute, second) home_rt,
#                         SUM(away_goal) OVER (PARTITION BY match_id ORDER BY match_id, period, minute, second) away_rt
#                         FROM iso_goals
#                         ),
#                         game_start as (
#                         SELECT *
#                         FROM (SELECT distinct match_id FROM iso_goals)
#                         CROSS JOIN (SELECT 1 period, '00:00:00.000' event_timestamp, 0 event_minute, 0 event_second, 0 home_rt, 0 away_rt)
#                         ),
#                         add_game_start as (
#                         SELECT match_id, period, timestamp, minute, second, home_rt, away_rt
#                         FROM rt_goals

#                         UNION

#                         SELECT match_id, period, event_timestamp, event_minute, event_second, home_rt, away_rt
#                         FROM game_start
#                         ),
#                         lead_goal_events as (
#                         SELECT match_id, period start_period, timestamp start_timestamp, minute start_minute, second start_second, home_rt home_score, away_rt away_score,
#                         LEAD(period,1) OVER (PARTITION BY match_id ORDER BY match_id, period, minute, second) end_period,
#                         LEAD(timestamp,1) OVER (PARTITION BY match_id ORDER BY match_id, period, minute, second) end_timestamp,
#                         LEAD(minute,1) OVER (PARTITION BY match_id ORDER BY match_id, period, minute, second) end_minute,
#                         LEAD(second,1) OVER (PARTITION BY match_id ORDER BY match_id, period, minute, second) end_second
#                         FROM add_game_start
#                         ),
#                         create_half_splits as (
#                         SELECT distinct match_id, 2 start_period, '00:00:00.000' event_timestamp, 45 event_minute, 0 event_second, home_score, away_score 
#                         FROM lead_goal_events
#                         WHERE start_period < 2 AND end_period > 1

#                         UNION

#                         SELECT distinct match_id, 3 start_period, '00:00:00.000' event_timestamp, 90 event_minute, 0 event_second, home_score, away_score 
#                         FROM lead_goal_events
#                         WHERE start_period < 3 AND end_period > 2

#                         UNION

#                         SELECT distinct match_id, 4 start_period, '00:00:00.000' event_timestamp, 105 event_minute, 0 event_second, home_score, away_score 
#                         FROM lead_goal_events
#                         WHERE start_period < 4 AND end_period > 3

#                         UNION

#                         SELECT distinct match_id, 5 start_period, '00:00:00.000' event_timestamp, 45 event_minute, 0 event_second, home_score, away_score 
#                         FROM lead_goal_events
#                         WHERE start_period < 5 AND end_period > 4

#                         ),
#                         add_other_splits as (

#                         SELECT match_id, start_period, start_timestamp, start_minute, start_second, home_score, away_score
#                         FROM lead_goal_events

#                         UNION

#                         SELECT match_id, start_period, event_timestamp, event_minute, event_second, home_score, away_score
#                         FROM create_half_splits
#                         )
#                         SELECT match_id, start_period, start_timestamp, start_minute, start_second, home_score, away_score,
#                         LEAD(start_period,1) OVER (PARTITION BY match_id ORDER BY match_id, start_period, start_minute, start_second) end_period,
#                         LEAD(start_timestamp,1) OVER (PARTITION BY match_id ORDER BY match_id, start_period, start_minute, start_second) end_timestamp,
#                         LEAD(start_minute,1) OVER (PARTITION BY match_id ORDER BY match_id, start_period, start_minute, start_second) end_minute,
#                         LEAD(start_second,1) OVER (PARTITION BY match_id ORDER BY match_id, start_period, start_minute, start_second) end_second
#                         FROM add_other_splits              
#                      """)
# print(y_coords)

