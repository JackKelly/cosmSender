'''
Simple module for sending data to Cosm.
It caches datapoints to limit the number of API requests.
If an API request fails then the data is saved in the cache
and sent when the API request next succeeds.

Installation:
    Place this file in a directory.
    Add that directory to the environment variable PYTHONPATH

Usage:
>>> from cosmSender import CosmSender

>>> # Now set configure the details for newly created datastreams
>>> dataStreamDefaults = {
...     "min_value"    : "0.0",
...     "unit": { "type"  : "derivedSI",
...               "label" : "watt",
...               "symbol": "W"
...             }
...     }

>>> # Create a new CosmSender object (add your APIKEY and FEED id)
>>> c=CosmSender(<APIKEY>, <FEED>, dataStreamDefaults, cacheSize=1)
>>> # use cacheSize=0 to send data to Cosm as soon as it arrives at this script

>>> # Send data for dataStream '8' with value '1'.
>>> # Because this is the first time that we have referenced dataStream '8', 
>>> # CosmSender will send Cosm the dataStreamDefaults for dataStream '8'
>>> c.sendData('8','1')

>>> # Send another datapoint to CosmSender.  Because cacheSize is set to 1,
>>> # CosmSender will cache this datapoint (with its correct timecode)
>>> # and will not send it to Cosm yet.
>>> c.sendData('8','2')

>>> # Send another datapoint.
>>> # This point will be sent together with the previous data point.
>>> c.sendData('8','3')

>>> # Flush cache before finishing
>>> c.flush()

'''

import urllib2 # for sending data to Cosm
import json    # for assembling JSON data for Cosm
import time
import sys

class CosmSender( object ):

    def __init__( self, api_key, feed, dataStreamDefaults={}, cacheSize=0 ):
        self.api_key = api_key
        self.feed    = str(feed)
        self.dataStreamDefaults = dataStreamDefaults
        self.cache = {}
        self.cacheSize = cacheSize

        if not isinstance(self.dataStreamDefaults, dict):
            raise TypeError('dataStreamDefaults must be a dict.')
        if not isinstance(self.api_key, (str, unicode)):
            raise TypeError('api_key must be a str or unicode.')


    def sendData( self, dataStreamID, currentValue, debug=False ):
        """
        Sends data to Cosm.

        dataStreamID and currentValue must both be strings.

        'cacheSize' is the number of datapoints to cache before sending to Cosm.
        """
        
        if not isinstance(dataStreamID, (str, unicode)):
            raise TypeError('dataStreamID must be a str or unicode object.')
        if not isinstance(currentValue, (str, unicode)):
            raise TypeError('currentValue must be a str or unicode object.')

        if debug:
            print '\nsendData(dataStreamID=%s, currentValue=%s)' % (dataStreamID, currentValue)

        if self.cache.has_key( dataStreamID ):            
            # Add datapoint to cache
            ISO8601_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

            self.cache[ dataStreamID ]['datapoints'].append({
                    "at": ISO8601_time,
                    "value": currentValue
                    })

            if debug:
                print '  Added to cache: ' + str(self.cache[dataStreamID]['datapoints'][-1])

            if len(self.cache[ dataStreamID ]['datapoints']) > self.cacheSize:  
                try:
                    self.sendCacheToCosm( dataStreamID, debug )
                except Exception, e:
                    sys.stderr.write('WARNING: An error occured sending data to Cosm: ')
                    sys.stderr.write(str(e))
                    sys.stderr.write(' CosmSender will store this data and try to re-send later.\n')
        
        else:
            # self.cache has no key corresponding to dataStreamID.
            # This implies that we haven't yet sent any data to Cosm for this ID 
            # so we must send the dataStreamDefaults to Cosm for this ID
            self.cache[ dataStreamID ] = {'datapoints':[]}
            dataStreamDict       = self.dataStreamDefaults.copy()
            dataStreamDict['id'] = dataStreamID
            dataStreamDict['current_value'] = currentValue
            jsonData =  json.dumps({
                          "version":"1.0.0",
                          "datastreams": [ dataStreamDict ]
                        })
            try:
                self.sendJson( jsonData, 'http://api.cosm.com/v2/feeds/'+self.feed, 'PUT', debug )
            except Exception, e:
                raise


    def flush( self, debug=False ):
        """
        Flush cache.
        """
        for dataStreamID in self.cache.keys():
            if debug:
                print "\nFlushing dataStreamID = %s" % (dataStreamID)
            self.sendCacheToCosm( dataStreamID, debug )


    def sendCacheToCosm( self, dataStreamID, debug=False ):
        """
        Sends contents of self.cache[dataStreamID] to Cosm.
        If there are more than 500 datapoints then uses multiple API requests
        (because Cosm can't handle more than 500 datapoints per API request)
        """

        url = 'http://api.cosm.com/v2/feeds/'+self.feed+'/datastreams/'+ dataStreamID +'/datapoints'

        # The Cosm API can only handle 500 data points per API request
        # But let's play safe and assume it can only handle 450
        maxDataPoints = 450
        numAPIrequestsRequired = (len( self.cache[dataStreamID]['datapoints'] ) // maxDataPoints) + 1

        if debug:
            print '\nsendCacheToCosm( dataStreamID = %s )' % dataStreamID
            print ' numAPIrequestsRequired = %d' % (numAPIrequestsRequired)

        success = True

        for APIrequest in range(0, numAPIrequestsRequired):

            startIndex = APIrequest*maxDataPoints
            endIndex   = (APIrequest+1)*maxDataPoints
            jsonData = json.dumps( {"datapoints": self.cache[dataStreamID]['datapoints'][startIndex:endIndex]  } )

            if debug:
                print '\n startIndex=%d, endIndex=%d ' % (startIndex, endIndex)
                print ' lenght = %d' % (len(self.cache[dataStreamID]['datapoints']))

            try:
                self.sendJson( jsonData, url, 'POST', debug )
            except Exception, e:
                success = False
                raise

        if success:
            self.cache[dataStreamID] = {'datapoints':[]} # if no exception occured then reset list


    def sendJson( self, jsonData, url, method, debug=False ):
        '''
        Send JSON to Cosm.
        Adapted from http://stackoverflow.com/a/111988
        example settings for 'method' include 'PUT' and 'POST'
        '''
        
        if debug:
            print '\nsendJson'
            print '  jsonData = ' + jsonData
            print '  url      = ' + url
            print '  method   = ' + method

        opener  = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url, data=jsonData)
        request.add_header('X-ApiKey', self.api_key)
        request.get_method = lambda: method

        try:
            opener.open(request)
        except Exception, e:
            raise


# Basic testing code:
if __name__ == '__main__':

    dataStreamDefaults = {
            "min_value"    : "0.0",
            "unit": { "type"  : "derivedSI",
                      "label" : "watt",
                      "symbol": "W"
                    }
            }

    apikey = "" # SET THIS!
    feed   = "" # SET THIS!

    p = CosmSender(apikey, feed, dataStreamDefaults, 650)

    for i in range(0,700):
        p.sendData('6',  str(i), True)
    
    p.flush(True)
