
import sqlite3, json
from pathlib import Path

BASE_CARS = [
("Maruti Suzuki","Swift","Hatchback",5,1299,["Petrol","CNG"],["Manual","Automatic"],8,8,7),
("Maruti Suzuki","Baleno","Hatchback",5,1699,["Petrol","CNG"],["Manual","Automatic"],9,8,8),
("Maruti Suzuki","Fronx","SUV",5,2099,["Petrol","CNG"],["Manual","Automatic"],9,8,8),
("Maruti Suzuki","Brezza","SUV",5,2299,["Petrol","CNG"],["Manual","Automatic"],8,9,8),
("Maruti Suzuki","Grand Vitara","SUV",5,2999,["Petrol","Hybrid"],["Manual","Automatic"],9,9,9),
("Maruti Suzuki","Ertiga","MUV",7,2699,["Petrol","CNG"],["Manual","Automatic"],8,8,9),
("Maruti Suzuki","XL6","MUV",6,3199,["Petrol","CNG"],["Manual","Automatic"],8,9,9),
("Hyundai","Grand i10 Nios","Hatchback",5,1499,["Petrol","CNG"],["Manual","Automatic"],8,7,7),
("Hyundai","i20","Hatchback",5,1899,["Petrol"],["Manual","Automatic"],8,8,8),
("Hyundai","Aura","Sedan",5,1799,["Petrol","CNG"],["Manual","Automatic"],8,8,8),
("Hyundai","Verna","Sedan",5,2799,["Petrol"],["Manual","Automatic"],7,9,8),
("Hyundai","Venue","SUV",5,2299,["Petrol","Diesel"],["Manual","Automatic"],8,8,8),
("Hyundai","Creta","SUV",5,3399,["Petrol","Diesel"],["Manual","Automatic"],8,9,9),
("Hyundai","Alcazar","SUV",7,3899,["Petrol","Diesel"],["Manual","Automatic"],8,9,9),
("Hyundai","Ioniq 5","Luxury",5,7999,["Electric"],["Automatic"],9,10,9),
("Tata","Tiago","Hatchback",5,1399,["Petrol","CNG"],["Manual","Automatic"],8,7,7),
("Tata","Tiago EV","Hatchback",5,1899,["Electric"],["Automatic"],10,7,7),
("Tata","Altroz","Hatchback",5,1899,["Petrol","Diesel","CNG"],["Manual","Automatic"],8,8,8),
("Tata","Tigor","Sedan",5,1799,["Petrol","CNG"],["Manual","Automatic"],8,8,8),
("Tata","Tigor EV","Sedan",5,1999,["Electric"],["Automatic"],10,8,8),
("Tata","Punch","SUV",5,1999,["Petrol","CNG"],["Manual","Automatic"],8,8,8),
("Tata","Punch EV","SUV",5,2399,["Electric"],["Automatic"],10,8,8),
("Tata","Nexon","SUV",5,2499,["Petrol","Diesel","CNG"],["Manual","Automatic"],8,9,9),
("Tata","Nexon EV","SUV",5,2799,["Electric"],["Automatic"],10,9,9),
("Tata","Harrier","SUV",5,3799,["Diesel"],["Manual","Automatic"],7,10,9),
("Tata","Safari","SUV",7,4299,["Diesel"],["Manual","Automatic"],7,10,10),
("Mahindra","XUV 3XO","SUV",5,2399,["Petrol","Diesel"],["Manual","Automatic"],8,8,8),
("Mahindra","XUV700","SUV",7,4299,["Petrol","Diesel"],["Manual","Automatic"],7,10,10),
("Mahindra","Scorpio N","SUV",7,4199,["Petrol","Diesel"],["Manual","Automatic"],7,9,10),
("Mahindra","Thar","SUV",4,3999,["Petrol","Diesel"],["Manual","Automatic"],6,8,10),
("Mahindra","Thar Roxx","SUV",5,4499,["Petrol","Diesel"],["Manual","Automatic"],6,9,10),
("Mahindra","BE 6","SUV",5,4599,["Electric"],["Automatic"],10,9,9),
("Mahindra","XEV 9e","SUV",5,5299,["Electric"],["Automatic"],10,10,9),
("Toyota","Glanza","Hatchback",5,1799,["Petrol","CNG"],["Manual","Automatic"],9,8,8),
("Toyota","Rumion","MUV",7,2899,["Petrol","CNG"],["Manual","Automatic"],8,8,9),
("Toyota","Urban Cruiser Hyryder","SUV",5,3199,["Petrol","Hybrid"],["Manual","Automatic"],9,9,9),
("Toyota","Innova Crysta","MUV",7,3799,["Diesel"],["Manual"],7,10,10),
("Toyota","Innova Hycross","MUV",7,4499,["Petrol","Hybrid"],["Automatic"],9,10,10),
("Toyota","Fortuner","Luxury",7,6999,["Petrol","Diesel"],["Manual","Automatic"],6,10,10),
("Kia","Sonet","SUV",5,2299,["Petrol","Diesel"],["Manual","Automatic"],8,8,8),
("Kia","Seltos","SUV",5,3199,["Petrol","Diesel"],["Manual","Automatic"],8,9,9),
("Kia","Carens","MUV",7,3399,["Petrol","Diesel"],["Manual","Automatic"],8,9,9),
("Kia","EV6","Luxury",5,8299,["Electric"],["Automatic"],10,10,9),
("Honda","Amaze","Sedan",5,1899,["Petrol"],["Manual","Automatic"],8,8,8),
("Honda","City","Sedan",5,2699,["Petrol"],["Manual","Automatic"],8,9,9),
("Honda","City e:HEV","Sedan",5,3499,["Hybrid"],["Automatic"],10,9,9),
("Honda","Elevate","SUV",5,2899,["Petrol"],["Manual","Automatic"],8,9,9),
("Skoda","Kylaq","SUV",5,2699,["Petrol"],["Manual","Automatic"],7,9,9),
("Skoda","Kushaq","SUV",5,3199,["Petrol"],["Manual","Automatic"],7,9,9),
("Skoda","Slavia","Sedan",5,2999,["Petrol"],["Manual","Automatic"],7,9,8),
("Volkswagen","Virtus","Sedan",5,3199,["Petrol"],["Manual","Automatic"],7,9,8),
("Volkswagen","Taigun","SUV",5,3299,["Petrol"],["Manual","Automatic"],7,9,9),
("MG","Comet EV","Hatchback",4,1599,["Electric"],["Automatic"],10,6,5),
("MG","Windsor EV","MUV",5,2699,["Electric"],["Automatic"],10,8,8),
("MG","Astor","SUV",5,2899,["Petrol"],["Manual","Automatic"],7,9,8),
("MG","Hector","SUV",5,3499,["Petrol","Diesel"],["Manual","Automatic"],7,9,9),
("MG","ZS EV","SUV",5,3299,["Electric"],["Automatic"],10,9,8),
("Renault","Kwid","Hatchback",5,1199,["Petrol"],["Manual","Automatic"],8,6,6),
("Renault","Kiger","SUV",5,1999,["Petrol"],["Manual","Automatic"],8,8,8),
("Nissan","Magnite","SUV",5,1999,["Petrol"],["Manual","Automatic"],8,8,8),
("Citroen","C3","Hatchback",5,1699,["Petrol"],["Manual","Automatic"],8,8,8),
("Citroen","Basalt","SUV",5,2399,["Petrol"],["Manual","Automatic"],8,8,8),
("Jeep","Compass","SUV",5,4499,["Diesel","Petrol"],["Manual","Automatic"],6,9,9),
("Jeep","Meridian","Luxury",7,5699,["Diesel"],["Manual","Automatic"],6,10,9),
("BYD","Atto 3","SUV",5,4199,["Electric"],["Automatic"],10,9,8),
("BYD","Seal","Luxury",5,6499,["Electric"],["Automatic"],10,10,8),
("BYD","eMAX 7","MUV",7,4899,["Electric"],["Automatic"],10,9,9),
("BMW","2 Series","Luxury",5,7499,["Petrol","Diesel"],["Automatic"],6,10,8),
("BMW","3 Series","Luxury",5,8999,["Petrol","Diesel"],["Automatic"],6,10,8),
("BMW","X1","Luxury",5,8999,["Petrol","Diesel"],["Automatic"],6,10,9),
("BMW","iX1","Luxury",5,9999,["Electric"],["Automatic"],10,10,9),
("Mercedes-Benz","A-Class","Luxury",5,8499,["Petrol","Diesel"],["Automatic"],6,10,8),
("Mercedes-Benz","C-Class","Luxury",5,10499,["Petrol","Diesel"],["Automatic"],6,10,9),
("Mercedes-Benz","GLA","Luxury",5,9999,["Petrol","Diesel"],["Automatic"],6,10,9),
("Audi","A4","Luxury",5,9499,["Petrol"],["Automatic"],6,10,8),
("Audi","Q3","Luxury",5,9999,["Petrol"],["Automatic"],6,10,9),
("Volvo","XC40 Recharge","Luxury",5,10999,["Electric"],["Automatic"],10,10,9),
("Mini","Cooper S","Luxury",4,7999,["Petrol"],["Automatic"],6,9,7),
]

