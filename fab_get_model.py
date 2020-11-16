import pysftp #pip install pysftp
import json
import paho.mqtt.client as mqtt #pip install paho-mqtt
import paho.mqtt.publish as publish
import os
import datetime
import traceback
# *********************************************************************
# Config

MQTT_SERVER = "qa.mqtt.idi-plus.com"  
MQTT_PORT = 1883  
MQTT_ALIVE = 60  
MQTT_TOPIC1 = "/123/123" 
NFS_SERVER = "13.57.162.188"
NFS_PORT = 32222
USER = "models"
PASSWD = "liteonmodels"
LOCAL_PATH = "./"


def on_connect(client, userdata, flags, rc):
    #subscribe topic
    try:
      client.subscribe(MQTT_TOPIC1)
    except Exception as e:
      print(e)
      publish.single(MQTT_TOPIC1+'/res',json.dumps({'code':'0','msg':str(e),'topic':MQTT_TOPIC1}),hostname=MQTT_SERVER,port=MQTT_PORT)
      with open('log.txt', 'a+') as f:
        print(datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')+"\n type error: " + str(e), file=f)
        print(traceback.format_exc(), file=f)

def on_message(client, userdata, message):
  try:
    payload =bytes.decode(message.payload)
    payload_list = json.loads(payload)
    msg = json.loads(payload_list['message'])
    model_path = msg['model_path']
    subject = msg['subject']
    model_version = msg['model_version']
    #get model extension
    model_extension = os.path.splitext(model_path)[1]
    model_extension = model_extension if len(model_extension.split('_')) == 1 else model_extension.split('_')[0]
    #origin filename
    # origin_filename = (os.path.splitext(model_path)[0]).split('/')[-1] + model_extension
    local_model_path = LOCAL_PATH+subject+'/'+subject+model_extension

    #get model
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(NFS_SERVER,port=NFS_PORT, username=USER, password=PASSWD,cnopts=cnopts) as sftp:
      print(model_path)
      if(sftp.isfile(model_path)):
        print("copy model from",model_path)
        print('LOCAL_PATH',LOCAL_PATH+subject)
        if not os.path.isdir(LOCAL_PATH+subject):
          os.mkdir(LOCAL_PATH+subject)

        #sftp get model
        print('local_model_path',local_model_path)
        sftp.get(model_path,localpath=local_model_path)
        print("Success copy")
        client.publish(MQTT_TOPIC1+'/res', json.dumps({'code':'1','msg':'success','topic':MQTT_TOPIC1}))
        sftp.close()
      else:
      #exception file does not exist
        sftp.close()
        raise FileExistsError(model_path + 'file does not exist')
      

      
  except Exception as e:
    print(e)
    publish.single(MQTT_TOPIC1+'/res',json.dumps({'code':'0','msg':str(e),'topic':MQTT_TOPIC1}),hostname=MQTT_SERVER,port=MQTT_PORT)
    with open('log.txt', 'a+') as f:
      print(datetime.datetime.now().strftime(
          '%Y-%m-%d %H:%M:%S')+"\n type error: " + str(e), file=f)
      print(traceback.format_exc(), file=f)
      
    


if __name__ == '__main__':
  client = mqtt.Client()
  client.on_connect = on_connect
  client.on_message = on_message
  #connect mqtt broker
  client.connect(MQTT_SERVER, MQTT_PORT, MQTT_ALIVE)
  while True:
    try:
      client.loop_forever()
    except KeyboardInterrupt:
        print('close')
        client.disconnect()
        exit(0)
    except Exception as e:
      print(e)
      publish.single(MQTT_TOPIC1,json.dumps({'code':'0','msg':str(e),'topic':MQTT_TOPIC1}),hostname=MQTT_SERVER,port=MQTT_PORT)
      with open('log.txt', 'a+') as f:
        print(datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')+"\n type error: " + str(e), file=f)
        print(traceback.format_exc(), file=f)
