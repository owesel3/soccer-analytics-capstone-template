import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'
#'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'
#'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/eda'

duckdb.sql(f"""
                              SELECT tg.*, GK, BACKS, MIDFIELDERS, FORWARDS, ATTACKING_MIDFIELDERS, DEFENDING_MIDFIELDERS, CENTER_FORWARDS, ATTACK_FORMATION, MIDFIELD_FORMATION, DEFENSE_FORMATION, OVERALL_FORMATION, PLAYERS_ON_PITCH,
                              RANK() OVER (ORDER BY tg.match_id, tg.team_id, tg.period, tg.interval_start) TEAM_COMPOSITION_PK
                              FROM read_parquet('{project_location}/eda/team_groupings_timeline.parquet')  tg
                              INNER JOIN read_parquet('{project_location}/eda/team_formation_timeline.parquet')  tf
                                ON tg.match_id = tf.match_id
                                AND tg.team_id = tf.team_id
                                AND tg.period = tf.period
                                AND tg.interval_start = tf.interval_start
                                AND tg.interval_end = tf.interval_end
                           
                    """).write_parquet('team_composition.parquet')
