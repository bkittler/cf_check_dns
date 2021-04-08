#! /usr/bin/env python
# coding utf-8

import sys
import os
import json
import socket
import requests

"""Python script to check all dns entry from cloudflare json export"""
__author__ = "Benjamin Kittler"
__copyright__ = "Copyright 2021, KITTLER"
__credits__ = ["Benjamin Kittler"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Benjamin Kittler"
__email__ = "kittler @T. gmail. com"
__status__ = "integration"

def main(argv):                         
    # print argument for verification
    print ("Import file: {}".format(argv[0]))
    file = str(argv[0])
    check(file)

def ping_name(name):
    addr1 = socket.gethostbyname_ex(name)
    print("Resolution -> {}".format(addr1[2]))
    #import pdb; pdb.set_trace()
    try:
        hostname = format(name)
        response = os.system("ping -c 1 " + hostname + " > /dev/null 2>&1")
        if response == 0:
            print("Response ping : OK")
        else:
            print("Response ping : KO")
    except requests.ConnectionError:
        print("Response ping : failed to connect")

def request_name(name):
    addr1 = socket.gethostbyname_ex(name)
    print("Resolution -> {}".format(addr1[2]))
    try:
        url = "https://" + format(name)
        response = requests.head(url,allow_redirects=True)
        print("Response code HTTPS :" + str(response.status_code))
    except requests.ConnectionError:
        try:
            url = "http://" + format(name)
            response = requests.head(url,allow_redirects=True)
            print("Response code HTTP:" + str(response.status_code))
        except requests.ConnectionError:
            print("Response code HTTP/HTTPS: failed to connect")
            ping_name(name)


def check(file_to_check):
    print('check...')
    try:
        file = open(file_to_check, "r")
    except:
        exit('open file failed')
    
    # lines contain all line of file
    lines = file.readlines()
    # close the file after read all lines
    file.close()

    for line in lines:
        start = line.strip()
        json_acceptable_string = start.replace("'", "\"")
        json_acceptable_string = json_acceptable_string.replace("issue \"", "issue ")
        json_acceptable_string = json_acceptable_string.replace("\"\"", "\"")
        json_acceptable_string = json_acceptable_string.replace("True", "\"True\"")
        json_acceptable_string = json_acceptable_string.replace("False", "\"False\"")
        datajson = json.loads(json_acceptable_string)

        if datajson['proxied'] == "True":
            datajson['proxied'] = bool("True")
        else:
            datajson['proxied'] = bool("")
        entriesToRemove = ('id', 'zone_id', 'zone_name', 'created_on', 'modified_on', 'locked', 'meta', 'proxiable')
        for k in entriesToRemove:
            datajson.pop(k, None)
        if datajson['proxied'] == "False":
            datajson['proxied'] = bool("")

        if datajson['proxied'] is False and (datajson['type'] == "A" or datajson['type'] == "CNAME"): # hors Cloudflare
            print("Testing : {}".format(datajson['name']) +  "  Type {}".format(datajson['type']) + "-> {}".format(datajson['content']))
            #import pdb; pdb.set_trace()
            request_name(datajson['name'])

        elif datajson['proxied'] is True and (datajson['type'] == "A" or datajson['type'] == "CNAME"): # via Cloudflare
            print ("Testing : {}".format(datajson['name']) + "  Type {}".format(datajson['type']) + "-> Cloudflare")
            #import pdb; pdb.set_trace()
            request_name(datajson['name'])

        elif datajson['proxied'] is True and (datajson['type'] == "CAA" or datajson['type'] == "TXT" or datajson['type'] == "AAAA" ): # via Cloudflare
            print ("Testing : {}".format(datajson['name']) + "  Type {}".format(datajson['type']) + "-> Cloudflare")
            #import pdb; pdb.set_trace()
            print("Ignored")

        elif datajson['proxied'] is False and (datajson['type'] == "CAA" or datajson['type'] == "TXT" or datajson['type'] == "AAAA" ): # hors Cloudflare
            print("Testing : {}".format(datajson['name']) +  "  Type {}".format(datajson['type']) + "-> {}".format(datajson['content']))
            #import pdb; pdb.set_trace()
            print("Ignored")

        else: # Pas A ni CNAME
            print ("Testing : {}".format(datajson['name']) + "  Type {}".format(datajson['type']) +  "-> Cloudflare")
            #import pdb; pdb.set_trace()
            ping_name(datajson['name'])

    exit()

if __name__ == "__main__":
    main(sys.argv[1:])