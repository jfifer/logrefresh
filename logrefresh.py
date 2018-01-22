import subprocess
import sys
import time
import re
import paramiko
import json
import subprocess
from pprint import pprint

def main(argv):
  paramiko.util.log_to_file("paramiko.log")
  ssh = paramiko.SSHClient()
  print paramiko.__version__
  with open("/home/jfifer/logrefresh/logstash.conf") as json_data:
    config = json.load(json_data)
  for server in config['servers'] :
    name = server['name']
    host = server['host']
    username = server['username']
    command = server['command']
    filelist = server['files']
    keypath = server['keypath']
    pkey = paramiko.RSAKey.from_private_key_file(server['keypath'])
    #print("Connecting to %s" % (host))
    try :
      client = paramiko.SSHClient()
      client.load_system_host_keys()
      client.set_missing_host_key_policy(paramiko.WarningPolicy)
      client.connect(host, port=22, username=username, pkey=pkey)
    except Exception as ex :
      print("Failed to connect to %s" % (ex))
    else:
      print("Connected to server %s" % (host))
      for filedata in filelist:
        filepath = filedata['filepath']
        filename = filedata['filename']
        hostpath = filedata['hostpath']
        scp_str = username+"@"+host+":"+hostpath
        print(scp_str)
        print(keypath)
        print(filepath)
        try:
          sts = subprocess.Popen(["scp", "-i", keypath, filepath, scp_str]).wait()
          pprint(sts)
        except subprocess.CalledProcessError as e :
          pprint(e.output)
        else:
          print("File transfer complete")
          if command == "systemctl":
            stop = "sudo systemctl stop logstash.service"
            start = "sudo systemctl start logstash.service"
          elif command == "init.d":
            stop = "sudo /etc/init.d/logstash stop"
            start = "sudo /etc/init.d/logstash start"
          stdin, stdout, stderr = client.exec_command(stop)
          print stdout.read()
          stdin, stdout, stderr = client.exec_command(start)
          print stdout.read()

if __name__ == "__main__":
  main(sys.argv[1:])
