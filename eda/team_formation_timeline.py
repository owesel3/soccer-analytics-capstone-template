import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'
#'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'
#'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/eda'

duckdb.sql(f"""
                              with get_player_type as (
                              SELECT mi.*, 
                              CASE WHEN POSITION_TYPE = 'GK' THEN 1 ELSE 0 END AS GK,
                              CASE WHEN POSITION_TYPE = 'M' THEN 1 ELSE 0 END AS MIDFIELDERS,
                              CASE WHEN POSITION_TYPE = 'B' THEN 1 ELSE 0 END AS BACKS,
                              CASE WHEN POSITION_TYPE = 'F' THEN 1 ELSE 0 END AS FORWARDS,
                              CASE WHEN POSITION_TYPE = 'F' AND POSITION_TYPE_ALT = 'CF' THEN 1 ELSE 0 END AS CENTER_FORWARDS,
                              CASE WHEN POSITION_TYPE = 'M' AND POSITION_BEHAVIOR = 'A' THEN 1 ELSE 0 END AS ATTACKING_MIDFIELDERS,
                              CASE WHEN POSITION_TYPE = 'M' AND POSITION_BEHAVIOR = 'D' THEN 1 ELSE 0 END AS DEFENDING_MIDFIELDERS
                              FROM read_parquet('{project_location}/eda/period_lineups.parquet')  mi
                              WHERE player_id IS NOT NULL
                              ),
                              position_stats as (
                              SELECT match_id, team_id, period, interval_start, interval_end, 
                              SUM(GK) GK,
                              SUM(BACKS) BACKS,
                              SUM(MIDFIELDERS) MIDFIELDERS,
                              SUM(FORWARDS) FORWARDS, 
                              SUM(ATTACKING_MIDFIELDERS) ATTACKING_MIDFIELDERS,
                              SUM(DEFENDING_MIDFIELDERS) DEFENDING_MIDFIELDERS,
                              SUM(CENTER_FORWARDS) CENTER_FORWARDS
                              FROM get_player_type
                              GROUP BY match_id, team_id, period, interval_start, interval_end
                              ), 
                              get_subformation as (
                              SELECT position_stats.*, --GK, BACKS, MIDFIELDERS, ATTACKING_MIDFIELDERS, DEFENDING_MIDFIELDERS, FORWARDS,CENTER_FORWARDS, 
                              CASE
                              WHEN FORWARDS = 0 THEN NULL 
                              WHEN FORWARDS > 0 
                                 AND CENTER_FORWARDS > 0 AND FORWARDS != CENTER_FORWARDS THEN CAST(CENTER_FORWARDS as varchar) || '-' || CAST(CENTER_FORWARDS as varchar) ELSE CAST(FORWARDS as varchar) END AS ATTACK_FORMATION,
                              CASE 
                                 WHEN DEFENDING_MIDFIELDERS > 0 AND ATTACKING_MIDFIELDERS > 0 AND MIDFIELDERS - DEFENDING_MIDFIELDERS - ATTACKING_MIDFIELDERS > 0 
                                 THEN CAST(DEFENDING_MIDFIELDERS as varchar) || '-' || CAST(MIDFIELDERS - DEFENDING_MIDFIELDERS - ATTACKING_MIDFIELDERS as varchar) || '-' || CAST(ATTACKING_MIDFIELDERS as varchar)
                                 WHEN DEFENDING_MIDFIELDERS > 0 AND ATTACKING_MIDFIELDERS = 0 AND MIDFIELDERS - DEFENDING_MIDFIELDERS  > 0 
                                 THEN CAST(DEFENDING_MIDFIELDERS as varchar) || '-' || CAST(MIDFIELDERS - DEFENDING_MIDFIELDERS as varchar)
                                 WHEN DEFENDING_MIDFIELDERS = 0 AND ATTACKING_MIDFIELDERS > 0 AND MIDFIELDERS - ATTACKING_MIDFIELDERS  > 0 
                                 THEN CAST(MIDFIELDERS as varchar) || '-' || CAST(MIDFIELDERS - ATTACKING_MIDFIELDERS as varchar)
                                 WHEN MIDFIELDERS - DEFENDING_MIDFIELDERS - ATTACKING_MIDFIELDERS = 0 AND DEFENDING_MIDFIELDERS != ATTACKING_MIDFIELDERS AND ATTACKING_MIDFIELDERS > 0 AND DEFENDING_MIDFIELDERS > 0
                                 THEN CAST(DEFENDING_MIDFIELDERS as varchar) || '-' || CAST(ATTACKING_MIDFIELDERS as varchar)
                                 ELSE CAST(MIDFIELDERS as varchar) 
                                 END AS MIDFIELD_FORMATION,
                              CAST(BACKS as varchar) DEFENSE_FORMATION
                              FROM position_stats
                           )
                           SELECT *
                           FROM (
                           SELECT get_subformation.*,
                           CASE
                           WHEN ATTACK_FORMATION IS NULL THEN DEFENSE_FORMATION || '-' || MIDFIELD_FORMATION
                           WHEN DEFENSE_FORMATION IS NULL THEN MIDFIELD_FORMATION || '-' || ATTACK_FORMATION
                           WHEN MIDFIELD_FORMATION IS NULL THEN DEFENSE_FORMATION || '-' || ATTACK_FORMATION
                           ELSE DEFENSE_FORMATION || '-' || MIDFIELD_FORMATION || '-' || ATTACK_FORMATION END AS OVERALL_FORMATION
                           , BACKS + MIDFIELDERS + FORWARDS + GK PLAYERS_ON_PITCH
                           FROM get_subformation
                           )
                    """).write_parquet('team_formation_timeline.parquet')
