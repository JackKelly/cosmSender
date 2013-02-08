Simple module for sending data to Cosm.
It caches datapoints to limit the number of API requests.
If an API request fails then the data is saved in the cache
and sent when the API request next succeeds.

Installation:
    Place this file in a directory.
    Add that directory to the environment variable PYTHONPATH

Usage:
```python
from cosmSender import CosmSender

# Configure data stream defaults
dataStreamDefaults = {
                      "min_value"    : "0.0",
                      "unit": { "type"  : "derivedSI",
                                "label" : "watt",
                                "symbol": "W" }
                      }

# Create a new CosmSender object (add your APIKEY and FEED id).
# Use cacheSize=0 to send data to Cosm as soon as it arrives at this script
c=CosmSender(<APIKEY>, <FEED>, dataStreamDefaults, cacheSize=1)

# Send data to dataStream '8' with value '1'.
# Because this is the first time that we have referenced dataStream '8', 
# CosmSender will send Cosm the dataStreamDefaults for dataStream '8'
c.sendData('8','1')

# Send another datapoint to CosmSender.  Because cacheSize is set to 1,
# CosmSender will cache this datapoint (with its correct timecode)
# and will not send it to Cosm yet.
c.sendData('8','2')

# Send another datapoint.
# This point will be sent together with the previous data point.
c.sendData('8','3')

# Flush cache before finishing
c.flush()

```
