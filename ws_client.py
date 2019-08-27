import websocket
import json
import requests
from functools import partial
import threading
try:
    import thread
except ImportError:
    import _thread as thread
import time
# import signal
# signal.signal(signal.SIGINT, signal.SIG_DFL)

def on_message(ws, message):
  print(message)
  r = requests.post('http://192.168.40.58:5000/post/sensor', data=message)
  print('posted')

def on_error(ws, error):
  print(error)

def on_close(ws):
  print("### closed ###")
  
# def on_open(ws):
#   def run(*args):   
#     ws.send(json.dumps({ 
#       "ck": "PK1RGS352WXY7F4KCP",
#       "resources": [
#         "/v1/device/18356946691/sensor/egg_cam/rawdata"
#       ]
#     }))
#     while True:
#       time.sleep(1)
#     ws.close()
#     print("thread terminating...")

#   thread.start_new_thread(run, ())

def on_open(ws, device_id, sensor_id):
  ws.send(json.dumps({ 
    "ck": "PK1RGS352WXY7F4KCP",
    "resources": [
      "/v1/device/{}/sensor/{}/rawdata".format(device_id, sensor_id)
      ]
  }))

def threading_func(ws):
  ws.run_forever()
  print('finished')

if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws1 = websocket.WebSocketApp("ws://iot.cht.com.tw:80/iot/ws/rawdata",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    chan1 = partial(on_open, device_id=18356946691, sensor_id='egg_cam')
    ws1.on_open = chan1
    ws2 = websocket.WebSocketApp("ws://iot.cht.com.tw:80/iot/ws/rawdata",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    chan2 = partial(on_open, device_id=18360010126, sensor_id='jade_cam')
    ws2.on_open = chan2
    run_event = threading.Event()
    run_event.set()
    t1 = threading.Thread(target=threading_func, args=(ws1,))
    t2 = threading.Thread(target=threading_func, args=(ws2,))
    t1.start()
    t2.start()
    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        print('attempting to close threads...')
        ws1.close()
        ws2.close()
        run_event.clear()
        t1.join()
        t2.join()
        print('threads successfully closed')
    # ws2.run_forever()




