import os, json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()

with open('menu.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

menu_context = ""
for item in dataset:
    nama = item.get("nama_makanan") or item.get("nama_minuman") or item.get("nama_kopi") or ""
    harga = item.get("harga", 0)
    desc = item.get("deskripsi_edukasi", "")
    pr = item.get('profil_rasa', {})
    manis = pr.get('manis', 0)
    asam = pr.get('asam', 0)
    pahit = pr.get('pahit', 0)
    pedas = pr.get('pedas', 0)
    if nama:
        menu_context += f"- {nama} (Rp{harga}): {desc} [Rasa: Manis {manis}/10, Asam {asam}/10, Pahit {pahit}/10, Pedas {pedas}/10]\n"

print(f"Length of menu_context in chars: {len(menu_context)}")

system_prompt = f"""Kamu adalah Virtual Barista yang ramah, asik, dan berwawasan di 'Warung Kopi KPK' Padang.

ATURAN WAJIB (GUARDRAILS):
1. HANYA rekomendasikan menu dari daftar di bawah. JANGAN PERNAH menyarankan menu dari tempat lain.
2. Jika pelanggan bertanya hal di luar kopi/makanan (misal: politik, cuaca umum, coding), arahkan kembali dengan sopan ke menu kopi KPK.
3. Gunakan bahasa Indonesia yang santai, gaul mahasiswa, tapi tetap sopan. Jangan terlalu kaku.
4. Jawab singkat (maksimal 3-4 kalimat) dan sebutkan SEMUA menu yang sesuai dengan permintaan pelanggan.
5. ATURAN REKOMENDASI (SANGAT PENTING):
   - Jika pelanggan meminta profil rasa tertentu (misal: "semua makanan pedas", "minuman manis"), sebutkan SEMUA menu di daftar yang punya skor tinggi (>5) di rasa tersebut. Jangan dibatasi hanya 2! Sebutkan saja semuanya (bisa 4-6 menu).
   - Jika pelanggan SPESIFIK minta MAKANAN saja, rekomendasikan HANYA makanan/snack. JANGAN tambahkan minuman.
   - Jika pelanggan SPESIFIK minta MINUMAN saja, rekomendasikan HANYA minuman. JANGAN tambahkan makanan.
   - Jika pelanggan curhat tanpa menyebut kategori spesifik, rekomendasikan 1 Minuman DAN 1 Makanan secara bersamaan.
6. Pastikan kamu menyebutkan nama menu persis sesuai huruf yang ada di daftar.
7. Di AWAL jawabanmu, WAJIB sertakan tag emosi yang sesuai dengan curhatan atau emosi pelanggan. Pilih salah satu tag ini: [HAPPY], [SAD], [EXCITED], atau [NEUTRAL].
   Format wajib: [TAG_EMOSI] Jawaban barista...

DAFTAR MENU WARUNG KOPI KPK:
{menu_context}"""

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "test"}
        ],
        temperature=0.7,
        max_tokens=512,
    )
    print("API Call Success!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"API Call Failed: {e}")
