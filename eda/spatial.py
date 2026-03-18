import duckdb
duckdb.sql(f"""INSTALL spatial""")
duckdb.sql(f"""LOAD spatial""")