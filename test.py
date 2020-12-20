# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 08:57:09 2020

@author: Agung
"""
import inageoparser

#%%
test = """
Kali Ciliwung Meluap, 17 RW di 8 Kelurahan Jakarta Terendam Banjir

Sebanyak 17 RW yang tersebar di delapan kelurahan di Jakarta terendam banjir pada Selasa (19/5/2020) pagi
Ketinggian air antara 10 sentimeter sampai 100 sentimeter

Kepala Pusat Data dan Informasi Kebencanaan Badan Penanggulangan Bencana Daerah (BPBD) Jakarta M Insaf mengatakan, banjir disebabkan luapan Kali Ciliwung
 "Update pukul 03.00 WIB, ada 17 RW tergenang akibat luapan Kali Ciliwung," ujar Insaf saat dikonfirmasi
 Akibat banjir tersebut, ada 128 warga di Kelurahan Balekambang, Jakarta Timur, yang mengungsi di dua lokasi
 "Pengungsi 38 KK (kepala keluarga) dengan 128 jiwa, pos pengungsian dua lokasi di Balekambang," kata Insaf
 Berikut rincian banjir yang terjadi di Jakarta pada Selasa pagi ini:

4 RW di Kelurahan Kampung Melayu, Jakarta Timur, ketinggian air 10-50 sentimeter
2 RW di Kelurahan Bidara Cina, Jakarta Timur, ketinggian air 30-100 sentimeter
6 RW di Kelurahan Cawang, Jakarta Timur, ketinggian air 20-150 sentimeter
1 RW di Kelurahan Balekambang, Jakarta Timur, ketinggian air 40-100 sentimeter
1 RW di Kelurahan Pejaten Timur, Jakarta Selatan, ketinggian air 100 sentimeter
1 RW di Kelurahan Kebon Baru, Jakarta Selatan, ketinggian air 50 sentimeter
1 RW di Kelurahan Manggarai, Jakarta Selatan, ketinggian air 50 sentimeter
1 RW Kelurahan Pengadegan, Jakarta Selatan, ketinggian air 10-50 sentimeter

"""
load_crf()
predict(test)

t1 = """
Corona di Banten 804 Kasus, Angka PDP dan ODP Turun -- Serang - Pasien terkonfirmasi Corona di Banten hari ini bertambah delapan orang. Sehingga keseluruhan angka positif jadi 804 kasus, 343 sudah sembuh dan 67 di antaranya meninggal dunia. Data yang disampaikan oleh Gugus Tugas Percepatan Penanganan COVID-19 pada pukul 18.00 WIB ini menunjukkan bahwa ada tren penurunan angka Pasien Dalam Pengawasan (PDP) dan Orang Dalam Pemantauan (ODP). Jumlah PDP turun drastis dari sebelumnya yang selalu bertambah puluhan orang, tapi hari ini hanya ada tambahan 7 pasien. Total PDP kemudian menjadi 2.413 orang. Rinciannya 1.095 sudah sembuh dan 268 meninggal dunia. Begitu pun dengan ODP yang biasanya bertambah sampai puluhan orang, maka hari ini hanya bertambah empat. Catatannya, ODP keseluruhan berjumlah 8.952 dan tinggal 963 yang masih dipantau oleh tim kesehatan di masing-masing daerah. Adapun dari 8 penambahan pasien positif terjadi di Kota Tangerang tiga pasien sehingga total ada 359 kasus di daerah ini. Kedua, pasien bertambah di Kabupaten Tangerang sebanyak 5 orang sehingga total ada 184 kasus. Sebagai catatan, daerah Tangerang Selatan (Tangsel) yang jadi salah satu episentrum Corona di Banten sejak Kamis (28/5) tak ada penambahan jumlah kasus. Daerah ini masih melaporkan angka kasus terpapar sebanyak 230 pasien. Selain Tangsel, beberapa hari ini pun daerah seperti Kota Serang angka pasien positif masih 11 kasus. Kabupaten Serang 10 kasus, Kota Cilegon 5 kasus, Pandeglang 3 kasus dan Lebak ada 2 kasus.
"""



t1 = """

Bandung -- Tiga pria di Kota Bandung yang berboncengan satu motor tewas menabrak trotoar
Insiden nahas itu terjadi Senin (30/7/2018) dini hari pukul 02.10 WIB di Jalan Kopo tepatnya di depan Rumah Sakit Immanuel, Kota Bandung
Satu pengemudi yang belum diketahui identitasnya meninggal dunia di TKP
Sementara dua lainnya tewas di rumah sakit

"Awalnya hanya satu orang yang meninggal 
Tetapi saat ini sudah tiga orang yang meninggal dunia," ucap Kasatlantas Polrestabes Bandung AKBP Agung Reza Pratidina saat dikonfirmasi via pesan singkat
Agung menuturkan, peristiwa tersebut berawal saat korban mengendarai sepeda motor jenis bebek dengan membonceng dua rekannya
Saat tiba di Jalan Kopo depan Rumah Sakit Immanuel, motor yang dikendarai oleng hingga menabrak trotoar dan menabrak pohon
"Mereka datang dari arah Dago
Saat di Tempat Kejadian Perkara (TKP) atau di jalan umum, pengemudi tidak dapat menguasai kendaraanya dengan wajar, sehingga menabrak," katanya
Pengemudi tewas di TKP
Sementara dua temannya yakni Kurniawan dan satu lagi belum diketahui identitasnya, meninggal di rumah sakit
"Mereka berboncengan tiga," kata Agung

"""

t2 = """

Bandung -- Kecelakaan mobil yang terjadi di Lengkong, Bandung, melibatkan truk dari Sumedang dengan dua mobil lokal
Kecelakaan tersebut menewaskan 2 orang dan 2 orang terluka

"""