from flask import Flask, redirect, request
import json
import atexit
import pickle

app = Flask(__name__)

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
        # dict: deviceId->location

url = "127.0.0.1:5000"

@app.route('/')
def redirect_to_home():
        return redirect("/home")

@app.route('/home')
def home():
        return "redirected!"

@app.route('/daddy/<username>')
def daddy(username):
        if username in dict_baby_db:
                return parsed_daddy(username)
        else:
                return "This is not a daddy :("

@app.route('/baby/<username>')
def baby(username):
        if username in dict_baby_db:
                return parsed_baby(username)
        else:
                return "This is not a baby :("

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

@app.route('/post/sensor', methods=['POST'])
def post():
        data = request.data
        sensor_log.append(data)
        parse_sensor_data(data)
        return str(data)

@app.route('/post/sensor/log')
def post_log():
        return str(sensor_parsed)

def add_daddy(username, pswd, money):
        if username in dict_daddy_db:
                return False
        else:
                dict_daddy_db[username] = {
                        "pswd":pswd,
                        "money":money }
                return True

def add_baby(username, ppl_cnt, favor, money):
        if username in dict_baby_db:
                return False
        else:
                dict_baby_db[username] = {
                        "ppl_cnt":ppl_cnt, 
                        "favor":favor, 
                        "money":money }
                return True

def add_registration(location, time, name):
        if name in dict_baby_db:
                list_registration_db.append((location, time, name))
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
        f.close()

# Pre-existing data
add_baby(username="秉玨", ppl_cnt="100", favor="200", money="500")
add_baby(username="英弘", ppl_cnt="10", favor="60", money="1000")
add_baby(username="Ian", ppl_cnt="100", favor="200", money="500")
add_registration("7F", "2019-08-27 18:22:32", "秉玨")
add_registration("Room", "2019-08-27 20:46:30", "秉玨")
add_registration("Room", "2019-08-27 23:15:07", "英弘")

# at exit, store all important files
atexit.register(pickle_persistent_data)