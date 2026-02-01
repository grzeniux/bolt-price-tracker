import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.ticker import MultipleLocator
from config import Config

def parse_price(price_str):
    return float(price_str.replace('zł', '').replace(',', '.').replace('\xa0', '').strip())

def add_price_labels(ax, df):
    for cat in df['Category'].unique():
        cat_data = df[df['Category'] == cat].dropna(subset=['Price'])
        
        if cat_data.empty: continue

        max_point = cat_data.loc[cat_data['Price'].idxmax()]
        min_point = cat_data.loc[cat_data['Price'].idxmin()]
        
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

    for _, row in df.iterrows():
        try:
            options = json.loads(row['options'])
            
            for cat, val in options.items():
                if cat not in TARGET_CATEGORIES:
                    continue

                if "|" in val:
                    parts = val.split("|")
                    price_final = parse_price(parts[0])
                else:
                    price_final = parse_price(val)

                plot_data.append({
                    'Time': row['date_hour'],
                    'Category': cat,
                    'Price': price_final
                })
        except:
            continue

    if not plot_data:
        print("No data found.")
        return

    raw_df = pd.DataFrame(plot_data)
    raw_df = raw_df.set_index('Time')
    
    resampled_dfs = []
    for cat in TARGET_CATEGORIES:
        cat_df = raw_df[raw_df['Category'] == cat]
        if cat_df.empty: continue
        
        cat_resampled = cat_df.resample('30min').mean(numeric_only=True)
        cat_resampled['Category'] = cat
        resampled_dfs.append(cat_resampled)
    
    plot_df = pd.concat(resampled_dfs).reset_index()

    plt.figure(figsize=(14, 8))
    sns.set_theme(style="whitegrid")
    
    custom_palette = {
        "Bolt": "#2563EB",
        "Comfort": "#F59E0B",
        "Green": "#10B981"
    }
    
    custom_dashes = {
        "Bolt": "",        
        "Comfort": "",      
        "Green": (4, 2)     
    }

    ax = sns.lineplot(
        data=plot_df, 
        x='Time', 
        y='Price', 
        hue='Category', 
        style='Category',       
        dashes=custom_dashes,   
        palette=custom_palette,
        linewidth=3,            
        markers=True,
        markersize=8
    )

    add_price_labels(ax, plot_df)

    plt.title('Real-Time Price Monitor', fontsize=18, fontweight='bold')
    plt.ylabel('Payable Price (PLN)', fontsize=14)
    plt.xlabel('Time', fontsize=14)

    locator = mdates.HourLocator(interval=2) 
    ax.xaxis.set_major_locator(locator)
    
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_formatter(formatter)
    
    plt.setp(ax.get_xticklabels(), fontsize=11)

    ax.yaxis.set_major_locator(MultipleLocator(2))
    plt.setp(ax.get_yticklabels(), fontsize=11)

    plt.legend(bbox_to_anchor=(0.02, 0.98), loc='upper left', title="Category", frameon=True)
    
    plt.tight_layout()
    plt.savefig(Config.CHART_FILE, dpi=300)
    print(f"Chart generated successfully: {Config.CHART_FILE}")

if __name__ == "__main__":
    generate_comparison_chart()