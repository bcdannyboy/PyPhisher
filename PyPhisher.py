from optparse import OptionParser
import smtplib
import random
import string
import shutil
import datetime
import time
import os
from subprocess import call
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

class Logger():
    def __init__(self, outputfile, logfile):
        if outputfile is not 0:
            self.output = open(outputfile, 'w+')
        if logfile is not 0:
            self.log = open(logfile, 'w+')

    def Log(self, message):
        logstring = str(datetime.datetime.now()) + "," + message + "\n"
        self.log.write(logstring)

    def Output(self, message):
        outstring = str(datetime.datetime.now()) + "," + message + "\n"
        self.log.write(outstring)

class Sender():
    def __init__(self, options):
        self.opt = options

        self.TrackerIDs = []
        self.ToAddress = []
        self.FromAddress = []

        self.OutputFile = ""
        self.LogFile = ""

        self.SendMail()


    def generateTrackers(self, amt, apachepath):
        for i in range(0, amt):
            trackdotfile = os.getcwd() + "/trackdot.gif"
            copyloc = os.path.join(apachepath, self.generateTrackID()) + ".gif"
            call(["cp", trackdotfile, copyloc])
            #shutil.copystat(trackdot, os.path.join(apachepath,self.generateTrackID() + ".gif"))

    def generateTrackID(self):
        id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.TrackerIDs.append(id)
        return id

    def Track(self, logfile, tracktime):
        hit = []

        while datetime.datetime.now() != datetime.timedelta(tracktime):
            logfile = open(logfile, 'r')
            logfile.seek(0,2)
            line = logfile.readline()
            if not line:
                time.sleep(0.1)
                continue
            else:
                for ID in self.TrackerIDs:
                    if ID in line:
                        print "ID Hit: " + ID
                        hit.append(ID)
            logfile.close()

        return hit

    def SendMail(self):
        singleto = 0
        tofile = 0

        singlefrom = 0
        fromfile = 0

        email_type = 0
        require_tls = 0

        additionalheaders = 0

        track = 0
        attach = 0
        log = 0
        output = 0
        watchlog = 0

        if self.opt.to_Address:
            to_Address = self.opt.to_Address
            singleto = 1
        if self.opt.to_First:
            to_fname = self.opt.to_First
        if self.opt.to_Last:
            to_lname = self.opt.to_Last
        if self.opt.to_File:
            to_File = self.opt.to_File

        if self.opt.from_Address:
            from_Address = self.opt.from_Address
            singlefrom = 1
        if self.opt.from_First:
            from_fname = self.opt.from_First
        if self.opt.from_Last:
            from_lname = self.opt.from_Last
        if self.opt.from_File:
            from_File = self.opt.from_File
            fromfile = 1

        if self.opt.smtp_Server:
            smtp_Server = self.opt.smtp_Server
        if self.opt.smtp_Port:
            smtp_Port = self.opt.smtp_Port
        if self.opt.require_tls:
            if self.opt.require_tls.lower() == 'y':
                require_tls = 1
        if self.opt.smtp_Username:
            smtp_user = self.opt.smtp_Username
        if self.opt.smtp_Password:
            smtp_pass = self.opt.smtp_Password

        if self.opt.email_Type:
            if str(self.opt.email_Type).lower() == "plain":
                email_type = 1
        if self.opt.body_File:
            body_File = self.opt.body_File
        if self.opt.subject_File:
            subject_File = self.opt.subject_File
        if self.opt.header_File:
            header_File = self.opt.header_File
            additionalheaders = 1

        if self.opt.Track_Email:
            track = 1
        if self.opt.Track_Path:
            track_Path = self.opt.Track_Path
        if self.opt.Track_Domain:
            track_Domain = self.opt.Track_Domain
        if self.opt.Track_Time:
            tracktime = int(self.opt.Track_Time)
        if self.opt.Apache_Log:
            apache_Log = self.opt.Apache_Log
            watchlog = 1

        if self.opt.attachment_file:
            attach_File = self.opt.attachment_file
            attach = 1
        if self.opt.Output_File:
            output_File = self.opt.Output_File
            output = 1
        if self.opt.Log_File:
            log_File = self.opt.Log_File
            log = 1


        if output is 1 and log is 1:
            Writer = Logger(output_File, log_File)
        elif output is 0 and log is 1:
            Writer = Logger(0, log_File)
        elif output is 1 and log is 0:
            Writer = Logger(output_File, 0)

        if singleto is 1:
            self.ToAddress.append(to_Address)
        elif self.opt.to_File:
            with open(to_File) as f:
                lines = f.readlines()

                for line in lines():
                    self.ToAddress.append(line)

        if singlefrom is 1:
            self.FromAddress.append(from_Address)
        else:
            with open(from_File) as f:
                lines = f.readlines()

                for line in lines():
                    self.FromAddress.append(line)

        if track is 1:
            self.generateTrackers(len(self.ToAddress), track_Path)

        smtp = smtplib.SMTP(smtp_Server, smtp_Port)

        if require_tls is 1:
            smtp.starttls()

        if log:
            Writer.Log("Logging in to SMTP")

        smtp.login(smtp_user, smtp_pass)

        with open(body_File, 'r') as bodyfile:
            body = bodyfile.read()
        with open(subject_File, 'r') as subjectfile:
            subject = subjectfile.read()

        i = 0
        for taddr in self.ToAddress:
            for faddr in self.FromAddress:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = faddr
                msg['To'] = taddr

                if track is 1:
                    if log:
                        Writer.Log("Attaching tracking dot")

                    body = str(body) + '<img src="' + str(track_Domain) + '/' + str(self.TrackerIDs[i]) + '.gif"/>'

                if email_type is 1:
                    body = MIMEText(body,"plain")
                else:
                    body = MIMEText(body,"html")

                if log:
                    Writer.Log("Attaching Body")
                msg.attach(body)

                if attach is 1:
                    att = MIMEBase('application', "octet-stream")
                    att.set_payload(open(attach_File, "rb").read())
                    Encoders.encode_base64(att)
                    head, tail = os.path.split(attach_File)


                    att.add_header('Content-Disposition', 'attachment; filename="' + tail + '"')
                    if log:
                        Writer.Log("Attaching File: " + tail)
                    msg.attach(att)

                if additionalheaders:
                    with open(header_File) as f:
                        lines = f.readlines()

                        for line in lines:
                            split = line.split(":")
                            msg[split[0]] = split[1]

                if log:
                    Writer.Log("Sending email to: " + msg['To'] + " from: " + msg['From'])

                smtp.sendmail(msg['From'], msg['To'], msg.as_string())

                if output:
                    Writer.Output("Sent to: " + msg['To'] + " from: " + msg['From'])

            i = i + 1

            if track is 1:
                hits = self.Track(apache_Log, tracktime)

            if output:
                for hit in hits:
                    Writer.Output("Tracker Hit: " + hit)



usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)

parser.add_option("-t", "--to", dest="to_Address",
                  help="Single address to email.", metavar="TO@EXAMPLE.COM")
parser.add_option("--tf", "--toFirst", dest="to_First",
                  help="First name of recipient", metavar="FIRSTNAME")
parser.add_option("--tl", "--toLast", dest="to_Last",
                  help="Last name of recipient", metavar="LASTNAME")
parser.add_option("-T", "--toFile", dest="to_File",
                  help="File of to names and email addresses", metavar="FILE")

parser.add_option("-f", "--from", dest="from_Address",
                  help="Address to send from", metavar="FROM@EXAMPLE.COM")
parser.add_option("--ff", "--fromFirst", dest="from_First",
                  help="First name of sender", metavar="FIRSTNAME")
parser.add_option("--fl", "--fromLast", dest="from_Last",
                  help="Last name of sender", metavar="LASTNAME")
parser.add_option("-F", "--fromFile", dest="from_File",
                  help="File of from names and addresses")

parser.add_option("-s", "--smtp", dest="smtp_Server",
                  help="SMTP Server", metavar="SMTPSERVER")
parser.add_option("-p", "--port", dest="smtp_Port",
                  help="SMTP Port", metavar="SMTPPORT")
parser.add_option("-l", "--tls", dest="require_tls",
                  help="Does the server require TLS?", metavar="Y/N")
parser.add_option("-U", "--username", dest="smtp_Username",
                  help="SMTP Username", metavar="USERNAME")
parser.add_option("-P", "--password", dest="smtp_Password",
                  help="SMTP Password", metavar="PASSWORD")

parser.add_option("-x", "--type", dest="email_Type",
                  help="Type of Email (plaintext/html)", metavar="Plain/HTML")
parser.add_option("-b", "--body", dest="body_File",
                  help="Body File", metavar="FILE")
parser.add_option("-S", "--subject", dest="subject_File",
                  help="Subject File", metavar="FILE")
parser.add_option("-H", "--header", dest="header_File",
                  help="Additional Email Headers", metavar="FILE")

parser.add_option("-r", "--track", dest="Track_Email",
                  help="Track the email?", metavar="Y/N")
parser.add_option("-R", "--trackpath", dest="Track_Path",
                  help="Path to apache public html directory", metavar="PATH")
parser.add_option("-d", "--trackdomain", dest="Track_Domain",
                  help="Domain to host tracker on", metavar="EXAMPLE.COM")
parser.add_option("-v", "--apachelog", dest="Apache_Log",
                  help="Path to apache log file", metavar="FILE")
parser.add_option("--tt", "--tracktime", dest="Track_Time",
                  help="time to track apache log in minutes")

parser.add_option("-a", "--attach", dest="attachment_file",
                  help="File to attach", metavar="FILE")
parser.add_option("-o", "--Output", dest="Output_File",
                  help="Path to .txt output file", metavar="FILE")
parser.add_option("-L", "--Log", dest="Log_File",
                  help="Path to .txt log file", metavar="FILE")
(options, args) = parser.parse_args()

if str(options.Track_Email).lower() is "y" and not options.Track_Path and not options.Track_Domain:
    print "option -t requires option -R and option -d and vice versa"
    exit()

if not options.smtp_Server or not options.smtp_Port or not options.smtp_Username or not options.smtp_Password:
    print "SMTP information is required"
    exit()

if options.to_Address and options.to_File:
    print "-t and -T are mutually exclusive"
    exit()

if options.from_Address and options.from_File:
    print "-f and -F are mutually exclusive"
    exit()



Send = Sender(options)
