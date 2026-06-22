import json
import logging
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from groq import Groq

# 1. BACA BRANKAS RAHASIA
load_dotenv()

# 2. AMBIL KUNCI API DARI .ENV
api_key_groq = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key_groq)

app = Flask(__name__)

# ==========================================
# FUNGSI AI RAG MENGGUNAKAN GROQ (LLaMA 3.3 70B)
# ==========================================
def ask_ai_barista(user_message, dataset):
    menu_context = ""
    for item in dataset:
        nama = item.get('nama_makanan') or item.get('nama_minuman') or item.get('nama_kopi') or ''
        harga = item.get('harga', 0)
        desc = item.get('deskripsi_edukasi', '')
        if nama:
            menu_context += f"- {nama} (Rp{harga}): {desc}\n"

    system_prompt = f"""Kamu adalah Virtual Barista yang ramah, asik, dan berwawasan di 'Warung Kopi KPK' Padang.
    
ATURAN WAJIB (GUARDRAILS):
1. HANYA rekomendasikan menu dari daftar di bawah. JANGAN PERNAH menyarankan menu dari tempat lain.
2. Jika pelanggan bertanya hal di luar kopi/makanan (misal: politik, cuaca umum, coding), arahkan kembali dengan sopan ke menu kopi KPK.
3. Gunakan bahasa Indonesia yang santai, gaul mahasiswa, tapi tetap sopan. Jangan terlalu kaku.
4. Jawab singkat (maksimal 3 kalimat) dan berikan 1 rekomendasi spesifik yang paling masuk akal dengan perasaan pelanggan.
5. Jika pelanggan meminta saran, curhat, atau mencari rekomendasi, kamu WAJIB menyebutkan 1 nama Minuman DAN 1 nama Makanan/Snack secara bersamaan.
6. Pastikan kamu menyebutkan nama menu persis sesuai huruf yang ada di daftar.
7. Di AWAL jawabanmu, WAJIB sertakan tag emosi yang sesuai dengan curhatan atau emosi pelanggan. Pilih salah satu tag ini: [HAPPY], [SAD], [EXCITED], atau [NEUTRAL].
   Format wajib: [TAG_EMOSI] Jawaban barista...
   Contoh format:
   [SAD] Wah, jangan sedih Kak...
   [HAPPY] Asyik banget Kak...

CONTOH PERCAKAPAN:
Pelanggan: "Lagi capek habis nugas nih bang."
Barista: "[SAD] Wah, semangat terus nugasnya, Kak! Biar capeknya hilang dan mata seger lagi, aku saranin cobain Kopi Susu KPK dan Pisang Goreng. Manisnya pas, kopinya nendang buat *boost* energi kamu!"

DAFTAR MENU WARUNG KOPI KPK:
{menu_context}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=512,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error API Groq: {e}")
        return None

# ==========================================
# PENGATURAN TERMINAL & DATASET
# ==========================================
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def load_data():
    try:
        with open('menu.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Gagal memuat menu.json: {e}")
        return []

dataset_menu = load_data()

def get_item_name(item):
    return item.get('nama_makanan') or item.get('nama_minuman') or item.get('nama_kopi') or ''

def get_item_image(item):
    return item.get('gambar_makanan') or item.get('gambar_minuman') or item.get('gambar_kopi') or ''

# ==========================================
# RUTE HALAMAN WEB
# ==========================================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/katalog')
def katalog():
    data = load_data() 
    kategori_menu = {}
    for item in data:
        kat = item.get('kategori', 'Lainnya')
        if kat not in kategori_menu:
            kategori_menu[kat] = []
        kategori_menu[kat].append(item)
    return render_template('katalog.html', kategori_menu=kategori_menu)

@app.route('/edukasi')
def edukasi():
    return render_template('edukasi.html')

@app.route('/rating')
def rating():
    return render_template('rating.html')

# ==========================================
# RUTE LOGIKA CHATBOT TERPUSAT (PURE AI)
# ==========================================
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower()
    if not user_message:
        return jsonify({"response": "Pesan kosong.", "includes_cards": False, "emotion": "neutral"})

    user_message_clean = user_message.strip()

    # SEMUA PESAN LANGSUNG MASUK KE AI
    raw_ai_response = ask_ai_barista(user_message_clean, dataset_menu)
    
    emotion = "neutral"
    ai_response = raw_ai_response

    if raw_ai_response:
        import re
        # Ekstrak tag emosi dari Gemini: [HAPPY], [SAD], dll.
        match = re.match(r'^\[(HAPPY|SAD|EXCITED|NEUTRAL)\](.*)', raw_ai_response.strip(), re.IGNORECASE | re.DOTALL)
        if match:
            emotion = match.group(1).lower()
            ai_response = match.group(2).strip()
        includes_cards_ai = False
        cards_data_ai = []
        coffee_name_ai = ""
        radar_data_ai = [0, 0, 0, 0]

        dataset_sorted = sorted(dataset_menu, key=lambda x: len(get_item_name(x)), reverse=True)
        for k in dataset_sorted:
            
            # 1. SCAN MENU UTAMA
            nama_menu = get_item_name(k)
            if nama_menu and len(nama_menu) > 2 and nama_menu.lower() in ai_response.lower():
                includes_cards_ai = True
                if not any(card['name'] == nama_menu for card in cards_data_ai):
                    cards_data_ai.append({"name": nama_menu, "img": get_item_image(k)})
                
                if not coffee_name_ai:
                    coffee_name_ai = nama_menu
                    radar_data_ai = [
                        k.get('profil_rasa', {}).get('manis', 0),
                        k.get('profil_rasa', {}).get('asam', 0),
                        k.get('profil_rasa', {}).get('pahit', 0),
                        k.get('profil_rasa', {}).get('pedas', 0)
                    ]

            # 2. SCAN ANAK CABANG MAKANAN
            rek_makanan = k.get('rekomendasi_makanan', {})
            nama_makanan = rek_makanan.get('nama_makanan', '')
            if nama_makanan and len(nama_makanan) > 2 and nama_makanan.lower() in ai_response.lower():
                includes_cards_ai = True
                if not any(card['name'] == nama_makanan for card in cards_data_ai):
                    gambar_makanan = rek_makanan.get('gambar_makanan') or '/static/Menukpk/Cireng.png'
                    cards_data_ai.append({"name": nama_makanan, "img": gambar_makanan})
                    
            # 3. SCAN ANAK CABANG MINUMAN
            rek_minuman = k.get('rekomendasi_minuman', {})
            nama_minuman = rek_minuman.get('nama_minuman', '')
            if nama_minuman and len(nama_minuman) > 2 and nama_minuman.lower() in ai_response.lower():
                includes_cards_ai = True
                if not any(card['name'] == nama_minuman for card in cards_data_ai):
                    gambar_minuman = rek_minuman.get('gambar_minuman') or '/static/Menukpk/Teh Es.png'
                    cards_data_ai.append({"name": nama_minuman, "img": gambar_minuman})

        return jsonify({
            "response": f"✨ <i>(AI Barista)</i><br><br>{ai_response}", 
            "includes_cards": includes_cards_ai,
            "cards": cards_data_ai,
            "coffee_name": coffee_name_ai,
            "radar_data": radar_data_ai,
            "emotion": emotion
        })

    return jsonify({
        "response": "Waduh, koneksi ke otak AI lagi terganggu nih. Coba tanya lagi sebentar ya!", 
        "includes_cards": False,
        "emotion": "sad"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)