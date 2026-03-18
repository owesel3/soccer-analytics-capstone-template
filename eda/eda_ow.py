"""
Soccer Analytics EDA Template
Soccer Analytics EDA Template
Comprehensive exploratory data analysis for Polymarket (optional) and Statsbomb data
Using Polars for high-performance data processing
"""

import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
import os
import re
os.makedirs("figures", exist_ok=True)

warnings.filterwarnings('ignore')

# Configure plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
POLYMARKET_DIR = DATA_DIR / "Polymarket"
STATSBOMB_DIR = DATA_DIR / "Statsbomb"


def print_section_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_subsection(title):
    """Print formatted subsection header"""
    print(f"\n--- {title} ---")


def analyze_polymarket_markets():
    """Analyze soccer_markets.parquet"""
    print_section_header("POLYMARKET: SOCCER MARKETS")
    
    df = pl.read_parquet(POLYMARKET_DIR / "soccer_markets.parquet")
    
    print(f"Total markets: {len(df):,}")
    print(f"Columns: {df.columns}")
    print(f"\nData types:\n{df.dtypes}")
    
    print_subsection("Missing Values")
    null_counts = df.null_count()
    print(null_counts if null_counts.sum_horizontal()[0] > 0 else "No missing values")
    
    print_subsection("Market Status")
    active_count = df["active"].sum()
    closed_count = df["closed"].sum()
    print(f"Active markets: {active_count:,} ({active_count/len(df)*100:.1f}%)")
    print(f"Closed markets: {closed_count:,} ({closed_count/len(df)*100:.1f}%)")
    
    print_subsection("Volume Statistics")
    print(df["volume"].describe())
    print(f"\nTotal volume: ${df['volume'].sum():,.2f}")
    print(f"Markets with volume > 0: {(df['volume'] > 0).sum():,}")
    
    print_subsection("Category Distribution")
    print(df["category"].value_counts())
    
    print_subsection("Temporal Coverage")
    print(f"First market created: {df['created_at'].min()}")
    print(f"Last market created: {df['created_at'].max()}")
    print(f"Earliest end date: {df['end_date'].min()}")
    print(f"Latest end date: {df['end_date'].max()}")
    
    print_subsection("Top Markets by Volume")
    print(df.select(["question", "volume", "active", "closed"]).sort("volume", descending=True).head(10))


def analyze_polymarket_tokens():
    """Analyze soccer_tokens.parquet"""
    print_section_header("POLYMARKET: SOCCER TOKENS")
    
    df = pl.read_parquet(POLYMARKET_DIR / "soccer_tokens.parquet")
    
    print(f"Total tokens: {len(df):,}")
    print(f"Unique markets: {df['market_id'].n_unique():,}")
    print(f"Unique token IDs: {df['token_id'].n_unique():,}")
    
    print_subsection("Tokens per Market")
    tokens_per_market = df.group_by("market_id").agg(pl.len().alias("token_count"))
    print(tokens_per_market["token_count"].describe())
    print(f"\nMarkets with 2 outcomes (binary): {(tokens_per_market['token_count'] == 2).sum():,}")
    print(f"Markets with >2 outcomes: {(tokens_per_market['token_count'] > 2).sum():,}")
    
    print_subsection("Outcome Distribution")
    print(df["outcome"].value_counts().head(20))


def analyze_polymarket_trades():
    """Analyze soccer_trades.parquet"""
    print_section_header("POLYMARKET: SOCCER TRADES")
    
    df = pl.read_parquet(POLYMARKET_DIR / "soccer_trades.parquet")
    
    print(f"Total trades: {len(df):,}")
    print(f"Unique markets: {df['market_id'].n_unique():,}")
    print(f"Unique tokens: {df['token_id'].n_unique():,}")
    
    print_subsection("Trade Volume Statistics")
    print(df["size"].describe())
    print(f"\nTotal trade size: {df['size'].sum():,.2f}")
    
    print_subsection("Price Distribution")
    print(df["price"].describe())
    print(f"\nPrices by quartile:")
    print(f"  0-25%: {(df['price'] <= 0.25).sum():,} trades")
    print(f"  25-50%: {((df['price'] > 0.25) & (df['price'] <= 0.5)).sum():,} trades")
    print(f"  50-75%: {((df['price'] > 0.5) & (df['price'] <= 0.75)).sum():,} trades")
    print(f"  75-100%: {(df['price'] > 0.75).sum():,} trades")
    
    print_subsection("Trade Side Distribution")
    print(df["side"].value_counts())
    buy_count = (df["side"] == "BUY").sum()
    sell_count = (df["side"] == "SELL").sum()
    print(f"\nBuy/Sell ratio: {buy_count / sell_count:.2f}")
    
    print_subsection("Temporal Analysis")
    print(f"First trade: {df['timestamp'].min()}")
    print(f"Last trade: {df['timestamp'].max()}")
    date_range = (df["timestamp"].max() - df["timestamp"].min()).total_seconds() / (24 * 3600)
    print(f"Date range: {date_range:.0f} days")
    
    trades_per_day = df.group_by(pl.col("timestamp").dt.date()).agg(pl.len().alias("count"))
    print(f"\nTrades per day - Mean: {trades_per_day['count'].mean():.0f}, Median: {trades_per_day['count'].median():.0f}")
    
    print_subsection("Most Active Markets")
    print(df["market_id"].value_counts().head(10))


