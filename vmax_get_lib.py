import requests, json, pprint, time, socket, datetime
#Needed for HTML parsing and getting list of SPAs:
from HTMLParser import HTMLParser, HTMLParseError
from htmlentitydefs import name2codepoint
import re, urllib2, sys, argparse

requests.packages.urllib3.disable_warnings() #disable certificate warnings


#User and pass definition, just in case it changes in future
user = 'smc'
password = 'smc'

def help():
  with open('readme.txt', 'r') as f:
    read_data = f.read()
    print f

#COnstrucitng the array of SPAs and SIDs beneath:
# {SPA{sid, sid, sid...}, SPA{sid, sid, sid...}}
#Ouch, the classes and HTML parsing
class _HTMLToText(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'br') and not self.hide_output:
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self._buf.append('\n')

    def handle_endtag(self, tag):
        if tag == 'p':
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = False

    def handle_data(self, text):
        if text and not self.hide_output:
            self._buf.append(re.sub(r'\s+', ' ', text))

    def handle_entityref(self, name):
        if name in name2codepoint and not self.hide_output:
            c = unicode(name2codepoint[name])
            self._buf.append(c)

    def handle_charref(self, name):
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith('x') else int(name)
            self._buf.append(unicode(n))

    def get_text(self):
        return re.sub(r' +', ' ', ''.join(self._buf))
	
def html_to_text(html):
    """
    Given a piece of HTML, return the plain text it contains.
    This handles entities and char refs, but not javascript and stylesheets.
    """
    parser = _HTMLToText()
    try:
        parser.feed(html)
        parser.close()
    except HTMLParseError:
        pass
    return parser.get_text()

def SPAs_get():
  #Get the list of all unispheres
  #print "Getting the list of Unispheres from http://sanmobility.edc.cingular.net/storage_ops/tools/accessemc.html"
  #http://sanmobility.edc.cingular.net/storage_ops/tools/unispheres.htm
  try:
    response = urllib2.urlopen('http://sanmobility.edc.cingular.net/storage_ops/tools/accessemc.html')
    #print "Unispheres read"
  except:
    print "ERROR: %s" % e.reason
    
  #Read it and close the stream
  html = response.read()
  response.close()
  
  #Get the list of all arrays from scart
  #print "Getting list of frames from SCaRT http://scart.it.att.com/storage/audit/FusionCharts/dashboard/csv/all-frames.html"
  try:
    response = urllib2.urlopen('http://scart.it.att.com/storage/audit/FusionCharts/dashboard/csv/all-frames.html')
    #print "SCaRT read"
  except:
    print "ERROR: %s" % e.reason
    
  #Read it and close the stream
  html_scart_storage = response.read()
  response.close()
  
  #Now to process the mess
  spa_and_array = re.split("\n",html_to_text(html))
  spa_and_port = re.split("\n",html)

  spas_url = []
  spas_frames = []
  
  #Get EMC storage frames from SCaRT to array
  storage_frames = re.sub('</tr>',"</tr><tr><td><br></td></tr>",html_scart_storage)
  storage_frames = re.split("\n", html_to_text(storage_frames))
  storage_frame_array = []
  for sid in storage_frames:
    sid_array = []
    sid_array = re.split(" ",sid)
    if sid_array[8] == 'EMC': #8th is the vendor, 7th is the SID
      storage_frame_array.append(sid_array)
  #pprint.pprint(storage_frame_array)
  
  for line in spa_and_port:
    if "href" in line:
      line = re.search('\"https://(.+?)\"',line)
      if line != None:
        spa = unicode(line.group(1))
        if re.search('84',spa) != None:
          spas_url.append(spa)
  
  for line_array in spa_and_array:
    if "Arrays" in line_array:
      line_array = re.search(':(.+?)\(Arrays(.+?)\)',line_array)
      #print line_array
      if line_array != None:
        spa_fqdn = str.strip(str(line_array.group(1)))
        spa_server_name = re.search('^(.+?)\.',spa_fqdn)
        #print spa_fqdn
        if spa_server_name != None:
          spa_hostname = spa_server_name.group(1)
        spa_frames = unicode(line_array.group(2))
        spa_frames = re.split(",",spa_frames)
        #cleanup SIDs
        for index in range(len(spa_frames)):
          try:
            spa_frames[index] = spa_frames[index].strip()
            if len(spa_frames[index]) < 4:
              spa_frames[index] = "0"+spa_frames[index]
          except:
            print "Error in frame # acquisition"
          #find the full SID maybe?
          for sid_row in storage_frame_array:
            #spa_frames[index] = spa_frames[index]+":NA"
            sid_row_lookup = re.search(spa_frames[index]+"$",sid_row[7])
            if sid_row_lookup != None:
              spa_frames[index] = spa_frames[index]+":"+sid_row[7]
            else: 
              if len(spa_frames[index]) == 12:
                spa_frames[index] = spa_frames[index]+":"+spa_frames[index]
              #print sid_row[7]
        #initialize the array - needs to be here to clear for each row
        spas_frames_items = []
        #Pair the link and storage frames
        spa_port_url = 'Parse_error'
        for spa_url in spas_url:
          url_lookup = re.search(spa_hostname,spa_url)
          if url_lookup != None:
            spa_port_url = spa_url
        #construct the sub-lists 
        spas_frames_items.append(spa_port_url)
        spas_frames_items.append(spa_frames)
        #put it together to multi-dim list
        spas_frames.append(spas_frames_items)
  return spas_frames

