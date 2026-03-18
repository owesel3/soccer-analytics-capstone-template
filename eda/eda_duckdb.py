import duckdb
#import pandas as pd


project_location = 'C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data'

con = duckdb.connect()

#result_tuples = con.execute(f"SELECT * FROM read_parquet('C:/Users/Tyler/Documents/GitHub/soccer-analytics-capstone-template/data/Statsbomb/events.parquet') LIMIT 100").fetchall()
#print(result_tuples)

events = duckdb.sql(f"SELECT type, COUNT(*) FROM read_parquet('{project_location}/Statsbomb/events.parquet') WHERE match_id = 15973 GROUP BY type LIMIT 100")
#print(events.limit.0)
#print(events)

events2 = duckdb.sql(f"SELECT possession, possession_team_id, possession_team FROM read_parquet('{project_location}/Statsbomb/events.parquet') WHERE match_id = 15973 ORDER BY index_num LIMIT 100")
#print(events.limit.0)
print(events2)


#duckdb.sql(f"SELECT * FROM read_parquet('{project_location}/Statsbomb/events.parquet') WHERE match_id = 15973 ORDER BY index_num LIMIT 500").write_csv('sample_match.csv', header=True)
#print(events.limit.0)

lineups = duckdb.sql(f"SELECT * FROM read_parquet('{project_location}/Statsbomb/lineups.parquet') WHERE match_id = 15973 LIMIT 100")
#print(lineups)
#print(lineups.columns)


matches = duckdb.sql(f"SELECT * FROM read_parquet('{project_location}/Statsbomb/matches.parquet') WHERE match_id = 15973 LIMIT 100")
#print(matches)
#print(matches.columns)

duckdb.sql(f"""SELECT * 
                FROM read_parquet('{project_location}/Statsbomb/events.parquet')
                WHERE match_id = 15973 """).write_csv('soccer_match.csv', header=True)


events_subset = duckdb.sql(f"SELECT id, index_num, period, minute, second, timestamp, CAST(IFNULL(string_split(timestamp, '.')[2],'000') AS INTEGER) ts_millisecond, duration FROM read_parquet('{project_location}/Statsbomb/events.parquet') WHERE match_id = 15973 LIMIT 100")
#print(events_subset)
#print(events_subset.columns)

# match_timeline = duckdb.sql(f"""SELECT *
#                                 FROM (
#                                         SELECT * 
#                                         FROM read_parquet('{project_location}/Statsbomb/events.parquet') 
#                                         WHERE match_id = 15973 
#                                     ) e

#                             """
                                        
                                        
                                        
#                                         )

# print(match_timeline)
# print(match_timeline.columns)


# duckdb.sql(f"""SELECT type, COUNT(*) 
#                 FROM read_parquet('{project_location}/Statsbomb/events.parquet')
#                 WHERE match_id = 15973 
#                 GROUP BY type 
#                 LIMIT 100""").show(max_rows=100)

# duckdb.sql(f"""SELECT *
#                 FROM read_parquet('{project_location}/Statsbomb/events.parquet')
#                 WHERE match_id = 15973 AND type = 'Substitution'
#                 LIMIT 100""").show(max_rows=100, max_col_width=10000)

subs = duckdb.sql(f"""SELECT player_id, substitution_replacement_id
                 FROM read_parquet('{project_location}/Statsbomb/events.parquet')
                 WHERE match_id = 15973 AND type = 'Substitution'
                 LIMIT 100""")

#print(subs)
#print(subs.columns)

event360 = duckdb.sql(f"""SELECT *
                 FROM read_parquet('{project_location}/Statsbomb/three_sixty.parquet')
                 """)

#print(event360)
#print(event360.columns)

soccer_market = duckdb.sql(f"""SELECT *
                 FROM read_parquet('{project_location}/Polymarket/soccer_markets.parquet')
                 LIMIT 100
                 """)
#print(soccer_market)
#print(soccer_market.columns)

soccer_odds = duckdb.sql(f"""SELECT *
                 FROM read_parquet('{project_location}/Polymarket/soccer_odds_history.parquet')
                 LIMIT 100
                 """)
#print(soccer_odds)
#print(soccer_odds.columns)

soccer_events = duckdb.sql(f"""SELECT *
                 FROM read_parquet('{project_location}/Polymarket/soccer_event_stats.parquet')
                 LIMIT 100
                 """)
#print(soccer_events)
#print(soccer_events.columns)

soccer_summary = duckdb.sql(f"""SELECT *
                 FROM read_parquet('{project_location}/Polymarket/soccer_summary.parquet')
                 ORDER BY volume DESC
                 LIMIT 100
                 """)
print(soccer_summary)
print(soccer_summary.columns)


duckdb.sql(f"""SELECT * 
                FROM read_parquet('{project_location}/Polymarket/soccer_trades.parquet') 
                LIMIT 1500""").write_csv('soccer_trades.csv', header=True)

soccer_trades = duckdb.sql(f"""SELECT *
                 FROM read_parquet('{project_location}/Polymarket/soccer_trades.parquet')
                 LIMIT 100
                 """)
#print(soccer_trades)
#print(soccer_trades.columns)


soccer_matches = duckdb.sql(f"""SELECT distinct season, competition
                 FROM read_parquet('{project_location}/Statsbomb/matches.parquet')
                 WHERE SEASON IN ('2020','2022','2024') AND country_name = 'Europe' AND is_international = TRUE AND match_status_360 = 'available'
                 LIMIT 100
                 """)
print(soccer_matches)
print(soccer_matches.columns)