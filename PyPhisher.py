from optparse import OptionParser
import smtplib
import random
import string
import shutil
import datetime
import time
import os
import thread
from subprocess import call
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

class Logger():
    def __init__(self, logpath):
        self.ClassName = "Logger"
        self.logpath = logpath

    def write(self, level, message):
        logstring = str(datetime.datetime.now()) + "," + level + "," + message + "\n"
        file = open(self.logpath,"w+")
        file.write(logstring)

class PyPhisher():
    def __init__(self, ToFilePath, SMTPServer, SMTPPort, SMTPUsername, SMTPPassword, RequireTLS, BodyPath, WWWPath, OutputPath, LogPath, TrackPath, TrackTime):
        self.Version = "2.0"
        self.ToFilePath = ToFilePath

        self.SMTPServer = SMTPServer
        self.SMTPPort = SMTPPort
        self.SMTPUsername = SMTPUsername
        self.SMTPPassword = SMTPPassword
        self.RequireTLS = RequireTLS

        self.BodyPath = BodyPath

        self.WWWPaths = WWWPath

        self.OutputPath = OutputPath
        self.TrackPath = TrackPath
        self.TrackTime = TrackTime
        self.Log = Logger(LogPath)

        self.TrackerIDs = []
        self.OutputMessages = []

        self.TimesUp = 0

        self.send()

    def Output(self, hits):
        file = open(self.OutputPath,"w+")
        file.write("PyPhisher 2.0 Output\n")
        file.write("Time: " + str(datetime.datetime.now()) + "\n\n\n")
        for item in self.OutputMessages:
            file.write(item + "\n")
        file.write("\n\nTracker Hits: \n")
        for hit in hits:
            file.write("HIT: " + hit + "\n")

    def Timer(self):
        self.Log.write("INFO", "TrackTime = " + str(self.TrackTime))
        time.sleep(60*int(self.TrackTime))
        self.TimesUp = 1

    def Track(self):
        self.Log.write("INFO", "Tracking web log: " + self.TrackPath)
        hit = []
        thread.start_new_thread(self.Timer)
        weblog = open(self.TrackPath,'r')
        while self.TimesUp == 0:
            weblog.seek(0,2)
            line = weblog.readline()
            if not line:
                time.sleep(0.1)
                continue
            else:
                for ID in self.TrackerIDs:
                    if ID in line:
                        print "ID Hit: " + ID
                        hit.append(ID)

        return hit

    def generateTracker(self, WWWpath):
        trackid = self.generateTrackID()
        trackdotfile = os.getcwd() + "/trackdot.gif"
        copyloc = os.path.join(WWWpath, trackid) + ".gif"
        call(["cp", trackdotfile, copyloc])
        return trackid

    def generateTrackID(self):
        id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.TrackerIDs.append(id)
        return id

    def send(self):
        self.Log.write("INFO","PyPhisher 2.0 Started...")

        bodies = []

        for body in self.BodyPath:
            with open(body,"r") as BodyFile:
                lines = BodyFile.readlines()

                bodytype = 1 # 1 = html, 0 = plaintext
                CampaignID = ""
                body = ""

                for line in lines:
                    if line.startswith("!#~"):

                        linesplit = line.split("!#~")
                        lineitem = linesplit[1]

                        if lineitem.startswith("TYPE") or lineitem.startswith("CAMPAIGN"):
                            lineitem = lineitem.split("=")
                            if lineitem[1].lower() == "html":
                                bodytype = 1
                            elif lineitem[1].lower() == "plain":
                                bodytype = 0
                            else:
                                CampaignID = lineitem[1]

                    body = body + line
                    bodies.append(CampaignID, bodytype, body)

        emailindex = 0
        with open(self.ToFilePath,"r") as ToFile:
            self.Log.write("INFO","Reading ToFile...")
            lines = ToFile.readlines()

            try:
                smtplib.SMTP(self.SMTPServer,self.SMTPPort)
                self.Log.write("INFO","Connected to SMTP Server: " + self.SMTPServer + ":" + str(self.SMTPPort))
            except:
                self.Log.write("ERROR", "Unable to connect to SMTP Server: " + self.SMTPServer + ":" + str(self.SMTPPort))
                print "[ERROR] Unable to connect to SMTP server"

            if self.RequireTLS is 1:
                try:
                    smtp.starttls()
                    self.log.write("INFO","TLS Initiated...")
                except:
                    self.log.write("ERROR", "Unable to initiate TLS")
                    print "[ERROR] Unable to initiate TLS"

            try:
                smtp.login(self.SMTPUsername, self.SMTPPassword)
                self.log.write("INFO", "Logged into SMTP Server")
            except:
                self.log.write("ERROR", "Unable to login to SMTP Server")
                print "[ERROR] Unable to login to SMTP Server"

            for line in lines:
                if line.startswith("#") or len(line) < 1:
                    continue;
                else:
                    emailindex = emailindex + 1
                    split = line.split(",")
                    To_FirstName = split[0]
                    To_LastName = split[1]
                    To_Title = split[2]
                    ToAddress = split[3]
                    From_Name = split[4]
                    From_Address = split[5]
                    Subject = split[6]
                    attachmentpath = split[7]
                    track = split[8]
                    domain = split[9]
                    campaignID = split[10]

                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = Subject
                    msg['From'] = From_Name + "<" + From_Address + ">"
                    msg['To'] = To_FirstName + " " + To_LastName + "<" + ToAddress + ">"

                    campaignid = bodies[0]
                    type = bodies[1]
                    body = bodies[2]

                    self.OutputMessages.append("TO " + msg['To'] + " | FROM " + msg['From'] + " | CampaignID " + campaignid)

                    body = body.replace("{{To_FirstName}}", To_FirstName)
                    body = body.replace("{{To_LastName}}", To_LastName)
                    body = body.replace("{{To_Title}}", To_Title)
                    body = body.replace("{{ToAddress}}", ToAddress)
                    body = body.replace("{{From_Name}}", From_Name)
                    body = body.replace("{{From_Address}}", From_Address)
                    self.Log.write("INFO", "Replaced body commands with variables for email " + str(emailindex))

                    bodytype = ""

                    if track.lower() == "y":
                        bodytype = "html"
                        trackerid = ""
                        for www in self.WWWPaths:
                            if www.split(":")[1] == domain:
                                foundit = foundit + 1
                                trackerid = generateTracker(www.split(":")[0])
                                body = str(body) + str(track_Domain) + '/' + trackerid + '.gif"/>'
                                self.Log.write("INFO", "Added tracker (" + trackerid + ") to email " + str(emailindex))

                        if len(trackerid) < 1: # Default to the first path in the list
                            trackerid = generateTracker(self.WWWPaths[0].split(":")[0])

                    else:
                        if type == 1:
                            bodytype = "html"
                        else:
                            bodytype = "plain"


                    body = MIMETEXT(body,bodytype)
                    msg.attach(body)
                    self.Log.write("INFO", "Attached body of type " + bodytype + " to email " + str(emailindex))

                    if attachmentpath.lower() == "na":
                        continue;
                    else:
                        att = MIMEBASE('application',"octet-stream")
                        att.set_payload(open(attachmentpath,"rb").read())
                        Encoders.encode_base64(att)
                        head, tail = os.path.split(attachmentpath)

                        att.add_header('Content-Disposition', 'attachment; filename="' + tail + '"')
                        msg.attach(att)
                        self.Log.write("INFO", "Attached file " + tail + " to email " + str(emailindex))

                        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
                        self.Log.write("INFO", "Sent Email: " + str(emailindex))
                        print str(emailindex) + ": Sent To [ " + msg['To'] + "] From [" + msg['From'] + "]"

        hits = self.Track()

        self.Output(hits)

