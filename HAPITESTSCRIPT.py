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

# set up special matplotlib plotting requirements


 














USER_AGENT = 'hapibot-a/1.0; https://github.com/hapi-server/data-specification/wiki/hapi-bots.md#hapibot-a'

#declaring variables and defining functions

finalLog = ['**********************************', 'RESULTS:']

exceptLog = ['**********************************', 'ERRORS:']
 
servers    = ['http://hapi-server.org/servers/SSCWeb/hapi',
 'https://cdaweb.gsfc.nasa.gov/hapi',
 'http://planet.physics.uiowa.edu/das/das2Server/hapi', 
 'https://iswa.gsfc.nasa.gov/IswaSystemWebApp/hapi',
 'http://lasp.colorado.edu/lisird/hapi',
 'http://hapi-server.org/servers/TestData2.0/hapi',
 'http://amda.irap.omp.eu/service/hapi', 
 'https://vires.services/hapi',
 'https://jfaden.net/HapiServerDemo/hapi'
 ]

#servers    = ['http://hapi-server.org/servers/SSCWeb/hapi','https://jfaden.net/HapiServerDemo/hapi' ]
 

 

#error/success color escape codes
class tColors:
    success = '\033[92m'
    fail = '\033[91m'
    endC = '\033[0m'
    
    

#tests the server for a 200 response code
def testHTTPCode(cS):
    headers= { "User-Agent" : USER_AGENT }
    x = requests.get(cS,headers=headers) #, verify=False)
    
    if x.status_code == 200:
        print(f"{tColors.success}Server is up!{tColors.endC}")
        
    else:
        print(f"{tColors.fail}ERRROR, BAD HTTP response status code: {tColors.endC}" + "[" + str(x.status_code) + "]")
        


    







#begin testing

def myurlopen( url ):
    print('url ' + url )
    headers = { 'User-Agent': USER_AGENT }
    response = requests.get(url, headers=headers)
    return response
    
