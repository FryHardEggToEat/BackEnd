from flask import Flask, redirect, request
from flask_cors import CORS
import json
import atexit
import pickle
from datetime import datetime

app = Flask(__name__)
CORS(app)

# load database from pickle
try:
        with open("database(baby)", "rb") as f:
                dict_baby_db = pickle.load(f)
        with open("database(daddy)", "rb") as f:
                dict_daddy_db = pickle.load(f)
        with open("database(registration)", "rb") as f:
                list_registration_db = pickle.load(f)
        with open("database(sensor_log)", "rb") as f:
                sensor_log = pickle.load(f)
        with open("database(sensor_parsed)", "rb") as f:
                sensor_parsed = pickle.load(f)
        with open("database(total_amount)", "rb") as f:
                total_amount = pickle.load(f)
        with open("database(donate_log)", "rb") as f:
                donate_log = pickle.load(f)
except OSError as e:
        print("Reconstructing all data...")
        # baby: {username:{ppl_cnt,favor,money}
        dict_baby_db = {}
        # daddy: {username:{pswd,money}}
        dict_daddy_db = {}
        # registration: (location,time,name)
        list_registration_db = []
        # sensor data log
        sensor_log = []
        # parsed sensor data: {id,deviceId,time,ppl_cnt,favor}
        sensor_parsed = []
        # donate log: {time: (username, money)}
        donate_log = {}
        # dict: deviceId->location
        id_to_location = {}
        # total amount
        total_amount = [0]

url = "127.0.0.1:5000"

@app.route('/')
def redirect_to_home():
        return redirect("/home")

@app.route('/home')
def home():
        return "redirected!"

@app.route('/daddy/<username>')
def daddy(username):
        if username in dict_daddy_db:
                return parsed_daddy(username)
        else:
                return "This is not a daddy :("

@app.route('/daddy/log')
def daddy_log():
        return json.dumps(donate_log)

@app.route('/baby/<username>')
def baby(username):
        if username in dict_baby_db:
                return parsed_baby(username)
        else:
                return "This is not a baby :("

@app.route('/baby/all')
def baby_all():
        return json.dumps(dict_baby_db)

@app.route('/distribute')
def distribute():
        ppl_sum = 0
        for usr in dict_baby_db:
                ppl_sum += dict_baby_db[usr]["ppl_cnt"]
        unit = total_amount[0] / ppl_sum
        for usr in dict_baby_db:
                dict_baby_db[usr]["money"] += int(unit * dict_baby_db[usr]["ppl_cnt"])
        total_amount[0] = 0
        return json.dumps({"who":"昶劭!"})

@app.route('/events')
def events():
        return str(list_registration_db)

@app.route('/events/<query>')
def events_query(query):
        queried = []
        for event in list_registration_db:
                if query in event:
                        queried.append(event)
        return str(queried)

@app.route('/total')
def total():
        return str(total_amount[0])

@app.route('/post/sensor', methods=['POST'])
def post():
        data = request.data
        print("data:", data)
        sensor_log.append(data)
        parse_sensor_data(data)
        return str(data)

@app.route('/post/sensor/log')
def post_log():
        return str(sensor_parsed)

@app.route('/post/new_daddy', methods=['POST'])
def post_new_daddy():
        data = request.data
        print("data:", data)
        decoded = data.decode("UTF-8")
        listed = decoded.split(" ")
        if int(listed[1]) < 0:
                return data
        add_daddy(listed[0], "", listed[1])
        total_amount[0] += int(listed[1])
        donate_log[datetime.now().strftime("%Y%m%d %H:%M:%S")] = (listed[0], listed[1])
        return data

@app.route('/post/new_baby', methods=['POST'])
def post_new_baby():
        data = request.data
        print("data:", data)
        decoded = data.decode("UTF-8")
        loaded = json.loads(decoded)
        add_baby(loaded.get("username"), 0, 0, 0)
        return data

@app.route('/post/new_event', methods=['POST'])
def new_event():
        data = request.data
        print("data:", data)
        decoded = data.decode("UTF-8")
        listed = decoded.split(" ")
        add_registration(listed[0], listed[1], listed[2], listed[3])
        return data

def add_daddy(username, pswd, money):
        if username in dict_daddy_db:
                return False
        else:
                dict_daddy_db[username] = {
                        "pswd":pswd,
                        "money":money }
                return True

def add_baby(username, ppl_cnt:int, favor, money:int):
        if username in dict_baby_db:
                return False
        else:
                dict_baby_db[username] = {
                        "ppl_cnt":ppl_cnt, 
                        "favor":favor, 
                        "money":money }
                return True

def add_registration(location, s_time, e_time, name):
        if name in dict_baby_db:
                list_registration_db.append((location, s_time, e_time, name))
                return True
        else:
                return False

def parse_sensor_data(raw_bin_data):
        decoded = raw_bin_data.decode("UTF-8")
        loaded = json.loads(decoded)
        # parsed sensor data: {id,deviceId,time,ppl_cnt,favor}
        sensor_parsed.append({
                "id":loaded.get("id"),
                "deviceId":loaded.get("deviceId"),
                "time":loaded.get("time"),
                "ppl_cnt":loaded.get("value")[0],
                "favor":loaded.get("value")[1] })

def parsed_daddy(username):
        details = dict_daddy_db.get(username)
        return f"""username: {username},\n
        ppl_cnt: {details.get("money")}"""

def parsed_baby(username):
        details = dict_baby_db.get(username)
        return f"""username: {username},\n
        ppl_cnt: {details.get("ppl_cnt")},\n
        favor: {details.get("favor")},\n
        money: {details.get("money")}"""

def pickle_persistent_data():
        with open("database(baby)", "wb") as f:
                pickle.dump(dict_baby_db,f)
        with open("database(daddy)", "wb") as f:
                pickle.dump(dict_daddy_db,f)
        with open("database(registration)", "wb") as f:
                pickle.dump(list_registration_db,f)
        with open("database(sensor_log)", "wb") as f:
                pickle.dump(sensor_log,f)
        with open("database(sensor_parsed)", "wb") as f:
                pickle.dump(sensor_parsed,f)
        with open("database(total_amount)", "wb") as f:
                pickle.dump(total_amount,f)
        with open("database(donate_log)", "wb") as f:
                pickle.dump(donate_log,f)
        f.close()

# Pre-existing data
"""
add_baby(username="秉玨", ppl_cnt=100, favor=200, money=0)
add_baby(username="英弘", ppl_cnt=10, favor=60, money=0)
add_baby(username="Ian", ppl_cnt=100, favor=200, money=0)
add_baby(username="劭爺", ppl_cnt=10000, favor=20000, money=0)
add_registration("7F", "2019-08-27 18:22:32", "秉玨")
"""

# at exit, store all important files
atexit.register(pickle_persistent_data)