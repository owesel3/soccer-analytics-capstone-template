import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'
#'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'
#'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/eda'

duckdb.sql(f"""
                          with lineup_checks as (
                        SELECT match_id, team_id, player_id, country_id, from_period, to_period, from_time, to_time, next_time, position_name, next_position
                        FROM (
                                    SELECT lineup.*, LEAD(from_time,1) OVER (PARTITION BY match_id, team_id, player_id ORDER BY match_id, team_id, player_id, from_period, to_period, from_time) next_time
                                    , LEAD(position_name,1) OVER (PARTITION BY match_id, team_id, player_id ORDER BY match_id, team_id, player_id, from_period, to_period, from_time) next_position
                                    FROM read_parquet('{project_location}/data/Statsbomb/lineups.parquet') lineup
                                    )
                         ),
                         
                         bad_matches as (
                         SELECT distinct match_id
                         FROM read_parquet('{project_location}/data/Statsbomb/lineups.parquet') 
                         WHERE IFNULL(to_period,100) < from_period
                         OR from_time = IFNULL(to_time,'N/A')
                         OR (IFNULL(to_period,100) = from_period AND from_time >= IFNULL(to_time,'N/A'))

                         UNION

                        SELECT distinct match_id
                        FROM lineup_checks
                        WHERE next_time != to_time
                        AND next_time IS NOT NULL
                        AND next_position != position_name
                        AND from_period <= to_period
                         ),
                           half_timestamps as (
                              SELECT match_id, team_id, period, minute, second, timestamp, start_date + TO_MINUTES(minute) + TO_SECONDS(second) period_timestamp, type
                              FROM (SELECT distinct match_id, team_id, period, minute, second, timestamp, strptime('2026-01-01' , '%Y-%m-%d') start_date, type
                                    FROM read_parquet('{project_location}/data/Statsbomb/events.parquet') 
                                    WHERE type IN ('Half End', 'Half Start')
                                    )
                        ),
                        correct_lineups as (
                        SELECT match_id, team_id, player_id, country_id, from_period, to_period, from_time, to_time, position_name
                        FROM read_parquet('{project_location}/data/Statsbomb/lineups.parquet') lineup

                        UNION
                        
                        SELECT match_id, team_id, player_id, country_id, from_period, to_period, to_time, next_time, position_name
                        FROM lineup_checks
                        WHERE next_time != to_time
                        AND next_time IS NOT NULL
                        AND next_position = position_name
                        AND from_period <= to_period
                        ),
                         initial_dates as (
                        SELECT distinct l.match_id, l.team_id, player_id, country_id, position_name, from_time, to_time, from_period, IFNULL(to_period, mp.max_period) to_period , 
                         strptime('2026-01-01' , '%Y-%m-%d') start_date,
                         CAST(LEFT(from_time, INSTR(from_time, ':') - 1 ) AS INTEGER)  from_minute, 
                         CAST(SUBSTR(from_time, LEN(from_time) - 1) AS INTEGER) from_second,
                         IFNULL(CAST(LEFT(to_time, INSTR(to_time, ':') - 1 ) AS INTEGER), mp2.minute)  to_minute, 
                         IFNULL(CAST(SUBSTR(to_time, LEN(to_time) - 1) AS INTEGER), mp2.second) to_second
                         FROM correct_lineups l
                         --read_parquet('{project_location}/data/Statsbomb/lineups.parquet') l
                         LEFT JOIN (SELECT match_id, MAX(period) max_period from half_timestamps GROUP BY match_id) mp
                              ON l.match_id = mp.match_id
                        LEFT JOIN (SELECT distinct match_id, team_id, period, minute, second FROM half_timestamps) mp2
                              ON mp.match_id = mp2.match_id
                              AND mp.max_period = mp2.period
                         WHERE l.match_id NOT IN (SELECT match_id FROM bad_matches)
                         AND from_period IS NOT NULL 
                           ),

                           convert_timestamp as (

                           SELECT initial_dates.match_id, initial_dates.team_id, player_id, country_id, position_name, from_time, to_time, from_period, to_period , 
                           start_date, from_minute, from_second, to_minute, to_second,
                           start_date + TO_MINUTES(from_minute) + TO_SECONDS(from_second) start_date_adj,
                           CASE 
                           WHEN to_minute IS NOT NULL THEN start_date + TO_MINUTES(to_minute) + TO_SECONDS(to_second) 
                           ELSE h_end.period_timestamp
                           END AS end_date_adj
                           FROM initial_dates
                        LEFT JOIN (SELECT match_id, MAX(period) max_period from half_timestamps GROUP BY match_id) mp
                              ON initial_dates.match_id = mp.match_id
                           LEFT JOIN (SELECT match_id, period, team_id, MAX(period_timestamp) period_timestamp FROM half_timestamps WHERE type = 'Half End' GROUP BY match_id, period, team_id) h_end
                              ON initial_dates.match_id = h_end.match_id
                              AND initial_dates.team_id = h_end.team_id
                              AND IFNULL(initial_dates.to_period, mp.max_period) = h_end.period
                           WHERE from_period < IFNULL(to_period,100) 
                                    OR (from_period = to_period 
                                          AND to_minute IS NOT NULL 
                                          AND start_date + TO_MINUTES(to_minute) + TO_SECONDS(to_second) > start_date_adj)
                                    OR (from_period = to_period 
                                          AND to_minute IS NULL )

                                    
                         ),

                        all_lineup_times as (
                           SELECT distinct match_id, team_id, period_tracked, period_time interval_start
                           FROM (SELECT distinct match_id, team_id, start_date_adj period_time, from_period period_tracked
                                 FROM convert_timestamp
                                 WHERE from_period IS NOT NULL 
                                          AND from_time IS NOT NULL 
                                          AND IFNULL(start_date_adj,TODAY()) != IFNULL(end_date_adj,TODAY())

                                 UNION
                                 
                                 SELECT distinct match_id, team_id, end_date_adj, to_period
                                 FROM convert_timestamp
                                 WHERE from_period IS NOT NULL 
                                          AND to_period IS NOT NULL 
                                          AND to_time IS NOT NULL 
                                          AND IFNULL(start_date_adj,TODAY()) != IFNULL(end_date_adj,TODAY())

                                 UNION

                                 SELECT distinct match_id, team_id, period_timestamp, period
                                 FROM half_timestamps
                                 
                                 )
                            ),

                              all_lineup_changes as (
                                 SELECT *
                                 FROM (
                                       SELECT match_id, team_id, period_tracked period, interval_start, LEAD(interval_start,1) OVER (PARTITION BY match_id, team_id, period_tracked ORDER BY match_id, team_id, period_tracked, interval_start) interval_end
                                       FROM all_lineup_times
                                       )
                                 WHERE period IS NOT NULL 
                                          AND interval_start != IFNULL(interval_end, TODAY()) 
                                          AND interval_end IS NOT NULL

                                 ),
                           period_start_end as (
                           SELECT match_id, period, 
                           MIN(interval_start) period_start, 
                           MAX(interval_end) period_end
                           FROM all_lineup_changes
                           GROUP BY match_id, period
                           ),
                        player_match_timeline as (
                              SELECT distinct player_multi_period.match_id, team_id, player_id, country_id, position_name, period,
                                    start_date_adj player_start_date, end_date_adj player_end_date
                              FROM (SELECT convert_timestamp.*
                                    FROM convert_timestamp
                                    WHERE from_period != to_period) player_multi_period
                              INNER JOIN period_start_end p
                                    ON player_multi_period.match_id = p.match_id
                                    AND period = from_period
                              WHERE start_date_adj < end_date_adj
                              

                              UNION

                              SELECT distinct player_multi_period2.match_id, team_id, player_id, country_id, position_name, period,
                                    period_start , period_end
                              FROM (SELECT convert_timestamp.*
                                    FROM convert_timestamp
                                    WHERE from_period != to_period) player_multi_period2
                              INNER JOIN period_start_end p3
                                    ON player_multi_period2.match_id = p3.match_id
                                    AND period > from_period
                                    AND period < to_period

                              UNION

                              SELECT distinct player_multi_period3.match_id, team_id, player_id, country_id, position_name, period,
                                    start_date_adj, end_date_adj
                              FROM (SELECT convert_timestamp.*
                                    FROM convert_timestamp
                                    WHERE from_period != to_period) player_multi_period3
                              INNER JOIN period_start_end p4
                                    ON player_multi_period3.match_id = p4.match_id
                                    AND period = to_period
                              WHERE start_date_adj < end_date_adj

                              UNION

                              SELECT distinct player_multi_period4.match_id, team_id, player_id, country_id, position_name, period,
                                    start_date_adj , end_date_adj
                              FROM (SELECT convert_timestamp.*
                                    FROM convert_timestamp
                                    WHERE from_period = to_period) player_multi_period4
                              INNER JOIN period_start_end p5
                                    ON player_multi_period4.match_id = p5.match_id
                                    AND period = from_period
                              WHERE start_date_adj < end_date_adj

                        ),
                        match_intervals as (
                        SELECT distinct alc.*, player_id, country_id, position_name
                        FROM all_lineup_changes alc
                        LEFT JOIN player_match_timeline pmt
                              ON alc.match_id = pmt.match_id
                              AND alc.team_id = pmt.team_id
                              AND alc.period = pmt.period
                              AND alc.interval_start >= player_start_date
                              AND alc.interval_start < player_end_date
                        ),
                        get_player_position as (
                        SELECT match_intervals.*, 
                         CASE WHEN POSITION_SIDE IN ('RC','LC') THEN 'C' ELSE POSITION_SIDE END AS POSITION_SIDE_ADJ, 
                         POSITION_TYPE_ALT, POSITION_BEHAVIOR, POSITION_TYPE
                        FROM match_intervals
                        LEFT JOIN read_parquet('{project_location}/eda/position_type.parquet') pt
                              ON match_intervals.position_name = pt.position_name
                        WHERE match_id NOT IN (SELECT match_id FROM bad_matches) 
                              AND match_id NOT IN (
                                                SELECT distinct match_id 
                                                      FROM (
                                                      SELECT match_id, team_id, period, interval_start, interval_end, COUNT(*)
                                                      FROM match_intervals
                                                      GROUP BY match_id, team_id, period, interval_start, interval_end
                                                      HAVING COUNT(*) > 11 OR COUNT(*) < 9
                                                      )
                                                )

                         ),
                        get_ranks as (
                        SELECT team_id, match_id, period, interval_start, interval_end, player_id, country_id, POSITION_SIDE_ADJ, POSITION_TYPE_ALT, POSITION_BEHAVIOR, POSITION_TYPE,
                        RANK() OVER (PARTITION BY match_id, team_id, period, interval_start, POSITION_SIDE_ADJ ORDER BY match_id, team_id, period, interval_start, POSITION_SIDE_ADJ, player_id) PLAYER_POSITION_SIDE_ADJ_ID_RANK,
                        RANK() OVER (PARTITION BY match_id, team_id, period, interval_start, POSITION_TYPE ORDER BY match_id, team_id, period, interval_start, POSITION_TYPE, player_id) PLAYER_POSITION_TYPE_ID_RANK,
                        RANK() OVER (PARTITION BY match_id, team_id, period, interval_start, POSITION_TYPE_ALT ORDER BY match_id, team_id, period, interval_start, POSITION_TYPE_ALT, player_id) PLAYER_POSITION_TYPE_ALT_ID_RANK,
                        RANK() OVER (PARTITION BY match_id, team_id, period, interval_start, country_id ORDER BY match_id, team_id, period, interval_start, country_id, player_id) PLAYER_COUNTRY_ID_RANK,
                        RANK() OVER (PARTITION BY match_id, team_id, period, interval_start, interval_end ORDER BY match_id, team_id, period, interval_start, interval_end, player_id) PLAYER_SQUAD_RANK
                        
                        FROM get_player_position
                        )
                        SELECT gr.team_id,  gr.match_id, gr.period, gr.interval_start, gr.interval_end, gr.player_id, gr.country_id, gr.POSITION_SIDE_ADJ, gr.POSITION_TYPE, gr.POSITION_TYPE_ALT, gr.POSITION_BEHAVIOR,
                        SUM(CASE WHEN gr.country_id = gr2.country_id THEN 1 ELSE 0 END) PLAYERS_SAME_COUNTRY,
                        SUM(CASE WHEN gr.country_id != gr2.country_id THEN 1 ELSE 0 END) PLAYERS_DIFF_COUNTRY,
                        SUM(CASE WHEN gr.POSITION_TYPE = gr2.POSITION_TYPE AND gr.country_id = gr2.country_id THEN 1 ELSE 0 END) POSITION_SAME_COUNTRY,
                        SUM(CASE WHEN gr.POSITION_TYPE = gr2.POSITION_TYPE AND gr.country_id != gr2.country_id THEN 1 ELSE 0 END) POSITION_DIFF_COUNTRY,
                        SUM(CASE WHEN gr.POSITION_SIDE_ADJ = gr2.POSITION_SIDE_ADJ AND gr.country_id = gr2.country_id THEN 1 ELSE 0 END) SIDE_SAME_COUNTRY,
                        SUM(CASE WHEN gr.POSITION_SIDE_ADJ = gr2.POSITION_SIDE_ADJ AND gr.country_id != gr2.country_id THEN 1 ELSE 0 END) SIDE_DIFF_COUNTRY

                        FROM get_ranks gr
                        LEFT JOIN get_ranks gr2
                              ON gr.team_id = gr2.team_id
                              AND gr.match_id = gr2.match_id
                              AND gr.period = gr2.period
                              AND gr.interval_start = gr2.interval_start
                              AND gr.interval_end = gr2.interval_end
                              AND gr.player_id != gr2.player_id
                        GROUP BY gr.team_id,  gr.match_id, gr.period, gr.interval_start, gr.interval_end, gr.player_id, gr.country_id, gr.POSITION_SIDE_ADJ, gr.POSITION_TYPE, gr.POSITION_TYPE_ALT, gr.POSITION_BEHAVIOR
                    """).write_parquet('period_lineups.parquet')
