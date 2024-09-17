#Pesan error tersebut terjadi karena kebijakan eksekusi script di sistem PowerShell kamu membatasi eksekusi script. Untuk memperbaikinya, kamu perlu mengubah kebijakan eksekusi sementara agar PowerShell dapat menjalankan script, seperti yang diperlukan untuk mengaktifkan virtual environment.
#Jalankan perintah ini untuk sementara mengubah kebijakan eksekusi: Powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

#Setelah menjalankan perintah di atas, aktifkan virtual environment dengan perintah berikut: Powershell
.\venv\Scripts\Activate.ps1

#Cek daftar library yang sudah terinstal menggunakan pip:
pip list

#Cek apakah library tertentu sudah terinstal: 
pip show pandas

#cek docker images
docker images

#cek container docker yang ada di komputer
docker ps

#cek semua container yang running maupun stop
docker ps -a

#cek semua container yang mengandung kata tertentu
docker ps -a --filter "name=^/de-basic"

#menjalankan docker untuk build docker compose dengan UBUNTU(WSL)
sudo docker-compose up -d

#cara stop container dengan awalan tertentu
docker stop $(docker ps -q --filter "name=de-basic")

#menghapus container dengan kata tertentu
docker rm $(docker ps -a -q --filter "name=^/de-basic")

#cara pull airflow secara manual
docker pull apache/airflow:2.10.1

#setelah pull manual baru jalankan
sudo docker compose up -d

#menghentikan semua container yang sedang running
docker kill $(docker ps -q)

#jika ingin build postgres saja
docker-compose up -d --no-deps --build postgres

#menghapus container
docker-compose down

#Rebuild, jika ingin rebuild library baru di requirements.txt
docker-compose build

#Jika ingin melihat IP address postgres
docker inspect <container_id_postgres>

#postgresql di server pgadmin
http://localhost:5050/browser/
username: admin@admin.com
password: root

#connection postgresql di airflow UI
connection_id: retail_connection
host: 172.19.0.4
password: airflow
port: 5432
username: airflow


#menghapus docker banyak images tertentu dengan Bash
docker rmi -f $(docker images | grep '^airflow_project' | awk '{print $3}')

#menghapus docker images tertentu dengan Bash
docker rmi <image_id>