def hapiTest(cHS,seed):
    
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

    random.seed(seed)
    
    #test HTTP code to check for 200 response
    testHTTPCode(cHS)
    
    
    #create the catalog URL
    catalogURL = cHS
    catalogURL += '/catalog'
    
    try:
    
        #load all available dataset ids and store them in a python list for further use
        
        serverResponse = myurlopen(catalogURL)
        DataSetList = json.loads(serverResponse.text)
        refinedList = DataSetList.get('catalog') #just a note, hapi 2.0 has the 'catalog' key:value item at the top of the json, while 3.0 has it at the bottom. 
            
            #get HAPI version for later use
        hapiVer = DataSetList.get('HAPI')
            
        print('hapiVer=',hapiVer)
            
            
            #this actually returns a python list of python dictionaries... hence the .get of the key "id"
            #down below to get its value
                
                
        idList = []
        for i in range(len(refinedList)):
            idList.append(refinedList[i].get('id')) 
                    
                    
        print('first parameter: ',idList[0])
        print('last parameter: ',idList[-1])
        print('len(refinedList)=',len(refinedList))
        sys.stdout.flush()
        
    except Exception as e:
        print('Exception!')
        sys.stdout.flush()
        exceptLog.append(str(e) + " occured on " + cHS + "  process: getting dataset IDs")
        
        
    #get a random dataset ID to choose time/params from the info
    
    randID = random.choice(idList)
    print('randID=', randID)
    infoURL = cHS
    #create the info URL
    infoURL += '/info?id=' + randID
    
    #make a list of all available parameters for said dataset (from info url) and choose a random one
        
    try:
    
        #load all available parameter ids and store them in a python list for further use
        sys.stdout.flush()
 
        serverResponse = myurlopen(infoURL)
        DataSetList = json.loads(serverResponse.text)
        refinedList = DataSetList.get('parameters') #just a note, hapi 2.0 has the 'catalog' key:value item at the top of the json, while 3.0 has it at the bottom. 
        #this actually returns a python list of python dictionaries... hence the .get of the key "name"
        #down below to get the parameter name
            
            
        pList = []
        for i in range(len(refinedList)):
            pList.append(refinedList[i].get('name')) 
                
                
        print('first parameter: ',pList[0])
        print('last parameter: ',pList[-1])
        print('len(refinedList)=',len(refinedList))
        
    except Exception as e:
       
        exceptLog.append(str(e) + " occured on " + cHS + "  process: getting parameters")
        
        
        
        
        
    #get a random parameter
    del pList[0] #gets rid of time(no need to plot time)
    randPara = random.choice(pList)
    print('randPara=',randPara)
    
    #search for the startDate and stopDate within a random dataset. 
    try:
        sys.stdout.flush()

        serverResponse = myurlopen(infoURL)
        infoList = json.loads(serverResponse.text)
        startDate = infoList.get('startDate')
        stopDate = infoList.get('stopDate')
        
        sampleStartDate= infoList.get('sampleStartDate')
        sampleStopDate= infoList.get('sampleStopDate')
        
        print(str(startDate) + '/' +  str(stopDate))
        if sampleStartDate!=None :
            print('sampleStartDate ' + str(sampleStartDate) +  '/' +  str(sampleStopDate))
        else:
            print('sampleStartDate not available')
            
        #convert the ISO 8061 strings to python datetime objects for later random date generation
        #with a special case for different servers that use microseconds and special case for DAS2 and HapiTestServer as they have odd time formats
        
        if cHS == "http://hapi-server.org/servers/TestData2.0/hapi": #special case for Hapi test server
            startDate = datetime.datetime.strptime(startDate,'%Y-%m-%dZ')
            stopDate = datetime.datetime.strptime(stopDate,'%Y-%m-%dZ')
            
        elif cHS == "http://planet.physics.uiowa.edu/das/das2Server/hapi": #special case or Das2 server
            
            if randID == 'Cassini/Ephemeris/Saturn,60s' or randID == 'Cassini/MAG/VectorKSO': #very specific time formatting for these two datasets that has unorthodox time format compared to the rest of the server
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
            

        if sampleStartDate==None:        
            #generate a test "start date" 15 mins before the dataset stopdate, to check if the latest data is all good/parseable (therefore the rest of the data should be ok.) well, maybe...
            k = 15
            testStartDate= ( stopDate - timedelta(minutes = k) ).isoformat() + 'Z'
            testStopDate = stopDate.isoformat() + 'Z'
            expandCount = 5 # TODO: 
        else:
            testStartDate = sampleStartDate
            testStopDate= sampleStopDate
            expandCount = 0
            
        print(str(startDate) + '/' +  str(testStopDate))
    
    except Exception as e:
        
        exceptLog.append(str(e) + " occured on " + cHS + " process:  getting timestamps")
        
        
    #using the start and stop date, select a random start and stop date within the timeframe for use in sampling (pd dataframe)
    
    
    
        
        
    
        
        
    
        
    
    
    
    
    
    
    print('testStartDate=', testStartDate)
    print('testStopDate=', testStopDate)
        
    #create the final random link- with a special case for 2.0 vs 3.0- & only to get CSVs!
    dataEmpty = True #boolean for getting new urls until data has populated 
    testInterval = 60
    increaser = 4
    try:
        
        while dataEmpty:
                    
            if hapiVer == '3.0':
                        
                    
                finalURL = cHS + '/data?id=' + randID + '&parameters=' + randPara + '&start=' + testStartDate + '&stop=' + testStopDate + '&format=csv' #'&include=header'
                    
                print(finalURL)
                sys.stdout.flush()
        
            if hapiVer == '2.0' or hapiVer == '1.1':
                finalURL = cHS + '/data?id=' + randID + '&parameters=' + randPara + '&time.min=' + testStartDate + '&time.max=' + testStopDate + '&format=csv' #'&include=header'
                    
                print(finalURL)
            
            print( 'HAPI verifier URL:' )
            print( 'https://hapi-server.org/verify/?url=%s&id=%s&parameter=%s&time.min=%s&time.max=%s' % ( cHS, randID, randPara, testStartDate, testStopDate ) )
            sys.stdout.flush()
 
            #load csv file from finalURL
            try:
                csvResponse = myurlopen(finalURL)
                csvResponse = pd.DataFrame(csvResponse)
                #csvResponse = pd.read_csv(finalURL) #turns it into a pandas dataframe
            except:
                
                csvResponse = []
                
                csvResponse = pd.DataFrame(csvResponse) #makes into an empty dataframe to prevent errors
                

            
            dataRows = csvResponse.shape[0] #this returns the # of rows in the dataframe
            
            
            if dataRows < 2: #2 to avoid tick issue???
                
                print(f"{tColors.fail}No data found... increasing time range{tColors.endC}")
                
                #1 second delay between requests- to not overwhelm servers
                time.sleep(1)
                
                
                testStopDate = stopDate - timedelta(minutes = testInterval)
                
                testStartDate = testStopDate.isoformat() + 'Z'
                
                if ( sampleStartDate!=None ):
                    raise Exception('no data found in sampleStartDate to sampleStopDate!')
                    
                if ( testInterval > (1440*10) ):
                    raise Exception("time interval too long")
                
                if testInterval == 3840: #64 hours in mins, if it reaches this point go straight to collecting a years worth of data
                    increaser = 300
                
                #increase the time range by 4x each time, until data is found, if not the exception will catch an out of bounds HAPI error, most likely meaning empty data. 15 mins, 1 hr, 4hr, 16hr, 64hr
                testInterval *= increaser
                
                
                
                
            else:
                print(f"{tColors.success}Found Data! ")
                dataEmpty = False
                
                   
    except Exception as e:
        exceptLog.append( 'python3 HAPITESTSCRIPT.py '+str(seed)+' '+cHS + '\n' + str(e) + " occured on " + finalURL + " process:  loading CSV. Likely empty dataset")
        print(str(e))
    
        
    
        
    do_plot = False
    
    if not do_plot:
        return
    
    print( f"On to the plot!{tColors.endC}")
    
    #With the random link, check to see if the resulting CSV is parseable! 
    #and if the metadata allows for a good plot using Hapiplot!
    #try:
        
    try:
            
        
            
    
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
       
        exceptLog.append(str(e) + " occured on " + finalURL + " process:  plotting data")
        
        
        
        
        print(f"{tColors.fail}HAPI failed to plot on {tColors.endC}" + str(cHS))
        finalLog.append(cHS + '--ERROR')
  


