'''
Copyright (c) 2014 Bernd Klein

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import logging

# pip install requests
import requests
from eventsource.client import EventSourceClient

# set logger to DEBUG for detail returns
logger = logging.getLogger("spark-logger")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

class SparkCore(object):
    # init
    def __init__(self, user, password, deviceID, access_token=""):
        self.user = user
        self.password = password
        self.deviceID = deviceID
        self.access_token = access_token
        if self.access_token == "":
            self.access_token = self.getAccessToken()
        self.deviceURL = 'https://api.spark.io/v1/devices/' + self.deviceID + '/'

    # get an access token for your Spark Core
    def getAccessToken(self):
        # send post request and fetch output
        postParameters = {'grant_type': 'password', 'username': self.user, 'password': self.password}
        r = requests.post('https://api.spark.io/oauth/token', auth=('spark', 'spark'), data=postParameters)
        json = r.json()
        logger.debug("getAccessToken: "+str(json))
        # returns access token
        return json['access_token']

    # get list of all access tokens
    def getAllTokens(self):
        # send get request and return output
        r = requests.get('https://api.spark.io/v1/access_tokens', auth=(self.user, self.password))

        # returns a list of all your tokens
        return r.text

    # delete an access token
    def deleteToken(self, token):
        # send delete request and return output
        r = requests.delete('https://api.spark.io/v1/access_tokens/' + token, auth=(self.user, self.password))

        # returns the response, should be 'true'
        return r.text

    # start a function, must be defined in your setup() function with Spark.function()
    def sendFunctionRequest(self, functionName, functionParameter):
        # define postParameters
        postParameters = {'access_token': self.access_token, 'command': functionParameter}
        # send post request and return output
        r = requests.post(self.deviceURL + functionName, data=postParameters)
        json = r.json()
        logger.debug("sendFunctionRequest: "+str(json))
        # returns an int
        return json['return_value']

    # read value of a variable, must be defined in your setup() function with Spark.variable()
    def readVariable(self, variableName):
        getParameters = {'access_token': self.access_token}
        r = requests.get(self.deviceURL + variableName,params=getParameters)
        json = r.json()
        logger.debug("readVariable: "+str(json))
        # returns the value of your variable
        return json['result']

    def subscribe(self,event_name,callback):
        client = EventSourceClient("api.spark.io/v1/devices",self.deviceID+"/events",event_name+"?access_token="+self.access_token,callback,ssl=True,retry=8)
        client.poll()