def analyze_polymarket_odds_history():
    """Analyze soccer_odds_history.parquet"""
    print_section_header("POLYMARKET: SOCCER ODDS HISTORY")
    
    df = pl.read_parquet(POLYMARKET_DIR / "soccer_odds_history.parquet")
    
    print(f"Total odds snapshots: {len(df):,}")
    print(f"Unique markets: {df['market_id'].n_unique():,}")
    print(f"Unique tokens: {df['token_id'].n_unique():,}")
    
    print_subsection("Price Statistics")
    print(df["price"].describe())
    
    print_subsection("Temporal Coverage")
    print(f"First snapshot: {df['timestamp'].min()}")
    print(f"Last snapshot: {df['timestamp'].max()}")
    date_range = (df["timestamp"].max() - df["timestamp"].min()).total_seconds() / (24 * 3600)
    print(f"Date range: {date_range:.0f} days")
    
    print_subsection("Snapshots per Token")
    snapshots_per_token = df.group_by("token_id").agg(pl.len().alias("count"))
    print(snapshots_per_token["count"].describe())
    
    print_subsection("Price Volatility Analysis")
    # Calculate price changes for each token
    df_sorted = df.sort(["token_id", "timestamp"])
    df_with_changes = df_sorted.with_columns(
        pl.col("price").diff().over("token_id").alias("price_change")
    )
    
    print(f"Mean absolute price change: {df_with_changes['price_change'].abs().mean():.4f}")
    print(f"Max price increase: {df_with_changes['price_change'].max():.4f}")
    print(f"Max price decrease: {df_with_changes['price_change'].min():.4f}")


def analyze_polymarket_event_stats():
    """Analyze soccer_event_stats.parquet"""
    print_section_header("POLYMARKET: SOCCER EVENT STATS")
    
    df = pl.read_parquet(POLYMARKET_DIR / "soccer_event_stats.parquet")
    
    print(f"Total events: {len(df):,}")
    print(f"Unique event slugs: {df['event_slug'].n_unique():,}")
    
    print_subsection("Markets per Event")
    print(df["market_count"].describe())
    print(f"\nTotal markets across all events: {df['market_count'].sum():,}")
    
    print_subsection("Volume per Event")
    print(df["total_volume"].describe())
    print(f"\nTotal volume across all events: ${df['total_volume'].sum():,.2f}")
    
    print_subsection("Temporal Coverage")
    print(f"Earliest market start: {df['first_market_start'].min()}")
    print(f"Latest market end: {df['last_market_end'].max()}")
    
    print_subsection("Top Events by Volume")
    print(df.select(["event_slug", "market_count", "total_volume"]).sort("total_volume", descending=True).head(10))
    
    print_subsection("Top Events by Market Count")
    print(df.select(["event_slug", "market_count", "total_volume"]).sort("market_count", descending=True).head(10))


