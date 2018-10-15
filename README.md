# PyPhisher Version 2.0
PyPhisher is a lightweight, portable, easy to use, Python Phishing campaign generator / general mass emailer.
For usage information simply enter "Python PyPhisher.py" into a command line.

## Features
1. Send multiple emails using different domains, web host paths, bodies, and campaign identifiers
2. Replace in-body commands (i.e. {{To_FirstName}}) with their variable counterparts
3. Create, attach, and track 1x1 pixel tracking gifs
4. Send both plaintext and html emails with and without attachments.

## Body Commands
1. {{To_FirstName}} - first name of reveiver
2. {{To_LastName}} - last name of receiver
3. {{To_Title}} - title of receiver (i.e. mr., mrs., etc.)
4. {{ToAddress}} - receiver email address
5. {{From_Name}} - name of sender
6. {{From_Address}} - sender email address

## TODO 
1. Add ability to implement custom email headers
2. Add ability to implement custom body commands
3. Auto-generate email templates 
