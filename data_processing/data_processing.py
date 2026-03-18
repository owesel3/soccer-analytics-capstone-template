"""
Ingest + version StatsBomb
Open Match event data; 
normalize IDs (team/player/competiton)
create train/val/test splits
"""

import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
STATSBOMB_DIR = DATA_DIR / "Statsbomb"


def print_section_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_subsection(title):
    """Print formatted subsection header"""
    print(f"\n--- {title} ---")

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

def ingest_and_version():
    df = pl.read_parquet(STATSBOMB_DIR / "events.parquet")

def normalize_team_IDs():
    df = pl.read_parquet(STATSBOMB_DIR / "events.parquet")
    # print(df.columns)  
    print(df['team_id'].unique())
    print(df['player_id'].unique())
    print(df['match_id'].unique())

# def normalize_IDs():


def main():
    """Run complete EDA"""
    print("\n" + "=" * 80)
    print("  SOCCER ANALYTICS - COMPREHENSIVE EDA")
    print("  Using Polars for high-performance data processing")
    print("=" * 80)
    
    
    # Statsbomb analysis
    if STATSBOMB_DIR.exists():
        # analyze_statsbomb_events()
        normalize_team_IDs()

    else:
        print("\n[ERROR] Statsbomb data directory not found. Please run data/download_data.py first.")
    

    print("\n" + "=" * 80)
    print("  EDA COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()