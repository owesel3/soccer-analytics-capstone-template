import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'

duckdb.sql(f"""
                        with half_timestamps as (
                              SELECT distinct match_id, period, minute, 
                                start_date + TO_MINUTES(minute) + TO_SECONDS(second) period_timestamp, type
                              FROM (SELECT distinct match_id, team_id, period, minute, second, timestamp, strptime('2026-01-01' , '%Y-%m-%d') start_date, type
                                    FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') 
                                    WHERE type IN ('Half End', 'Half Start')
                                    )
                                    ),
                        iso_goals as (
                        SELECT match_id, period, start_date + TO_MINUTES(minute) + TO_SECONDS(second) goal_timestamp, home_goal, away_goal
                        FROM (SELECT e.match_id, id, index_num, period, timestamp, minute, second, duration,
                                strptime('2026-01-01' , '%Y-%m-%d') start_date,
                                CASE WHEN team_id = home_team_id THEN 1 ELSE 0 END AS home_goal,
                                CASE WHEN team_id = away_team_id THEN 1 ELSE 0 END AS away_goal

                                FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') e
                                LEFT JOIN read_parquet('{project_location}/data/Statsbomb/matches.parquet') m
                                ON e.match_id = m.match_id
                                WHERE shot_outcome = 'Goal'
                                )
                        UNION

                        SELECT match_id, period, period_timestamp, NULL home_goal, NULL away_goal
                        FROM half_timestamps
                        ),
                        rt_goals as (
                        SELECT match_id, period, goal_timestamp, 
                        IFNULL(SUM(home_goal) OVER (PARTITION BY match_id ORDER BY match_id, period, goal_timestamp),0) home_rt,
                        IFNULL(SUM(away_goal) OVER (PARTITION BY match_id ORDER BY match_id, period, goal_timestamp),0) away_rt
                        FROM iso_goals
                        ),
                        iso_significant_events as (
                        SELECT match_id, period, goal_timestamp, home_rt, away_rt
                        FROM (
                        SELECT rt_goals.*,
                        CASE 
                        WHEN IFNULL(LAG(period,1) OVER (partition by match_id, period order by match_id, period, goal_timestamp),-1) != period THEN 1
                        WHEN IFNULL(LAG(home_rt,1) OVER (partition by match_id, period order by match_id, period, goal_timestamp),-1) != home_rt THEN 1
                        WHEN IFNULL(LAG(away_rt,1) OVER (partition by match_id, period order by match_id, period, goal_timestamp),-1) != away_rt THEN 1
                        ELSE 0
                        END as iso_row
                        FROM rt_goals
                        )
                        WHERE iso_row = 1
                        )
                        SELECT match_id, period, home_rt home_goals, away_rt away_goals, goal_timestamp start_date, LEAD(goal_timestamp,1) OVER (partition by match_id, period order by match_id, period, goal_timestamp) end_date
                        FROM iso_significant_events
                                """).write_parquet('match_score_timeline.parquet')

