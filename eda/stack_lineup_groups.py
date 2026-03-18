import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'
#'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'
#'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/eda'

duckdb.sql(f"""
                        with find_position_type as (
                        SELECT team_id, match_id, period, interval_start, interval_end, player_id, PLAYER_POSITION_TYPE_ID_RANK, POSITION_TYPE
                         FROM read_parquet('{project_location}/eda/period_lineups.parquet') 
                         ),
                        group_position_type as (
                        PIVOT (
                        SELECT distinct match_id, team_id, period, interval_start, interval_end, player_id, POSITION_TYPE,
                        'position_' || CAST(PLAYER_POSITION_TYPE_ID_RANK as varchar) PLAYER_ID_RANK
                        FROM find_position_type
                              )
                              ON PLAYER_ID_RANK
                              USING MIN(player_id)
                              GROUP BY match_id, team_id, period, interval_start, interval_end, POSITION_TYPE
                        ),
                        find_squad as (
                        SELECT team_id, match_id, period, interval_start, interval_end, player_id, PLAYER_SQUAD_RANK
                         FROM read_parquet('{project_location}/eda/period_lineups.parquet') 
                         ), 
                         group_squad as (
                        PIVOT (
                        SELECT distinct match_id, team_id, period, interval_start, interval_end, player_id,
                        'position_' || CAST(PLAYER_SQUAD_RANK as varchar) PLAYER_ID_RANK
                        FROM find_squad
                              )
                              ON PLAYER_ID_RANK
                              USING MIN(player_id)
                              GROUP BY match_id, team_id, period, interval_start, interval_end
                        ),
                         find_country as (
                        SELECT team_id, match_id, period, interval_start, interval_end, player_id, PLAYER_COUNTRY_ID_RANK, country_id
                         FROM read_parquet('{project_location}/eda/period_lineups.parquet')                          
                         ),
                         group_country as (
                        PIVOT (
                        SELECT distinct match_id, team_id, period, interval_start, interval_end, player_id, country_id,
                        'position_' || CAST(PLAYER_COUNTRY_ID_RANK as varchar) PLAYER_ID_RANK
                        FROM find_country
                              )
                              ON PLAYER_ID_RANK
                              USING MIN(player_id)
                              GROUP BY match_id, team_id, period, interval_start, interval_end, country_id
                        ),
                         find_position_type_alt as (
                        SELECT team_id, match_id, period, interval_start, interval_end, player_id, PLAYER_POSITION_TYPE_ALT_ID_RANK, POSITION_TYPE_ALT
                         FROM read_parquet('{project_location}/eda/period_lineups.parquet') 
                         ),
                         group_position_type_alt as (

                        PIVOT (
                        SELECT distinct match_id, team_id, period, interval_start, interval_end, player_id, POSITION_TYPE_ALT,
                        'position_' || CAST(PLAYER_POSITION_TYPE_ALT_ID_RANK as varchar) PLAYER_ID_RANK
                        FROM find_position_type_alt
                              )
                              ON PLAYER_ID_RANK
                              USING MIN(player_id)
                              GROUP BY match_id, team_id, period, interval_start, interval_end, POSITION_TYPE_ALT
                        ),
                         find_position_side as (
                        SELECT team_id, match_id, period, interval_start, interval_end, player_id, PLAYER_POSITION_SIDE_ADJ_ID_RANK, POSITION_SIDE_ADJ
                         FROM read_parquet('{project_location}/eda/period_lineups.parquet') 
                         ),
                        group_position_side as (

                        PIVOT (
                        SELECT distinct match_id, team_id, period, interval_start, interval_end, player_id, POSITION_SIDE_ADJ,
                        'position_' || CAST(PLAYER_POSITION_SIDE_ADJ_ID_RANK as varchar) PLAYER_ID_RANK
                        FROM find_position_side
                              )
                              ON PLAYER_ID_RANK
                              USING MIN(player_id)
                              GROUP BY match_id, team_id, period, interval_start, interval_end, POSITION_SIDE_ADJ
                        
                        ),
                        stack_groups as (
                        SELECT match_id, team_id, period, interval_start, interval_end, POSITION_TYPE GROUP_ATTRIBUTE, 'Position Type' GROUP_NAME,
                        position_1, position_2, position_3, position_4, position_5, position_6, NULL position_7, NULL position_8, NULL position_9, NULL position_10, NULL position_11
                        FROM group_position_type
                        
                        UNION

                        SELECT match_id, team_id, period, interval_start, interval_end, 'Full Squad' GROUP_ATTRIBUTE, 'Full Squad' GROUP_NAME,
                        position_1, position_2, position_3, position_4, position_5, position_6, position_7, position_8, position_9, position_10, position_11
                        FROM group_squad

                        UNION

                        SELECT match_id, team_id, period, interval_start, interval_end, CAST(country_id as varchar) GROUP_ATTRIBUTE, 'Country' GROUP_NAME,
                        position_1, position_2, position_3, position_4, position_5, position_6, position_7, position_8, position_9, position_10, position_11
                        FROM group_country

                        UNION

                        SELECT match_id, team_id, period, interval_start, interval_end, POSITION_TYPE_ALT GROUP_ATTRIBUTE, 'Position Type Alt' GROUP_NAME,
                        position_1, position_2, position_3, position_4, position_5, position_6, NULL position_7, NULL position_8, NULL position_9, NULL position_10, NULL position_11
                        FROM group_position_type_alt

                        UNION

                        SELECT match_id, team_id, period, interval_start, interval_end, POSITION_SIDE_ADJ GROUP_ATTRIBUTE, 'Position Side' GROUP_NAME,
                        position_1, position_2, position_3, position_4, position_5, position_6, position_7, position_8, position_9, position_10, NULL position_11
                        FROM group_position_side
                        )

                        SELECT *
                        FROM stack_groups


      

                    """).write_parquet('stack_lineup_groups.parquet')