#Function to print out a header with the unisphere URL and version. Returns the major version number
def version_check_header(unisphere):
  print unisphere
  try:
    version = getVersion(unisphere, user, password)
  except:
    version = 666
  if version == 666:
    unisphere_major = 666
    print "You have a big problem, mister"
  else:
    unisphere_major = int(version[1])
  #print "https://%s" % spa_full_array[i][0]
  print "Unishpere version: "+str(unisphere_major)
  return unisphere_major
	  

def list_spa_esom(spa_full_array):
  unisphere = "https://"+spa_full_array[0]
  #Report time frame, defaults to 4 hours
  HOURS=3600*1000*24
  #timestamp in ms, for json usage  
  time_now_ms = int(time.time()*1000)
  #timestamp in s for normal usage
  time_now =  int(time.time())

  print "\n--------------------------------------------------------------------------------"
  unisphere_major = version_check_header(unisphere)
  print "--------------------------------------------------------------------------------"
  for j in range(len(spa_full_array[1])):
    array_sid = re.split(':',spa_full_array[1][j])
    if len(array_sid) > 1:
      full_sid = array_sid[1]
      sys.stdout.write("Checking frame -> ") 
      sys.stdout.write(full_sid)
      sys.stdout.write(": ")
      #we need to specify what to get and from where 
      requestObj = {'endDate': time_now_ms, #End time to specify is now.
        'startDate': time_now_ms-HOURS, #start time is 60 minutes before that (*)24hrs
        'metrics': ['WP','WP_LIMIT','RESPONSE_TIME_READ','RESPONSE_TIME_WRITE',], #array of what metrics we want
        'symmetrixId': full_sid #symmetrix ID (full 12 digits)
        }
      if unisphere_major == 1 :
        requestObj = {"arrayParam":
        requestObj
        }
      try:
        result = vmax_detail_metrics(unisphere,unisphere_major,full_sid,24,"/restapi/performance/Array/metrics",requestObj)
        if result[0]['timestamp'] <= time_now_ms:
          print "%s records found, OK" % len(result) 
        else:
          print "ERROR: %s" % result
      except:
        print "ERROR acquiring data from "+array_sid[1]
        exception = 1
    else:
      #now if we cannot find the frame in scart, but we know it exists in unisphere
      if len(array_sid[0]) == 12:
        try:
          result = vmax_detail_metrics(unisphere,unisphere_major,array_sid[0],24,"/restapi/performance/Array/metrics",requestObj)
          if result[0]['timestamp'] <= time_now_ms:
            print "%s records found, OK" % len(result) 
          else:
            print "ERROR: %s" % result
        except:
          print "ERROR acquiring data from "+array_sid[1]
          exception = 1
      else:
        #not in scart and no idea if in unisphere
        print "Checking frame -> %s: ERROR, unable to locate frame in SCaRT" % array_sid[0]

def select_spa(symmID):
  unisphere_list = []
  spa_full_array = SPAs_get()
  for i in range(len(spa_full_array)):
    unisphere = "https://"+spa_full_array[i][0]
    for j in range(len(spa_full_array[i][1])):
      array_sid = re.split(':',spa_full_array[i][1][j])
      if len(array_sid) > 1:
        full_sid = array_sid[1]
        #short_sid = array_sid[0]
        sid_row_lookup = re.search(symmID+"$",full_sid)
        if sid_row_lookup != None:
          unisphere_list.append(unisphere)
          unisphere_list.append(full_sid) 
          break 
  #returns a list of [unisphere][full_sid]
  return unisphere_list

def vmax_list_for_unisphere(unisphere,unisphere_major):
  target_url = unisphere+"/restapi/performance/Array/keys"
  try:
    responseObj = jsonGet(target_url, user, password)
  except: 
    return "Unisphere not accessible. Services running? Correct server? Is it on network?" 
  if unisphere_major > 1:
    responseObj = responseObj["arrayInfo"]
  else:
    responseObj = responseObj["arrayKeyResult"]["arrayInfo"]
  symmIDs = []
  for i in range(0,len(responseObj)):
    symmIDs.append(responseObj[i]['symmetrixId'])
  return symmIDs



