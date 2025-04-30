# osrm_manager.py
import os
import subprocess
import sqlite3
from typing import Tuple, List
import re

class OSRMManager:
    def __init__(self, db_path="osrm-data/maps.db", maps_dir="osrm-data/maps", use_docker=True, docker_image="osrm/osrm-backend:latest"):
        self.maps_dir = maps_dir
        os.makedirs(self.maps_dir, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.use_docker = use_docker
        self.docker_image = docker_image
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS maps (
                name TEXT PRIMARY KEY,
                north REAL,
                south REAL,
                east REAL,
                west REAL,
                dir_name TEXT,
                profile TEXT,
                port INTEGER
            )
        ''')
        self.conn.commit()

    def download_extract_region(self, name: str, north: float, south: float, east: float, west: float, profile: str = "car"):
        full_pbf = "osrm-data/taiwan-latest.osm.pbf"
        if not os.path.exists(full_pbf):
            raise FileNotFoundError("請先手動下載 taiwan-latest.osm.pbf 到 osrm-data 目錄下")

        map_dir = os.path.join(self.maps_dir, f"{west}-{south}-{east}-{north}")
        os.makedirs(map_dir, exist_ok=True)
        bbox = f"{west},{south},{east},{north}"
        out_pbf = os.path.join(self.maps_dir, f"{west}-{south}-{east}-{north}",f"{profile}.osm.pbf")
        c = self.conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO maps (name, north, south, east, west, dir_name, profile, port)
            VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
        ''', (name, north, south, east, west, f"{west}-{south}-{east}-{north}", profile))
        self.conn.commit()

        if os.path.exists(out_pbf):
            print(f"Region {bbox} already exists, skipping extraction.")
            return
        print(f"Extracting region {name} with bounding box {bbox} from {full_pbf} to {out_pbf}")
        subprocess.run(["osmconvert", full_pbf, f"-b={bbox}", f"-o={out_pbf}"], check=True)


    def build_osrm(self, name: str):
        c = self.conn.cursor()
        c.execute("SELECT dir_name , profile FROM maps WHERE name = ?", (name,))
        row = c.fetchone()
        if not row:
            raise ValueError(f"No map named '{name}' found in DB")
        dir_name, profile = row

        profile_file = f"/data/profiles/{profile}.lua"
        map_dir = os.path.join(self.maps_dir, dir_name)
        mnt_dir = os.getcwd() + "/osrm-data"
        os.makedirs(map_dir, exist_ok=True)

        docker_cmd = ["sudo", "docker", "run", "-it", "--rm", "-v", f"{mnt_dir}:/data",self.docker_image]

        if not os.path.exists(os.path.join(self.maps_dir, dir_name, f"{profile}.osrm")):
            # Extract
            subprocess.run(docker_cmd + ["osrm-extract", "-p", profile_file, f"/data/maps/{dir_name}/{profile}.osm.pbf"], check=True)
        # Partition
        subprocess.run(docker_cmd + ["osrm-partition", f"/data/maps/{dir_name}/{profile}.osrm"],  check=True)
        # Customize
        subprocess.run(docker_cmd + ["osrm-customize", f"/data/maps/{dir_name}/{profile}.osrm"], check=True)

    def start_server(self, name: str, port: int = 5000):
        c = self.conn.cursor()
        # Check if the port is already in use
        c.execute("SELECT name, port FROM maps WHERE port = ?", (port,))
        row = c.fetchone()
        if row:
            if row[0] == name:
                print(f"Map '{name}' is already running on port {port}")
                return
            raise ValueError(f"Port {port} is already in use by map '{row[0]}'")
        c.execute("SELECT dir_name , profile FROM maps WHERE name = ?", (name,))
        row = c.fetchone()
        if not row:
            raise ValueError(f"No map named '{name}' found in DB")
        dir_name, profile = row

        mnt_dir = os.getcwd() + "/osrm-data"
        docker_cmd = ["sudo", "docker", "run", "-it", "--rm", "--network=host", "-v", f"{mnt_dir}:/data",self.docker_image]
        process = subprocess.Popen(
            docker_cmd+["osrm-routed", "--algorithm", "MLD", "--port", str(port), f"/data/maps/{dir_name}/{profile}.osrm"],
            stdout=open("osrm.log", "w"),
            stderr=subprocess.STDOUT
        )

        c = self.conn.cursor()
        c.execute("UPDATE maps SET port = ? WHERE name = ?", (port, name))
        self.conn.commit()

        return process

    def list_maps(self):
        c = self.conn.cursor()
        c.execute("SELECT name, profile, port FROM maps")
        return c.fetchall()

    def stop_server(self, port: int):
        # 找出使用該 port 的 container ID
        try:
            result = subprocess.check_output([
                "sudo", "docker", "ps", "--filter", f"publish={port}", "--format", "{{.ID}}"
            ]).decode().strip()
            
            if result:
                print(f"Killing container using port {port}: {result}")
                subprocess.run(["sudo", "docker", "kill", result], check=True)
            else:
                print(f"No container is using port {port}")
        
        except subprocess.CalledProcessError as e:
            print(f"Failed to find or kill container on port {port}: {e}")

        c = self.conn.cursor()
        c.execute("UPDATE maps SET port = NULL WHERE port = ?", (port,))
        self.conn.commit()

    def delete_map(self, name: str):
        c = self.conn.cursor()
        c.execute("SELECT dir_name FROM maps WHERE name = ?", (name,))
        row = c.fetchone()
        if row:
            dir_name = row[0]
            map_dir = os.path.join(self.maps_dir, name)
            if os.path.exists(map_dir):
                subprocess.run(["rm", "-rf", map_dir])
            if os.path.exists(dir_name):
                os.remove(dir_name)
            c.execute("DELETE FROM maps WHERE name = ?", (name,))
            self.conn.commit()
    def valid_map_exist(self, x: float, y: float) -> Tuple[str, str]:
        c = self.conn.cursor()
        c.execute("SELECT name, profile FROM maps WHERE north > ? AND south < ? AND east > ? AND west < ?", (y, y, x, x))
        row = c.fetchone()
        if row:
            return row[0], row[1]
        else:
            return None, None