def analyze_polymarket_summary():
    """Analyze soccer_summary.parquet"""
    print_section_header("POLYMARKET: SOCCER SUMMARY")
    
    df = pl.read_parquet(POLYMARKET_DIR / "soccer_summary.parquet")
    
    print(f"Total market summaries: {len(df):,}")
    
    print_subsection("Token Count Distribution")
    print(df["token_count"].value_counts().sort("token_count"))
    
    print_subsection("Trade Count Statistics")
    print(df["trade_count"].describe())
    print(f"\nTotal trades: {df['trade_count'].sum():,}")
    print(f"Markets with no trades: {(df['trade_count'] == 0).sum():,}")
    
    print_subsection("Volume Statistics")
    print(df["volume"].describe())
    
    print_subsection("Active Status")
    active_count = df["active"].sum()
    print(f"Active markets: {active_count:,} ({active_count/len(df)*100:.1f}%)")
    
    print_subsection("Temporal Analysis")
    # Only analyze markets with trades
    df_with_trades = df.filter(pl.col("trade_count") > 0)
    print(f"\nMarkets with trades: {len(df_with_trades):,}")
    print(f"First trade overall: {df_with_trades['first_trade'].min()}")
    print(f"Last trade overall: {df_with_trades['last_trade'].max()}")
    
    # Market duration
    df_with_duration = df_with_trades.with_columns(
        ((pl.col("last_trade") - pl.col("first_trade")).dt.total_seconds() / 3600).alias("duration")
    )
    print(f"\nMarket duration (hours):")
    print(df_with_duration["duration"].describe())
    
    print_subsection("Most Traded Markets")
    print(df.select(["question", "trade_count", "volume", "active"]).sort("trade_count", descending=True).head(10))


def analyze_statsbomb_matches():
    """Analyze matches.parquet"""
    print_section_header("STATSBOMB: MATCHES")
    
    df = pl.read_parquet(STATSBOMB_DIR / "matches.parquet")
    
    print(f"Total matches: {len(df):,}")
    print(f"Columns: {df.columns}")
    
    print_subsection("Competition Distribution")
    print(df["competition_name"].value_counts())
    
    print_subsection("Season Distribution")
    print(df["season_name"].value_counts())
    
    print_subsection("Gender Distribution")
    print(df["gender"].value_counts())
    
    print_subsection("Competition Types")
    print(f"Youth competitions: {df['is_youth'].sum():,}")
    print(f"International competitions: {df['is_international'].sum():,}")
    
    print_subsection("Score Statistics")
    print("Home scores:")
    print(df["home_score"].describe())
    print("\nAway scores:")
    print(df["away_score"].describe())
    
    df_with_totals = df.with_columns((pl.col("home_score") + pl.col("away_score")).alias("total_goals"))
    print("\nTotal goals per match:")
    print(df_with_totals["total_goals"].describe())
    
    print_subsection("Match Results")
    df_with_results = df.with_columns(
        pl.when(pl.col("home_score") > pl.col("away_score"))
        .then(pl.lit("Home Win"))
        .when(pl.col("away_score") > pl.col("home_score"))
        .then(pl.lit("Away Win"))
        .otherwise(pl.lit("Draw"))
        .alias("result")
    )
    print(df_with_results["result"].value_counts())
    
    print_subsection("Temporal Coverage")
    # Cast match_date to Date type for calculations
    # Note: Using str.to_date() requires the string format to be specified or standard YYYY-MM-DD
    # The output shows YYYY-MM-DD, so default handling or explicit format should work.
    # We create a temporary series/df with the casted column.
    
    # Try parsing as Date
    try:
        dates = df["match_date"].str.to_date()
        min_date = dates.min()
        max_date = dates.max()
        
        print(f"First match: {min_date}")
        print(f"Last match: {max_date}")
        
        if min_date is not None and max_date is not None:
            date_range = (max_date - min_date).total_seconds() / (24 * 3600)
            print(f"Date range: {date_range:.0f} days")
    except Exception as e:
        print(f"Could not calculate date range: {e}")
        print(f"First match (str): {df['match_date'].min()}")
        print(f"Last match (str): {df['match_date'].max()}")
    
    print_subsection("Most Common Teams")
    all_teams = pl.concat([df.select("home_team").rename({"home_team": "team"}), 
                           df.select("away_team").rename({"away_team": "team"})])
    print(all_teams["team"].value_counts().head(10))


