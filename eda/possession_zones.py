import duckdb
import math
import matplotlib.pyplot as plt
import numpy as np

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template'
#'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'
#'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/eda'


duckdb.sql(f"""
                        with e as (
                        SELECT match_id, id, period, index_num, possession, possession_team_id, team_id
                        FROM read_parquet('{project_location}/data/Statsbomb/events.parquet')
                        WHERE location_x IS NOT NULL AND possession_team_id = team_id
                        --AND match_id = 15946 
                        ),
                        label_zone as (
                        SELECT e.*, EVENT_ZONE_START
                        FROM e
                         LEFT JOIN read_parquet('{project_location}/eda/event_proximity.parquet') ep
                           ON e.match_id = ep.match_id
                           AND e.id = ep.id
                           AND e.period = ep.period
                        ),
                        zone_changes as (
                        SELECT label_zone.*,
                        CASE WHEN IFNULL(LAG(EVENT_ZONE_START,1) OVER (PARTITION BY match_id, period, possession, possession_team_id ORDER BY match_id, period, possession, index_num),'N/A') != IFNULL(EVENT_ZONE_START,'N/A') THEN 1
                        ELSE 0
                        END AS ZONE_CHANGE
                        FROM label_zone
                        ),
                        iso_changes as (
                        SELECT match_id, period, index_num, possession, possession_team_id, EVENT_ZONE_START
                        FROM zone_changes
                        WHERE ZONE_CHANGE = 1
                        )
                        SELECT match_id, period, possession, COUNT(*) - 1 zone_hops,
                        string_agg(EVENT_ZONE_START,'-' ORDER BY index_num) zones_hit
                        FROM iso_changes
                        GROUP BY match_id, period, possession
                    """).write_parquet('possession_zones.parquet')
