#Simple Command Line Arg script for testing a random dataset&parameter given a HAPI url
import sys
import requests
import json
import urllib.request
from urllib.request import urlopen
import random
import pandas as pd
import datetime
from datetime import timedelta
import ssl
import certifi

import time

import csv


from hapiclient import hapi


from hapiplot import hapiplot

#avoid ssl veri
#ssl._create_default_https_context = ssl._create_unverified_context











#declaring variables and defining functions

finalLog = ['**********************************', 'RESULTS:']

exceptLog = ['**********************************', 'ERRORS:']

servers    = ['http://hapi-server.org/servers/SSCWeb/hapi',
 'https://cdaweb.gsfc.nasa.gov/hapi',
 'http://planet.physics.uiowa.edu/das/das2Server/hapi', #works very rarely, website is messed up
 'https://iswa.gsfc.nasa.gov/IswaSystemWebApp/hapi',
 'http://lasp.colorado.edu/lisird/hapi',
 'http://hapi-server.org/servers/TestData2.0/hapi',
 'http://amda.irap.omp.eu/service/hapi', 
 'https://vires.services/hapi'
 ]

#error/success color escape codes
class tColors:
    success = '\033[92m'
    fail = '\033[91m'
    endC = '\033[0m'
    
    

#tests the server for a 200 response code
def testHTTPCode(cS):
    x = requests.get(cS) #, verify=False)
    
    if x.status_code == 200:
        print(f"{tColors.success}Server is up!{tColors.endC}")
        
    else:
        print(f"{tColors.fail}ERRROR, BAD HTTP response status code: {tColors.endC}" + "[" + str(x.status_code) + "]")
        #sys.exit("Expected 200 response code, got HTTP response status code of " + str(x.status_code) + "...TERMINATE PROCESS")


    







#begin testing