def analyze_statsbomb_events():
    """Analyze events.parquet"""
    print_section_header("STATSBOMB: EVENTS")
    
    df = pl.read_parquet(STATSBOMB_DIR / "events.parquet")
    
    print(f"Total events: {len(df):,}")
    print(f"Unique matches: {df['match_id'].n_unique():,}")
    print(f"Unique event types: {df['type'].n_unique():,}")
    
    print_subsection("Event Type Distribution")
    print(df["type"].value_counts().head(20))
    
    print_subsection("Period Distribution")
    print(df["period"].value_counts().sort("period"))
    
    print_subsection("Events per Match")
    events_per_match = df.group_by("match_id").agg(pl.len().alias("count"))
    print(events_per_match["count"].describe())
    
    print_subsection("Play Pattern Distribution")
    print(df["play_pattern"].value_counts())
    
    print_subsection("Shot Analysis")
    shots = df.filter(pl.col("type") == "Shot")
    print(f"Total shots: {len(shots):,}")
    print(f"Shots with xG data: {shots['shot_statsbomb_xg'].is_not_null().sum():,}")
    
    if shots["shot_statsbomb_xg"].is_not_null().sum() > 0:
        print("\nxG Statistics:")
        print(shots["shot_statsbomb_xg"].describe())
    
    print_subsection("Pass Analysis")
    passes = df.filter(pl.col("type") == "Pass")
    print(f"Total passes: {len(passes):,}")
    print(f"\nPass outcomes:")
    print(passes["pass_outcome"].value_counts())
    
    successful_passes = passes["pass_outcome"].is_null().sum()
    print(f"\nSuccessful passes: {successful_passes:,} ({successful_passes/len(passes)*100:.1f}%)")
    
    print_subsection("Spatial Distribution")
    print("X coordinates (0-120):")
    print(df["location_x"].describe())
    print("\nY coordinates (0-80):")
    print(df["location_y"].describe())
    
    print_subsection("Most Active Players")
    print(df["player"].value_counts().head(10))
    
    print_subsection("Most Active Teams")
    print(df["team"].value_counts().head(10))


def analyze_statsbomb_lineups():
    """Analyze lineups.parquet"""
    print_section_header("STATSBOMB: LINEUPS")
    
    df = pl.read_parquet(STATSBOMB_DIR / "lineups.parquet")
    
    print(f"Total lineup records: {len(df):,}")
    print(f"Unique matches: {df['match_id'].n_unique():,}")
    print(f"Unique players: {df['player_name'].n_unique():,}")
    
    print_subsection("Position Distribution")
    print(df["position_name"].value_counts())
    
    print_subsection("Jersey Numbers")
    print(df["jersey_number"].describe())
    print(f"\nMost common jersey numbers:")
    print(df["jersey_number"].value_counts().head(10))
    
    print_subsection("Disciplinary Actions")
    cards = df.filter(pl.col("card_type").is_not_null())
    print(f"Total cards: {len(cards):,}")
    print(f"\nCard type distribution:")
    print(cards["card_type"].value_counts())
    
    if len(cards) > 0:
        print(f"\nCard reasons:")
        print(cards["card_reason"].value_counts())
    
    print_subsection("Players per Match")
    players_per_match = df.group_by("match_id").agg(pl.col("player_name").n_unique().alias("player_count"))
    print(players_per_match["player_count"].describe())
    
    print_subsection("Most Frequent Players")
    print(df["player_name"].value_counts().head(10))
    
    print_subsection("Most Frequent Teams")
    print(df["team_name"].value_counts().head(10))


def analyze_statsbomb_three_sixty():
    """Analyze three_sixty.parquet"""
    print_section_header("STATSBOMB: THREE SIXTY TRACKING")
    
    df = pl.read_parquet(STATSBOMB_DIR / "three_sixty.parquet")
    
    print(f"Total tracking records: {len(df):,}")
    print(f"Unique events: {df['event_uuid'].n_unique():,}")
    print(f"Unique matches: {df['match_id'].n_unique():,}")
    
    print_subsection("Player Role Distribution")
    teammate_count = df["teammate"].sum()
    actor_count = df["actor"].sum()
    keeper_count = df["keeper"].sum()
    print(f"Teammate records: {teammate_count:,} ({teammate_count/len(df)*100:.1f}%)")
    print(f"Actor records: {actor_count:,} ({actor_count/len(df)*100:.1f}%)")
    print(f"Keeper records: {keeper_count:,} ({keeper_count/len(df)*100:.1f}%)")
    
    print_subsection("Tracked Players per Event")
    players_per_event = df.group_by("event_uuid").agg(pl.len().alias("count"))
    print(players_per_event["count"].describe())
    
    print_subsection("Spatial Distribution")
    print("X coordinates:")
    print(df["location_x"].describe())
    print("\nY coordinates:")
    print(df["location_y"].describe())
    
    print_subsection("Visible Area Coverage")
    has_visible_area = df["visible_area"].is_not_null().sum()
    print(f"Records with visible area data: {has_visible_area:,} ({has_visible_area/len(df)*100:.1f}%)")


