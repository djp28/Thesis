"""
PopCon backend application
Author: Antonio Pierro, antonio.pierro@cern.ch, Aidas Tilmantas
"""
import os
import time

import cherrypy
import json

import popconSQL
import json_provider

import threading

import json2html

import service

PAGES_DIR = 'pages' # FIXME: Clean this up -mos

class PopCon:
    def __init__(self):
        self.auth = "./auth.xml" # FIXME: Drop this argument from everywhere -mos
        self.recent_activity_result = ''
    #selected tab name field
    page = ""    
    #possible tabs names
    tabsNames = ["EcalLaserExpressTimeBasedO2O", "EcalDAQO2O",
                 "SiStripDetVOffTimeBasedO2O", "RunInfoStart",
                 "OfflineDropBox", "EcalPedestalsTimeBasedO2O",
                 "EcalDCSO2O", "RunInfoStop", "EcalLaserTimeBasedO2O"]

    @cherrypy.expose
    def index(self, *args, **kwargs):
        ##++> attention, index is not called for the .html pages ...
        print '++++> in index, args = "'+'-'.join(args)+'"'
        #if in url there is no parameters (because we don't need them)
        if len(kwargs) == 0:
            #if we have page request in /..../
            if len(args) == 1:
                #if that request is PopConCronjobTailFetcher.html
                if "PopConCronjobTailFetcher.html" in args:
                    #if that request is first and only one
                    if args[0] == "PopConCronjobTailFetcher.html":
                        #set return value
                        #return the page
                        return open(os.path.join(PAGES_DIR, 'PopConCronjobTailFetcher.html'), "rb").read()
                    #if request is not the first one as it should be
                    else: 
                        #raise error
                        raise cherrypy.HTTPError(405, "BAD REQUEST!!!!! YOU ENETERED [" + args[0] + "] Should be popcon/PopConCronjobTailFetcher.html")
                #same as above
                elif "PopConRecentActivityRecorded.html" in args:
                    if args[0] == "PopConRecentActivityRecorded.html":
                        return open(os.path.join(PAGES_DIR, 'PopConRecentActivityRecorded.html'), "rb").read()
                    else:
                        raise cherrypy.HTTPError(405, "BAD REQUEST!!!!! YOU ENETERED [" + args[0] + "] Should be popcon/PopConRecentActivityRecorded.html")
                #same as above
                elif "popconActivityHisto.html" in args:
                    if args[0] == "popconActivityHisto.html":
                        return open(os.path.join(PAGES_DIR, 'popconActivityHisto.html'), "rb").read()
                    else:
                        raise cherrypy.HTTPError(405, "BAD REQUEST!!!!! YOU ENETERED [" + args[0] + "] Should be popcon/popconActivityHisto.html")
                #if request is not one of the possible
                else:
                    #raise error
                    raise cherrypy.HTTPError(405, "BAD REQUEST!!!!! NO MATCHING AVIABLE REQUESTS!!!")
            #if we don't have page request in /..../
            elif len(args) == 0:
                #set response type
                #return index(home) page
                return open(os.path.join(PAGES_DIR, 'index.html'), "r").read()
            #if we have too much arguments in /.../.../..../..../
            else:
            #    #raise error
                raise cherrypy.HTTPError(405, "BAD REQUEST!!!!! THERE SHOULD BE /popcon/ or /popcon/name.htlm  name - wanted request name")
        #if we have params which we don't need
        else:
            #if "PopConCronjobTailFetcher" in args:
            #    if "hashName" in kwargs:
            #        return self.PopConCronjobTailFetcher(kwargs["hashName"])
            #for safety reasons raise error
            raise cherrypy.HTTPError(405, "BAD REQUEST!!!!! THERE HAS TO BE NO PARAMETERS!!!")

    @cherrypy.expose
    def PopConRecentActivityRecorded(self, *args, **kwargs):
        rownumbers=500
        account=""
        payloadContainer=""
        iovTag=""
        startDate=""
        endDate=""
        if len(args) == 0 and len(kwargs) == 0:
            RACData = popconSQL.popconSQL().PopConRecentActivityRecorded(self.auth, rownumbers, account, payloadContainer, iovTag, startDate, endDate)
        else:
            raise cherrypy.HTTPError(405, "There has to be no arguments or parameters!!!!!")
        return json.dumps(RACData)
        
    def PopConRecentActivityRecorded_diff(self):
        last_id = '-1'
        rez = []
        r = self.PopConRecentActivityRecorded()
        js = json.loads(r)
        data = js['aaData']
        if last_id == '-1':
            return '["last_id", %d]' % int(data[0][0])
        else:
            try:
                tmp = int(last_id)
            except ValueError:
                return ''
        for i in data:
            if int(i[0]) > tmp:
                rez.append(i)
              
        if rez != []:
            return json.dumps(rez)
        else:
            return 'No data'

    # getQuataInfo method
    # @TODO: change name, JsonProvider
    def get_quotaInfo(self, *args, **kwargs):
	    return json_provider.JsonProvider().Elements_pie(data_dict = json_provider.JsonProvider().queryRow2dict(popconSQL.popconSQL().get_quotaInfo()))
    
    # @TODO: JsonProvider, future-usage: startDate and endDate
    @cherrypy.expose
    def popconActivityHisto(self, *args, **kwargs):
        account=""
        startDate=""
        endDate=""
        if len(args) == 0 and len(kwargs) == 0:
            AHData = popconSQL.popconSQL().popconActivityHisto(self.auth, account)
            #AHDataInJson = json_provider.JsonProvider().json_dict_output(data_dict=AHData, title="Activity History recorded")
            AHDataInJson = json_provider.JsonProvider().json_dict_output_barstack2(data_dict=AHData, title="Activity History recorded")
            AHDataInJson2 ="""
{ "elements": [ { "type": "bar_stack", "colours": [ "#C4D318", "#50284A", "#7D7B6A" ], "values": [ [ 2.5, 5, 2.5 ], [ 2.5, 5, 1.25, 1.25 ], [ 5, { "val": 5, "colour": "#ff0000" } ], [ 2, 2, 2, 2, { "val": 2, "colour": "#ff00ff" } ] ], "keys": [ { "colour": "#C4D318", "text": "Kiting", "font-size": 13 }, { "colour": "#50284A", "text": "Work", "font-size": 13 }, { "colour": "#7D7B6A", "text": "Drinking", "font-size": 13 }, { "colour": "#ff0000", "text": "XXX", "font-size": 13 }, { "colour": "#ff00ff", "text": "What rhymes with purple? Nurple?", "font-size": 13 } ], "tip": "X label [#x_label#], Value [#val#]
Total [#total#]" } ], "title": { "text": "Stuff I'm thinking about, Tue May 18 2010", "style": "{font-size: 20px; color: #F24062; text-align: center;}" }, "x_axis": { "labels": { "labels": [ "Winter", "Spring", "Summer", "Autmn" ] } }, "y_axis": { "min": 0, "max": 14, "steps": 2 }, "tooltip": { "mouse": 2 } }
"""
        else:
            raise cherrypy.HTTPError(405, "No arguments or parameters allowed for this function !!!!!")
        return AHDataInJson

    # function for getting all information to PopConCronJobTailFetcher if no of tabs are selected
    #  or get information about not selected tabs
    @cherrypy.expose
    def PopConCronjobTailFetcher(self, *args, **kwargs):
        #if there is no params in url between / ...  /.../ and if there is correct parameter hashName
        if len(args) == 0 and len(kwargs) == 1 and "hashName" in kwargs:
            #get informaion about all tabs from db
            CTF = popconSQL.popconSQL().PopConCronjobTailFetcher(self.auth)
            #if in url there were selected tab
            if self.page != "":
                #if that selected tab is OfflneDropBox
                if self.page == "OfflineDropBox":
                    # delete information about that tab because it was loaded and we don't have to reload 
                    del CTF["aaData"][self.page]
                    # set selected tab to null
                    self.page = ""
                #if selected tab is not OfflinDropBox
                else:
                    # check if there is errors or warnings in given information
                    # if yes add html class that we could mark up that info returns new data with marked classes
                    # if no just return the same information
                    CTF["aaData"] = self.insertWarningAndErrorMarkups(CTF["aaData"], self.page)
                    # do the same as above to OfflineDropBox(OfflineDropBox needs separate call because its information is different than others) return new data
                    CTF["aaData"]["OfflineDropBox"] = self.insertWarningAndErrorMarkups(CTF["aaData"]["OfflineDropBox"], "OfflineDropBox")
                    # delete info about that tab which was loaded alone
                    del CTF["aaData"][self.page]
                    self.page = ""
            #if in url there were no selected tabs - load all tabs at once
            else:
                #checks for the errors and warnings as described above
                CTF["aaData"] = self.insertWarningAndErrorMarkups(CTF["aaData"], self.page)
                CTF["aaData"]["OfflineDropBox"] = self.insertWarningAndErrorMarkups(CTF["aaData"]["OfflineDropBox"], "OfflineDropBox")
            #put information in dictionary
            items = {'items' : [CTF]}
        #if url were not like it has to be
        else:
            #raise error
            raise cherrypy.HTTPError(405, "There has to be no arguments or parameters!!!!!")
        #if everything went fine return information in json
        return json.dumps(items)

    #get information about only one tab which was selected (for faster page load)
    @cherrypy.expose
    def PopConCronjobTailFetcherShort(self, *args, **kwargs):
        #if we have correct parameter in page query to get info
        if "hashName" in kwargs:
            #if parameter value is one of correct possibilities
            if kwargs["hashName"] in self.tabsNames: 
                #add .log to fileName for db query
                fileName = kwargs["hashName"] + ".log"
                #set the tab name as loaded(that later we won't load it again)
                self.page = kwargs["hashName"]
             #if parameter value is bad
            else:
                #raise error
                raise cherrypy.HTTPError(405, "Bad parameter value after #!!!!! You typed: [" + kwargs["hashName"] +"]" )
        #if there is no needed parameter in page query to get info
        else:
            #raise error
            raise cherrypy.HTTPError(405, "Error while receiving data from server!!!")
        #If everything was good get information from db about tha tab (return value dict)
        CTF = popconSQL.popconSQL().PopConCronjobTailFetcher(self.auth, "where filename='{0}'".format(fileName))
        #if tab name was OfflineDropBox
        if self.page == "OfflineDropBox":
            #check if in information there is errors or warnings and mark up them if true
            CTF["aaData"]["OfflineDropBox"] = self.insertWarningAndErrorMarkups(CTF["aaData"]["OfflineDropBox"], self.page)
        #if tab name is not DropBox 
        else:
            #do error , warnings check and markup for that tab
            CTF["aaData"] = self.insertWarningAndErrorMarkups(CTF["aaData"], self.page)
        #put data in dict
        items = {'items' : [CTF]}
        #return information to page as json dict
        return json.dumps(items)
    
    def insertWarningAndErrorMarkups(self, data, page):
        # if checks and markup is needed for OfflineDropBox information
        if page == "OfflineDropBox":
            # split given information string to arrays by <br>
            infoInRightScreenPart = data[0][1].split("<br>")
            infoInLeftScreenPart = data[0][0].split("<br>")
            temp = []
            rememberTheDate = ""
            # going through array in which we have all information which has to be checked
            for index in range(len(infoInRightScreenPart)):
                # get each job date (because if we will find later in that job error or warning we will need to markup date in other page part(left))
                if infoInRightScreenPart[index].find("----- new cronjob started for Offline  at -----") != -1:
                    infoInRightScreenPart[index] = '<br>'+infoInRightScreenPart[index] # add line-break again in front to separate entries ...
                    # date is always in second line from line which is written above
                    # this assumes that there _always_ is another line after the one above.
                    rememberTheDate = infoInRightScreenPart[index +1]
                # if we found an error
                if infoInRightScreenPart[index].find("ERROR:") != -1 :
                    # we go through all dates in left part of page
                    for ind in range(len(infoInLeftScreenPart)):
                        # if we found there date which we remembered earlier(above)
                        if infoInLeftScreenPart[ind].find(rememberTheDate) != -1 :
                            # if it is not marked up
                            if infoInLeftScreenPart[ind].find('<p class = "error">') == -1 and infoInLeftScreenPart[ind].find("</p>") == -1 and rememberTheDate != "":
                                # mark up the page left part line by adding html class error
                                tempL = '<p class = "error">' + infoInLeftScreenPart[ind]+ "</p>"
                                # update information that error was found
                                data[0][2]["error"] = "1"
                                # update data with new marked up value
                                infoInLeftScreenPart[ind] = tempL
                            elif infoInLeftScreenPart[ind].find('<p class = "warning">') != -1  and rememberTheDate != "":
                                tempL = '<p class = "error">' + infoInLeftScreenPart[ind][21:]
                                data[0][2]["error"] = "1"
                                infoInLeftScreenPart[ind] = tempL   
                        # if we did not found error and there is no line break tags
                        if not infoInLeftScreenPart[ind].endswith("<br>")  and not infoInLeftScreenPart[ind].endswith("</p>"):
                            # leave information the same as it was just add line brake tag
                            infoInLeftScreenPart[ind] = infoInLeftScreenPart[ind] + "<br>"
                    # mark-up right page part error line with adding html class 
                    tempR = '<p class = "error">' + infoInRightScreenPart[index] + "</p><br>"
                    # append that line to data
                    temp.append(tempR)
                # if we did not find error on that line
                else:
                    # if there is warning in that line 
                    if infoInRightScreenPart[index].find("WARNING:") != -1 :
                        # we go through all dates in left part of page
                        for ind in range(len(infoInLeftScreenPart)):
                            # if we found there date which we remembered earlier(above)
                            if infoInLeftScreenPart[ind].find(rememberTheDate) != -1 :
                                # if it is not marked up
                                if infoInLeftScreenPart[ind].find('<p class = "warning">') == -1 and infoInLeftScreenPart[ind].find("</p>") == -1 and rememberTheDate != "" :
                                    # mark up the page left part line by adding html claas warning
                                    tempL = '<p class = "warning">' + infoInLeftScreenPart[ind] + "</p>"
                                    # update information that warning was found
                                    data[0][2]["error"] = "2"
                                    # update data with new marke up value
                                    infoInLeftScreenPart[ind] = tempL
                            # if we did not found warning and there is no line brake tags
                            if not infoInLeftScreenPart[ind].endswith("<br>")  and not infoInLeftScreenPart[ind].endswith("</p>"):
                                # leave information the same as it was just add line brake tag
                                infoInLeftScreenPart[ind] = infoInLeftScreenPart[ind] + "<br>"
                        # mark-up right page part warning line with adding html class
                        tempR = '<p class = "warning">' + infoInRightScreenPart[index] + "</p><br>"
                        # append that line to data
                        temp.append(tempR)
                    # if we did not find error or warning on that line
                    else:
                        # leave information the same but add line brakes 
                        temp.append("<p>" + infoInRightScreenPart[index] + "</p>")
            # update data with all made modifications to it
            if "".join(infoInLeftScreenPart).find('<p class = "warning">') == -1 and "".join(infoInLeftScreenPart).find('<p class = "error">') == -1:
                data[0][2]["error"] = 0
            for ind in range(len(infoInLeftScreenPart)):
                if not infoInLeftScreenPart[ind].endswith("<br>")  and not infoInLeftScreenPart[ind].endswith("</p>"): 
                    infoInLeftScreenPart[ind] = infoInLeftScreenPart[ind] + "<br>"
            data[0][0] = "".join(infoInLeftScreenPart)
            data[0][1] = "".join(temp)
            # return modified data
            return data
        # if selected tab name is nor OfflineDropBox
        else:
            #for every atb in given data
            for i in data:
                #if that data is not OfflineDropBox (because for that we have to do different actions)
                if i != "OfflineDropBox":
                    #split given information string into array of strings by <br>
                    infoInRightScreenPart = data[i][0][1].split("<br>")
                    infoInLeftScreenPart = data[i][0][0].split("<br>")
                    temp = []
                    rememberTheDate = ""
                    found = 0
                    index = 0
                    #we are looking in all right page screen information array of strings
                    while index < len(infoInRightScreenPart):
                        #if we found new started job information
                        if infoInRightScreenPart[index].find("----- new cronjob started for ") != -1:
                            #remember date for that job
                            rememberTheDate = infoInRightScreenPart[index +1]
                        #looking if there is Exception in line
                        if infoInRightScreenPart[index].find("cms::Exception") != -1:
                            # go through all left page part information(dates)
                            for j in range(len(infoInLeftScreenPart)):
                                # if we found date same as we remembered it (above) mark up it
                                if infoInLeftScreenPart[j].find(rememberTheDate) != -1:
                                    if infoInLeftScreenPart[j].find("""<p class = "error">""") == -1 and infoInLeftScreenPart[j].find("</p>") == -1 and rememberTheDate != "":
                                        tempL = """<p class = "error">""" + infoInLeftScreenPart[j] + "</p>"
                                        data[0][2]["error"] = "1"
                                        infoInLeftScreenPart[j] = tempL
                                # if we did not found it leave data as it was just add line brakes
                                if infoInLeftScreenPart[j].find("<br>") == -1  and infoInLeftScreenPart[j].find("</p>") == -1:
                                    infoInLeftScreenPart[j] = infoInLeftScreenPart[j] + "<br>"
                                # mark-up all lines from cms::Exception to ---- END line
                                try:
                                  while infoInRightScreenPart[index] != "---- END":
                                    if infoInRightScreenPart[index].find("""<p class = "error">""") == -1 and infoInRightScreenPart[index].find("</p>") == -1:
                                        tempR = """<p class = "error">""" + infoInRightScreenPart[index] + "</p>"
                                        temp.append(tempR)
                                        # move to next line
                                        index = index +1
                                except IndexError:
                                  pass
                            # mark that we found error
                            found = found -1
                        # if we did not found an error message
                        else:
                            # mark that we did not find error
                            found = found +1
                            # leave information the same but add line brakes
                            temp.append("<p>" + infoInRightScreenPart[index] + "</p>")
                        # mark that we did not found an error
                        index = index +1
                    # if we checked all lines and in all lines there were no errors
                    if found == index :
                        if "".join(infoInLeftScreenPart).find("""<p class = "error">""") == -1:
                            data[i][0][2]["error"] = 0
                        #leave information as it was 
                        data[i][0][0] = data[i][0][0]
                        data[i][0][1] = data[i][0][1]
                    #if we found error or few errors
                    else:
                        if "".join(infoInLeftScreenPart).find("""<p class = "error">""") == -1:
                            data[i][0][2]["error"] = 0
                        #add new(marke-up) information
                        data[i][0][0] = "".join(infoInLeftScreenPart)
                        data[i][0][1] = "".join(temp)
            #return processed data
            return data

    def PopConCronjobTailFetcherStatus(self, *args, **kwargs):
        serviceName='EcalDCSO2O'
        CTF = popconSQL.popconSQL().PopConCronjobTailFetcherStatus(self.auth,serviceName=serviceName)
        return json.dumps(CTF)

    def checkLongTail(self, *args, **kwargs):
        serviceName='OfflineDropBox'
        CTF = popconSQL.popconSQL().checkLongTail(self.auth,serviceName=serviceName)
        return json.dumps(CTF)

    def PopConCronjobStatus(self, *args, **kwargs):
        jobList = popconSQL.popconSQL().PopConCronjobStatus(self.auth)
        return json.dumps(jobList)


def main():
	service.start(PopCon())


if __name__ == '__main__':
	main()

