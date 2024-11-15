import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# Menambahkan logo
st.image("log.png", width=200)  # Sesuaikan dengan nama dan ukuran logo Anda

# Set judul halaman
st.title("ANEMIATOOR")

# Mengubah background menjadi warna lemon
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #FFF700;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fungsi untuk melatih dan membuat model RandomForest
def train_model():
    # Asumsi data latihan tersedia dalam file CSV 'anemia.csv'
    data = pd.read_csv('anemia.csv.csv')
    le = LabelEncoder()
    data['Gender'] = le.fit_transform(data['Gender'])  # Encode Gender menjadi numerik
    X = data[['Hb_Level', 'Age', 'Gender']]  # Fitur yang digunakan untuk prediksi
    y = data['Anemia']  # Label target

    # Membagi data menjadi data latih dan data uji
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Membuat dan melatih model RandomForest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Menghitung akurasi pada data uji
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    return model, accuracy

# Fungsi untuk memprediksi menggunakan model yang telah dilatih
def predict(model, input_data):
    return model.predict(input_data)

# Halaman prediksi (hanya jika sudah login)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Fungsi login sederhana
def login(username, password):
    return username == "admin" and password == "admin"

# Halaman login
if not st.session_state['logged_in']:
    st.write("Silakan login terlebih dahulu.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(username, password):
            st.session_state['logged_in'] = True  # Menyimpan status login di session state
            st.success("Login berhasil!")
        else:
            st.error("Login gagal. Silakan periksa username dan password Anda.")

# Halaman prediksi (hanya terlihat jika sudah login)
if st.session_state['logged_in']:
    st.title("SISTEM PREDIKSI PENYAKIT ANEMIA")

    # Menampilkan informasi tentang anemia
    st.subheader("Apa itu Anemia?")
    st.write("""Anemia adalah kondisi medis di mana tubuh kekurangan sel darah merah atau hemoglobin. Hemoglobin adalah protein yang membawa oksigen ke seluruh tubuh. Kondisi ini dapat menyebabkan kelelahan, pusing, dan gejala lainnya. Anemia dapat disebabkan oleh berbagai faktor, termasuk kekurangan zat besi, vitamin, atau penyakit tertentu.""")

    # Mengunggah file CSV untuk prediksi massal
    st.subheader("Unggah File CSV untuk Prediksi Massal")
    uploaded_file = st.file_uploader("Unggah file CSV", type=["csv"])

    # Jika ada file yang diunggah, proses file tersebut
    if uploaded_file is not None:
        try:
            # Membaca file CSV yang diunggah
            df = pd.read_csv(uploaded_file)

            # Menampilkan beberapa baris pertama dari data yang diunggah
            st.write("Data yang diunggah:")
            st.dataframe(df.head())

            # Memeriksa apakah kolom yang diperlukan ada dalam dataset
            if all(col in df.columns for col in ['Hb_Level', 'Age', 'Gender', 'Anemia']):
                # Encode Gender menjadi numerik
                le = LabelEncoder()
                df['Gender'] = le.fit_transform(df['Gender'])

                # Menyiapkan data untuk prediksi
                input_data = df[['Hb_Level', 'Age', 'Gender']]
                true_labels = df['Anemia']  # Kolom target (Anemia)

                # Melatih model setiap kali aplikasi dijalankan
                model, accuracy = train_model()

                # Melakukan prediksi untuk semua baris data
                predictions = predict(model, input_data)

                # Menambahkan hasil prediksi ke data asli
                df['Prediksi Anemia'] = predictions

                # Menampilkan hasil prediksi
                st.write("Hasil Prediksi:")
                st.dataframe(df)

                # Menampilkan akurasi model
                st.write(f"Akurasi Model: {accuracy * 100:.2f}%")
            else:
                st.error("File CSV tidak memiliki kolom yang diperlukan (Hb_Level, Age, Gender, Anemia). Pastikan file Anda sesuai format.")
        except Exception as e:
            st.error(f"Terjadi kesalahan dalam memproses file: {e}")

    # Input data pengguna untuk prediksi individual
    st.subheader("PPREDIKSI PENYAKIT ANEMIA")
    hb_level = st.number_input("Masukkan kadar Hemoglobin (g/dL):", min_value=0.0, max_value=20.0, step=0.1)
    age = st.number_input("Masukkan umur:", min_value=0, max_value=100, step=1)
    gender = st.selectbox("Pilih jenis kelamin:", ["Female", "Male"])
    gender_numeric = 1 if gender == "Male" else 0

    # Data input pengguna dalam bentuk DataFrame
    input_data = pd.DataFrame([[hb_level, age, gender_numeric]], columns=['Hb_Level', 'Age', 'Gender'])

    # Melatih model setiap kali aplikasi dijalankan
    model, accuracy = train_model()

    # Prediksi saat tombol ditekan
    if st.button("Prediksi"):
        prediction = predict(model, input_data)
        if prediction[0] == 0:
            st.write("Hasil Prediksi: Tidak mengalami anemia.")
            st.write("Tetaplah menjaga gaya hidup sehat agar tubuh selalu fit dan bebas dari risiko anemia atau masalah kesehatan lainnya.")
        else:
            st.write("Hasil Prediksi: Mengalami anemia.")
            st.write("Sebaiknya segera berkonsultasi dengan dokter untuk mendapatkan penanganan yang tepat. Konsumsi makanan kaya zat besi, perbanyak vitamin C, dan hindari alkohol berlebihan.")

    # Tombol Logout setelah prediksi
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()  # Menggunakan st.rerun() untuk memuat ulang halaman
