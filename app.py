# Nama file: app.py
# Deskripsi: Aplikasi web Flask untuk pemesanan jasa fotografi dengan panel admin.
#
# Cara Menjalankan:
# 1. Pastikan Anda memiliki Python terinstal.
# 2. Instal Flask dengan membuka terminal atau command prompt dan ketik:
#    pip install Flask
# 3. Simpan kode ini sebagai file bernama `app.py`.
# 4. Jalankan aplikasi dengan mengetik di terminal:
#    python app.py
#    (Sebuah file database bernama `bookings.db` akan otomatis dibuat)
# 5. Buka browser Anda dan kunjungi http://127.0.0.1:5000
# 6. Untuk masuk ke halaman admin, kunjungi http://127.0.0.1:5000/admin (Password: admin123)

import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session, g

# Inisialisasi aplikasi Flask
app = Flask(__name__)
# Kunci rahasia diperlukan untuk menggunakan session (untuk login)
app.secret_key = 'kunci_rahasia_fotografi_anda'

DATABASE = 'bookings.db'

# --- FUNGSI DATABASE ---

def get_db():
    """Membuka koneksi baru jika belum ada untuk konteks saat ini."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Menutup koneksi database di akhir request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Inisialisasi database dan membuat tabel jika belum ada."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Membuat file schema.sql secara virtual
# Dalam proyek nyata, ini akan menjadi file terpisah.
schema_sql = """
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    email TEXT NOT NULL,
    telepon TEXT NOT NULL,
    tanggal_acara TEXT NOT NULL,
    layanan TEXT NOT NULL,
    pesan TEXT,
    status TEXT NOT NULL DEFAULT 'Baru',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""
# Menulis schema ke file agar bisa dibaca oleh init_db()
with open('schema.sql', 'w') as f:
    f.write(schema_sql)


# --- DATA PAKET FOTOGRAFI ---
PACKAGES = [
    {
        "id": "pernikahan",
        "name": "Paket Pernikahan",
        "description": "Abadikan setiap momen sakral di hari bahagia Anda dengan hasil yang sinematik dan tak terlupakan.",
        "price": "Mulai dari Rp 5.500.000",
        "features": ["8 Jam Liputan", "2 Fotografer", "1 Album Kolase Eksklusif", "Semua File Diberikan"],
        "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8 mb-4 text-pink-500"><path d="M20.42 4.58a5.4 5.4 0 0 0-7.65 0l-.77.77-.77-.77a5.4 5.4 0 0 0-7.65 0C2.46 6.51 2 8.6 2 10.5c0 3.86 3.42 8.58 10 11.5 6.58-2.92 10-7.64 10-11.5 0-1.9-.46-3.99-1.58-5.92z"></path></svg>"""
    },
    {
        "id": "prewedding",
        "name": "Paket Pre-Wedding",
        "description": "Ceritakan kisah cinta Anda melalui sesi foto pre-wedding yang kreatif dan personal di lokasi pilihan Anda.",
        "price": "Mulai dari Rp 2.800.000",
        "features": ["4 Jam Sesi Foto", "1 Fotografer", "25 Foto Edit Terbaik", "Cetak 2 Foto 16R"],
        "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8 mb-4 text-blue-500"><path d="M12 2a3.12 3.12 0 0 1 3 3.12V18a3.12 3.12 0 0 1-3 3.12v0a3.12 3.12 0 0 1-3-3.12V5.12A3.12 3.12 0 0 1 12 2z"></path><path d="M12 2a3.12 3.12 0 0 0-3 3.12V18a3.12 3.12 0 0 0 3 3.12v0a3.12 3.12 0 0 0 3-3.12V5.12A3.12 3.12 0 0 0 12 2z"></path><path d="M12 22a3.12 3.12 0 0 1 3-3.12V5.12a3.12 3.12 0 0 1-3-3.12v0a3.12 3.12 0 0 1-3 3.12v13.76A3.12 3.12 0 0 1 12 22z"></path><path d="M12 22a3.12 3.12 0 0 0 3-3.12V5.12a3.12 3.12 0 0 0-3-3.12v0a3.12 3.12 0 0 0-3 3.12v13.76A3.12 3.12 0 0 0 12 22z"></path></svg>"""
    },
    {
        "id": "acara",
        "name": "Paket Acara Spesial",
        "description": "Liputan untuk berbagai acara penting seperti ulang tahun, lamaran, atau acara perusahaan.",
        "price": "Mulai dari Rp 1.500.000",
        "features": ["3 Jam Liputan", "1 Fotografer", "75+ Foto Edit", "Link Google Drive"],
        "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8 mb-4 text-green-500"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>"""
    },
    {
        "id": "wisuda",
        "name": "Paket Wisuda",
        "description": "Rayakan kelulusan Anda dengan foto yang elegan dan penuh kenangan bersama keluarga dan teman.",
        "price": "Mulai dari Rp 1.500.000",
        "features": ["2 Jam Sesi Foto", "1 Fotografer", "20 Foto Edit Terbaik", "Cetak 1 Foto 12R + Frame"],
        "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8 mb-4 text-purple-500"><path d="M22 10v6M2 10l10-5 10 5-10 5z"></path><path d="M6 12v5c0 1.66 4 3 6 3s6-1.34 6-3v-5"></path></svg>"""
    }
]

