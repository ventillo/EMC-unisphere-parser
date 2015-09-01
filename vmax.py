#!/usr/bin/python
#Library time 
import argparse, sys 
import requests, json, pprint, time, datetime

#vmax_get_lib.py file is a mandatory component 
import vmax_get_lib as api

# Disable warnings from untrusted server certificates
requests.packages.urllib3.disable_warnings() #disable certificate warnings

#User and pass definition, just in case it changes in future
user = 'smc'
password = 'smc'

#Get the arguments needed to run the unisphere parser
parser = argparse.ArgumentParser(description='VMAX restapi performance implementation for AT&T.')
rflags = parser.add_argument_group('Required arguments')
rflags.add_argument('-spa', required=False, help='Base Unisphere URL. e.g. https://10.0.0.1:8443/spa or /univmax')
rflags.add_argument('-time', required=False, help='Time frame in hours you want the report for. e.g. -time 8')
rflags.add_argument('-sid', required=False, help='full, or partial SID of the EMC frame')
rflags.add_argument('-fa', required=False, help='Specify the frontend director e.g. FA-10G')
rflags.add_argument('-da', required=False, help='Specify the frontend director e.g. DF-5A')
rflags.add_argument('-mode', required=True, help='Operational mode CHECK or DETAIL')

args = parser.parse_args()
symmID = args.sid
unisphere = args.spa
mode = args.mode
req_hours = args.time
FA = args.fa
DA = args.da



#Mode to check => cycle through SPAs defined on http://sanmobility.edc.cingular.net/storage_ops/tools/accessemc.html
if mode == 'CHECK':
  if unisphere:
    frames_under_spa = api.return_unisphere_frames(unisphere)
    unisphere = unisphere[8:]
    adjusted_frames_under_spa = []
    for sid in frames_under_spa:
      short_sid = sid[-4:]
      combined_sid = short_sid+':'+sid
      adjusted_frames_under_spa.append(combined_sid)
    all_spas = []
    tmp_spa = []
    tmp_spa.append(unisphere)
    tmp_spa.append(adjusted_frames_under_spa)
    all_spas.append(tmp_spa)
  else:
    all_spas = api.SPAs_get()
  #print all_spas
  for i in range(len(all_spas)):
    unisphere = all_spas[i]
    api.list_spa_esom(unisphere)

elif mode == "LIST":
  print "Listing arrays."
  all_spas = api.SPAs_get()
  unisphere_list = []
  #if -spa is defined, just list this one. If none is defined, list all 
  if unisphere:
    api.list_unisphere_frames(unisphere)
  else:
    for i in range(len(all_spas)):
      unisphere = "https://"+all_spas[i][0]
      api.list_unisphere_frames(unisphere)


elif mode == "FAS":
  print "This is the detailed output, under construction"
  if len(symmID) < 12:
    try:
      spa_list = api.select_spa(symmID)
      #This is the full SymmID from scart
      symmID = spa_list[1]
      #This is the SPA from the accesslist
      unisphere = spa_list[0]
    except:
      print "Sure about the SID number? Is it EMC? Is it in museum?"
      exit(1)

  #backwards compatibilty my ass
  unisphere_version = api.getVersion(unisphere, user, password)
  unisphere_major = int(unisphere_version[1])
  #Get a reasonable format for the unisphere version
  print "\nUnisphere version: %s (SID: %s)" % (unisphere_version,symmID)
  print "Unisphere address: %s\n" % unisphere

  #we need to specify what to get and from where
  requestObj = {'symmetrixId': symmID}

  if unisphere_major == 1 :
    requestObj = {"feDirectorKeyParam":
      requestObj
    }

  data_array = api.vmax_detail_metrics(unisphere,unisphere_major,symmID,req_hours,"/restapi/performance/FEDirector/keys",requestObj)
  if unisphere_major == 1 :
    data_array = data_array['feDirectorKeyResult']['feDirectorInfo']
  else:
    data_array = data_array['feDirectorInfo']
  result_length=len(data_array)
  detail_result = []
  for i in range(0,result_length-1):
    result_row = data_array[i]['directorId']
    detail_result.append(result_row)
  pprint.pprint(detail_result)