def analyze_statsbomb_reference():
    """Analyze reference.parquet"""
    print_section_header("STATSBOMB: REFERENCE DATA")
    
    df = pl.read_parquet(STATSBOMB_DIR / "reference.parquet")
    
    print(f"Total reference records: {len(df):,}")
    
    print_subsection("Entity Type Distribution")
    print(df["table_name"].value_counts())
    
    print_subsection("Entities by Type")
    for table_name in df["table_name"].unique().to_list():
        subset = df.filter(pl.col("table_name") == table_name)
        print(f"\n{table_name.upper()}:")
        print(f"  Count: {len(subset):,}")
        print(f"  Sample entries: {subset['name'].head(5).to_list()}")


def cross_dataset_analysis():
    """Analyze relationships between Polymarket and Statsbomb data"""
    print_section_header("CROSS-DATASET ANALYSIS")
    
    # Load key files
    pm_markets = pl.read_parquet(POLYMARKET_DIR / "soccer_markets.parquet")
    sb_matches = pl.read_parquet(STATSBOMB_DIR / "matches.parquet")
    
    print_subsection("Temporal Coverage Comparison")
    print("Polymarket:")
    print(f"  Date range: {pm_markets['created_at'].min()} to {pm_markets['created_at'].max()}")
    print(f"  Total markets: {len(pm_markets):,}")
    
    print("\nStatsbomb:")
    print(f"  Date range: {sb_matches['match_date'].min()} to {sb_matches['match_date'].max()}")
    print(f"  Total matches: {len(sb_matches):,}")
    
    print_subsection("Data Volume Summary")
    print("Polymarket files:")
    for file in POLYMARKET_DIR.glob("*.parquet"):
        df = pl.read_parquet(file)
        print(f"  {file.name}: {len(df):,} rows")
    
    print("\nStatsbomb files:")
    for file in STATSBOMB_DIR.glob("*.parquet"):
        df = pl.read_parquet(file)
        print(f"  {file.name}: {len(df):,} rows")

def plot_heat_map(df, value_col, team, title, cmap="hot"):
    #plot outlilne generated by AI (chatGPT)
    team_df = df.filter(pl.col("team") == team)
    pandas_df = team_df.select(["x_bin", "y_bin", value_col]).to_pandas()
    heat_map = (pandas_df.pivot(index="y_bin", columns="x_bin", values=value_col).fillna(0).values)
    plt.figure(figsize=(12,8))
    plt.imshow(heat_map, origin="lower", aspect="auto",cmap=cmap)
    plt.colorbar(label=value_col)
    plt.title(f"{title} - {team}")
    plt.xlabel("Pitch length (x bins)")
    plt.ylabel("Pitch width (y bins)")
    plt.tight_layout()
    plt.savefig(f"figures/{title}_{team}.png", dpi=200, bbox_inches="tight")
    plt.close()     

def plot_all_hmaps(df, value_col, title):
    #all the heatmaps by team
    teams = df.select("team").unique().drop_nulls().to_series().to_list()
    for team in teams:
        #regex generated by AI (chatGPT)
        team = team.strip()
        team = re.sub(r"[\\/]", "_", team)
        team = re.sub(r"[^a-zA-Z0-9._-]", "", team)
        plot_heat_map(df, value_col, team, title, cmap="hot")

