import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from config import Config

def parse_price(price_str):
    """Czyści tekst ceny do float."""
    return float(price_str.replace('zł', '').replace(',', '.').replace('\xa0', '').strip())

def generate_promo_chart():
    try:
        df = pd.read_csv(Config.CSV_FILE)
    except:
        print("❌ Brak pliku CSV.")
        return

    df['data_godzina'] = pd.to_datetime(df['data_godzina'])
    plot_data = []

    for _, row in df.iterrows():
        try:
            options = json.loads(row['wszystkie_opcje'])
            for cat, val in options.items():
                
                # Sprawdzamy czy jest promocja (separator |)
                if "|" in val:
                    parts = val.split("|")
                    price_now = parse_price(parts[0])
                    price_old = parse_price(parts[1])
                    is_promo = True
                else:
                    price_now = parse_price(val)
                    price_old = price_now # Brak starej ceny
                    is_promo = False

                plot_data.append({
                    'Czas': row['data_godzina'],
                    'Kategoria': cat,
                    'Cena': price_now,
                    'StaraCena': price_old if is_promo else None,
                    'Promocja': is_promo
                })
        except:
            continue

    if not plot_data:
        print("⚠️ Pusto.")
        return

    plot_df = pd.DataFrame(plot_data)

    plt.figure(figsize=(16, 9))
    sns.set_theme(style="whitegrid")

    # 1. Rysujemy linie (Ceny do zapłaty)
    sns.lineplot(
        data=plot_df, x='Czas', y='Cena', 
        hue='Kategoria', style='Kategoria',
        markers=True, dashes=False, linewidth=2, markersize=8
    )

    # 2. Dodajemy punkty "Starej ceny" (tylko tam gdzie była promocja)
    promo_points = plot_df[plot_df['Promocja'] == True]
    if not promo_points.empty:
        sns.scatterplot(
            data=promo_points, x='Czas', y='StaraCena', 
            color='red', marker='x', s=100, label='Cena bez zniżki', zorder=10
        )
        # Rysujemy cieniutką linię łączącą Starą i Nową cenę
        for _, point in promo_points.iterrows():
            plt.plot([point['Czas'], point['Czas']], [point['Cena'], point['StaraCena']], 
                     color='red', linestyle=':', alpha=0.5)

    plt.title('Monitoring Bolt: Ceny Realne vs Promocje', fontsize=18)
    plt.ylabel('Cena (PLN)')
    plt.xlabel('Godzina')
    
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(Config.CHART_FILE, dpi=300)
    print(f"✅ Wygenerowano: {Config.CHART_FILE}")    
    plt.show()

if __name__ == "__main__":
    generate_promo_chart()