elif mode == "DAS":
  print "This is the detailed output, under construction"
  if len(symmID) < 12:
    try:
      spa_list = api.select_spa(symmID)
      #This is the full SymmID from scart
      symmID = spa_list[1]
      #This is the SPA from the accesslist
      unisphere = spa_list[0]
    except:
      print "Sure about the SID number? Is it EMC? Is it in museum?"
      exit(1)

  #backwards compatibilty my ass
  unisphere_version = api.getVersion(unisphere, user, password)
  unisphere_major = int(unisphere_version[1])
  #Get a reasonable format for the unisphere version
  print "\nUnisphere version: %s (SID: %s)" % (unisphere_version,symmID)
  print "Unisphere address: %s\n" % unisphere

  #we need to specify what to get and from where
  requestObj = {'symmetrixId': symmID}

  if unisphere_major == 1 :
    requestObj = {"beDirectorKeyParam":
      requestObj
    }

  data_array = api.vmax_detail_metrics(unisphere,unisphere_major,symmID,req_hours,"/restapi/performance/BEDirector/keys",requestObj)
  if unisphere_major == 1 :
    data_array = data_array['beDirectorKeyResult']['beDirectorInfo']
  else:
    data_array = data_array['beDirectorInfo']
  result_length=len(data_array)
  detail_result = []
  for i in range(0,result_length-1):
    result_row = data_array[i]['directorId']
    detail_result.append(result_row)
  pprint.pprint(detail_result)


elif mode == "DET":
  print "This is the detailed output, under construction"
  if len(symmID) < 12:
    try:
      spa_list = api.select_spa(symmID)
      #This is the full SymmID from scart
      symmID = spa_list[1]
      #This is the SPA from the accesslist
      unisphere = spa_list[0]
    except:
      print "Sure about the SID number? Is it EMC? Is it in museum?"
      exit(1)

  #backwards compatibilty my ass
  unisphere_version = api.getVersion(unisphere, user, password)
  unisphere_major = int(unisphere_version[1])
  #Get a reasonable format for the unisphere version
  print "\nUnisphere version: %s (SID: %s)" % (unisphere_version,symmID)
  print "Unisphere address: %s\n" % unisphere

  #Report time frame, defaults to 4 hours
  try:
    HOURS=3600*1000*int(req_hours)
  except:
    HOURS=3600*1000*4
  #timestamp in ms, for json usage  
  time_now_ms = int(time.time()*1000)
  #timestamp in s for normal usage
  time_now =  int(time.time())
  

  #we need to specify what to get and from where
  if FA:
    print "%s\n" % (FA)
    req_url = "/restapi/performance/FEDirector/metrics"
    requestObj = {'endDate': time_now_ms, #End time to specify is now.
      'startDate': time_now_ms-HOURS, #start time is 60 minutes before that (*)24hrs
      'metrics': ['HA_MB_PER_SEC','IO_RATE','RESPONSE_TIME_READ','RESPONSE_TIME_WRITE','PERCENT_BUSY'], #array of what metrics we want
      'symmetrixId': symmID, #symmetrix ID (full 12 digits) 
      'directorId': FA
      }
    if unisphere_major == 1 :
      requestObj = {"feDirectorParam":
        requestObj
      }
    # Just a header for the table	
    #print "{0:25} {1:15} {2:10} {3:8} {4:15} {5:25} {6:20}".format("TIME","TIMESTAMP","BUSY","RD_RESP","WR_RESP","IO/s", "MB/s")
    print "{0:23} {1:6} {2:9} {3:13} {4:12} {5:12}".format("TIME","BUSY","RD_RESP","WR_RESP","IO/s", "MB/s")
    print "--------------------------------------------------------------------------------------------------------------------------------"
    
    # Get the actual information for the whole array
    data_array = api.vmax_detail_metrics(unisphere,unisphere_major,symmID,req_hours,req_url,requestObj)
    result_length=len(data_array)
    detail_result = []
    for i in range(0,result_length-1):
      time_stamp = data_array[i]["timestamp"] / 1000
      time_point = datetime.datetime.fromtimestamp(time_stamp)
      busy = float(data_array[i]['PERCENT_BUSY'])
      io_sec = data_array[i]['IO_RATE']
      mb_sec = data_array[i]['HA_MB_PER_SEC']
      rd_resp = float(data_array[i]['RESPONSE_TIME_READ'])
      wr_resp = float(data_array[i]['RESPONSE_TIME_WRITE'])
      result_row = "{0} {1:4.0f}% {2:8.2f} {3:9.2f} {4:12.2f} {5:12.2f}".format(time_point,busy,rd_resp,wr_resp,io_sec,mb_sec)
      detail_result.append(result_row)
    pprint.pprint(detail_result)
  
  elif DA:
    print "%s\n" % (DA)
    req_url = "/restapi/performance/BEDirector/metrics"
    requestObj = {'endDate': time_now_ms, #End time to specify is now.
      'startDate': time_now_ms-HOURS, #start time is 60 minutes before that (*)24hrs
      'metrics': ['PERCENT_BUSY','IO_RATE','MB_RATE','READS','WRITES','PERCENT_NON_IO_BUSY'], #array of what metrics we want
      'symmetrixId': symmID, #symmetrix ID (full 12 digits) 
      'directorId': DA
      }
    if unisphere_major == 1 :
      requestObj = {"beDirectorParam":
        requestObj
      }
  
    # Just a header for the table	
    #print "{0:25} {1:15} {2:10} {3:8} {4:15} {5:25} {6:20}".format("TIME","TIMESTAMP","BUSY","RD_RESP","WR_RESP","IO/s", "MB/s")
    print "{0:23} {1:6} {2:9} {3:13} {4:12} {5:12}".format("PERCENT_BUSY","IO_RATE","MB_RATE","READS","WRITES","PERCENT_NON_IO_BUSY")
    print "--------------------------------------------------------------------------------------------------------------------------------"
    
    # Get the actual information for the whole array
    data_array = api.vmax_detail_metrics(unisphere,unisphere_major,symmID,req_hours,req_url,requestObj)
    result_length=len(data_array)
    detail_result = []
    for i in range(0,result_length-1):
      time_stamp = data_array[i]["timestamp"] / 1000
      time_point = datetime.datetime.fromtimestamp(time_stamp)
      busy = float(data_array[i]['PERCENT_BUSY'])
      io_sec = data_array[i]['IO_RATE']
      mb_sec = data_array[i]['MB_RATE']
      rd_io = float(data_array[i]['READS'])
      wr_io = float(data_array[i]['WRITES'])
      non_io_busy = float(data_array[i]["PERCENT_NON_IO_BUSY"])
      result_row = "{0} {1:4.0f}% {2:8.2f} {3:9.2f} {4:12.2f} {5:12.2f} {6:12.2f}".format(time_point,busy,mb_sec,rd_io,wr_io,io_sec,non_io_busy)
      detail_result.append(result_row)
    pprint.pprint(detail_result)