def hapiTest(cHS):
    
    #a way to measure process time
    start_time = time.perf_counter ()
    

    #get url from system
    """
    try:
        cHS = sys.argv[1]
        
    except:
        print("URL NOT RECEIVED")
        sys.exit("URL NOT RECEIVED, TERMINATE PROCESS")
    """
    
    #make sure url matches known list of servers
    if cHS in servers:
        print("URL MATCHES KNOWN HAPI SERVER")
            
    else:
        print("URL DOES NOT MATCH KNOWN HAPI SERVER")
        #sys.exit("URL DOES NOT MATCH KNOWN HAPI SERVER, TERMINATE PROCESS")
        
    
    
    #test HTTP code to check for 200 response
    testHTTPCode(cHS)
    
    
    #create the catalog URL
    catalogURL = cHS
    catalogURL += '/catalog'
    
    
    try:
    
        #load all available dataset ids and store them in a python list for further use
            
        serverResponse = urlopen(catalogURL)
        DataSetList = json.loads(serverResponse.read())
        refinedList = DataSetList.get('catalog') #just a note, hapi 2.0 has the 'catalog' key:value item at the top of the json, while 3.0 has it at the bottom. 
            
            #get HAPI version for later use
        hapiVer = DataSetList.get('HAPI')
            
        print(hapiVer)
            
            
            #this actually returns a python list of python dictionaries... hence the .get of the key "id"
            #down below to get its value
                
                
        idList = []
        for i in range(len(refinedList)):
            idList.append(refinedList[i].get('id')) #so far only AMDA and planet physics works?
                    
                    
        print(idList[0])
        print(idList[-1])
        print(len(refinedList))
        
    except Exception as e:
        
        exceptLog.append(e + " occured on " + cHS + "  process: getting dataset IDs")
        
        
    #get a random dataset ID to choose time/params from the info
    randID = random.choice(idList)
    print(randID)
    infoURL = cHS
    #create the info URL
    infoURL += '/info?id=' + randID
    
    
    
    #make a list of all available parameters for said dataset (from info url) and choose a random one
    
    try:
    
        #load all available parameter ids and store them in a python list for further use
            
        serverResponse = urlopen(infoURL)
        DataSetList = json.loads(serverResponse.read())
        refinedList = DataSetList.get('parameters') #just a note, hapi 2.0 has the 'catalog' key:value item at the top of the json, while 3.0 has it at the bottom. 
        #this actually returns a python list of python dictionaries... hence the .get of the key "name"
        #down below to get the parameter name
            
            
        pList = []
        for i in range(len(refinedList)):
            pList.append(refinedList[i].get('name')) #so far only AMDA and planet physics works?
                
                
        print(pList[0])
        print(pList[-1])
        print(len(refinedList))
        
    except Exception as e:
       
        exceptLog.append(e + " occured on " + cHS + "  process: getting parameters")
        
        
        
        
        
    #get a random parameter
    randPara = random.choice(pList)
    print(randPara)
    
    #search for the startDate and stopDate within a random dataset. 
    try:
        serverResponse = urlopen(infoURL)#, cafile='/Users/palacst1/Desktop/finalPemCert.pem')
        infoList = json.loads(serverResponse.read())
        startDate = infoList.get('startDate')
        stopDate = infoList.get('stopDate')
        
        print(str(startDate) + '\n' +  str(stopDate))
        
        #convert the ISO 8061 strings to python datetime objects for later random date generation
        #with a special case for different servers that use microseconds and special case for DAS2 and HapiTestServer as they have odd time formats
        
        if cHS == "http://hapi-server.org/servers/TestData2.0/hapi": #special case for Hapi test server
            startDate = datetime.datetime.strptime(startDate,'%Y-%m-%dZ')
            stopDate = datetime.datetime.strptime(stopDate,'%Y-%m-%dZ')
            
        elif cHS == "http://planet.physics.uiowa.edu/das/das2Server/hapi": #special case or Das2 server
            
            if randID == 'Cassini/Ephemeris/Saturn,60s': #very specific time formatting for this one dataset that has unorthodox time format compared to the rest of the server
                startDate = datetime.datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S")
                stopDate = datetime.datetime.strptime(stopDate, "%Y-%m-%d")
            else:
                startDate = datetime.datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S")
                stopDate = datetime.datetime.strptime(stopDate, "%Y-%m-%dT%H:%M")
            
        
        elif len(startDate) > 20: #special case for microseconds, checks the length of the ISO time string
            
            startDate = datetime.datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S.%fZ")
            stopDate = datetime.datetime.strptime(stopDate, "%Y-%m-%dT%H:%M:%S.%fZ")
            
        
            
        else: #case for no microseconds
            startDate = datetime.datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%SZ")
            stopDate = datetime.datetime.strptime(stopDate, "%Y-%m-%dT%H:%M:%SZ")
            
        
        #generate a test "start date" one hour before the dataset stopdate, to check if the latest data is all good/parseable (therefore the rest of the data should be ok.)
        k = 15
        testDate = stopDate - timedelta(minutes = k)
    
        print(str(startDate) + '\n' +  str(testDate))
    
    except Exception as e:
        
        exceptLog.append(e + " occured on " + cHS + " process:  getting timestamps")
        
        
    #using the start and stop date, select a random start and stop date within the timeframe for use in sampling(using a pandas dataframe method I stole from stackoverflow)
    
    
    
        
        
    
        
        
    
        
    
    
    
    
    
    #convert testDate(this is our start date for testing purposes) to ISO Format string(do the same for stopDate(Also a datetime object))
    testStartDate = testDate.isoformat() + 'Z'
    
    testStopDate = stopDate.isoformat() + 'Z'
    
    print(testStartDate)
    print(testStopDate)
    
    
    #create the final random link- with a special case for 2.0 vs 3.0- & only to get CSVs!
    
    
    if hapiVer == '3.0':
        
    
        finalURL = cHS + '/data?id=' + randID + '&parameters=' + randPara + '&start=' + testStartDate + '&stop=' + testStopDate + '&format=csv&include=header'
    
        print(finalURL)
        
    if hapiVer == '2.0' or hapiVer == '1.1':
        finalURL = cHS + '/data?id=' + randID + '&parameters=' + randPara + '&time.min=' + testStartDate + '&time.max=' + testStopDate + '&format=csv&include=header'
    
        print(finalURL)
        
    
    
    
    #With the random link, check to see if the resulting CSV is parseable! 
    #and if the metadata allows for a good plot using Hapiplot!
    #try:
        
    try:
            
        try:
                
            serverResponse = urlopen(finalURL)#, cafile='/Users/palacst1/Desktop/finalPemCert.pem')
            DataSetList = csv.reader(serverResponse)
            
        except Exception as e:
           
           exceptLog.append(e + " occured on " + cHS + " process:  loading CSV")
            
    
        server     = cHS
        dataset    = randID
        parameters = randPara
        start      = testStartDate
        stop       = testStopDate
        opts       = {'logging': True, 'usecache': True}
            
        data, meta = hapi(server, dataset, parameters, start, stop, **opts)
            
            
        popts = {'useimagecache': False, 'logging': True, 'returnimage': True}
            
        hapiplot(data, meta, **popts)
        # Plot parameter 
            
            
            
        end_time = time.perf_counter ()
            
        finalLog.append(cHS + ' plotted successfully.')
        print(f"{tColors.success}Success!!!!!{tColors.endC}" + " Time: " + str(round((end_time - start_time), 3)) + " seconds")
            #sys.exit(0)

    except Exception as e:
       
        exceptLog.append(str(e) + " occured on " + cHS + " process:  plotting data")
        
        
        
        
        print(f"{tColors.fail}HAPI failed to plot on {tColors.endC}" + str(cHS))
        finalLog.append(cHS + '--ERROR')
    #sys.exit('CSV PARSE FAILED! COULD NOT PARSE CSV with python.csv')
    #return status code? (stdout?)
    #0 is failure, 1 is success  - talk to Jeremy