LOCATIONS=["Thane","Vile Parle","Bandra","Andheri","Powai","Chembur","Lower Parel","Navi Mumbai","Borivali","Dadar","Worli","Goregaon","Mulund","BKC","Kurla","Airoli","Vashi","Kharghar","Wadala","Sion","Ghatkopar","Malad","Kandivali"]
COLORS=["Graphite","Silver","Pearl White","Midnight Grey","Black","Stone Grey","Blue"]
YEARS=list(range(2018,2027))

SCHEMA = """
CREATE TABLE IF NOT EXISTS cars(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 brand TEXT, model TEXT, category TEXT, seats INTEGER, price INTEGER,
 fuel TEXT, transmission TEXT, efficiency REAL, comfort REAL, highway REAL,
 rating REAL, trips INTEGER, year INTEGER, color TEXT, location TEXT,
 locations_json TEXT, bags INTEGER, available INTEGER DEFAULT 1,
 approved INTEGER DEFAULT 1, owner_listing INTEGER DEFAULT 0,
 images_json TEXT DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS bookings(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 code TEXT, car_id INTEGER, driver_name TEXT, licence TEXT, start_date TEXT,
 duration_days INTEGER, pickup_location TEXT, total INTEGER, status TEXT
);
"""

def ensure_database(path):
    path=Path(path)
    con=sqlite3.connect(path)
    con.executescript(SCHEMA)
    count=con.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
    if count<200:
        con.execute("DELETE FROM cars")
        rows=[]; idx=1
        target=240
        for b in BASE_CARS:
            variants=4
            for i in range(variants):
                fuel=b[5][i%len(b[5])]
                tr=b[6][(i+(i//2))%len(b[6])]
                loc=LOCATIONS[(idx*7+i*3)%len(LOCATIONS)]
                year=YEARS[(idx+i)%len(YEARS)]
                price=max(999,b[4]-(2026-year)*55+(i%3)*120)
                locs=[]
                for off in (0,5,10,14,19):
                    cand=LOCATIONS[(idx+off)%len(LOCATIONS)]
                    if cand not in locs: locs.append(cand)
                    if len(locs)==3: break
                rows.append((b[0],b[1],b[2],b[3],price,fuel,tr,b[7],b[8],b[9],round(4.2+((idx*7)%8)/10,1),
                             32+((idx*17)%390),year,COLORS[idx%len(COLORS)],loc,json.dumps(locs),
                             4 if b[3]>=7 else (2 if b[2]=="Hatchback" else 3),0 if idx%13==0 else 1,1,0,"[]"))
                idx+=1
                if len(rows)>=target: break
            if len(rows)>=target: break
        con.executemany("""INSERT INTO cars
          (brand,model,category,seats,price,fuel,transmission,efficiency,comfort,highway,rating,trips,year,color,location,locations_json,bags,available,approved,owner_listing,images_json)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",rows)
    con.commit(); con.close()
