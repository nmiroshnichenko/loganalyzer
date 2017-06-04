#!/usr/bin/env python

'''
Created on Nov 5, 2009

@author: Nikolay Miroshnichenko
'''

import apachelog, sys

class LogAnalyzer:

    def __init__(self, filename, format_value, options):

        self.logfile = None # log file object        
        self.format = None # log file format
        self.secondsSum = 0 # total number of seconds
        self.requestsSum = 0 # total number of requests
        self.avgRequestsPerSec = 0 # average of the requests per second
        self.minRequestsPerSec = 0 # minimum of the requests per second
        self.maxRequestsPerSec = 0 # maximum of the requests per second
        
        # filename is an obligatory parameter
        if filename != None or filename != '':
            try:
                self.logfile = open(filename, 'r')
            except IOError:
                raise('Cannot open', filename)
            except:
                raise('Unknown error occurred')
        else:
            raise FileNotFoundError('File not found')
        
        if (format_value != None) or (format_value != ''):
            self.format = format_value
        else:
            try:
                self.format = self._whatFormat()
            except UnknownFormatError:
                raise
        
        if options != None or options != '':
            self.options = options
        else:
            self.options = None
        
#        try:
#            self.analyze()
#        except:
#            raise
    
    def _whatFormat(self): #TODO: currently it doesn't work
        """
        Verifies if a given file complies with any standard access log file format
        and returns the name of this format or the UnknownFormatError exception.
        """
        
        try:
            line = self.logfile.readline()
        except:
            raise('Cannot read the first line of the file')
        
        formats = 'extended','common','vhcommon' 
        for f in formats:
            try:
                p = apachelog.parser(apachelog.formats[f])
                data = p.parse(line)
            except:
                next
            else:
                return f
        raise UnknownFormatError('Unknown log file format')

    def analyze(self):
        """
        options include '--totals-only'
        """
        
        requests_number = 0 # number of requests for a current second
        previous_timestamp = '' # timestamp from a previous line
        #TODO: add logic to deal with possible not continuous equal timestamps
        
        for line in self.logfile:
            try:
                p = apachelog.parser(apachelog.formats[self.format])
                data = p.parse(line)
            except:
                sys.stderr.write("Unable to parse line: %s" % line)
                raise #TODO: extend options (--ignore-bad-lines)
            
            # getting the timestamp
            try:
                timestamp = data.get('%t')
            except:
                sys.stderr.write("Unable to get data: %s" % data)
                raise #TODO: extend options (--ignore-parse-errors)
            
            if timestamp == previous_timestamp:
                requests_number += 1
            else:
                if (self.options != '--totals-only') and (previous_timestamp != ''):
                    # print summary for the previous second
                    s = "%s = %s" % (previous_timestamp, requests_number)
                    print s
                
                self.secondsSum += 1 
                self.requestsSum += requests_number
                
                if requests_number > self.maxRequestsPerSec:
                    self.maxRequestsPerSec = requests_number

                if requests_number < self.minRequestsPerSec:
                    self.minRequestsPerSec = requests_number
                
                if self.minRequestsPerSec == 0:
                    self.minRequestsPerSec = requests_number
                
                requests_number = 1
                previous_timestamp = timestamp
                
        self.logfile.close
        
        self.avgRequestsPerSec = float(self.requestsSum) / self.secondsSum
        
        return
        
    def getRequestsSum(self):
        return self.requestsSum
    
    def getSecondsSum(self):
        return self.secondsSum
    
    def getMinRequestsPerSec(self):
        return self.minRequestsPerSec
    
    def getAvgRequestsPerSec(self):
        return self.avgRequestsPerSec
    
    def getMaxRequestsPerSec(self):
        return self.maxRequestsPerSec

class FileNotFoundError(BaseException):
    pass

class UnknownFormatError(BaseException):
    pass
            
if __name__ == "__main__":
    
    import time 
    start_time = time.clock()
    parameters = sys.argv[1:]
    param_number = len(parameters)

    if param_number == 1:
        logfile = parameters[0]
        options = ''
    elif param_number == 2:
        if parameters[1] == '--totals-only':
            logfile = parameters[0]
            options = parameters[1]
    else:
        print "Usage: LogAnalyzerClass filename [--totals-only]" #TODO: format passing 
        raise SystemExit
    
    format = 'extended' #TODO: format passing

    try:
        l = LogAnalyzer(logfile, format, options)
    except:
        print "An error occurred while initiating the process"
        raise

    try:
        l.analyze()
    except:
        print "An error occurred while running the process"
        raise
 
    end_time = time.clock()
    duration = end_time - start_time
    
    s = """ Summary for %s
    Total number of requests = %s
    Total number of seconds = %s
    Minimum requests per seconds = %s
    Average requests per seconds = %s
    Maximum requests per seconds = %s
 Duration of the analysis = %s seconds
    """ % (
    logfile,
    l.getRequestsSum(),
    l.getSecondsSum(),
    l.getMinRequestsPerSec(),
    l.getAvgRequestsPerSec(),
    l.getMaxRequestsPerSec(),
    duration
    )

    print s

    