print "PyPhisher Version 2.0"
print "Daniel Bloom - Daniel@bcdefense.com | Daniel_Bloom@fanniemae.com"
print "Twitter: @bcdannyboy"
usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)

parser.add_option("-t", "--to", dest="arg_ToFile",
                  metavar="/Path/To/ToFile.txt", help="Path to ToFile")
parser.add_option("-c", "--config", dest="arg_ConfigFile",
                  metavar="/Path/To/PyPhisher.config", help="Config File Path")
(options, args) = parser.parse_args()


if not options.arg_ToFile or not options.arg_ConfigFile:
    parser.print_help()
    exit()
else:
    SMTP = ""
    Port = 25
    Username = ""
    Password = ""
    RequireTLS = 0
    WWWPath = []
    OutputPath = ""
    LogPath = ""
    BodyPath = []
    TrackPath = ""
    TrackTime = ""

    ToFile = options.arg_ToFile
    with open(options.arg_ConfigFile,"r") as ConfigFile:
        lines = ConfigFile.readlines()

        for line in lines:
            if line.startswith("#") or len(line) < 2:
                continue;
            else:
                split = line.split("=")
                command = line[0].strip()
                option = line[1].strip()

                if command == "SMTP":
                    splitSMTP = option.split(":")

                    SMTP = splitSMTP[0].strip()
                    try:
                        Port = int(splitSMTP[1].strip())
                    except:
                        print "[ERROR]: Invalid Port"
                        exit()

                elif command == "SMTPCredentials":
                    splitSMTP = option.split(":")

                    Username = splitSMTP[0]
                    Password = splitSMTP[1]

                elif command == "RequireTLS":
                    if option == "TRUE":
                        RequireTLS = 1
                    else:
                        RequireTLS = 0

                elif command == "WWWPath":
                    WWWPath = option.split(",")

                elif command ==  "OutPath":
                    OutputPath = option

                elif command == "LogPath":
                    LogPath = option

                elif command == "BodyPath":
                    BodyPath = option.split(",")

                elif command == "WebServerLog":
                    TrackPath = option

                elif command == "TrackTime":
                    TrackTime = int(option)


    print ToFile
    print SMTP
    print Port
    print Username
    print Password
    print RequireTLS
    print BodyPath
    print WWWPath
    print OutputPath
    print LogPath
    print TrackPath
    print TrackTime
    PyPhisher = PyPhisher(ToFile, SMTP, Port, Username, Password, RequireTLS,
                          BodyPath, WWWPath, OutputPath, LogPath, TrackPath, TrackTime)
