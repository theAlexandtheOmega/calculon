#!/usr/bin/python3
from sqlobject import *
import discord, time, os, sys, settings
global settings
settings=settings.Settings()
def startEnd(uid, cid):
    start=int(time.time())
    timer=timers.getTimer(uid, cid)
    if timer:
            end=start+timer.duration
    else:
        end=start+settings['duration']
    return [start, end]
def createCxn():
 global settings
 cxnString=settings['database']
 cxn=connectionForURI(cxnString)
 sqlhub.processConnection=cxn
 return True
class props(SQLObject):
    voteOwner = StringCol()
    startDate = IntCol()
    endDate = IntCol()
    title = StringCol()
    channelID = StringCol()
    messageID = StringCol()
    body = StringCol()
    hidden = BoolCol()
    complete=BoolCol()
    outcome=StringCol()
    def makeProp(cid, subject, description, uid,  hidden=False):
        connected=createCxn()
        times=startEnd(uid, cid)
        while connected: 
            prop=props(
                messageID='NULL',
                voteOwner=uid,
                startDate=times[0], 
                endDate=times[1],
                channelID=cid,
                title=subject,
                body=description, 
                hidden=hidden,
                complete=False, 
                outcome='active'
                )
            connected=False
        return prop
    def updateProp(id, pid):
        connected=createCxn()
        while connected:
            prop=props.get(id)
            prop.messageID=pid 
            connected=False
        return prop
    def closeProp(pid):
        connected=createCxn()
        while connected:
            prop=props.get(pid)
            vote=votes.getVotes(prop.id, True)
            if vote[0] > vote[1]: 
                prop.outcome='pass'
                prop.complete=True
            elif vote[0] < vote[1]:
                prop.outcome='fail'
                prop.complete=True
            elif vote[0]==vote[1]:
                if vote[0]==0:
                    prop.outcome='abstain'
                else:    
                    prop.outcome='tied'
                prop.complete=True
            connected=False
        return prop
    def getProp(pid):
        connected=createCxn()
        while connected: 
            prop=props.select(props.q.id==pid).count()
            if prop != None:
                connected=False
                return props.get(pid)
            else:
                connected=False
        return False
    def checkProp(pid):
        connected=createCxn()
        exists=False
        while connected: 
            prop=props.get(pid)
            if prop != None and prop.complete==False:
                exists=True
            connected=False
        return exists
    def getPending():
        connected=createCxn()
        while connected:
            bills=props.select(props.q.complete==False)
            if bills != None:
              connected=False
            else:
              connected=False
              return False
        return bills
class votes(SQLObject):
    userID = StringCol()
    propID = IntCol()
    vote = BoolCol()
    def voteOn(uid, pid, vte):
        connected=createCxn()
        while connected:
            prop=props.selectBy(id=pid, complete=False).count()
            if prop==0:
                return False
            vote=votes.selectBy(userID=uid, propID=pid).count()
            if vote==0: 
                vote=votes(
                    userID=uid,
                    propID=pid, 
                    vote=vte
                    )
            else:
                vote=votes.selectBy(propID=pid, userID=uid).getOne()
                vote.vote=vte
            connected=False
        return True
    def getVotes(pid, hidden=True):
            yays=votes.selectBy(propID=pid, vote=True).count()
            nays=votes.selectBy(propID=pid, vote=False).count()
            return [yays, nays]
    def getVote(uid, pid):
        connected=createCxn()
        while connected: 
            vote=votes.selectBy(userID=uid, propID=pid)
            if vote != None: 
                return vote[0]
            else:
                return False
    def deleteVote(id):
        connected=createCxn()
        while connected: 
            votes.delete(id)
            connected=False
        return
class timers(SQLObject):
    userID=StringCol()
    channelID=StringCol()
    duration=IntCol()
    def getTimers(uid):
        connected=createCxn()
        while connected: 
            usertimers=timers.select(timers.q.userID==uid)
            connected=False
        if usertimers != None:
            return usertimers
        else: 
            return False
    def setTimer(uid, cid, dur):
        connected=createCxn()
        timer=timers.getTimer(uid, cid)
        while connected:
            if timer:
                timer.duration=dur
            else:    
                timer=timers(
                    userID=uid,
                    channelID=cid,
                    duration=dur)
            connected=False
        return True
    def getTimer(uid, cid):
        connected=createCxn()
        while connected:
            timer=timers.selectBy(userID=uid, channelID=cid)
            connected=False
        if timer.count() > 0:
            return timer.getOne()
        else:
            return False
class comments(SQLObject):
    userID=StringCol()
    mention=StringCol()
    propID=IntCol()
    comment=StringCol()
    def addComment(uid, mntn, pid, cmmnt):
        if props.checkProp(pid)==False:
            return False
        connected=createCxn()
        while connected:
            comment=comments(
                userID=uid,
                mention=mntn, 
                propID=int(pid),
                comment=cmmnt
                )
            connected=False
        return True
    def getComments(pid):
        if props.checkProp(pid):
            connected=createCxn()
            while connected:
                cmmnts=comments.select(comments.q.propID==pid)
                connected=False
            if cmmnts != None:
                return cmmnts
            else: 
                return False
        else: 
            return False             