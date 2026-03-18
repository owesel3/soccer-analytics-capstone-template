import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'
#'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'
#'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/eda'

duckdb.sql(f"""
                         with lineup_check as (
                        SELECT match_id, team_id, period, interval_start, interval_end, TEAM_COMPOSITION_PK
                        FROM read_parquet('{project_location}/eda/team_composition.parquet') 
                        ),
                        event_times as (
                        SELECT id, match_id, possession, period, strptime('2026-01-01' , '%Y-%m-%d') + TO_MINUTES(minute) + TO_SECONDS(second) event_timestamp
                        FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') 
                        ),
                        final_query as (
                        SELECT distinct et.possession, et.match_id, et.period, 
                        --CASE WHEN home_team_id = lc.team_id THEN 'Home' WHEN away_team_id = lc.team_id THEN 'Away' ELSE NULL END AS HOME_AWAY, 
                        lc.team_id,
                        TEAM_COMPOSITION_PK
                        FROM event_times et
                        INNER JOIN lineup_check lc
                           ON et.match_id = lc.match_id
                           AND et.period = lc.period
                           AND event_timestamp >= lc.interval_start
                           AND event_timestamp < lc.interval_end
                        --LEFT JOIN (SELECT match_id, home_team_id, away_team_id FROM read_parquet('{project_location}/data/Statsbomb/matches.parquet') ) e
                           --ON et.match_id = e.match_id
                        --WHERE lc.team_id IS NOT NULL
                        )
                        SELECT *
                        FROM final_query 
                    """).write_parquet('possession_players_on_pitch.parquet')