from pyparsing import col
import streamlit as st
from supabase import create_client

# 1. Setup
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

# 1. Sidebar Navigasi
role = st.sidebar.selectbox("Login Sebagai:", ["Pelanggan", "Owner Resto"])

if role == "Pelanggan":
    st.title("🍜 Selamat Datang di Resto Kami")
    # --- KODE HALAMAN PELANGGAN LU DI SINI ---
    st.title("🍜 Menu dan Pemesanan")

        # 2. Tampilkan Menu (Read)
    st.subheader("Daftar Menu")
    response = supabase.table("menu_resto").select("id, item_name, price, description, image_url").execute()
        
    jumlah_kolom = 3
    cols = st.columns(jumlah_kolom)

    import streamlit as st

# 1. Inisialisasi Keranjang di awal (biar gak error pas pertama buka)
if 'keranjang' not in st.session_state:
    st.session_state.keranjang = {} # Isinya: {id_menu: jumlah}

# --- Loop Menu Lu yang Tadi ---
for index, item in enumerate(response.data):
    col = cols[index % jumlah_kolom]
    menu_id = item['id']
    
    with col:
        with st.container(border=True):
            st.image(item['image_url'], width='stretch')
            st.markdown(f"**{item['item_name']}**")
            st.caption(f"Rp {item['price']:,}")
            
            # 2. Bikin baris buat tombol + - dan angka jumlah
            c1, c2, c3 = st.columns([1, 1, 1])
            
            # Ambil jumlah saat ini dari session_state
            qty = st.session_state.keranjang.get(menu_id, 0)
            
            with c1:
                if st.button("➖", key=f"min_{menu_id}"):
                    if qty > 0:
                        st.session_state.keranjang[menu_id] = qty - 1
                        st.rerun() # Refresh biar angkanya langsung ganti

            with c2:
                st.markdown(f"<h4 style='text-align: center;'>{qty}</h4>", unsafe_allow_html=True)

            with c3:
                if st.button("➕", key=f"plus_{menu_id}"):
                    st.session_state.keranjang[menu_id] = qty + 1
                    st.rerun()
st.divider()
st.header("🛒 Keranjang Belanja")

total_bayar = 0
pesanan_final = []

for m_id, jml in st.session_state.keranjang.items():
    if jml > 0:
        # Cari info menu (nama & harga) berdasarkan ID
        detail = next(m for m in response.data if m['id'] == m_id)
        subtotal = jml * detail['price']
        total_bayar += subtotal
        
        st.write(f"✅ {detail['item_name']} x {jml} = **Rp {subtotal:,}**")
        pesanan_final.append({"menu_id": m_id, "jumlah": jml, "subtotal": subtotal})
        
if total_bayar > 0:
    st.subheader(f"Total: Rp {total_bayar:,}")
    nama_pembeli = st.text_input("Nama Kamu:")
    
    if st.button("🚀 Kirim Pesanan ke Dapur"):

        header_res = supabase.table("pesanan").insert({
                "customer_name": nama_pembeli,
                "total_harga": total_bayar
            }).execute()
        
        for item in pesanan_final:
            m_id = item['menu_id']
            qty = item['jumlah']
            total_per_item = item['subtotal']
            order_id = header_res.data[0]['id_pesanan']  # Ambil ID pesanan yang baru dibuat
            
            supabase.table("pesanan_detail").insert({
                "id_pesanan": order_id,
                "customer_name": nama_pembeli, 
                "menu_id": m_id,
                "jumlah": qty,
                "total_harga": total_per_item
            }).execute()

        # DI SINI LOGIC INSERT KE SUPABASE (Header & Detail)
        # Abis itu jangan lupa kosongin keranjang:
        st.session_state.keranjang = {}
        st.success("Pesanan meluncur, bro!")
else:
    st.info("Belum ada menu yang dipilih. Yuk jajan!")



    
# else:
#     # 2. Proteksi Halaman Owner
#         st.title("📊 Login Owner")
#         password = st.sidebar.text_input("Masukkan Password Owner:", type="password")
    
#     # Password-nya lu tentuin sendiri di sini, misal "admin123"
#         if password == "vidd4869":
#             st.success("Welcome, Owner!")
#             st.subheader("Dashboard Penjualan")
#             # --- KODE HALAMAN OWNER (OMZET, DLL) DI SINI ---
#             data_pesanan = supabase.table("pesanan").select(
#                 "id_pesanan, customer_name, total_harga)"
#             ).execute()

#             for p in data_pesanan.data:
#                 st.markdown(f"**Pesanan ID:** {p['id_pesanan']} - **Customer:** {p['customer_name']} - **Total Harga:** Rp {p['total_harga']}")
#                 st.markdown("---")

#             total_omzet = sum(p['total_harga'] for p in data_pesanan.data)
#             st.metric("Total Omzet", f"Rp {total_omzet}")

#             #filter omzet perhari atau perbulan
#             periode = st.selectbox("Pilih Periode:", ["Harian", "Bulanan"])
#             if periode == "Harian":
#                 st.subheader("Omzet per Hari")
#                 data_omzet_harian = supabase.table("pesanan").select(
#                     "date_time, total_harga"
#                 ).execute()

#                 omzet_per_hari = {}
#                 for p in data_omzet_harian.data:
#                     tanggal = p['date_time'][:28]  # Ambil bagian tanggal (YYYY-MM-DD)
#                     total_harga = p['total_harga']
#                     if tanggal in omzet_per_hari:
#                         omzet_per_hari[tanggal] += total_harga
#                     else:
#                         omzet_per_hari[tanggal] = total_harga
#                 tanggal_list = list(omzet_per_hari.keys())
#                 omzet_list = list(omzet_per_hari.values())
#                 st.bar_chart(data={"Tanggal": tanggal_list, "Omzet": omzet_list})
#             else:
#                 st.subheader("Omzet Bulan Ini")
#                 data_omzet_bulanan = supabase.table("pesanan").select(
#                     "date_time, total_harga"
#                 ).execute()
#                 omzet_per_bulan = {}
#                 for p in data_omzet_bulanan.data:
#                     bulan = p['date_time'][0:3]  # Ambil bagian bulan (MM)
#                     total_harga = p['total_harga']
#                     if bulan in omzet_per_bulan:
#                         omzet_per_bulan[bulan] += total_harga
#                     else:
#                         omzet_per_bulan[bulan] = total_harga
#                 bulan_list = list(omzet_per_bulan.keys())
#                 omzet_bulan_list = list(omzet_per_bulan.values())
#                 st.bar_chart(data={"Bulan": bulan_list, "Omzet": omzet_bulan_list})


#             total_pesanan = len(set(p['id_pesanan'] for p in data_pesanan.data))
#             st.metric("Total Pesanan", total_pesanan)


# elif password == "":
#         st.warning("Silakan masukkan password di sidebar.")
# else: 
#         st.error("Lau Sape Mpruy?")
  

 