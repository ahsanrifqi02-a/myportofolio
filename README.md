### Tugas Individu PBP

Nama : Ahsan Rifqi Prasetyo
NPM : 2506624266
Kelas : PBP F

### Tugas 1

1. Saya menggunakan berbagai macam elemen semantik seperti <article>, <section>, dan <nav>. Hal ini memudahkan saya dalam membagi website ke beberapa section dan elemen tersebut memudahkan saya menavigasi bagian yang akan saya modify.
2. Tantangan yang saya temukan adalah nav-bar yang overlapping ketika saya mengecilkan width screennya, sehingga saya mendapatkan solusi yaitu dengan menggunakan menu drop-down yang muncul ketika berada di mobile.
3. Batasan utama web statis adalah maintenance overhead karena setiap penambahan proyek atau pengalaman baru mengharuskan kita mengedit kode HTML secara manual dan melakukan deploy ulang. Untuk mengatasinya pada iterasi berikutnya, fungsionalitas dinamis yang paling ideal ditambahkan adalah sistem manajemen data berbasis database (arsitektur Model–Template–Views/MTV pada Django) yang terhubung dengan antarmuka admin atau form input, di mana data project dan experience disimpan di database lalu dirender secara otomatis ke template HTML menggunakan perulangan tanpa perlu mengubah struktur kode maupun styling CSS-nya lagi.

AI disclosure
Dalam pembuatan tugas ini, saya menggunakan Gemini AI sebagai asisten untuk membuat struktur awal sehingga saya dapat memodifikasinya dengan preferensi saya sendiri dan untuk mengajarkan saya tentang fitur media query serta keyframes untuk responsivitas web sehingga navbar berubah ketika screen widthnya mencapai threshold tertentu. Fitur keyframes digunakan untuk membuat text animation yang di implementasikan di bagian hero sehingga lebih menarik.

Bagian yang di build dengan AI sudah di comment dan dapat dilihat langsung di index.html dan style.css.


### Tugas 2

1. Pertama, ada permintaan masuk (HTTP Request) lalu browser mengirimkan url ke server Django. 
- Peran yang di handle oleh urls.py (di portofolio) yang bertindak sebagai gate pertama dan memeriksa daftar (urlpatterns) global, ketika melihat request tanpa prefix khusus sistem akan meneruskan route ke modul URL dengan fungsi (include('main.urls'))
- Peran yang di handle oleh urls.py (di main) yang bertindak sebagai pengatur route internal aplikasi. Sistem Django mencocokkan path (mis. skills/) dengan named route (show_skills), ketika cocok akan memanggil fungsi views.show_skills.
- Peran views.py sebagai controller yang berisi fungsi yang menerima request dan mengeksekusi fungsi untuk mengambil data dari database.
- Peran models.py adalah untuk mendefinisikan struktur data tabel di database. File ini menerima query yang akan dieksekusi ke databse lalu me-return data dalam bentuk objek.
- Peran template adalah sebagai layer untuk user interface agar terlihat oleh user. Template berisi iterasi yang akan memanggil method dan merender suatu data yang di return, serta menghandle section yang empty.
2. Karena dengan menyimpan data pada model akan memberikan kemudahan dalam beberapa hal seperti skalabilitas, hal ini dikarenakan ketika template di hardcode akan menyebabkan beberapa inkonsistensi, misal tidak ada data yang ditampilkan atau data baru yang ditampilkan harus ditambah secara langsung di template. Jika menggunakan model kita dapat menghandle data baru yang baru saja ditambahkan dengan menggunakan iterasi dan kita juga dapat menghandle ketika data tidak ada menggunakan empty state. Separation of Concerns, hal ini membuat template html berfokus kepada struktur tampilan visual dan tata letak web dan data dikelola di basis data.
3. Perbedaan makemigrations dan migrate terletak pada fungsinya. 
- Fungsi makemigrations untuk memeriksa dan mendeteksi perbuahan yang kita buat pada file models.py. Command ini hanya mencatat rancangan instruksi perubahan skema struktur di database. Ketika command ini dilakukan maka akan menyusun migrations yang berisi mis. 0002_skills.py.
- Fungsi migrate untuk membaca file migrasi yang belum diaplikasikan dan mengexecute instruksi SQL ke database. Mengubah skema database secara langsung dan mencata riwayat eksekusi pada (django_migrations) agar migrasi yang sama tidak dijalankan ulang. Django akan mengambil file migrasi mis. 0002_skills.py dan menerjemahkan menjadi query SQL, lalu dimasukkan di db.sqlite3 dan dicatat agar tidak diexecute dua kali. 

AI Disclosure
Dalam pembuatan tugas ini, saya menggunakan Gemini AI sebagai asisten untuk membantu saya mengajarkan bagaimana cara men-develop test.py dengan baik. Setelah itu membantu saya dalam me-refactor kode saya agar lebih terstruktur dan clean sehingga tidak spaghetti code. Membantu saya dalam menstrukturisasi experience about, skills, dan contact ke page yang baru dengan menambahkan data baru sehingga best-practice.