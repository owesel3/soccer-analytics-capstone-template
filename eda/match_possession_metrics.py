import duckdb
import math

#IF NOT INSTALLED THEN INSTALL spatial

project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/eda'
#'C://Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'

match_possession = duckdb.sql(f"""
                           SELECT match_id, possession_team_id, SUM(passes) passes, SUM(pass_attempts) pass_attempts, SUM(total_distance) total_distance, SUM(high_passes) high_passes, 
                                    SUM(ground_passes) ground_passes, SUM(low_passes) low_passes, SUM(drop_kick_passes) drop_kick_passes, SUM(head_passes) head_passes,
                                    SUM(left_foot_passes) left_foot_passes, SUM(right_foot_passes) right_foot_passes, SUM(other_passes) other_passes, SUM(straight_passes) straight_passes,
                                    SUM(through_ball_passes) through_ball_passes, SUM(total_possession_time) total_possession_time
                            FROM read_parquet('{project_location}/possession_metrics.parquet') 
                            GROUP BY match_id, possession_team_id
                                """)#.write_parquet('match_possession_metrics.parquet')

print(match_possession)