#final notes: some sites have UTC Zulu as :XXX, some have it as .XXX
#also hapi 2.0 uses time.min and time.max to stream data...




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

    global servers 
    
    print( len(sys.argv), ' ***' )
    sys.stdout.flush()


    if len(sys.argv)==2:
        if sys.argv[1]=='--help':
            print( 'Usage:\n  python HAPITESTSCRIPT.py [seed] [url]\n' )
            exit(-1)
        else:
            seed= int(sys.argv[1])
    elif len(sys.argv)==3:
        seed= int(sys.argv[1]) 
        server= sys.argv[2]
    else:
        seed= random.randint(0,100000)    
     
    test_start_time = time.perf_counter ()

    if len(sys.argv)<3:
        print('Running tests with seed %d' % ( seed ) )
        random.seed(seed)

        seeds= [0]* len(servers)
        for i in range(len(servers)):
            seeds[i]= random.randint(0,10000)
    else:
        print('Running one test on one server.')
        seeds= [ seed ]
        servers= [ server ]

    sys.stdout.flush()
    for i in range(len(servers)):
        z= servers[i]
        print('#################')
        print('Running test with seed %d: %s' % ( seeds[i], z ) )
        sys.stdout.flush()
                    
        hapiTest(z,seeds[i])
    
    for o in finalLog:
        
        print(o)
        
    
    
    test_end_time = time.perf_counter ()
    
    print("Total Test Time: " + str(round((test_end_time - test_start_time), 3)) + " seconds")
    
    #print all exceptions that occured for debugging purposes:
    print( '== Exceptions ==' )
    count = 0 
    for s in exceptLog[2:]:
       count = count + 1
       print( " %02d: %s"  % ( count, s ) )
    if count==0:
       print( "(none)" )

    if len(exceptLog)<3:
        sys.exit(0)
    else:
        sys.exit(1)

main()
    
    

#das2 has the data on dataset info ID page?? Works 50% of the time??????

#Just realized.. Das2 streams some of its data from a deprecated server: http://mapsview.engin.umich.edu/
#DAS2 is a mess.. wrap in try errors

#SSC web is plottable 99% of the time... 


    

"""
ERRORS/ISSUES SO FAR:
    1. Some parameter data are strings... like vectorstr on HAPITEST2
    2. Certain parameters have no data for the current 15 minute time sample- implement a dynamic way around this- DONE
    3. Certain servers have non-standard data organization
    4. some servers have no data for the last 8 hours of listed date.. but as soon as you get to its start you are met with LOTS of data- some servers measure by milliseconds, others daily. lol

missing datasets on iswa: RBSP_B_RBSPICE_part_P1M



"""
    
    







    




