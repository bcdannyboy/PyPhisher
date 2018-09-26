# coding: utf-8

import datetime
import os
from subprocess import call
import random
import string
import shutil
import time
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

import Log

class PyPhisher():
    def __init__(self):
        self.version = 1.0
        self.log = Log.Logger()
        self.log.MainLog("PYPHISHER", "PyPhisher initiated.")
        self.trackerhost = ""
        self.tracked = 0
        self.attachment = ""
        self.trackerwait = 0
        self.subject = ""
        self.format = ""
        self.smtpserver = ""
        self.smtpport = 0
        self.epass = ""
        self.body = ""
        self.tls = 0
        self.attachmentname = ""
        self.apachelog = ""
        self.efrom = ""
        self.apachewww = ""
        self.EmailList = []
        self.TrackerIDs = []

    def cls(self):
		try:
			call('clear' if os.name is 'posix' else 'cls')
		except:
			print "[Error] Unable to clear screen"

    # copy 1x1 pixel gif and rename to ID in /var/www/html folder (apache)
    def generateTrackers(self):
        for ID in self.TrackerIDs:
            trackdot = "trackdot.gif"
            shutil.copy(trackdot, self.apachewww + ID[0] + ".gif")

    # generate tracker ID names
    def generateTrackerIDs(self):
        for item in self.EmailList:
            id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            self.TrackerIDs.append([id,0])

    def OutputTracking(self):
        trackfile = open("PyPhisher_Tracker_Output.txt", 'w+')

        for ID in self.TrackerIDs:
            if ID[1] is 0:
                trackfile.write(ID + ",EMAIL UNOPENED\n")
            else:
                trackfile.write(ID + ",TRACKER TRIGGERED\n")

    # read apache logs to track email
    def Track(Self):
        time = datetime.datetime.now()

        while datetime.datetime.now() != (time + datetime.timedelta(self.trackerwait)):
            logfile = open(self.apachelog, 'r')
            logfile.seek(0,2)
            line = logfile.readline()
            if not line:
                time.sleep(0.1) # wait 0.1 seconds
                continue
            else:
                for ID in self.TrackerIDs:
                    if ID[0] in line:
                        ID[1] = 1

        self.OutputTracking()

    # send emails
    def Send(self):
        smtp = smtplib.SMTP(self.smtpserver, self.smtpport)

        if self.tls is 1:
            smtp.starttls()

        smtp.login(self.efrom, self.epass)

        i = 0
        for addr in self.EmailList:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self.subject
            msg['From'] = self.efrom
            msg['To'] = addr

            if self.tracked is 1:
                self.body = self.body + '<img src="' + self.trackerhost + '/' + self.TrackerIDs[i] + '.gif"/>'
            body = MIMEText(self.body, self.format)

            msg.attach(body)

            if len(self.attachment) is not 0:
                att = MIMEbase('application', "octet-stream")
                att.set_payload(open(self.attachment,"rb").read())
                Encoders.encode_base64(att)

                att.add_header('Content-Disposition', 'attachment; filename="' + self.attachmentname + '"')
                msg.attach(att)

            smtp.sendmail(msg['To'], msg['From'], msg.as_string())
            self.log.EmailLog("Sent email to " + msg['From'])
            i = i + 1

        if self.tracked is 1:
            print "All emails sent. moving to tracker."
            self.cls()
            self.Track()
        else:
            print "All emails sent untracked. Goodbye."
            exit()

    # get config info
    def Config(self):

        self.smtpserver = raw_input("║ Enter SMTP Server address: ")

        port = raw_input("║ Enter SMTP Port: ")

        try:
            self.smtpport = int(port)
        except Exception:
            print "[ERROR] Invalid Input: " + str(port)
            self.log.ErrorLog("Invalid Input: (" + str(port) + ")")
            self.cls()
            self.Config()

        tls = raw_input("║ does the the server require tls? (y/n): ")

        if tls is "y":
            self.tls = 1

        self.efrom = raw_input("║ Enter sender email address: ")
        self.epass = raw_input("║ Enter sender password: ")
        self.subject = raw_input("║ Enter Email Subject: ")

        print "║ What format should the email body be?"
        print "║ Options: 1 = html, 2 = plaintext"
        print "║ Note: If you would like to track emails HTML is necessary"
        format = raw_input("║ Format: ")

        try:
            format = int(format)
        except Exception:
            print "[ERROR] Invalid Input: " + str(format)
            self.log.ErrorLog("Invalid Input: (" + str(format) + ")")
            self.cls()
            self.Config()

        if format is 1:
            self.format = "html"
        else:
            self.format = "plain"

        body = raw_input("║ Enter path to body file: ")

        try:
            with open(body, 'r') as bodyfile:
                self.body = bodyfile.read()
        except Exception:
            print "[ERROR] could not read body file"
            self.log.ErrorLog("could not read body file: (" + str(body) + ")")
            self.cls()
            self.Config()

        attachment = raw_input("║ Does the email contain an attachment? (y/n): ")

        if attachment is "y":
            self.attachment = raw_input("║ Enter Attachment Path: ")
            self.attachmentname = raw_input("║ Enter Attachment Name (i.e. file.pdf): ")

        tracked = raw_input("║ Should emails be tracked? (y/n): ")

        if tracked is "y":
            self.tracked = 1
            self.format = "html"
            self.trackerhost = raw_input("║ Enter address of tracker host (i.e. 127.0.0.1, phishing.com, etc.): ")
            self.apachelog = raw_input("║ Enter path to apache access.log file: ")
            self.apachewww = raw_input("║ Enter path to apache html folder (i.e. /var/www/html): ")
            self.generateTrackerIDs()
            self.generateTrackers()

        print "║ How long should the tracker wait before outputting final report?"
        print "║ Input should be in minutes (i.e. 10 = 10 minutes)"
        self.trackerwait = raw_input("║ Wait Time: ")

        self.Send()

    def Phisher(self):
        print "╭────────────────────────────────────╮"
        print "│             PyPhisher              │"
        print "│   Version: 1.0      Daniel Bloom   │"
        print "╞════════════════════════════════════╡"
        print "│   How Should Emails Be Processed?  │"
        print "│                                    │"
        print "│ 1. Manual Enter                    │"
        print "│ 2. Read From File                  │"
        print "│ 3. Exit                            │"
        print "╰────────────────────────────────────╯"
        opt = raw_input("║ Please Enter Your Option: ")

        try:
            opt = int(opt)
        except Exception:
            print "[ERROR] Invalid Input: " + str(opt)
            self.log.ErrorLog("Invalid Input: (" + str(opt) + ")")
            self.cls()
            self.Phisher()

        if opt < 1 or opt > 3:
            print "[ERROR] Invalid Input: " + str(opt)
            self.log.ErrorLog("Invalid Input: (" + str(opt) + ")")
            self.cls()
            self.Phisher()

        if opt is 1:
            while 1:
                emailaddr = raw_input("║ Enter email address or 'END' to finish: ")
                if emailaddr == "END":
                    break
                else:
                    self.EmailList.append(emailaddr)

            self.log.EmailLog("Gathered list of from user.")
            self.cls()
            self.Config()

        elif opt is 2:
            pathname = raw_input("║ Enter file path: ")

            with open(pathname) as f:
                lines = f.readlines()

                for line in lines():
                    self.EmailList.append(line)

            self.log.EmailLog("Gathered list of from user.")
            self.cls()
            self.Config()

        elif opt is 3:
            exit()

PP = PyPhisher()
PP.Phisher()
