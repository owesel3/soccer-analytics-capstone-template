import duckdb

project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'
#'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'
#'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/eda'

duckdb.sql(f"""
                            SELECT initial_types.*,
                               CASE 
                               WHEN UPPER(POSITION_TYPE_ALT) IN ('WB', 'B') THEN 'B'
                               WHEN UPPER(POSITION_TYPE_ALT) IN ('F', 'W', 'CF') THEN 'F'
                                WHEN UPPER(POSITION_TYPE_ALT) IN ('GK') THEN 'GK'
                               WHEN UPPER(POSITION_TYPE_ALT) IN ('M') THEN 'M'
                               ELSE NULL
                               END AS POSITION_TYPE
                               FROM (
                           SELECT position_type.*,
                               CASE 
                               WHEN UPPER(position_name) LIKE '%LEFT CENTER%' THEN 'LC'
                               WHEN UPPER(position_name) LIKE '%RIGHT CENTER%' THEN 'RC'
                               WHEN UPPER(position_name) LIKE '%CENTER%' THEN 'C'
                               WHEN UPPER(position_name) LIKE '%LEFT%' THEN 'L'
                               WHEN UPPER(position_name) LIKE '%RIGHT%' THEN 'R'
                               WHEN UPPER(position_name) LIKE '%GOALKEEPER%' THEN 'GK'
                               WHEN UPPER(position_name) LIKE '%SECONDARY%' THEN 'C'
                               ELSE NULL
                               END AS POSITION_SIDE,
                               CASE 
                               WHEN UPPER(position_name) LIKE '%MID%' THEN 'M'
                               WHEN UPPER(position_name) LIKE '%WING BACK%' THEN 'WB'
                               WHEN UPPER(position_name) LIKE '%BACK%' THEN 'B'
                               WHEN UPPER(position_name) LIKE '%CENTER FORWARD%' THEN 'CF'
                               WHEN UPPER(position_name) LIKE '%GOALKEEPER%' THEN 'GK'
                               WHEN UPPER(position_name) LIKE '%WING%' THEN 'W'
                               WHEN UPPER(position_name) LIKE '%FORWARD%' THEN 'F'
                               ELSE NULL
                               END AS POSITION_TYPE_ALT,
                               CASE 
                               WHEN UPPER(position_name) LIKE '%ATTACK%' THEN 'A'
                               WHEN UPPER(position_name) LIKE '%DEFENSIVE%' THEN 'D'
                               ELSE NULL
                               END AS POSITION_BEHAVIOR,
                              RANK () OVER (ORDER BY POSITION_NAME) POSITION_TYPE_PK
                            FROM (
                               SELECT distinct position_name
                                FROM read_parquet('{project_location}/Statsbomb/lineups.parquet') 
                                WHERE position_name IS NOT NULL
                                 ) position_type
                                 ) initial_types
                    """).write_parquet('position_type.parquet')

