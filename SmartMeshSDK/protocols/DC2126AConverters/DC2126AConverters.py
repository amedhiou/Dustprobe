#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('DC2126AConverters')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

ENERGYSOURCE_BATTERY    = 'battery'
ENERGYSOURCE_SOLAR      = 'solar'
ENERGYSOURCE_ALL        = [
    ENERGYSOURCE_BATTERY,
    ENERGYSOURCE_SOLAR,
]

class DC2126AConverters(object):
    
    #===== temperature conversion
    
    RANGES_SIZE         = 474
    RANGESSIZELIST      = [8,61,55,50,45,41,38,35,33,31,29,27,26,24,23,22,21,21,19,18,18,17,17,16,15,15,14,14,14,13,12,13,12,12,11,11,11,11,10,10,10,9,10,9,9,9,9,8,9,8,8,8,8,7,8,7,7,8,7,7,6,7,7,6,7,6,6,6,6,6,6,6,6,5,6,5,6,5,6,5,5,5,5,5,5,5,5,5,4,5,5,4,5,4,5,4,5,4,4,4,5,4,4,4,4,4,4,4,4,4,4,3,4,4,4,3,4,4,3,4,3,4,3,4,3,4,3,3,4,3,3,4,3,3,3,3,4,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,2,3,3,2,3,3,3,2,3,2,3,3,2,3,2,3,3,2,3,2,3,2,2,3,2,3,2,3,2,2,3,2,2,3,2,2,3,2,2,3,2,2,2,3,2,2,2,2,3,2,2,2,2,2,2,3,2,2,2,2,2,2,2,2,2,2,2,2,3,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,2,2,2,2,1,2,2,2,2,1,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,1,2,2,1,2,2,2,1,2,2,1,2,2,1,2,1,2,2,1,2,2,1,2,1,2,2,1,2,1,2,2,1,2,1,2,2,1,2,1,2,1,2,1,2,1,2,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,1,2,1,2,1,2,1,2,1,2,1,1,2,1,2,1,2,1,2,1,1,2,1,2,1,1,2,1,2,1,1,2,1,2,1,1,2,1,2,1,1,2,1,1,2,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,0]
    CODESLIST           = [456,463,471,479,487,494,502,510,6,14,21,29,37,45,53,61,69,77,85,93,101,109,117,125,133,141,149,157,165,174,182,190,198,206,215,223,231,239,248,256,264,273,281,289,298,306,315,323,331,340,348,357,365,374,383,391,400,408,417,426,434,443,452,460,469,478,486,495,504,1,10,19,27,36,45,54,63,72,81,90,99,108,117,126,135,144,153,162,172,181,190,199,208,218,227,236,245,255,264,273,283,292,302,311,320,330,339,349,358,368,378,387,397,406,416,426,435,445,455,464,474,484,494,504,1,11,21,31,41,51,61,71,81,91,101,111,121,131,141,151,161,171,182,192,202,212,223,233,243,253,264,274,285,295,305,316,326,337,347,358,368,379,390,400,411,422,432,443,454,464,475,486,497,508,7,17,28,39,50,61,72,83,94,105,116,127,139,150,161,172,183,195,206,217,228,240,251,262,274,285,297,308,320,331,343,354,366,377,389,401,412,424,436,448,459,471,483,495,507,7,19,31,42,54,67,79,91,103,115,127,139,151,164,176,188,200,213,225,237,250,262,275,287,300,312,325,337,350,362,375,388,400,413,426,439,451,464,477,490,503,4,17,30,43,56,69,82,95,108,122,135,148,161,174,188,201,215,228,241,255,268,282,295,309,322,336,350,363,377,391,405,418,432,446,460,474,488,502,4,18,32,46,60,74,88,102,117,131,145,159,174,188,203,217,231,246,260,275,290,304,319,334,348,363,378,393,407,422,437,452,467,482,497,0,15,30,45,60,76,91,106,121,137,152,167,183,198,214,229,245,261,276,292,307,323,339,355,371,386,402,418,434,450,466,482,498,2,18,35,51,67,83,100,116,132,149,165,182,198,215,232,248,265,282,298,315,332,349,366,382,399,416,433,450,468,485,502,7,24,42,59,76,94,111,128,146,164,181,199,216,234,252,269,287,305,323,341,359,377,395,413,431,449,467,485,504,10,28,47,65,84,102,121,139,158,176,195,214,232,251,270,289,308,327,346,365,384,403,422,441,461,480,499,7,26,46,65,85,104,124,143,163,183,203,223,242,262,282,302,322,342,363,383,403,423,443,464,484,505,13,34,54,75,95,116,137,158,178,199,220,241,262,283,304,326,347,368,389,411,432,453,475,496,6,27,49,71,93,114,136,158,180,202,224,246,268,290,313,335,357,380,402,424,447,470,492,3,25,48,71,94,117,140,163,186,209,232,255,278,302,325,348,372,395,419,443,466,490,2,26,49,73,97,121,145,169,194,218,242,267,291,315,340,364,389,414,438,463,488,1,26,51,76,101,126,151,176,202,227,252,278,303,329,355,380,406,432,458,484,510,24,50,76,102,128,155,181,208,234,261,287,314,341,367,394,421,448,475,502,17,45,72,99,127,154,181,209,237,264,292,320,348,376,404,432,460,488,4,33,61,89,118,146,175,204,232,261,290,319,348,377,406,435,465,494,11,41,70,100,129,159,189,219,249,278,309,339,369,399,429,460,490,9,39,70,101,131,162,193,224,255,286,317,349,380,411,443,474,506,26,57,89,121,153,185,217,249,281,314,346,379,411,444,476,509,30,63,96,129,162,195,228,262,295,329,362,396,430,463,497,19,53,87,121,156,190,224,259,293,328,363,397,432,467,502,25,60,96,131,166,202,237,273,309,344,380,416,452,488,13,49,85,122,158,195,232,268,305,342,379,416,453,491,16,53,91,129,166,204,242,280,318,356,394,432,471,509,36,74,113,152,191,230,269,308,347,387,426,466,505,33,73,112,152,192,233,273,313,354,394,435,475,4,45,86,127,168,209,251,292,334,375,417,459,501,31,73,115,157,199,242,284,327,370,413,456,499,30,73,116,160,203,247,291,335,378,422,467,511,43,88,132,177,221,266,311,356,401,447,492,25,71,117,162,208,254,300,346,393,439,486,20,67,114,161,208,255,302,349,397,444,492,28,76,124,172,220,268,317,365,414,462,511,48,97,147,196,245,295,344,394,444,494,32,82,133,183,234,284,335,386,437,488,28,79,130,182,234,286,338,390,442,494,35,87,140,193,245,299,352,405,458,0,54,107,161,215,269,324,378,432,487,30,85,140,195,250,306,361,417,472,16,72,129,185,241,298,354,411,468,13,70,128,185,243,300,358,416,474,21,79,137,196,255,314,373,432,491,39,98,158,218,278,338,398,459,7,68,129,190,251,312,373,435,497,46,108,171,233,295,358,420,483,34,97,160,224,287,351,415,479,31,95,160,224,289,354,419,484,37,103,168,234,300,366,432,499,53,120,186,253,321,388,455,11,79,147,215,283,351,420,488,45,114,183,253,322,392,462,19,90,160,230,301,372,443,2,73,144,216,288,360,432,504,64,137,209,282,355,429,502,64,137,211,285,360,434,509,71,146,221,297,372,448,12,88,164,240,316,393,470,35,112,190,267,345,423,501,67,146,224,303,382,461,29,108,188,268,348,428,509,77,158,239,320,402,483,53,135,217,299,382,464,35,118,202,285,369,453,25,109,193,278,363,448,21,106,192,278,364,450,24,111,197,284,372,459,35,122,210,298,387,475,52,141,230,320,409,499,77,167,258,348,439,18,109,201,293,384,477,57,149,242,335,428,9,103,197,291,385,479,62,157,252,347,443,27,122,219,315,412,508,94,191,288,386,484,70,168,267,366,465,52,152,251,351,452,40,141,242,343,444,34,135,237,340,442,33,136,239,342,446,38,142,247,351,456,49,154,260,366,472,66,173,279,386,494,89,197,305,413,10,118,227,337,446,44,154,264,374,485,84,195,307,418,18,131,243,356,469,70,184,297,411,14,128,243,358,473,77,193,309,425,30,147,264,381,499,105,223,341,460,67,186,306,426,34,154,275,396,5,126,248,370,492,103,226,349,472,84,207,332,456,69,194,319,445,59,185,311,438,53,180,308,436,52,180,309,438,55,185,315,445,63,194,325,456,76,208,340,472,93,226,360,493,115,249,384,7,142,277,413,37,174,310,447,73,210,348,486,113,251,391,18,158,298,438,67,208,349,491,120,263,405,36,179,323,466,98,243,388,21,166,312,458,92,239,386,21,169,316,465,101,250,399,37,187,337,488,127,278,429,69,221,374,15,168,321,475,117,272,427,70,226,381,26,182,339,496,142,300,458,105,264,423,71,230,391,39,200,362,12,174,336,499,150,313,477,129,294,459,112,277,443,98,264,431,87,254,422,79,250,419,76,246,417,75,246,418,78,250,422,83,256,430,92,266,441,104,279,455,119,296,473,138,316,494,160,339,6,186,366,34,215,396,65,247,429,100,283,466,138,322,506,179,365,38,224,411,85,273,460,136,325,1,190,380,58,248,439,118,309,501,182,374,55,249,443,125,320,3,198,394,78,275,472,157,355,42,240,439,127,327,15,216,417,106,308,511,201,404,96,300,504,197,402,96,302,508,203,410,106,314,11,220,429,127,337,36,247,458,158,370,71,284,498,200,414,117,332,36,252,468,173,391,96,315,21,240,460,168,388,97,318,28,250,473,183,407,119,343,56,281,506,220,447,162,389,105,333,50,279,508,226,456,175,407,126,358,79,312,34,267,502,225,460,184,420,144,381,107,345,71,310,37,277,5,246,487,216,458,189,432,163,407,139,384,117,363,97,343,78,325,61,310,46,296,33,283,22,273,13,265,5,258,511,253,507,250,505,249,505,250,507,252,510,256,3,263,10,271,19,281,30,292,43,306,58,322,74,339,92,358,112,379,134,402,158,427,184,454,212,482,241,1,272,33,306,67,341,103,378,141,417,181,457,222,500,266,32,311,79,359,127,408,177,459,229,0,283,54,339,111,396,170,456,230,5,293,68,357,134,423,201,491,270,49,340,121,413,194,488,270,52,347,131,426,211,508,293,79,377,164,463,250,39,339,128,430,220,10,313,105,408,201,506,299,93,399,194,501,296,92,401,198,507,305,104,415,214,14,326,127,440,242,44,359,162,477,281,86,403,208,14,332,139,458,266,74,395,204,13,335,146,469,280,92,416,229,42,368,182,508,324,139,467,283,100,429,247,65,396,215,35,367,187,8,342,163,498,320,143,479,303,128,465,290,116,454,281,108,447,275,104,445,274,104,446,277,108,452,284,116,461,294,128,474,308,143,491,327,163,0,349,186,24,375,214,53,405,245,85,438,280,121,476,318,161,5,361,205,50,407,252,98,457,303,151,510,358,207,55,416,266,116,478,329,180,32,396,248,101,466,320,174,28,395,250,106,474,330,187,44,413,271,129,500,359,218,78,450,310,171,32,406,268,130,505,368,231,95,471,336,201,66,443,309,176,42,421,289,156,25,405,274,143,12,394,264,135,6,389,260,132,4,389,261,135,8,394,268,143,17,404,280,156,32,420,297,174,51,441,319,197,75,466,345,225,105,497,377,258,139,20,414,295,178,60,455,338,221,104,500,384,269,153,38,436,321,207,93,491,377,264,151,39,438,326,214,102,503,392,281,170,60,462,352,242,132,23,426,317,209,101,504,397,289,181,74,479,372]
    
    #===== power source threshold
    
    SOLAR_TH            = 700          # in mV. If adcValue>SOLAR_TH, DC2126A powered by solar panel.
    BATTERY_TH          = 650          # in mV. If adcValue<BATTERY_TH, DC2126A powered by battery.
    
    #======================== singleton pattern ===============================
    
    _instance           = None
    _init               = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DC2126AConverters,cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        
        # don't re-initialize an instance (needed because singleton)
        if self._init:
            return
        self._init = True
        
        # store params
        
        # log
        log.info("creating instance")
        
        # local variables
        self.TemperatureBaseValueIndex = []
        self.TemperatureRangeSize      = []
        self.energysource              = {}
        
        # load table
        self._loadTable()
    
    #======================== public ==========================================
    
    def convertTemperature(self,value):   
        '''
        \brief Convert raw temperature value to Celsius.
        '''
        
        # value between bits 28 - 19
        tempVals   = [0x01FF&(value>>19)]
        
        # value between bits 18 - 10
        tempVals  += [0x01FF&(value>>10)]
        
        return self._searchTemperature(tempVals)
    
    def convertAdcValue(self,value):   
        '''
        \brief Convert raw ADC values to mV.
        '''
        
        return float(value)/10.0
    
    def convertEnergySource(self,mac,adcValue):
        
        mac        = tuple(mac)
        
        returnVal  = None
        
        if   adcValue > self.SOLAR_TH:
            returnVal                  = ENERGYSOURCE_SOLAR
        elif adcValue < self.BATTERY_TH:
            returnVal                  = ENERGYSOURCE_BATTERY
        else:
            if mac not in self.energysource:
                self.energysource[mac] = ENERGYSOURCE_BATTERY
            returnVal                  = self.energysource[mac]
        
        assert returnVal
        return returnVal
    
    #======================== private =========================================
    
    #===== temperature conversion
    
    def _loadTable(self):
        nextValueIndex=0
        for i in range(self.RANGES_SIZE):
            rsize                           = self.RANGESSIZELIST[i]
            self.TemperatureBaseValueIndex += [nextValueIndex]
            self.TemperatureRangeSize      += [rsize]
            nextValueIndex                 += rsize
    
    def _searchTemperature(self,value):
        '''
        \brief Search Celsius temperature from a given value as a list.
        '''
        
        # use value[0] as a index in the TemperatureBaseValueIndex and
        # TemperatureRangeSize arrays
        indexTemp       = value[0] - 8 
        
        if indexTemp<0 or indexTemp>=self.RANGES_SIZE:
            log.warning("Invalid indexTemp {0}".format(indexTemp))
            return None
        
        baseVI          = self.TemperatureBaseValueIndex[indexTemp]
        rsize           = self.TemperatureRangeSize[indexTemp]
        
        # Use value[1] to search code close to it
        closeCodeIndex  = rsize-1
        for i in range(1,rsize):
            if self.CODESLIST[baseVI+i]>value[1]:
                diff    = self.CODESLIST[baseVI+i] - value[1]
                diff2   = value[1] - self.CODESLIST[baseVI+i-1]
                if diff < diff2:
                    closeCodeIndex= i
                else:
                    closeCodeIndex= i-1
                break
        
        multFactor      = baseVI+closeCodeIndex
        valueC          = 70-(multFactor*0.05)
        
        return valueC
