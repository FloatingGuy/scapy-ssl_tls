#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# Author : tintinweb@oststrom.com <github.com/tintinweb>
'''
Create python dictionary from IANA only TLS registry

requires Python 2.7 (xml.etree.ElementTree)
'''
import sys
import os
import datetime
import urllib2
import re
import xml.etree.ElementTree as ET

URL_TLSPARAMETERS = "https://www.iana.org/assignments/tls-parameters/tls-parameters.xml"

if sys.version_info[0]*10+sys.version_info[1] < 27:
    raise SystemExit('This utility requires Python 2.7 or higher.')

def pprint(name,d):
    '''dump as python dict
    '''
    print "%s = {"%name
    for k in sorted(d):
        print "    %s: '%s',"%(k,d[k])
    print "    }"

def normalize_key(strval):
    '''normalize key
       form a string of 0x1234 or 1234
    '''
    if '-' in strval:
        # skip ranges
        return None
    elif '0x' in strval:
        strval = "0x" + strval.replace('0x','').replace(',','')
    else:
        strval = "0x%0.2x"%(int(strval))
    return strval.lower()

def normalize_value(strval):
    '''normalize values
       strip TLS_ prefix
    '''
    return strval.lstrip("TLS_")

def normalize_title(strval):
    '''normalize registry titles
       convert -,<spaces>,parenthesis to _; strip multiple underscores and conver to uppercase
    '''
    return re.sub(r'(-+|\s+|\([^\)]+\))','_',strval).rstrip("_").upper()

def xml_registry_to_dict(xmlroot, _id, 
                         xml_key = './{http://www.iana.org/assignments}value',
                         xml_value = './{http://www.iana.org/assignments}description', 
                         xml_title = './{http://www.iana.org/assignments}title',
                         normalize_value = normalize_value, normalize_key = normalize_key, normalize_title=normalize_title):
    d = {}
    registry = xmlroot.find("{http://www.iana.org/assignments}registry[@id='%s']"%_id)
    title = normalize_title(registry.find(xml_title).text)
    for record in registry.findall("./{http://www.iana.org/assignments}record"):
        try:
            key = normalize_key(record.find(xml_key).text)
            value = normalize_value(record.find(xml_value).text)
            if key and value:
                d[key]=value
        except AttributeError, ae:
            print "# Skipping: %s"%repr(ae)
    return title, d

def main(source, ids):
    print "# -*- coding: UTF-8 -*-"
    print "# Generator: %s"%os.path.basename(__file__)
    print "# date:      %s"%datetime.date.today()
    print "# source:    %s"%source
    print "#            WARNING! THIS FILE IS AUTOGENERATED, DO NOT EDIT!"
    print ""
    
    if source.lower().startswith("https://") or source.lower().startswith("https://"):
        xml_data = urllib2.urlopen(source).read()
    elif os.path.isfile(source):
        with open(source,'r') as f:
            xml_data=f.read()
    else:
        raise Exception("Source not supported (url,file)!")
    
    xmlroot = ET.fromstring(xml_data)
    if not ids:
        # fetch all ids
        ids = (registry.attrib.get("id") for registry in xmlroot.findall("{http://www.iana.org/assignments}registry") if registry.attrib.get("id"))

    for _id in ids:
        title,d = xml_registry_to_dict(xmlroot, _id=_id)
        pprint(title,d)

if __name__=="__main__":
    ids = sys.argv[1].strip().split(",") if len(sys.argv)>1 else None
    main(source = URL_TLSPARAMETERS, ids = ids)
