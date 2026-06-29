"""
Smart Plant Pot – EDA Script
Phân tích + Clean dataset TARP.csv → xuất tarp_clean.csv + eda_report.png
Chạy: python eda.py
Output: tarp_clean.csv, eda_report.png
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── 1. LOAD ───────────────────────────────────────────────────────────────────
print("📂 1. Loading dataset...")
df = pd.read_csv('TARP.csv')
df.columns = df.columns.str.strip()
print(f"   Shape: {df.shape}")
print(f"   Columns: {df.columns.tolist()}")

# ── 2. TỔNG QUAN ──────────────────────────────────────────────────────────────
print("\n📋 2. Tổng quan")
print(df.dtypes.to_string())

# ── 3. MISSING VALUES → quyết định bỏ cột ────────────────────────────────────
print("\n🔍 3. Missing Values")
missing     = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(1)
missing_df  = pd.DataFrame({'count': missing, 'percent': missing_pct})
missing_df  = missing_df[missing_df['count'] > 0].sort_values('count', ascending=False)
print(missing_df.to_string())

# Bỏ cột missing > 50%
drop_cols = missing_pct[missing_pct > 50].index.tolist()
print(f"\n   → Bỏ {len(drop_cols)} cột missing > 50%: {drop_cols}")
df = df.drop(columns=drop_cols)

# ── 4. DUPLICATES → xóa ───────────────────────────────────────────────────────
print("\n🔁 4. Duplicates")
dup = df.duplicated().sum()
print(f"   Duplicate rows: {dup} → xóa")
df = df.drop_duplicates()
print(f"   Sau xóa: {len(df):,} rows")

# ── 5. THỐNG KÊ MÔ TẢ ────────────────────────────────────────────────────────
print("\n📊 5. Thống kê mô tả")
features = ['Soil Moisture', 'Temperature', 'Soil Humidity']
print(df[features].describe().round(2).to_string())

# ── 6. PHÂN PHỐI LABEL ────────────────────────────────────────────────────────
print("\n🏷️  6. Phân phối Label")
vc  = df['Status'].value_counts()
pct = df['Status'].value_counts(normalize=True).round(3) * 100
print(f"   ON  (tưới):       {vc['ON']:,}  ({pct['ON']:.1f}%)")
print(f"   OFF (không tưới): {vc['OFF']:,} ({pct['OFF']:.1f}%)")
print(f"   → Balanced, không cần resample")

# ── 7. OUTLIERS ───────────────────────────────────────────────────────────────
print("\n⚠️  7. Outliers (IQR method)")
for col in features:
    Q1  = df[col].quantile(0.25)
    Q3  = df[col].quantile(0.75)
    IQR = Q3 - Q1
    out = ((df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)).sum()
    print(f"   {col:<20}: {out} outliers → {'xóa' if out > 0 else 'không cần xử lý'}")
    if out > 0:
        df = df[~((df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR))]

# ── 8. CORRELATION ────────────────────────────────────────────────────────────
print("\n🔗 8. Correlation với Label")
df['label'] = (df['Status'] == 'ON').astype(int)
corr = df[features + ['label']].corr()['label'].drop('label').sort_values()
print(corr.round(3).to_string())

# ── 9. MEAN THEO STATUS ───────────────────────────────────────────────────────
print("\n📈 9. Mean theo Status")
print(df.groupby('Status')[features].mean().round(2).to_string())

# ── 10. SAVE CLEAN DATA ───────────────────────────────────────────────────────
df_clean = df[features + ['Status', 'label']].copy()
df_clean.to_csv('tarp_clean.csv', index=False)
print(f"\n💾 Saved: tarp_clean.csv ({len(df_clean):,} rows)")

# ── VISUALIZATION ─────────────────────────────────────────────────────────────
print("\n🎨 Tạo biểu đồ EDA...")

sns.set_theme(style='darkgrid')
fig = plt.figure(figsize=(18, 22))
fig.patch.set_facecolor('#0f0f1a')
gs  = gridspec.GridSpec(4, 3, figure=fig, hspace=0.45, wspace=0.35)

title_color = '#cdd6f4'
label_color = '#bac2de'
bg_color    = '#1e1e2e'
on_color    = '#89b4fa'
off_color   = '#f38ba8'

def style_ax(ax):
    ax.set_facecolor(bg_color)
    ax.tick_params(colors=label_color, labelsize=9)
    ax.xaxis.label.set_color(label_color)
    ax.yaxis.label.set_color(label_color)
    ax.title.set_color(title_color)
    for spine in ax.spines.values():
        spine.set_edgecolor('#313244')

# 1. Missing values
ax1 = fig.add_subplot(gs[0, 0])
miss_plot = missing_df[missing_df['count'] > 0]
colors_m  = ['#f38ba8' if v > 50000 else '#fab387' if v > 10000 else '#a6e3a1'
             for v in miss_plot['count']]
bars = ax1.barh(miss_plot.index, miss_plot['count'], color=colors_m)
ax1.set_title('Missing Values per Column', fontsize=11, fontweight='bold')
ax1.set_xlabel('Count')
for bar, val in zip(bars, miss_plot['count']):
    ax1.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
             f'{val:,}', va='center', fontsize=8, color=label_color)
style_ax(ax1)

# 2. Status pie
ax2 = fig.add_subplot(gs[0, 1])
counts = df_clean['Status'].value_counts()
wedges, texts, autotexts = ax2.pie(
    counts, labels=counts.index, autopct='%1.1f%%',
    colors=[on_color, off_color], startangle=90,
    textprops={'color': title_color, 'fontsize': 11})
for at in autotexts:
    at.set_color('#1e1e2e')
    at.set_fontweight('bold')
ax2.set_title('Status Distribution\n(ON=Tưới / OFF=Không tưới)',
              fontsize=11, fontweight='bold', color=title_color)
ax2.set_facecolor(bg_color)

# 3. Correlation heatmap
ax3 = fig.add_subplot(gs[0, 2])
corr_mat = df_clean[features + ['label']].corr()
sns.heatmap(corr_mat, annot=True, fmt='.2f', cmap='coolwarm',
            ax=ax3, linewidths=0.5, linecolor='#313244',
            annot_kws={'size': 9, 'color': 'white'},
            cbar_kws={'shrink': 0.8})
ax3.set_title('Correlation Matrix', fontsize=11, fontweight='bold')
ax3.tick_params(colors=label_color, labelsize=8)
ax3.set_facecolor(bg_color)

# 4-6. Histogram
for i, col in enumerate(features):
    ax = fig.add_subplot(gs[1, i])
    on_d  = df_clean[df_clean['Status'] == 'ON'][col]
    off_d = df_clean[df_clean['Status'] == 'OFF'][col]
    ax.hist(on_d,  bins=30, alpha=0.7, color=on_color,  label='ON',  density=True)
    ax.hist(off_d, bins=30, alpha=0.7, color=off_color, label='OFF', density=True)
    ax.axvline(on_d.mean(),  color=on_color,  linestyle='--', linewidth=1.5)
    ax.axvline(off_d.mean(), color=off_color, linestyle='--', linewidth=1.5)
    ax.set_title(f'{col}\nON={on_d.mean():.1f} | OFF={off_d.mean():.1f}',
                 fontsize=10, fontweight='bold')
    ax.set_xlabel(col)
    ax.set_ylabel('Density')
    ax.legend(fontsize=8, facecolor=bg_color, labelcolor=label_color)
    style_ax(ax)

# 7-9. Boxplot
for i, col in enumerate(features):
    ax = fig.add_subplot(gs[2, i])
    bp = ax.boxplot(
        [df_clean[df_clean['Status'] == 'ON'][col],
         df_clean[df_clean['Status'] == 'OFF'][col]],
        labels=['ON', 'OFF'], patch_artist=True, notch=True,
        medianprops={'color': 'white', 'linewidth': 2})
    bp['boxes'][0].set_facecolor(on_color  + '99')
    bp['boxes'][1].set_facecolor(off_color + '99')
    for w in bp['whiskers']: w.set_color(label_color)
    for c in bp['caps']:     c.set_color(label_color)
    ax.set_title(f'Boxplot: {col}', fontsize=10, fontweight='bold')
    ax.set_ylabel(col)
    style_ax(ax)

# 10. Scatter
ax10 = fig.add_subplot(gs[3, 0])
sample = df_clean.sample(3000, random_state=42)
on_s   = sample[sample['Status'] == 'ON']
off_s  = sample[sample['Status'] == 'OFF']
ax10.scatter(off_s['Soil Moisture'], off_s['Temperature'],
             alpha=0.4, s=10, color=off_color, label='OFF')
ax10.scatter(on_s['Soil Moisture'],  on_s['Temperature'],
             alpha=0.4, s=10, color=on_color, label='ON')
ax10.axvline(x=45, color='yellow', linestyle='--', linewidth=1.5, alpha=0.8,
             label='Threshold ~45')
ax10.set_xlabel('Soil Moisture')
ax10.set_ylabel('Temperature (°C)')
ax10.set_title('Soil Moisture vs Temperature', fontsize=10, fontweight='bold')
ax10.legend(fontsize=8, facecolor=bg_color, labelcolor=label_color)
style_ax(ax10)

# 11. Mean theo status bar
ax11 = fig.add_subplot(gs[3, 1])
means = df_clean.groupby('Status')[features].mean()
x     = np.arange(len(features))
w     = 0.35
ax11.bar(x - w/2, means.loc['ON'],  w, label='ON',  color=on_color,  alpha=0.8)
ax11.bar(x + w/2, means.loc['OFF'], w, label='OFF', color=off_color, alpha=0.8)
ax11.set_xticks(x)
ax11.set_xticklabels(['Soil\nMoisture', 'Temperature', 'Soil\nHumidity'],
                      color=label_color, fontsize=9)
ax11.set_title('Mean Value theo Status', fontsize=10, fontweight='bold')
ax11.legend(fontsize=8, facecolor=bg_color, labelcolor=label_color)
style_ax(ax11)

# 12. Summary
ax12 = fig.add_subplot(gs[3, 2])
ax12.set_facecolor(bg_color)
ax12.axis('off')
summary = [
    "📋 CLEANING SUMMARY",
    "",
    f"Raw:           100,000 rows",
    f"Drop missing:  {len(drop_cols)} cols (>50%)",
    f"Drop dup:      {dup} rows",
    f"Final clean:   {len(df_clean):,} rows",
    "",
    "Columns bỏ:",
    "  Air temp/humi  (76%)",
    "  ph, rain, NPK  (98%)",
    "",
    "Features giữ:",
    "  ✅ Soil Moisture",
    "  ✅ Temperature",
    "  ✅ Soil Humidity",
    "",
    "→ Saved: tarp_clean.csv",
]
ax12.text(0.05, 0.95, '\n'.join(summary),
          transform=ax12.transAxes, fontsize=9,
          verticalalignment='top', color=label_color,
          fontfamily='monospace',
          bbox=dict(boxstyle='round', facecolor='#313244', alpha=0.5))

fig.suptitle('🌿 Smart Pot – EDA Report (TARP Dataset)',
             fontsize=16, fontweight='bold', color=title_color, y=0.98)

plt.savefig('eda_report.png', dpi=150, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print("✅ Saved: eda_report.png")
print("🚀 Tiếp theo: python train.py")