#final notes: some sites have UTC Zulu as :XXX, some have it as .XXX
#also hapi 2.0 uses time.min and time.max to stream data...
#I get 50% success rate on Vires as they have both .Z and :Z 
#might wanna only request CSVs as not all servers have json response capability
#hopkins network is blocking from certain sites in Firefox 


#Test works on... Servers with microsecond and second time format.. Others to be fixed
"""
  #  http://hapi-server.org/servers/SSCWeb/hapi Yes
   # http://datashop.elasticbeanstalk.com/hapi - SERVER DOWN
   # https://cdaweb.gsfc.nasa.gov/hapi - YES-%100
    #http://planet.physics.uiowa.edu/das/das2Server/hapi No... Dates(.) yet to make a 1.1 url adapter has its own weird outdated time structure. Some datasets work for plotting but not all
   ##https://iswa.gsfc.nasa.gov/IswaSystemWebApp/hapi Yes
   #http://lasp.colorado.edu/lisird/hapi Yes
    #http://hapi-server.org/servers/TestData2.0/hapi NO... Dates (.) #also has its own dates that are a tad too short... unimportant as it is a test site
    http://amda.irap.omp.eu/service/hapi YES- %100 Lol i think I shut it down by lots of tests
    https://vires.services/hapi YES- 100% lets go accomodated for both time types 
"""



    
def main():
    
    test_start_time = time.perf_counter ()
    
    for z in servers:
        hapiTest(z)
    
    for o in finalLog:
        
        print(o)
        
    
    
    test_end_time = time.perf_counter ()
    
    print("Total Test Time: " + str(round((test_end_time - test_start_time), 3)) + " seconds")
    
    #print all exceptions that occured for debugging purposes:
    
    for j in exceptLog:
        print(j)
main()
    
    

#das2 has the data on dataset info ID page?? Works 50% of the time??????

#Just realized.. Das2 streams some of its data from a deprecated server: http://mapsview.engin.umich.edu/
#DAS2 is a mess.. wrap in try errors

#SSC web is plottable 99% of the time... 


    

"""
ERRORS SO FAR:
    1. Some parameter data are strings... like vectorstr on HAPITEST2
    2. Certain parameters have no data for the current 15 minute time sample- implement a dynamic way around this
    3. Certain servers have non-standard data organization
    4. some servers have no data for like the last 8 hours of listed date.. but as soon as you get to its start you are met with GBs of data- hard to navigate the 222 function as some servers measure by milliseconds, others daily. lol


4. MIGHT not get the first parameter of time: (1.1 it is "time", 2.0 it is "Time", 3.0 it is "Timestamp")
"""
    
    







    




