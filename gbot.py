#!/usr/bin/env python

import socket
import string
from lxml import html
import requests
import json
import urllib.request
from html import unescape

import cfg

HOST = cfg.HOST
PORT = cfg.PORT
NICK = cfg.NICK
IDENT = cfg.IDENT
REALNAME = cfg.REALNAME
CHANNEL = cfg.CHANNEL
KEY = cfg.KEY
 
CONNECTED = 0

readbuffer = ""


s=socket.socket( )
s.connect((HOST, PORT))

s.send(bytes("NICK %s\r\n" % NICK, "UTF-8"))
s.send(bytes("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME), "UTF-8"))

def joinch(line):
    global CONNECTED
    if(line[1] == "005"):
        print("Connected! Joining channel")
        s.send(bytes("JOIN %s %s \r\n" % (CHANNEL,KEY), "UTF-8"));
        CONNECTED = 1

def getcmd(line):
    botcmd = ""
    if (len(line) > 3):
        if (line[3][:2] == ":!"):
            botcmd = line[3][1:]
    return (botcmd)
	
def getusr(line):
    sender = ""
    for char in line:
        if(char == "!"):
            break
        if(char != ":"):
            sender += char
    return (sender)

def getmsg(line):
    size = len(line)
    i = 3
    message = ""
    while(i < size): 
        message += line[i] + " "
        i = i + 1
    message.lstrip(":")
    return message[1:]
def say(msg):
    s.send(bytes("PRIVMSG %s :%s\r\n" % (CHANNEL, msg), "UTF-8"))
    return True
    

	
class commands:
    usrlist = []
    def smug(info,usrs):
        s = "Fuck you, "
        if (("gamah" in str.lower(info['msg'])) or (str.lower(NICK) in str.lower(info['msg'])) or(info['msg'].isspace())):
            s += info['user']
        else:
            s += info['msg'][:-1]
        s += "! :]"
        say(s)
    def swag(info,usrs):
       say("out of ten!")
    def paddy(info,usrs):
	    say("Get off my lawn!")
    def uncle(info,usrs):
        say("HACK THE PLANET!")
    def dogetick(info,usrs):
        say("1 DOGE = 1 DOGE")        
    def norris(info,usrs):
        msg = info['msg'].split()
        url = "http://api.icndb.com/jokes/random"
        if(len(msg) > 0):
            url += "?firstName=" + msg[0] + "&lastName="
        if(len(msg) > 1):
            url += msg[1]
        req = urllib.request.urlopen(url)
        resp = req.read()
        joke = json.loads(resp.decode('utf8'))
        say(unescape(joke['value']['joke']))
    def bacon(info,usrs):
        if(info['msg'].replace(" ","") in usrs):
            say("\001ACTION gives " + info['msg'] + " a delicious strip of bacon as a gift from " + info['user'] + "! \001")
        else:
            say("\001ACTION gives " + info['user'] + " a delicious strip of bacon.  \001")
    def listusr(info,users):
        say("I reckon there are " + str(len(users)) + " users!")
    cmdlist ={
        "!swag" : swag,
        "!paddy" : paddy,
        "!uncle" : uncle,
        "!dogetick" : dogetick,
        "!smug" : smug,
        "!cn" : norris,
        "!bacon" : bacon,
        "!users" : listusr
    }
    
    def parse(self,line):
		#info returned to main loop for further processing
        out = {
            'user' : getusr(line[0]),
	        'cmd' : line[1],
            'channel' :line[2],
            'msg' : getmsg(line)[len(getcmd(line)):],
            'botcmd' : getcmd(line)
        }
        #handle userlist here... WIP.
#        if (out['cmd'] == "353"):
#			#this is terrible... find a better way later
#            newusrs = line[6:]
#            newusrs = ' '.join(newusrs).replace('@','').split()
#            newusrs = ' '.join(newusrs).replace('%','').split()
#            newusrs = ' '.join(newusrs).replace('+','').split()
#            newusrs = ' '.join(newusrs).replace(':','').split()
#            newusrs = ' '.join(newusrs).replace('~','').split()
#            self.usrlist = self.usrlist + newusrs
#        if (out['cmd'] == "PART"):
#            self.usrlist.remove(out['user'])
#        if (out['cmd'] == "JOIN"):
#            self.usrlist.append(out['user'])
#        if (out['cmd'] == "KICK" or out['cmd'] == "QUIT"):
#            self.usrlist.remove(line[3])
        #run commands
        try:
            self.cmdlist[out['botcmd']](out,self.usrlist)
        except Exception as FUCK:
            print(FUCK)
        return(out)
    
bot = commands()
while 1:
    global CONNECTED
    readbuffer = readbuffer+s.recv(1024).decode("UTF-8",'ignore')
    temp = str.split(readbuffer, "\n")
    readbuffer=temp.pop( )
    for line in temp:
        line = str.rstrip(line)
        #print(line)
        line = str.split(line)
        #must respond to pings to receive new messages
        if(line[0] == "PING"):
            s.send(bytes("PONG %s\r\n" % line[1], "UTF-8"))
        elif(CONNECTED == 0):
            joinch(line)
        #housekeeping done, be a bot
        else:
            x = bot.parse(line)
            print (x)
            #print(bot.usrlist)
            if(x['msg'][:7] == "http://" or x['msg'][:4] == "www." or x['msg'][:8] == "https://"):
                try:
                    page = requests.get(line[3][1:])
                    tree = html.fromstring(page.text)
                    title = tree.xpath('//title/text()')
                    say("^ " + title[0])
                except Exception:
                    print("Bad url in message: ", x['msg'])
