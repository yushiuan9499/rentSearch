# rentSearch  
一個用來方便過濾教育部校外賃居網站的爬蟲程式  
## 功能
- 能利用通勤時間與距離、房間類型、房間坪數進行篩選  
- 能自由決定租金篩選範圍  
- 利用列表篩選租屋類型，不用一個一個點選  
- 能更自由的排序搜尋結果  
> [!WARNING]  
> 1. 本工具使用到許多第三方API，請不要濫用。  
> 2. 本工具是利用[Formosa 雲端租屋生活網](https://house.nfu.edu.tw/)的校外賃居網站資料進行爬蟲。  
>    不保證資料的正確性與完整性，僅供參考。  
> 3. 本工具計算通勤時間與距離的方式是利用OSRM。  
>    參數是人工設定的，並不保證正確性。  
## 安裝
==施工中==  
1. 安裝python  
2. 安裝python套件  
  ```bash
  pip install -r requirements.txt
  ```
3. 安裝osrm、docker、sqlite  
  ```bash
  # 安裝docker
  sudo apt-get install docker.io
  # 安裝osrm
  sudo apt-get install osmctools
  # 安裝sqlite
  sudo apt-get install sqlite3
  ```
4. 下載osrm資料  
  ```bash
  # 下載台灣的地圖
  wget https://download.geofabrik.de/asia/taiwan-latest.osm.pbf -O osrm-data/taiwan-latest.osm.pbf
  # 取得docker image版本
  sudo docker run --rm osrm/osrm-backend:latest osrm-extract --version
  ```
  去github安裝對應的版本，連結:[https://github.com/Project-OSRM/osrm-backend/releases/tag/<YOUR_VERSION>]
5. 切割出你要的地圖區域
## 使用
==施工中==
1. 啟動osrm server
2. 啟動網頁server
  ```bash
  python3 ./web.py
  ```
3. 使用瀏覽器打開網頁
  ```bash
  http://localhost:8000
  ```
