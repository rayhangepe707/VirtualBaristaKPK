import pandas as pd
import json

# 1. Pastikan nama file Excel-mu sesuai
file_path = "ultimate_virtual_barista_dataset.xlsx"

print("Membaca data dari Excel...")
df_menu = pd.read_excel(file_path, sheet_name='Advanced Menu Profile')
df_food = pd.read_excel(file_path, sheet_name='Food Menu')

menu_list = []

# 2. Melakukan perulangan untuk setiap baris menu di Excel
for index, row in df_menu.iterrows():
    kopi_id = f"K{index+1:03d}"
    nama_kopi = str(row['nama_menu'])
    
    # Mencari makanan yang cocok dari sheet Food Menu
    food_match = df_food[df_food['Rekomendasi Minuman'].astype(str).str.contains(nama_kopi, case=False, na=False)]
    
    if not food_match.empty:
        food_name = food_match.iloc[0]['Nama Menu']
    else:
        # Jika tidak ada yang spesifik, pasangkan secara berurutan
        food_name = df_food.iloc[index % len(df_food)]['Nama Menu']

    # Fungsi untuk mengatasi data kosong (NaN) di Excel
    def get_score(val, default):
        if pd.isna(val): return default
        return int(val) * 2  # Dikali 2 agar skalanya 1-10 untuk grafik radar

    # 3. Membentuk struktur JSON
    menu_item = {
        "id_kopi": kopi_id,
        "nama_kopi": nama_kopi,
        "kategori": str(row['kategori']).capitalize() if pd.notna(row['kategori']) else "Lainnya",
        "harga": int(row['harga']) if pd.notna(row['harga']) else 0,
        "deskripsi_edukasi": str(row['recommendation_reason']) if pd.notna(row['recommendation_reason']) else "Menu spesial dari Kopi KPK.",
        "profil_rasa": {
            "keasaman": get_score(row['fresh_score'], 2),
            "body": get_score(row['strong_score'], 4),
            "aroma": get_score(row['pahit_score'], 6), 
            "manis": get_score(row['manis_score'], 4)
        },
        "rekomendasi_makanan": {
            "nama_makanan": food_name,
            # Placeholder gambar (bisa diganti URL asli nanti)
            "gambar_makanan": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=200&q=80"
        },
        "gambar_kopi": "https://images.unsplash.com/photo-1559525839-b184a4d698c7?auto=format&fit=crop&w=200&q=80"
    }
    menu_list.append(menu_item)

# 4. Menyimpan hasilnya ke file menu.json
with open('menu.json', 'w', encoding='utf-8') as f:
    json.dump(menu_list, f, indent=4, ensure_ascii=False)

print(f"Berhasil! {len(menu_list)} menu telah dikonversi dan disimpan ke menu.json.")