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
                      with shot_info as (
                        SELECT e.match_id, --e.id, 
                         --strptime('2026-01-01' , '%Y-%m-%d') start_date,
                         --minute, second,
                        strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(minute) + TO_SECONDS(second) event_date,
                         e.period, e.team_id, e.possession, --location_x, location_y, 
                          --e.possession_team_id, --timestamp, duration, --location_x, location_y, 
                         player_id, --shot_end_location_x, shot_end_location_y, shot_end_location_z, 
                        shot_statsbomb_xg, shot_outcome, 
                        shot_technique, 
                         shot_body_part, shot_type, 
                         CASE WHEN shot_first_time THEN 1 ELSE 0 END AS shot_first_time, 
                         CASE WHEN shot_deflected THEN 1 ELSE 0 END AS shot_deflected, 
                         CASE WHEN shot_aerial_won THEN 1 ELSE 0 END AS shot_aerial_won, 
                         CASE WHEN shot_follows_dribble THEN 1 ELSE 0 END AS shot_follows_dribble, 
                         CASE WHEN shot_one_on_one THEN 1 ELSE 0 END AS shot_one_on_one,
                         CASE WHEN shot_open_goal THEN 1 ELSE 0 END AS shot_open_goal, 
                         CASE WHEN shot_redirect THEN 1 ELSE 0 END AS shot_redirect, 
                         CASE WHEN shot_saved_off_target THEN 1 ELSE 0 END AS shot_saved_off_target, 
                         CASE WHEN shot_saved_to_post THEN 1 ELSE 0 END AS shot_saved_to_post, 

                        EVENT_ZONE_START OFF_ZONE, DIST_TO_GOAL
                      
                        FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
                        LEFT JOIN read_parquet('{project_location}/eda/event_proximity.parquet') ep
                           ON e.match_id = ep.match_id
                           AND e.id = ep.id
                           AND e.period = ep.period
                          LEFT JOIN read_parquet('{project_location}/data/Statsbomb/matches.parquet') m
                            ON e.match_id = m.match_id
                        WHERE shot_end_location_x IS NOT NULL
                        --AND e.match_id = 15956
                        ),
                        get_score as (
                        SELECT shot_info.*, off_team.TEAM_COMPOSITION_PK OFF_TEAM_COMPOSITION_PK, def_team.TEAM_COMPOSITION_PK DEF_TEAM_COMPOSITION_PK,
                        home_away.HOME_AWAY OFF_HOME_AWAY, home_away2.team_id DEF_TEAM_ID, home_away2.HOME_AWAY DEF_HOME_AWAY,
                        IFNULL(IFNULL(score_check1.home_score, score_check2.home_score), score_check3.home_score) home_score,
                        IFNULL(IFNULL(score_check1.away_score, score_check2.away_score), score_check3.away_score) away_score,
                        off_team.PLAYERS_ON_PITCH - def_team.PLAYERS_ON_PITCH player_advantage
                        FROM shot_info
                        LEFT JOIN read_parquet('{project_location}/eda/team_composition.parquet') off_team
                          ON shot_info.match_id = off_team.match_id
                          AND shot_info.team_id = off_team.team_id
                          AND shot_info.period = off_team.period
                          AND shot_info.event_date >= off_team.interval_start
                          AND shot_info.event_date < off_team.interval_end
                        LEFT JOIN read_parquet('{project_location}/eda/team_composition.parquet') def_team
                          ON shot_info.match_id = def_team.match_id
                          AND shot_info.team_id != def_team.team_id
                          AND shot_info.period = def_team.period
                          AND shot_info.event_date >= def_team.interval_start
                          AND shot_info.event_date < def_team.interval_end
                        LEFT JOIN (                        
                                    SELECT match_id, home_team_id team_id, 'H' HOME_AWAY
                                    FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')

                                    UNION

                                    SELECT match_id, away_team_id team_id, 'A' HOME_AWAY
                                    FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')
                                    ) home_away
                           ON shot_info.match_id = home_away.match_id 
                           AND shot_info.team_id = home_away.team_id 
                          LEFT JOIN (                        
                                    SELECT match_id, home_team_id team_id, 'H' HOME_AWAY
                                    FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')

                                    UNION

                                    SELECT match_id, away_team_id team_id, 'A' HOME_AWAY
                                    FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet')
                                    ) home_away2
                           ON shot_info.match_id = home_away2.match_id 
                           AND shot_info.team_id != home_away2.team_id 

                           LEFT JOIN (
                                    SELECT match_id, start_period, end_period, home_score, away_score, 
                                    strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(start_minute) + TO_SECONDS(start_second) SCORE_TL_START,
                                    CASE
                                    WHEN end_minute IS NULL THEN NULL
                                    ELSE strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(end_minute) + TO_SECONDS(end_second) 
                                    END AS SCORE_TL_END
                                    FROM read_parquet('{project_location}/eda/match_score_timeline.parquet')
                                    WHERE start_period = end_period AND end_period IS NOT NULL
                                    ) score_check1
                            ON shot_info.match_id = score_check1.match_id
                            AND shot_info.period = score_check1.start_period
                            AND shot_info.event_date >= score_check1.SCORE_TL_START
                            AND shot_info.event_date < score_check1.SCORE_TL_END


                           LEFT JOIN (
                                    SELECT match_id, start_period, end_period, home_score, away_score, 
                                    strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(start_minute) + TO_SECONDS(start_second) SCORE_TL_START,
                                    CASE
                                    WHEN end_minute IS NULL THEN NULL
                                    ELSE strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(end_minute) + TO_SECONDS(end_second) 
                                    END AS SCORE_TL_END
                                    FROM read_parquet('{project_location}/eda/match_score_timeline.parquet')
                                    WHERE start_period != end_period AND end_period IS NOT NULL
                                    ) score_check2
                            ON shot_info.match_id = score_check2.match_id
                            AND (
                                  (shot_info.period = score_check2.start_period AND shot_info.event_date >= score_check2.SCORE_TL_START)
                                  OR 
                                  (shot_info.period = score_check2.end_period AND shot_info.event_date < IFNULL(score_check2.SCORE_TL_END, strptime('2027-01-01' , '%Y-%m-%d')))
                                  OR 
                                  (shot_info.period > score_check2.start_period AND shot_info.period < score_check2.end_period)
                                  )

                             LEFT JOIN (
                                    SELECT match_id, start_period, end_period, home_score, away_score, 
                                    strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(start_minute) + TO_SECONDS(start_second) SCORE_TL_START,
                                    CASE
                                    WHEN end_minute IS NULL THEN NULL
                                    ELSE strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(end_minute) + TO_SECONDS(end_second) 
                                    END AS SCORE_TL_END
                                    FROM read_parquet('{project_location}/eda/match_score_timeline.parquet')
                                    WHERE end_period IS NULL
                                    ) score_check3
                            ON shot_info.match_id = score_check3.match_id
                            AND (
                                  (shot_info.period = score_check3.start_period AND shot_info.event_date >= score_check3.SCORE_TL_START)
                                  OR 
                                  (shot_info.period > score_check3.start_period)
                                  )
                        )

                        SELECT get_score.*, 
                        CASE WHEN OFF_HOME_AWAY = 'H' THEN home_score - away_score ELSE away_score - home_score END AS goal_diff,
                        FROM get_score
                    """).write_parquet('shot_level_stats.parquet')