def vmax_detail_metrics(unisphere,unisphere_major,symmID,req_hours,url_append,requestObj):
  #Report time frame, defaults to 4 hours
  try:
    HOURS=3600*1000*int(req_hours)
  except:
    HOURS=3600*1000*4
  #timestamp in ms, for json usage  
  time_now_ms = int(time.time()*1000)
  #timestamp in s for normal usage
  time_now =  int(time.time())
  
  #The target we want info from - TODO: interactive
  target_url = unisphere+url_append

  #We do want some data
  responseObj = jsonPost(target_url,requestObj,user,password)

  #Different versions of unishpere have different structures
  if unisphere_major == 1:
    try:
      data_array = responseObj["iterator"]["resultList"]["result"]
    except:
      try:
         error = responseObj['message']
      except:
  	    error = responseObj
      #print "Error fetching data: %s" % error
      #print responseObj
      return error
      #exit();
  else:
    try:
      data_array = responseObj["resultList"]["result"]
    except:
      try:
  	    error = responseObj['message']
      except:
  	    error = responseObj
      #print "Error fetching data: %s" % error
      return error
      #exit();
  #Need to know the length of response
  result_length=len(data_array)
  if result_length > 0:
    return data_array	
  else:
  	return responseObj 
  

# Disable warnings from untrusted server certificates
try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings()
except Exception:
    print("Ignore messages related to insecure SSL certificates")

################
## make the json GET call to the public api
################
def jsonGet(targetUrl, user, password):
    # set the headers for how we want the response
    headers = {'content-type': 'application/json','accept':'application/json'}

    #make the actual request, specifying the URL, the JSON from above, standard basic auth, the headers and not to verify the SSL cert.
    #r = requests.post(target_uri, requestJSON, auth=('smc', 'smc'), headers=headers, verify=False)
    try:
        r = requests.get(targetUrl, auth=(user, password), headers=headers, verify=False)
    except:
        print("Exception:  Can't connect to API server URL:  " + targetUrl)
        print("Exiting")
        exit(1)

    #take the raw response text and deserialize it into a python object.
    try:
        responseObj = json.loads(r.text)
    except:
        print("Exception")
        print(r.text)

    # this test is specific to the contents of the Unisphere API
    if not responseObj.get("success", True):
        print(responseObj.get("message", "API failed to return expected result"))
        jsonPrint(responseObj)
        return dict()

    return responseObj

################
## make the json POST call to the public api
################
def jsonPost(targetUrl, requestObj, user, password):
    # set the headers for how we want the response
    headers = {'content-type': 'application/json','accept':'application/json'}

   #turn this into a JSON string
    requestJSON = json.dumps(requestObj, sort_keys=True, indent=4)
    #print(requestJSON)

    #make the actual request, specifying the URL, the JSON from above, standard basic auth, the headers and not to verify the SSL cert.
    try:
        r = requests.post(targetUrl, requestJSON, auth=(user, password), headers=headers, verify=False)
    except:
        print("Exception:  Can't connect to API server URL:  " + targetUrl)
        #print("Exiting")
        exit(1)

    #take the raw response text and deserialize it into a python object.
    try:
        responseObj = json.loads(r.text)
    except:
        print("Exception")
        print(r.text)
    #jsonPrint(responseObj)
    return responseObj


################
## print a json object nicely
################
def jsonPrint(jsonObj):
	print(json.dumps(jsonObj, sort_keys=False, indent=2))


#################################################################
## Functions to implement Unisphere REST API for VMAX3
#################################################################


################
## get the version of Unisphere (the API)
################
def getVersion(URL, user, password):
  target_uri = "%s/restapi/common/Application/list" % (URL)
  if 'https://Parse_error/restapi/common/Application/list' in target_uri:
    return 666
  else:
    responseKey = 'version'
    responseObj = jsonGet(target_uri, user, password)
    try: 
      unisphere_application=responseObj['application']['applicationInfo']
    except:
      unisphere_application=responseObj['applicationInfo']
    application_count=len(unisphere_application)
    unisphere_version = 0
    for i in range(0,application_count):
      if unisphere_application[i]['registeredName'] == 'UNIVMAX':
        unisphere_version = unisphere_application[i][responseKey]
    if unisphere_version == 0:  
      return dict()
    else:
      return unisphere_version

