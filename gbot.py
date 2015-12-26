#!/usr/bin/env python3

import socket
import string
from lxml import html
import requests
import json
import urllib.request
from html import unescape
import re

import cfg

# this thing is global so it only has to be compiled into a regex object once
URLpattern = re.compile(r"((http(s)?):\/\/|(www\.)|(http(s)?):\/\/(www\.))[?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)")


HOST = cfg.HOST
PORT = cfg.PORT
NICK = cfg.NICK
IDENT = cfg.IDENT
REALNAME = cfg.REALNAME
CHANNEL = cfg.CHANNEL
KEY = cfg.KEY

CONNECTED = 0

headers = {
    'User-Agent': 'gBot: The IRC bot for noobs by noobs',
}

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

# get the title from a link and send it to the channel
def getTitle(link):
    try:
        page = requests.get(link, headers=headers, timeout=5)
        page.encoding = 'UTF-8'
        tree = html.fromstring(page.text)
        title = tree.xpath('//title/text()')
        say("^ " + title[0].strip())
    except Exception:
        print("Bad url in message: ", link)

# checks if given string is a url
# it must start with either http(s):// and/or www. and contain only
# characters that are acceptable in URLs
def isURL(string):
    match = URLpattern.fullmatch(string)
    if match:
        return True
    else:
        return False


class commands:
    usrlist = {}
    def smug(info,usrs):
        msg = info['msg'].replace(" ","")
        s = "Fuck you, "
        if ((msg not in usrs) or (("gamah" in str.lower(info['msg'])) or (str.lower(NICK) in str.lower(info['msg'])) or(info['msg'].isspace()))):
            s += info['user']
        else:
            s += msg
        s += "! :]"
        say(s)
    def swag(info,usrs):
       say("out of ten!")
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
        say(unescape(joke['value']['joke']).replace("  ", " "))
    def bacon(info,usrs):
        msg = info['msg'].replace(" ","")
        if(msg in usrs):
            say("\001ACTION gives " + msg + " a delicious strip of bacon as a gift from " + info['user'] + "! \001")
        else:
            say("\001ACTION gives " + info['user'] + " a delicious strip of bacon.  \001")
    def listusr(info,users):
        say("I reckon there are " + str(len(users)) + " users!")
        print(users)
    def btc(info,usrs):
        money = 0
        cur = 'USD'
        msg = info['msg'].split()
        url = "https://api.bitcoinaverage.com/ticker/global/all"
        req = urllib.request.urlopen(url)
        resp = req.read()
        data = json.loads(resp.decode('utf8'))
        if(len(msg) > 0):
            if(msg[0] in data):
                cur = msg[0]
        say(info['user'] + ": 1 BTC = " + str(data[cur]['ask']) + " " + cur)
    def lenny(info,usrs):
        usr = ""
        msg = info['msg'].split()
        if(len(msg) > 0 and msg[0] in usrs):
            usr = msg[0]
        else:
            usr = info['user']
        say( usr + ": ( ͡° ͜ʖ ͡°)")
    def eightball(info,usrs):
        msg = info['msg'][len(info['botcmd']):]
        url = "http://8ball.delegator.com/magic/JSON/"
        req = urllib.request.urlopen(url + msg)
        resp = req.read()
        data = json.loads(resp.decode('utf8'))
        say(data['magic']['answer'])
    def wisdom(info,usrs):
        page = requests.get('http://wisdomofchopra.com/iframe.php')
        tree = html.fromstring(page.content)
        quote = tree.xpath('//table//td[@id="quote"]//header//h2/text()')
        say(quote[0][1:-3])
    cmdlist ={
        "!smug" : smug,
        "!swag" : swag,
        "!cn" : norris,
        "!bacon" : bacon,
        "!users" : listusr,
        "!btc" : btc,
        "!lenny" : lenny,
        "!8ball" : eightball,
        "!wisdom" : wisdom
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
        if (out['cmd'] == "353"):
			#this is terrible... find a better way later
            newusrs = line[5:]
            newusrs = ' '.join(newusrs).replace('@','').split()
            newusrs = ' '.join(newusrs).replace('%','').split()
            newusrs = ' '.join(newusrs).replace('+','').split()
            newusrs = ' '.join(newusrs).replace(':','').split()
            newusrs = ' '.join(newusrs).replace('~','').split()
            for usr in newusrs:
                self.usrlist[usr] = ""
        if(out['cmd'] == "NICK"):
            self.usrlist[out['channel'][1:]] = self.usrlist[out['user']]
            del self.usrlist[out['user']]
        if (out['cmd'] == "PART" or out['cmd'] == "QUIT"):
            del self.usrlist[out['user']]
        if (out['cmd'] == "JOIN" and out['user'] != NICK):
            self.usrlist[out['user']] = ""
        if (out['cmd'] == "KICK"):
            del self.usrlist[line[3]]
        #run commands
        try:
            if(out['channel'] == CHANNEL):
                if(out['botcmd'][1:] in self.usrlist.keys()):
                    if(out['botcmd'][1:] == out['user']):
                        self.usrlist[out['user']] = out['msg']
                    else:
                        if(not self.usrlist[out['botcmd'][1:]].isspace()):
                            say(self.usrlist[out['botcmd'][1:]])
                else:
                    self.cmdlist[out['botcmd']](out,self.usrlist)
        except Exception as FUCK:
            print(FUCK)
        return(out)

bot = commands()
while 1:
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

            # check if the message in a channel contains a protocol or or www.
            if (x['cmd'] == 'PRIVMSG' and x['channel'] == CHANNEL):
                if( x['msg'].find("http") != -1 or x['msg'].find("www.") != -1):
                    msgArray = x['msg'].split(" ")
                    for l in msgArray:
                        if (isURL(l)):
                            # check if the link has a protocol if not add http
                            if not l.lower().startswith("http"):
                                l = 'http://' + l
                            getTitle(l)
