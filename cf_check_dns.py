#! /usr/bin/env python
# coding utf-8


import sys
from sys import exit
import os
import json
import socket
import requests
import subprocess


# Python script to check all dns entry from cloudflare json export
__author__ = "Benjamin Kittler"
__copyright__ = "Copyright 2021, KITTLER"
__credits__ = ["Benjamin Kittler"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Benjamin Kittler"
__email__ = "kittler @T. gmail. com"
__status__ = "integration"

"""
Todo :
    create function to check dns entry : TXT, CAA, etc...
    create help
    add option to create external output file
"""

def main(argv):
    """
    The main receved argument and launch check function.

    Parameters
    ----------
    value : string
        Function receive string value to verify.

    """
    # print argument for verification
    print("Import file: {}".format(argv[0]))
    file = str(argv[0])
    check(file)


def ping_name(name, cloudflare):
    """
    Function to resolve name and ping this host.
    print the result of ping

    Parameters
    ----------
    name : string
        This variable contain the Name of json line (datajson['name'])
    cloudflare : int
        This variable is 1 if Cloudflare proxyt is used
        or if resolution not requested (already made)

    Returns
    -------
    None.

    """
    # make resolution
    if cloudflare == 0:
        try:
            addr1 = socket.gethostbyname_ex(name)
            print("Resolution -> {}".format(addr1[2]))
        except:
            print("Resolution failed")

    # import pdb; pdb.set_trace()
    try:
        hostname = format(name)
        response = os.system("ping -c 1 " + hostname + " > /dev/null 2>&1")
        if response == 0:
            print("Response ping : OK")
        else:
            print("Response ping : KO")
    except requests.ConnectionError:
        print("Response ping : failed to connect")


def request_name(name, cloudflare):
    """
    Function to resolve name and send https or http request to this host.
    print the Response code and if it fail, launch a ping to this host
    with ping_name() function (print the result of ping)

    Parameters
    ----------
    name : string
        This variable contain the Name of json line (datajson['name'])
    cloudflare : int
        This variable is 1 if Cloudflare proxyt is used

    Returns
    -------
    None.

    """

    # make resolution
    if cloudflare == 0:
        try:
            addr1 = socket.gethostbyname_ex(name)
            print("Resolution -> {}".format(addr1[2]))
        except:
            print("Resolution failed")

    try:
        url = "https://" + format(name)
        response = requests.head(url, allow_redirects=True, timeout=5)
        print("Response code HTTPS :" + str(response.status_code))
    except requests.exceptions.Timeout:
        print("Response code HTTPS: Timeout occurred")
        try:
            url = "http://" + format(name)
            response = requests.head(url, allow_redirects=True, timeout=5)
            print("Response code HTTP:" + str(response.status_code))
        except requests.exceptions.Timeout:
            print("Response code HTTP: Timeout occurred")
            ping_name(name, 1)
        except requests.ConnectionError:
            print("Response code HTTP/HTTPS: failed to connect")
            ping_name(name, 1)
    except requests.ConnectionError:
        try:
            url = "http://" + format(name)
            response = requests.head(url, allow_redirects=True, timeout=5)
            print("Response code HTTP:" + str(response.status_code))
        except requests.exceptions.Timeout:
            print("Response code HTTP: Timeout occurred")
            ping_name(name, 1)
        except requests.ConnectionError:
            print("Response code HTTP/HTTPS: failed to connect")
            ping_name(name, 1)


def resolv_name(name, cloudflare, dnstype):
    """
    Function to resolve name and print entry for TXT, CAA, AAAA.

    Parameters
    ----------
    name : string
        This variable contain the Name of json line (datajson['name'])
    cloudflare : int
        This variable is 1 if Cloudflare proxy is used
    dnstype : string
        This variable contain the type of dns entry (datajson['type'])
        
    Returns
    -------
    None.

    """
    # make resolution
    if cloudflare == 0 or dnstype != "TXT":
        try:
            addr1 = socket.gethostbyname_ex(name)
            print("Resolution -> {}".format(addr1[2]))
        except:
            print("Resolution failed")

    # Retrieve dns entry
    try:
        resolv1 = subprocess.Popen(["dig","-t",format(dnstype),format(name),"+short"], stdout=subprocess.PIPE).communicate()[0] 
        print("Entry verification : {}".format(resolv1))
    except requests:
        print("Entry verification : failed")


def check(file_to_check):
    """
    Function to open file, read each line and convert to json.
    For each line, identify entry, type and proxification throw cloudflare
    For each value, launch https/http test or ping test depending of type

    Parameters
    ----------
    file_to_check : String
    It's the name of file must be imported and checked

    Returns
    -------
    None.

    """
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
        # Clean each line
        start = line.strip()
        json_accept_str = start.replace("'", "\"")
        json_accept_str = json_accept_str.replace("issue \"", "issue ")
        json_accept_str = json_accept_str.replace("\"\"", "\"")
        json_accept_str = json_accept_str.replace("True", "\"True\"")
        json_accept_str = json_accept_str.replace("False", "\"False\"")
        datajson = json.loads(json_accept_str)

        # Correct bool value
        if datajson['proxied'] == "True":
            datajson['proxied'] = bool("True")
        else:
            datajson['proxied'] = bool("")

        # Delete entry not necessary
        entriesToRemove = ('id', 'zone_id', 'zone_name', 'created_on',
                           'modified_on', 'locked', 'meta', 'proxiable')
        for k in entriesToRemove:
            datajson.pop(k, None)
        if datajson['proxied'] == "False":
            datajson['proxied'] = bool("")

        # Type A or CNAME NOT throw Cloudflare
        if (datajson['proxied'] is False and
         (datajson['type'] == "A" or datajson['type'] == "CNAME")):
            print("Testing : {}".format(datajson['name']) +
                  "  Type {}".format(datajson['type']) +
                  "-> {}".format(datajson['content']))
            request_name(datajson['name'],0)

        # Type A or CNAME throw Cloudflare
        elif (datajson['proxied'] is True and
              (datajson['type'] == "A" or datajson['type'] == "CNAME")):
            print("Testing : {}".format(datajson['name']) +
                  "  Type {}".format(datajson['type']) + "-> Cloudflare")
            request_name(datajson['name'],1)

        # Type CAA, TXT or AAAA throw Cloudflare
        elif (datajson['proxied'] is True and
              (datajson['type'] == "CAA" or datajson['type'] == "TXT" or
              datajson['type'] == "AAAA")):
            print("Testing : {}".format(datajson['name']) +
                  "  Type {}".format(datajson['type']) +
                  "-> Cloudflare")
            resolv_name(datajson['name'], 1, datajson['type'])

        # Type CAA, TXT or AAAA NOT throw Cloudflare
        elif (datajson['proxied'] is False and
              (datajson['type'] == "CAA" or datajson['type'] == "TXT" or
              datajson['type'] == "AAAA")):
            print("Testing : {}".format(datajson['name']) +
                  "  Type {}".format(datajson['type']) +
                  "-> {}".format(datajson['content']))
            resolv_name(datajson['name'], 0, datajson['type'])

        # Type CAA, TXT or AAAA NOT throw Cloudflare
        elif (datajson['proxied'] is False and
              datajson['type'] == "MX"):
            print("Testing : {}".format(datajson['name']) +
                  "  Type {}".format(datajson['type']) +
                  "-> {}".format(datajson['content']))
            ping_name(datajson['name'],0)
            
        else:
            print("Testing : {}".format(datajson['name']) +
                  "  Type {}".format(datajson['type']) +
                  "-> {}".format(datajson['content']))
            print("Ignored")
    exit('end')


if __name__ == "__main__":
    main(sys.argv[1:])