# --- TEMPLATE HTML ---

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="id" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fotografi Profesional - Abadikan Momen Anda</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .hero-bg { background-image: linear-gradient(to right, rgba(0,0,0,0.6), rgba(0,0,0,0.2)), url('https://placehold.co/1600x900/a3a3a3/ffffff?text=Momen+Indah'); background-size: cover; background-position: center; }
    </style>
</head>
<body class="bg-gray-50 text-gray-800">
    <header class="bg-white/80 backdrop-blur-lg shadow-sm sticky top-0 z-50">
        <nav class="container mx-auto px-6 py-4 flex justify-between items-center">
            <a href="/" class="text-2xl font-bold text-gray-900">FotografiKu</a>
            <ul class="hidden md:flex items-center space-x-8">
                <li><a href="#layanan" class="text-gray-600 hover:text-blue-600 transition-colors">Layanan</a></li>
                <li><a href="#galeri" class="text-gray-600 hover:text-blue-600 transition-colors">Galeri</a></li>
                <li><a href="#pesan" class="bg-blue-600 text-white font-semibold px-5 py-2 rounded-full hover:bg-blue-700 transition-all">Pesan Sekarang</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section class="hero-bg text-white h-[60vh] md:h-[80vh] flex items-center">
            <div class="container mx-auto px-6">
                <h1 class="text-4xl md:text-6xl font-extrabold max-w-2xl leading-tight">Abadikan Momen Berharga Anda Secara Profesional</h1>
                <p class="mt-4 text-lg max-w-xl text-gray-200">Kami menyediakan jasa fotografi untuk pernikahan, pre-wedding, dan berbagai acara spesial dengan kualitas terbaik.</p>
                <a href="#pesan" class="mt-8 inline-block bg-blue-600 text-white font-bold px-8 py-3 rounded-full hover:bg-blue-700 transition-all text-lg">Hubungi Kami</a>
            </div>
        </section>
        <section id="layanan" class="py-20 bg-white">
            <div class="container mx-auto px-6 text-center">
                <h2 class="text-3xl md:text-4xl font-bold mb-4">Paket Layanan Kami</h2>
                <p class="text-gray-600 max-w-2xl mx-auto mb-12">Pilih paket yang paling sesuai dengan kebutuhan acara Anda. Kami siap memberikan hasil yang memuaskan.</p>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {% for pkg in packages %}
                    <div class="bg-gray-50 border border-gray-200 rounded-xl p-8 text-left flex flex-col hover:shadow-xl hover:-translate-y-2 transition-all duration-300">
                        <div class="flex-grow">
                            <div class="flex justify-center mb-4">{{ pkg.icon | safe }}</div>
                            <h3 class="text-2xl font-bold text-center mb-3">{{ pkg.name }}</h3>
                            <p class="text-gray-600 text-center mb-6">{{ pkg.description }}</p>
                            <ul class="space-y-3 mb-6">
                                {% for feature in pkg.features %}
                                <li class="flex items-center">
                                    <svg class="w-5 h-5 text-green-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                                    <span>{{ feature }}</span>
                                </li>
                                {% endfor %}
                            </ul>
                        </div>
                        <p class="text-center text-xl font-semibold text-blue-600 mt-auto">{{ pkg.price }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </section>
        <section id="galeri" class="py-20">
            <div class="container mx-auto px-6 text-center">
                <h2 class="text-3xl md:text-4xl font-bold mb-12">Galeri Portofolio</h2>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="grid gap-4">
                        <div><img class="h-auto max-w-full rounded-lg shadow-md transition-transform duration-300 hover:scale-105" src="https://placehold.co/500x700/e2e8f0/334155?text=Foto+1" alt="Foto Pernikahan"></div>
                        <div><img class="h-auto max-w-full rounded-lg shadow-md transition-transform duration-300 hover:scale-105" src="https://placehold.co/500x500/e2e8f0/334155?text=Foto+2" alt="Foto Pre-wedding"></div>
                    </div>
                    <div class="grid gap-4">
                        <div><img class="h-auto max-w-full rounded-lg shadow-md transition-transform duration-300 hover:scale-105" src="https://placehold.co/500x500/e2e8f0/334155?text=Foto+3" alt="Foto Acara"></div>
                        <div><img class="h-auto max-w-full rounded-lg shadow-md transition-transform duration-300 hover:scale-105" src="https://placehold.co/500x800/e2e8f0/334155?text=Foto+4" alt="Detail Foto"></div>
                    </div>
                    <div class="grid gap-4">
                        <div><img class="h-auto max-w-full rounded-lg shadow-md transition-transform duration-300 hover:scale-105" src="https://placehold.co/500x750/e2e8f0/334155?text=Foto+5" alt="Momen Spesial"></div>
                        <div><img class="h-auto max-w-full rounded-lg shadow-md transition-transform duration-300 hover:scale-105" src="https://placehold.co/500x500/e2e8f0/334155?text=Foto+6" alt="Candid Shot"></div>
                    </div>
                    <div class="grid gap-4">
                        <div><img class="h-auto max-w-full rounded-lg shadow-md transition-transform duration-300 hover:scale-105" src="https://placehold.co/500x500/e2e8f0/334155?text=Foto+7" alt="Outdoor Shot"></div>
                        <div><img class="h-auto max-w-full rounded-lg shadow-md transition-transform duration-300 hover:scale-105" src="https://placehold.co/500x600/e2e8f0/334155?text=Foto+8" alt="Indoor Shot"></div>
                    </div>
                </div>
            </div>
        </section>
        <section id="pesan" class="py-20 bg-white">
            <div class="container mx-auto px-6">
                <div class="max-w-2xl mx-auto text-center">
                    <h2 class="text-3xl md:text-4xl font-bold mb-4">Pesan Jasa Kami</h2>
                    <p class="text-gray-600 mb-8">Isi formulir di bawah ini untuk konsultasi atau pemesanan. Tim kami akan segera menghubungi Anda.</p>
                </div>
                <form action="/submit" method="post" class="max-w-2xl mx-auto bg-gray-50 p-8 rounded-xl shadow-lg border border-gray-200">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        <div>
                            <label for="nama" class="block text-sm font-medium text-gray-700 mb-1">Nama Lengkap</label>
                            <input type="text" id="nama" name="nama" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500">
                        </div>
                        <div>
                            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Alamat Email</label>
                            <input type="email" id="email" name="email" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500">
                        </div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        <div>
                            <label for="telepon" class="block text-sm font-medium text-gray-700 mb-1">Nomor Telepon (WhatsApp)</label>
                            <input type="tel" id="telepon" name="telepon" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500">
                        </div>
                        <div>
                            <label for="tanggal_acara" class="block text-sm font-medium text-gray-700 mb-1">Tanggal Acara</label>
                            <input type="date" id="tanggal_acara" name="tanggal_acara" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500">
                        </div>
                    </div>
                    <div class="mb-6">
                        <label for="layanan" class="block text-sm font-medium text-gray-700 mb-1">Pilih Layanan</label>
                        <select id="layanan" name="layanan" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500">
                            <option value="">-- Pilih salah satu --</option>
                            {% for pkg in packages %}
                            <option value="{{ pkg.id }}">{{ pkg.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-6">
                        <label for="pesan" class="block text-sm font-medium text-gray-700 mb-1">Pesan Tambahan</label>
                        <textarea id="pesan" name="pesan" rows="4" class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500" placeholder="Jelaskan kebutuhan Anda secara singkat..."></textarea>
                    </div>
                    <div>
                        <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 transition-all text-lg">Kirim Permintaan</button>
                    </div>
                </form>
            </div>
        </section>
    </main>
    <footer class="bg-gray-800 text-white py-10">
        <div class="container mx-auto px-6 text-center">
            <p>&copy; 2025 FotografiKu. Semua Hak Cipta Dilindungi.</p>
        </div>
    </footer>
</body>
</html>
"""

SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Permintaan Terkirim!</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; } </style>
</head>
<body class="bg-gray-100 flex items-center justify-center h-screen">
    <div class="text-center bg-white p-12 rounded-xl shadow-2xl max-w-lg mx-auto">
        <svg class="w-20 h-20 text-green-500 mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <h1 class="text-3xl font-bold text-gray-900 mb-3">Terima Kasih!</h1>
        <p class="text-gray-600 text-lg mb-8">Permintaan pemesanan Anda telah berhasil kami terima. Tim kami akan segera menghubungi Anda melalui email atau WhatsApp untuk konfirmasi lebih lanjut.</p>
        <a href="/" class="bg-blue-600 text-white font-semibold px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">Kembali ke Halaman Utama</a>
    </div>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style> body { font-family: 'Inter', sans-serif; } </style>
</head>
<body class="bg-gray-100 flex items-center justify-center h-screen">
    <div class="w-full max-w-md">
        <form action="/admin/login" method="post" class="bg-white shadow-2xl rounded-xl px-8 pt-6 pb-8 mb-4">
            <h1 class="text-3xl font-bold text-center mb-6 text-gray-800">Admin Login</h1>
            {% if error %}
                <p class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">{{ error }}</p>
            {% endif %}
            <div class="mb-6">
                <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                    Password
                </label>
                <input class="shadow-sm appearance-none border rounded-lg w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500" id="password" name="password" type="password" placeholder="******************">
            </div>
            <div class="flex items-center justify-between">
                <button class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:shadow-outline" type="submit">
                    Sign In
                </button>
            </div>
        </form>
    </div>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Admin - Pesanan Fotografi</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .status-baru { background-color: #e0f2fe; color: #0c4a6e; }
        .status-dikonfirmasi { background-color: #dcfce7; color: #166534; }
        .status-selesai { background-color: #e5e7eb; color: #4b5563; }
        .status-dibatalkan { background-color: #fee2e2; color: #991b1b; }
    </style>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto p-4 sm:p-6 lg:p-8">
        <header class="flex justify-between items-center mb-8">
            <h1 class="text-4xl font-bold text-gray-800">Dashboard Pesanan</h1>
            <a href="/admin/logout" class="bg-red-600 text-white font-semibold px-5 py-2 rounded-lg hover:bg-red-700 transition-colors">Logout</a>
        </header>
        
        <div class="bg-white rounded-xl shadow-lg overflow-hidden">
            <div class="overflow-x-auto">
                <table class="min-w-full text-sm text-left text-gray-600">
                    <thead class="text-xs text-gray-700 uppercase bg-gray-100">
                        <tr>
                            <th scope="col" class="px-6 py-3">ID</th>
                            <th scope="col" class="px-6 py-3">Pelanggan</th>
                            <th scope="col" class="px-6 py-3">Kontak</th>
                            <th scope="col" class="px-6 py-3">Detail Acara</th>
                            <th scope="col" class="px-6 py-3">Status</th>
                            <th scope="col" class="px-6 py-3">Aksi</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if not orders %}
                        <tr>
                            <td colspan="6" class="text-center py-10 text-gray-500">Belum ada pesanan yang masuk.</td>
                        </tr>
                        {% endif %}
                        {% for order in orders %}
                        <tr class="bg-white border-b hover:bg-gray-50">
                            <td class="px-6 py-4 font-medium text-gray-900">#{{ order.id }}</td>
                            <td class="px-6 py-4">
                                <div class="font-semibold">{{ order.nama }}</div>
                                <div class="text-xs text-gray-500">{{ order.email }}</div>
                            </td>
                            <td class="px-6 py-4">{{ order.telepon }}</td>
                            <td class="px-6 py-4">
                                <div class="font-semibold">{{ order.layanan }}</div>
                                <div class="text-xs text-gray-500">Tgl: {{ order.tanggal_acara }}</div>
                            </td>
                            <td class="px-6 py-4">
                                <span class="px-2 py-1 font-semibold leading-tight rounded-full text-xs status-{{ order.status | lower }}">
                                    {{ order.status }}
                                </span>
                            </td>
                            <td class="px-6 py-4">
                                <form action="/admin/update_status/{{ order.id }}" method="post" class="flex items-center gap-2">
                                    <select name="status" class="border-gray-300 rounded-md shadow-sm text-xs focus:ring-blue-500 focus:border-blue-500">
                                        <option value="Baru" {% if order.status == 'Baru' %}selected{% endif %}>Baru</option>
                                        <option value="Dikonfirmasi" {% if order.status == 'Dikonfirmasi' %}selected{% endif %}>Dikonfirmasi</option>
                                        <option value="Selesai" {% if order.status == 'Selesai' %}selected{% endif %}>Selesai</option>
                                        <option value="Dibatalkan" {% if order.status == 'Dibatalkan' %}selected{% endif %}>Dibatalkan</option>
                                    </select>
                                    <button type="submit" class="bg-blue-500 text-white px-3 py-1 rounded-md text-xs font-semibold hover:bg-blue-600">Update</button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- ROUTING APLIKASI ---

@app.route('/')
def home():
    """Menampilkan halaman utama."""
    return render_template_string(HOME_TEMPLATE, packages=PACKAGES)

@app.route('/submit', methods=['POST'])
def submit():
    """Menyimpan data dari formulir ke database."""
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        telepon = request.form['telepon']
        tanggal_acara = request.form['tanggal_acara']
        layanan_id = request.form['layanan']
        pesan = request.form['pesan']

        nama_layanan = next((pkg['name'] for pkg in PACKAGES if pkg['id'] == layanan_id), "Tidak Ditemukan")
        
        db = get_db()
        db.execute(
            'INSERT INTO bookings (nama, email, telepon, tanggal_acara, layanan, pesan) VALUES (?, ?, ?, ?, ?, ?)',
            (nama, email, telepon, tanggal_acara, nama_layanan, pesan)
        )
        db.commit()
        
        return redirect(url_for('success'))

@app.route('/success')
def success():
    """Menampilkan halaman konfirmasi."""
    return render_template_string(SUCCESS_TEMPLATE)

# --- ROUTING ADMIN ---

@app.route('/admin')
def admin_dashboard():
    """Menampilkan dashboard admin dengan semua pesanan."""
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    db = get_db()
    orders = db.execute('SELECT * FROM bookings ORDER BY timestamp DESC').fetchall()
    return render_template_string(ADMIN_TEMPLATE, orders=orders)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Menangani proses login admin."""
    error = None
    if request.method == 'POST':
        # Password sederhana, dalam aplikasi nyata gunakan hashing
        if request.form['password'] == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Password salah, silakan coba lagi.'
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/admin/logout')
def admin_logout():
    """Menangani proses logout admin."""
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    """Memperbarui status pesanan."""
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
        
    status = request.form['status']
    db = get_db()
    db.execute('UPDATE bookings SET status = ? WHERE id = ?', (status, order_id))
    db.commit()
    return redirect(url_for('admin_dashboard'))


# Menjalankan aplikasi
if __name__ == '__main__':
    init_db() # Inisialisasi database saat aplikasi pertama kali dijalankan
    app.run(debug=True)
