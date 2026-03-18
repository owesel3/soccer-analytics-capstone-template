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
                  with pass_events as (
                        SELECT match_id, id, 
                        --index_num, 
                      period, --timestamp, duration, --location_x, location_y, 
                        possession, possession_team_id, team_id, 
                         player_id, --pass_end_location_x, pass_end_location_y, 
                        pass_recipient_id, pass_length, pass_angle, pass_height, pass_body_part, pass_type, pass_outcome,
                         pass_technique, pass_assisted_shot_id, 
                         CASE WHEN pass_goal_assist = TRUE THEN 1 ELSE 0 END AS pass_goal_assist, 
                         CASE WHEN pass_shot_assist = TRUE THEN 1 ELSE 0 END AS pass_shot_assist, 
                         CASE WHEN pass_cross = TRUE THEN 1 ELSE 0 END AS pass_cross, 
                         CASE WHEN pass_switch = TRUE THEN 1 ELSE 0 END AS pass_switch, 
                         CASE WHEN pass_through_ball = TRUE THEN 1 ELSE 0 END AS pass_through_ball, 
                         CASE WHEN pass_aerial_won = TRUE THEN 1 ELSE 0 END AS pass_aerial_won, 
                         CASE WHEN pass_deflected = TRUE THEN 1 ELSE 0 END AS pass_deflected,
                         CASE WHEN pass_inswinging = TRUE THEN 1 ELSE 0 END AS pass_inswinging, 
                         CASE WHEN pass_outswinging = TRUE THEN 1 ELSE 0 END AS pass_outswinging, 
                         CASE WHEN pass_no_touch = TRUE THEN 1 ELSE 0 END AS pass_no_touch, 
                         CASE WHEN pass_cut_back = TRUE THEN 1 ELSE 0 END AS pass_cut_back, 
                         CASE WHEN pass_straight = TRUE THEN 1 ELSE 0 END AS pass_straight, 
                         CASE WHEN pass_miscommunication = TRUE THEN 1 ELSE 0 END AS pass_miscommunication,
                      strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(minute) + TO_SECONDS(second) event_date
                        FROM read_parquet('{project_location}/data/Statsbomb/events.parquet')
                        WHERE pass_length IS NOT NULL
                      ),
                        get_score as (
                        SELECT pass_events.*, POSITION_TYPE, EVENT_ZONE_START, EVENT_ZONE_END, off_team.TEAM_COMPOSITION_PK OFF_TEAM_COMPOSITION_PK, def_team.TEAM_COMPOSITION_PK DEF_TEAM_COMPOSITION_PK,
                        home_away.HOME_AWAY OFF_HOME_AWAY, home_away2.team_id DEF_TEAM_ID, home_away2.HOME_AWAY DEF_HOME_AWAY,
                        score_check1.home_score,
                        score_check1.away_score,
                        off_team.PLAYERS_ON_PITCH - def_team.PLAYERS_ON_PITCH player_advantage,
                        CASE
                        WHEN POSITION_TYPE = 'F' THEN off_team.FORWARDS_GROUPING_ID
                        WHEN POSITION_TYPE = 'M' THEN off_team.MIDFIELDERS_GROUPING_ID
                        WHEN POSITION_TYPE = 'B' THEN off_team.BACKS_GROUPING_ID
                        ELSE NULL
                        END AS PLAYER_GROUPING_ID
                        FROM pass_events
                        LEFT JOIN read_parquet('{project_location}/eda/event_proximity.parquet') ep
                              ON pass_events.match_id = ep.match_id
                              AND pass_events.id = ep.id
                        LEFT JOIN read_parquet('{project_location}/eda/team_composition.parquet') off_team
                          ON pass_events.match_id = off_team.match_id
                          AND pass_events.team_id = off_team.team_id
                          AND pass_events.period = off_team.period
                          AND pass_events.event_date >= off_team.interval_start
                          AND pass_events.event_date < off_team.interval_end
                        LEFT JOIN read_parquet('{project_location}/eda/team_composition.parquet') def_team
                          ON pass_events.match_id = def_team.match_id
                          AND pass_events.team_id != def_team.team_id
                          AND pass_events.period = def_team.period
                          AND pass_events.event_date >= def_team.interval_start
                          AND pass_events.event_date < def_team.interval_end
                        LEFT JOIN (                        
                                    SELECT match_id, home_team_id team_id, 'H' HOME_AWAY
                                    FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')

                                    UNION

                                    SELECT match_id, away_team_id team_id, 'A' HOME_AWAY
                                    FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')
                                    ) home_away
                           ON pass_events.match_id = home_away.match_id 
                           AND pass_events.team_id = home_away.team_id 
                          LEFT JOIN (                        
                                    SELECT match_id, home_team_id team_id, 'H' HOME_AWAY
                                    FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')

                                    UNION

                                    SELECT match_id, away_team_id team_id, 'A' HOME_AWAY
                                    FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')
                                    ) home_away2
                           ON pass_events.match_id = home_away2.match_id 
                           AND pass_events.team_id != home_away2.team_id 

                           LEFT JOIN (
                                    SELECT match_id, period, home_goals home_score, away_goals away_score, 
                                    start_date,
                                    end_date
                                    FROM read_parquet('{project_location}/eda/match_score_timeline.parquet')
                                    ) score_check1
                            ON pass_events.match_id = score_check1.match_id
                            AND pass_events.period = score_check1.period
                            AND pass_events.event_date >= score_check1.start_date
                            AND pass_events.event_date < score_check1.end_date
                          LEFT JOIN read_parquet('{project_location}/eda/period_lineups.parquet') pl
                            ON pass_events.match_id = pl.match_id
                            AND pass_events.period = pl.period
                            AND pass_events.player_id = pl.player_id
                            AND pass_events.event_date >= pl.interval_start
                            AND pass_events.event_date < pl.interval_end

                        ),
                        goal_diff_calc as (
                        SELECT get_score.*, 
                        CASE WHEN OFF_HOME_AWAY = 'H' THEN home_score - away_score ELSE away_score - home_score END AS goal_diff,
                        FROM get_score
                        ),
                        calc_pct as (
                        SELECT POSITION_TYPE, PERCENTILE_DISC([0.25,0.5,0.75]) WITHIN GROUP (ORDER BY pass_length) percentiles
                        FROM read_parquet('{project_location}/eda/pass.parquet') p
                        LEFT JOIN read_parquet('{project_location}/eda/player_match_timeline_with_score.parquet') pt
                          ON p.player_id = pt.player_id
                          AND p.match_id = pt.match_id
                          AND p.period = pt.period
                          AND event_date >= interval_start
                          AND event_date < interval_end
                        GROUP BY POSITION_TYPE
                        ),
                        position_percentile as (
                        SELECT POSITION_TYPE, percentiles[1] percentile_25, percentiles[2] percentile_50, percentiles[3] percentile_75 
                        FROM calc_pct
                        ),
                        apply_position_pct as (

                        SELECT goal_diff_calc.*,
                        CASE 
                        WHEN pass_length <= percentile_25 THEN 'Q1'
                        WHEN pass_length <= percentile_50 THEN 'Q2'
                        WHEN pass_length <= percentile_75 THEN 'Q3'
                        ELSE 'Q4'
                        END AS position_pass_quartile
                        FROM goal_diff_calc
                        LEFT JOIN position_percentile
                          ON goal_diff_calc.POSITION_TYPE = position_percentile.POSITION_TYPE
                        WHERE pass_length >= 0
                        )

                        SELECT match_id, period, possession, possession_team_id, team_id, player_id, pass_recipient_id, EVENT_ZONE_START, EVENT_ZONE_END, OFF_TEAM_COMPOSITION_PK, 
                        DEF_TEAM_COMPOSITION_PK, OFF_HOME_AWAY, DEF_TEAM_ID, DEF_HOME_AWAY, home_score, away_score, player_advantage, PLAYER_GROUPING_ID, goal_diff, pass_height,
                        --'pass_angle', 'pass_type', 'pass_outcome', 'pass_technique', 'pass_length',
                         
                        SUM(pass_goal_assist) pass_goal_assist, SUM(pass_shot_assist) pass_shot_assist, 
                        SUM(CASE WHEN pass_outcome IS NULL THEN pass_cross ELSE 0 END) pass_cross_success, 
                        SUM(CASE WHEN pass_outcome IS NOT NULL THEN pass_cross ELSE 0 END) pass_cross_fail,
                        SUM(pass_switch) pass_switch, 
                        SUM(CASE WHEN pass_outcome IS NULL THEN pass_through_ball ELSE 0 END) pass_through_ball_success, 
                        SUM(CASE WHEN pass_outcome IS NOT NULL THEN pass_through_ball ELSE 0 END) pass_through_ball_fail, 
                        SUM(pass_aerial_won) pass_aerial_won, 
                        SUM(pass_deflected) pass_deflected, 
                        SUM(pass_inswinging) pass_inswinging, 
                        SUM(pass_outswinging) pass_outswinging, 
                        SUM(pass_no_touch) pass_no_touch, SUM(pass_cut_back) pass_cut_back, SUM(pass_straight) pass_straight, SUM(pass_miscommunication) pass_miscommunication,
                        SUM(CASE WHEN pass_outcome IS NOT NULL THEN 1 ELSE 0 END) pass_success,
                        SUM(CASE WHEN position_pass_quartile = 'Q1' THEN 1 ELSE 0 END) pos_pct_q1,
                        SUM(CASE WHEN position_pass_quartile = 'Q2' THEN 1 ELSE 0 END) pos_pct_q2,
                        SUM(CASE WHEN position_pass_quartile = 'Q3' THEN 1 ELSE 0 END) pos_pct_q3,
                        SUM(CASE WHEN position_pass_quartile = 'Q4' THEN 1 ELSE 0 END) pos_pct_q4,
                        SUM(CASE WHEN pass_outcome IS NULL AND position_pass_quartile = 'Q1' THEN 1 ELSE 0 END) pos_pct_q1_success,
                        SUM(CASE WHEN pass_outcome IS NULL AND position_pass_quartile = 'Q2' THEN 1 ELSE 0 END) pos_pct_q2_success,
                        SUM(CASE WHEN pass_outcome IS NULL AND position_pass_quartile = 'Q3' THEN 1 ELSE 0 END) pos_pct_q3_success,
                        SUM(CASE WHEN pass_outcome IS NULL AND position_pass_quartile = 'Q4' THEN 1 ELSE 0 END) pos_pct_q4_success,
                        COUNT(*) pass_attempt
                        
                        FROM apply_position_pct

                        GROUP BY match_id, period, possession, possession_team_id, team_id, player_id, pass_recipient_id, EVENT_ZONE_START, EVENT_ZONE_END, OFF_TEAM_COMPOSITION_PK, 
                        DEF_TEAM_COMPOSITION_PK, OFF_HOME_AWAY, DEF_TEAM_ID, DEF_HOME_AWAY, home_score, away_score, player_advantage, PLAYER_GROUPING_ID, goal_diff, pass_height
                    """).write_parquet('pass_level_stats.parquet')
