import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.ticker import MultipleLocator
from config import Config
import numpy as np

def parse_price(price_str):
    """Cleans price string to float."""
    return float(price_str.replace('zł', '').replace(',', '.').replace('\xa0', '').strip())

def add_price_labels(ax, df):
    """Adds labels to the Min and Max price points for each category."""
    for cat in df['Category'].unique():
        cat_data = df[df['Category'] == cat].dropna(subset=['Price'])
        
        if cat_data.empty: continue

        # Find min and max points
        max_point = cat_data.loc[cat_data['Price'].idxmax()]
        min_point = cat_data.loc[cat_data['Price'].idxmin()]
        
        # Build list of points to label (avoid duplicates if min == max)
        points_to_label = [max_point]
        if min_point['Time'] != max_point['Time']:
            points_to_label.append(min_point)

        for point in points_to_label:
            ax.annotate(
                f"{point['Price']:.2f} zł",
                xy=(point['Time'], point['Price']),
                xytext=(0, 10),
                textcoords='offset points',
                ha='center',
                fontsize=9,
                fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#cccccc", alpha=0.8)
            )

def insert_gaps(df, gap_threshold='1h'):
    """
    Inserts empty rows (NaN) where the gap between measurements exceeds gap_threshold.
    Prevents connecting distant points with a line on the chart.
    """
    df = df.sort_values('Time')
    df['delta'] = df['Time'].diff()
    
    gap_mask = df['delta'] > pd.to_timedelta(gap_threshold)
    
    # Create a list of "artificial" rows with NaN to insert into gaps
    gap_rows = []
    for idx in df[gap_mask].index:
        gap_time = df.loc[idx, 'Time'] - pd.to_timedelta('1s')
        gap_row = df.loc[idx].copy()
        gap_row['Time'] = gap_time
        gap_row['Price'] = np.nan
        gap_rows.append(gap_row)
    
    if not gap_rows:
        return df.drop(columns=['delta'])
    
    # Combine original data with "gaps" and sort
    df_gaps = pd.DataFrame(gap_rows)
    df_final = pd.concat([df, df_gaps], ignore_index=True)
    df_final = df_final.sort_values('Time').reset_index(drop=True)
    
    return df_final.drop(columns=['delta'])

def generate_comparison_chart():
    try:
        df = pd.read_csv(Config.CSV_FILE)
    except Exception as e:
        print(f"CSV file not found or empty: {e}")
        return

    df['date_hour'] = pd.to_datetime(df['date_hour'])
    plot_data = []

    TARGET_CATEGORIES = ["Bolt", "Comfort", "Green"]

    print(f"Processing data for: {TARGET_CATEGORIES}...")

    # --- PARSING ---
    for _, row in df.iterrows():
        try:
            options = json.loads(row['options'])
            for cat, val in options.items():
                if cat not in TARGET_CATEGORIES: continue

                # Logic for double prices "11,20 zł | 22,39 zł"
                if "|" in val:
                    parts = val.split("|")
                    price_final = parse_price(parts[0]) # Take the first (discounted) price
                else:
                    price_final = parse_price(val)

                plot_data.append({
                    'Time': row['date_hour'],
                    'Category': cat,
                    'Price': price_final
                })
        except: continue

    if not plot_data:
        print("No valid data found.")
        return

    raw_df = pd.DataFrame(plot_data)

    # Process each category separately to insert gaps where needed
    processed_dfs = []
    for cat in TARGET_CATEGORIES:
        cat_df = raw_df[raw_df['Category'] == cat]
        if cat_df.empty: continue
        
        # Insert a gap if no data for over 65 minutes
        cat_with_gaps = insert_gaps(cat_df, gap_threshold='65min')
        processed_dfs.append(cat_with_gaps)
    
    plot_df = pd.concat(processed_dfs).reset_index(drop=True)

    plt.figure(figsize=(14, 8))
    sns.set_theme(style="whitegrid")
    
    custom_palette = {"Bolt": "#2563EB", "Comfort": "#F59E0B", "Green": "#10B981"}
    custom_dashes = {"Bolt": "", "Comfort": "", "Green": (4, 2)}

    ax = sns.lineplot(
        data=plot_df, 
        x='Time', 
        y='Price', 
        hue='Category', 
        style='Category',       
        dashes=custom_dashes,   
        palette=custom_palette,
        linewidth=2.5,            
        markers=True,
        markersize=7
    )

    # Price labels (Min/Max)
    add_price_labels(ax, plot_df)

    # --- FORMATTING ---
    plt.title('Real-Time Price Monitor', fontsize=18, fontweight='bold')
    plt.ylabel('Payable Price (PLN)', fontsize=14)
    plt.xlabel('Time', fontsize=14)

    # X-Axis
    locator = mdates.HourLocator(interval=1) # Every 1 hour for precision
    ax.xaxis.set_major_locator(locator)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.setp(ax.get_xticklabels(), fontsize=10)

    # Y-Axis
    ax.yaxis.set_major_locator(MultipleLocator(2))
    plt.setp(ax.get_yticklabels(), fontsize=10)

    # Vertical grid for hours
    ax.grid(True, which='major', axis='x', linestyle='--', alpha=0.5)

    plt.legend(bbox_to_anchor=(0.02, 0.98), loc='upper left', title="Category", frameon=True)
    
    plt.tight_layout()
    
    plt.savefig(Config.CHART_FILE, dpi=300)
    print(f"Chart generated successfully: {Config.CHART_FILE}")
    plt.show()

if __name__ == "__main__":
    generate_comparison_chart()