################
## get a list of symmetrix serial #'s known by Unisphere
################
def getSymms(URL, user, password):
    target_uri = "%s/univmax/restapi/system/symmetrix" % (URL)
    responseKey = 'symmetrixId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def list_unisphere_frames(unisphere):
  print "\n--------------------------------------------------------------------------------"
  unisphere_major = version_check_header(unisphere)
  print "--------------------------------------------------------------------------------"
  symmID_all_frames = vmax_list_for_unisphere(unisphere,unisphere_major) 
  if unisphere_major == 666:
    print "Not able to get list of EMCs"
  else:
    for i in range(len(symmID_all_frames)):
      sys.stdout.write(symmID_all_frames[i]) 
      sys.stdout.write("\n")
  print "--------------------------------------------------------------------------------"

def return_unisphere_frames(unisphere):
  unisphere_major = version_check_header(unisphere)
  symmID_all_frames = vmax_list_for_unisphere(unisphere,unisphere_major) 
  if unisphere_major == 666:
    print "Not able to get list of EMCs"
  else:
    return symmID_all_frames

################
## This call queries for a specific Authorized Symmetrix Object that is compatible with slo provisioning using its ID
################
def getSymm(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/system/symmetrix/%s" % (URL, symmId)
    responseKey = 'symmetrix'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()


def getSloSymms(URL, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix" % (URL)
    responseKey = 'symmetrixId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSloSymm(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s" % (URL, symmId)
    responseKey = 'symmetrix'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

def getSloDirectors(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/director" % (URL, symmId)
    responseKey = 'directorId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSloDirector(URL, symmId, directorId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/director/%s" % (URL, symmId, directorId)
    responseKey = 'director'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

def getSloPorts(URL, symmId, directorId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/director/%s/port" % (URL, symmId, directorId)
    responseKey = 'symmetrixPortKey'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSloPort(URL, symmId, directorId, portId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/director/%s/port/%s" % (URL, symmId, directorId, portId)
    responseKey = 'symmetrixPort'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

def getSloHosts(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/host" % (URL, symmId)
    responseKey = 'hostId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSloHost(URL, symmId, hostId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/host/%s" % (URL, symmId, hostId)
    responseKey = 'host'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

def getSloHostgrps(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/hostgroup" % (URL, symmId)
    responseKey = 'hostGroupId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSloHostgrp(URL, symmId, grpId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/hostgroup/%s" % (URL, symmId, grpId)
    responseKey = 'hostGroup'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

def getSloInitiators(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/initiator" % (URL, symmId)
    responseKey = 'initiatorId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSloInitator(URL, symmId, initiatorId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/initiator/%s" % (URL, symmId, initatorId)
    responseKey = 'initiator'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

def getSloMaskingviews(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/maskingview" % (URL, symmId)
    responseKey = 'maskingViewId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSloMaskingview(URL, symmId, mvId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/maskingview/%s" % (URL, symmId, mvId)
    responseKey = 'maskingView'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

def getSloMvConnections(URL, symmId, mvId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/maskingview/%s/connections" % (URL, symmId, mvId)
    responseKey = 'maskingViewConnection'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSloPorts(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/port" % (URL, symmId)
    responseKey = 'symmetrixPortKey'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSloPortgrps(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/portgroup" % (URL, symmId)
    responseKey = 'portGroupId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSloPortgrp(URL, symmId, pgId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/portgroup/%s" % (URL, symmId, pgId)
    responseKey = 'portGroup'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

def getSlos(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/slo" % (URL, symmId)
    responseKey = 'sloId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSlo(URL, symmId, sloId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/slo/%s" % (URL, symmId, sloId)
    responseKey = 'slo'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

def getSrpList(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/srp" % (URL, symmId)
    responseKey = 'srpId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

def getSrp(URL, symmId, srpId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/srp/%s" % (URL, symmId, srpId)
    responseKey = 'srp'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

################
## get a list of Storage Groups on a given SLO Symmetrix
################
def getSgList(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/storagegroup" % (URL, symmId)
    responseKey = 'storageGroupId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

################
## get the details of a particular SLO managed Storage Group
################
def getSg(URL, symmId, sgId, user, password):
    target_uri = "%s/univmax/restapi/sloprovisioning/symmetrix/%s/storagegroup/%s" % (URL, symmId, sgId)
    responseKey = 'storageGroup'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

################
## get a list of Thin Pools on a given Symmetrix
################
def getThinPoolList(URL, symmId, user, password):
    target_uri = "%s/univmax/restapi/provisioning/symmetrix/%s/thinpool" % (URL, symmId)
    responseKey = 'poolId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey]
    else:
        return dict()

################
## get the details of a particular Thin Pool
################
def getThinPool(URL, symmId, tpId, user, password):
    target_uri = "%s/univmax/restapi/provisioning/symmetrix/%s/thinpool/%s" % (URL, symmId, tpId)
    responseKey = 'poolId'
    responseObj = jsonGet(target_uri, user, password)
    if responseKey in responseObj:
        return responseObj[responseKey][0]
    else:
        return dict()

