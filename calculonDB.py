#!/usr/bin/python3

from sqlobject import *
import discord, time, os, sys

global sqlSettings

if os.path.isfile('data/hasrun.log') is False:
    connected=createCxn()
    while connected():
        try:
          discordServers.createTable()
          botModules.createTable()
          discordUsers.createTable()
          discordScores.createTable()
          connected=False
        except:
          print('tables not created or already present!')
          connected=False
          sys.exit(0)
    file=open('data/hasrun.log', 'w')
    file.write('db library has run, tables created.')
    file.close()


def setDB(database):
    global sqlSettings
    sqlSettings=database
    return True

def nextScore():
    return int(time.time()+60)

def createCxn():
 cxnString=sqlSettings
 cxn=connectionForURI(cxnString)
 sqlhub.processConnection=cxn
 return True

class botModules(SQLObject):
  serverID = StringCol()
  emote = BoolCol()
  mark = BoolCol()
  frame = BoolCol()
  flip = BoolCol()
  give = BoolCol()
  vote = BoolCol()
  mute = BoolCol()
  blowup = BoolCol()
  redose = BoolCol()  

def checkModules(sID):
  connected=createCxn()
  while connected: 
    mods=botModules.select(botModules.q.serverID==sID)
    if mods.count()==0: 
      bModule=botModules(
              serverID=sID, 
              emote = True,
              mark = True,
              frame = True,
              flip = True,
              give = True,
              vote = False,
              mute = False, 
              blowup = False,
    	      redose = False
              )
      mods=botModules.select(botModules.q.serverID==sID)
    mods=mods[0]
    connected=False
  return mods 

class discordServers(SQLObject):
  serverID = StringCol()
  joinDate = IntCol()
  mark = BoolCol()
  marked = StringCol()
  channelID = StringCol()
  logging = BoolCol()
  
def checkServer(sID):
  connected=createCxn()
  while connected:
    check=discordServers.select(discordServers.q.serverID==sID)
    if check.count() is 0:
      dServer=discordServers(
        serverID=sID, 
        joinDate=int(time.time()),
        mark=False,
        marked='No one',
        channelID='',
        logging=False
        )
    check=discordServers.select(discordServers.q.serverID==sID)
    connected=False
  return check[0]

def setLogging(server, cID, OnOFF=False):
    srvr=checkServer(server.id)   
    channel=server.get_channel(cID)
    while connected:
        if OnOff is False:
            srvr.logging=False
            connected=False     
        srvr.logging=OnOff
    return srvr.logging
    
def getLogging(server):
    srvr=checkServer(server.id)
    if srvr.logging: 
        channel=server.get_channel(srvr.channelID)
    else:
        return False
    return channel

def getServers():
  connected=createCxn()
  while connected: 
   table=discordServers.get()
   connected=False
  return table

def setMark(sID, mention):
  server=checkServer(sID)
  connected=createCxn()
  while connected:
    server.mark=True
    server.marked=mention
    connected=False
  return [server.mark, server.marked]

def checkMark(sID):
  server=checkServer(sID)
  return [server.mark, server.marked]

def clearMark(sID):
  server=checkServer(sID)
  connected=createCxn()
  while connected:
    server.mark=False
    server.marked='No one'
    connected=False
  return [server.mark, server.marked]

class discordUsers(SQLObject):
  discordID = StringCol()
  discriminator = StringCol()
  bot = BoolCol()

def checkUser(author):
  print('starting')
  connected=createCxn()
  while connected:
    check=discordUsers.select(discordUsers.q.discordID==author.id)
    if check.count()==0:
      dUser=discordUsers(
        discordID=author.id,
        discriminator=author.discriminator,
        bot=author.bot)
      check=discordUsers.select(discordUsers.q.discordID==author.id)
    connected=False
  return check[0]
  
class discordScores(SQLObject):
  discordID = StringCol()
  serverID = StringCol()
  score = IntCol()
  timeLock = IntCol()
  muted = BoolCol()
  botAdmin = BoolCol()  

def checkScore(sID, uID): 
  connected=createCxn()
  while connected:
    dScore=discordScores.selectBy(serverID=sID, discordID=uID)
    if dScore.count()==0:
      newSscore=discordScores(
        score=0, 
        discordID=uID,
        serverID=sID,
        timeLock=0, 
        muted=False,
	    botAdmin=False
       	)
      dScore=discordScores.selectBy(serverID=sID, discordID=uID)
    dScore=dScore[0]
    connected=False
  return dScore

def addScore(sID, uID, amount, timed=False):
    dScore=checkScore(sID, uID)
    connected=createCxn()
    while connected:
      if timed:
        scoreTime=int(time.time())
        if (scoreTime < dScore.timeLock):
          connected=0
          return False
      dScore.timeLock=nextScore()
      dScore.score=dScore.score+int(amount)
      connected=False
    return True

def subScore(sID, uID, amount):
    dScore=checkScore(sID, uID)
    connected=createCxn()
    while connected:
      if (dScore.score >= amount):
        dScore.score=(int(dScore.score)-int(amount))
      else: 
        return False
      connected=False
    return True

def checkMuted(sID, uID): 
  dScore=checkScore(sID, uID)
  return dScore.muted

def checkAdmin(sID, uID): 
  dScore=checkScore(sID, uID)
  return dScore.botAdmin

def setAdmin(sID, uID, OnOff): 
  dScore=checkScore(sID, uID)
  connected=createCxn()
  while connected: 
    dScore.botAdmin=OnOff
    connected=False
  return dScore.botAdmin

def setMuted(sID, uID, mute=False):
  if checkAdmin(sID, uID):
    return False
  dScore=checkScore(sID, uID)
  connected=createCxn()
  while connected:
    dScore.muted=mute
    connected=False
  return [True, dScore.muted]

  
