import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'

duckdb.sql(f"""
                      SELECT MIDFIELDERS_ATTACKING_GROUP_ID, FORWARDS_ATTACKING_GROUP_ID, team_id,
                      --player_id, 
                      EVENT_ZONE_END ,
                      --MAX(completed_pass_length) max_completed_pass_length, AVG(completed_pass_length) avg_completed_pass_length,
                      SUM(pass_goal_assist) pass_goal_assist, SUM(pass_shot_assist) pass_shot_assist, COUNT(completed_pass_length) completed_passes, COUNT(*) pass_attempts, 
                      --BACKS_DEFENDING_GROUP_ID, MIDFIELDERS_DEFENDING_GROUP_ID, 
                      --FORWARDS_ATTACKING_GROUP_ID, MIDFIELDERS_ATTACKING_GROUP_ID, 
                      MIDFIELDERS_DEFENDING,  BACKS_DEFENDING, MIDFIELDERS_ATTACKING, FORWARDS_ATTACKING,
                      FROM (
                          SELECT 
                          pl.team_id, player_id, EVENT_ZONE_END, --pass_length, 
                          CASE WHEN pass_outcome IS NULL THEN pass_length ELSE NULL END AS completed_pass_length,
                          --CASE WHEN EVENT_ZONE_END = EVENT_ZONE_START THEN 'Within' ELSE 'Outside' END AS PASS_WITHIN_ZONE,
                      dtc.BACKS_GROUPING_ID BACKS_DEFENDING_GROUP_ID, dtc.MIDFIELDERS_GROUPING_ID MIDFIELDERS_DEFENDING_GROUP_ID,
                      otc.FORWARDS_GROUPING_ID FORWARDS_ATTACKING_GROUP_ID, otc.MIDFIELDERS_GROUPING_ID MIDFIELDERS_ATTACKING_GROUP_ID,
                          pass_goal_assist, pass_shot_assist, dtc.MIDFIELDERS MIDFIELDERS_DEFENDING, dtc.BACKS BACKS_DEFENDING, otc.MIDFIELDERS MIDFIELDERS_ATTACKING, otc.FORWARDS FORWARDS_ATTACKING
                          FROM read_parquet('{project_location}/eda/pass_level_stats.parquet') pl
                          LEFT JOIN read_parquet('{project_location}/eda/team_composition.parquet') dtc
                            ON DEF_TEAM_COMPOSITION_PK = dtc.TEAM_COMPOSITION_PK 
                          LEFT JOIN read_parquet('{project_location}/eda/team_composition.parquet') otc
                            ON DEF_TEAM_COMPOSITION_PK = otc.TEAM_COMPOSITION_PK 
                          )
                      WHERE EVENT_ZONE_END LIKE 'O%'
                      AND MIDFIELDERS_ATTACKING_GROUP_ID IS NOT NULL
                      AND MIDFIELDERS_DEFENDING_GROUP_ID IS NOT NULL
                      GROUP BY MIDFIELDERS_ATTACKING_GROUP_ID, FORWARDS_ATTACKING_GROUP_ID,
                      --player_id, 
                      EVENT_ZONE_END, team_id,
                      --BACKS_DEFENDING_GROUP_ID, MIDFIELDERS_DEFENDING_GROUP_ID, 
                      --FORWARDS_ATTACKING_GROUP_ID, MIDFIELDERS_ATTACKING_GROUP_ID, 
                      MIDFIELDERS_DEFENDING,  BACKS_DEFENDING, MIDFIELDERS_ATTACKING, FORWARDS_ATTACKING
                      ORDER BY pass_goal_assist DESC

                                """).write_parquet('more_pass_level_metrics.parquet')