else:
  #search for the correct SPA and symmid from partial SID
  if len(symmID) < 12:
    try:
      spa_list = api.select_spa(symmID)
      #This is the full SymmID from scart
      symmID = spa_list[1]
      #This is the SPA from the accesslist
      unisphere = spa_list[0]
    except:
      print "Sure about the SID number? Is it EMC? Is it in museum?"
      exit(1)

  #backwards compatibilty my ass
  unisphere_version = api.getVersion(unisphere, user, password)
  unisphere_major = int(unisphere_version[1])
  #Get a reasonable format for the unisphere version
  print "\nUnisphere version: %s (SID: %s)" % (unisphere_version,symmID)
  print "Unisphere address: %s\n" % unisphere

  #Report time frame, defaults to 4 hours
  try:
    HOURS=3600*1000*int(req_hours)
  except:
    HOURS=3600*1000*4
  #timestamp in ms, for json usage  
  time_now_ms = int(time.time()*1000)
  #timestamp in s for normal usage
  time_now =  int(time.time())
  
  #we need to specify what to get and from where  
  requestObj = {'endDate': time_now_ms, #End time to specify is now.
    'startDate': time_now_ms-HOURS, #start time is 60 minutes before that (*)24hrs
    'metrics': ['WP','WP_LIMIT','RESPONSE_TIME_READ','RESPONSE_TIME_WRITE',], #array of what metrics we want
    'symmetrixId': symmID #symmetrix ID (full 12 digits)
    }
  if unisphere_major == 1 :
    requestObj = {"arrayParam":
      requestObj
    }
  # Just a header for the table	
  print "{2:22} {0:20} {1:10} {3:8} {4:10} {5:10}".format("TIMESTAMP","WP","DATE","WP%","READ RESP","WRITE RESP")
  print "--------------------------------------------------------------------------------"
  
  # Get the actual information for the whole array
  data_array = api.vmax_detail_metrics(unisphere,unisphere_major,symmID,req_hours,"/restapi/performance/Array/metrics",requestObj)
  #Need to know the length of response
  result_length=len(data_array)
  detail_result = []
  for i in range(0,result_length-1):
    time_stamp = data_array[i]["timestamp"] / 1000
    time_point = datetime.datetime.fromtimestamp(time_stamp)
    percentage = data_array[i]["WP"] / data_array[0]['WP_LIMIT'] * 100
    read_ms = data_array[i]["RESPONSE_TIME_READ"]
    write_ms = data_array[i]["RESPONSE_TIME_WRITE"]
    write_pending = data_array[i]["WP"]
    result_row = "{2} {0:13} {1:12g} {3:10.2f}% {4:10.2f} {5:10.2f}".format(time_stamp,write_pending,time_point,percentage,read_ms,write_ms)
    detail_result.append(result_row)
  pprint.pprint(detail_result)

  #we're in central European time, here - TODO: timezones
  time_now =  int(time.time())
  print "\nCurrent time (CET):", datetime.datetime.fromtimestamp(time_now)