def spatial_analysis():
    #binning methodology generated by AI (chatGPT)
    Bin_Size = 5  # meters
    df = pl.read_parquet(STATSBOMB_DIR / "events.parquet")
    df = df.with_columns([
        (pl.col("location_x") // Bin_Size).cast(pl.Int64).alias("x_bin"),
        (pl.col("location_y") // Bin_Size).cast(pl.Int64).alias("y_bin"),
    ])
    #team analysis
    #groupby line generated by AI (chatGPT)
    team_spatial = df.group_by(["team", "x_bin", "y_bin"]).count().rename({"count": "events"})
    plot_all_hmaps(team_spatial, "events", "Spatial Events")
    #Shot analysis
    shots = df.filter(pl.col("type") == "Shot")
    shot_spatial = shots.group_by(["team", "x_bin", "y_bin"]).agg([
        pl.count().alias("shots"),
        pl.col("shot_statsbomb_xg").sum().alias("total_xg"),
        pl.col("shot_statsbomb_xg").mean().alias("avg_xg"),
        ])
    plot_all_hmaps(shot_spatial, "total_xg", "Shots")
    print(shot_spatial)
    #pass analysis
    passes = df.filter(pl.col("type") == "Pass")
    pass_spatial = passes.group_by(["team", "x_bin", "y_bin"]).count().rename({"count": "passes"})
    plot_all_hmaps(pass_spatial, "passes", "Passes")

    print(pass_spatial)
    #successful pass analaysis
    successful_passes = df.filter(pl.col("pass_outcome").is_null().alias("successful"))
    pass_successful_spatial = successful_passes.group_by(["team", "x_bin", "y_bin"]).count().rename({"count": "successful_passes"})
    plot_all_hmaps(successful_passes, "successful_passes", "Successful Passes")
    print(pass_successful_spatial)
    # play_pattern
    # play_pattern_spatial = df.group_by(["team", "play_pattern", "x_bin", "y_bin"]).count()
    # print(play_pattern_spatial)


def spatial_analysis_2():
    #map all starts of possesions ending in a shot
    Bin_Size = 5  # meters
    df = pl.read_parquet(STATSBOMB_DIR / "events.parquet")
    df = df.with_columns([
        (pl.col("location_x") // Bin_Size).cast(pl.Int64).alias("x_bin"),
        (pl.col("location_y") // Bin_Size).cast(pl.Int64).alias("y_bin"),
    ])
    # print(df.columns)
    #genAI used for syntax
    shot_possessions = df.filter(pl.col("type") == "Shot").select(["match_id", "possession"]).unique()
    keys = shot_possessions.select(pl.struct(["match_id", "possession"]).alias("key")).to_series()
    shot_sequences = df. filter(pl.struct(["match_id", "possession"]).is_in(keys))
    shot_sequences_sorted = shot_sequences.sort(["match_id","possession", "minute", "second"])
    shot_sequences_binned =shot_sequences_sorted.group_by(["team", "x_bin", "y_bin"]).agg([
        pl.count().alias("shots"),
        pl.col("shot_statsbomb_xg").sum().alias("total_xg"),
        pl.col("shot_statsbomb_xg").mean().alias("avg_xg"),
        ])
    #heatmap of start of shot-ending possessions
    possession_starts = shot_sequences.group_by("match_id", "possession").first()
    plot_all_hmaps(possession_starts, "shot_statsbom_xg", "Start of Shot Possessions")
    #heatmap of whole possession xg total
    plot_all_hmaps(shot_sequences_binned, "total_xg", "Shot-Ending Possession Area")
    #passes of shot possessions
    passes = shot_sequences_sorted.filter(pl.col("type") == "Pass")
    pass_spatial = passes.group_by(["team", "x_bin", "y_bin"]).count().rename({"count": "passes"})
    plot_all_hmaps(pass_spatial, "passes", "Passes")
    #successfull passes of shot possessions
    successful_passes = shot_sequences.filter(pl.col("pass_outcome").is_null().alias("successful"))
    pass_successful_spatial = successful_passes.group_by(["team", "x_bin", "y_bin"]).count().rename({"count": "successful_passes"})
    plot_all_hmaps(pass_successful_spatial, "successful_passes", "Successful Passes")

def main():
    """Run complete EDA"""
    print("\n" + "=" * 80)
    print("  SOCCER ANALYTICS - COMPREHENSIVE EDA")
    print("  Using Polars for high-performance data processing")
    print("=" * 80)
    
    # # Polymarket analysis (Optional)
    # if POLYMARKET_DIR.exists():
    #     try:
    #         analyze_polymarket_markets()
    #         analyze_polymarket_tokens()
    #         analyze_polymarket_trades()
    #         analyze_polymarket_odds_history()
    #         analyze_polymarket_event_stats()
    #         analyze_polymarket_summary()
    #     except Exception as e:
    #         print(f"\n[SKIP] Error analyzing Polymarket data: {e}")
    # else:
    #     print("\n[SKIP] Polymarket data directory not found. Skipping Polymarket analysis.")
    
    # Statsbomb analysis
    if STATSBOMB_DIR.exists():
        # analyze_statsbomb_matches()
        # analyze_statsbomb_events()
        # analyze_statsbomb_lineups()
        # analyze_statsbomb_three_sixty()
        # analyze_statsbomb_reference()
        # spatial_analysis()
        spatial_analysis_2()
    else:
        print("\n[ERROR] Statsbomb data directory not found. Please run data/download_data.py first.")
    
    # # Cross-dataset analysis
    # if POLYMARKET_DIR.exists() and STATSBOMB_DIR.exists():
    #     cross_dataset_analysis()
    # else:
    #     print("\n[SKIP] Skipping cross-dataset analysis (requires both Polymarket and Statsbomb data).")
    
    # print("\n" + "=" * 80)
    # print("  EDA COMPLETE")
    # print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

