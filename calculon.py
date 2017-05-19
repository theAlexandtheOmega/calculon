#!/usr/bin/python3

import discord, time, random, re
import tokens, embedModels

from discord.ext.commands import Bot
global owner
owner='223564803224895488'
#tokenFile=open('token.txt', 'r')
#token=tokenFile.read()
#tokenFile.close()
token=tokens.calculonToken()

def logChannel(server):
  channelID='314297394399281154'
  logChan=server.get_channel(channelID)
  return logChan


def commandFlip(message):
    callMatrix={
    'h':['heads', "<:heads:311701066305503232>", 3],
    't':['tails', "<:tails:311701147457159189>", 3],
    'e':['edge', "<:edge:311701917614997505>", 10000]
     }
    output=list()
    call=str(message.content).replace("$flip", "")
    call=call.lstrip()
    print(call)
    if len(call)>>0:
      call=call[0]
    flip=random.randrange(1,1001)
    if flip==1001:
      flip='s'
    elif flip % 2==0: 
      flip='h'
    else:
      flip='t'
    print(flip) 
    print(call)
    payBot=calculonDB.subScore(message.server.id, message.author.id, 1)
    if call in ['h', 'e', 't'] and payBot:
      userCallString="%s flips a coin and calls %s..." % (message.author.mention, callMatrix[call][0])
    elif call in ['h', 'e', 't'] and payBot==False:
      output.append(calculon.send_message(message.channel, '*Calling a coin toss costs a point, Bro!*'))
      return [False,output]
    else: 
      call=0
      userCallString="%s flips a coin." % message.author.mention
    flipString="The coin lands.. %s.... %s!" % (callMatrix[flip][1], callMatrix[flip][0])
    if call==0: 
      winLoseString="Calculon steals your quarter!"	
    elif call==flip:
      payOut=calculonDB.addScore(message.server.id, message.author.id, callMatrix[call][2])
      winLoseString="%s wins!" % message.author.mention
    elif call != flip:
      winLoseString="%s loses!" % message.author.mention
    content="%s\n%s\n%s" % (userCallString, flipString, winLoseString)
    output.append(calculon.send_message(message.channel, content))
    return [True, output]

def commandEmote(message):
    type='emo'
    output=list()
    emote=str(message.content)
    author=message.author
    emote=emote.replace('$emote', '')
    if emote.lstrip()=='': 
      return [False, output]
    output.append(calculon.send_message(message.channel, '*%s %s*' % (author.mention, emote)))
    output.append(calculon.delete_message(message))
    addScore=calculonDB.addScore(message.server.id, message.author.id, 1, True)
    print(addScore)
    return [True, output]

def commandMark(message):
    type='mrk'
    output=list()
    content=str(message.content).replace('$mark', '')
    content=content.lstrip()
    if len(message.mentions)==1:
      payBot=calculonDB.subScore(message.server.id, message.author.id, 10)
      if payBot:
        butt=calculonDB.setMark(message.server.id, message.mentions[0].mention)
        output.append(calculon.send_message(message.channel, '*%s suddenly feels nervous.*' % butt[1]))
      else:
        output.append(calculon.send_message(message.channel, "*%s tries to mess with someone, but can't afford it!*" % message.author.mention))
      output.append(calculon.delete_message(message))
    if len(message.mentions)==0:
      if content.startswith("c"):
        butt=calculonDB.checkMark(message.server.id) 
        output.append(calculon.send_message(message.channel, "*%s is currently marked*" % butt[1]))
        output.append(calculon.delete_message(message))
        return [True, output]
      result=''
      payBot=calculonDB.subScore(message.server.id, message.author.id, 20)
      if payBot:
        butt=calculonDB.clearMark(message.server.id)
        output.append(calculon.send_message(message.channel, "*Calculon doesn't do impressions.*"))
        result=True
      else:
        output.append(calculon.send_message(message.channel, "*%s tries to clear someones name, but can't afford it!*" % message.author.mention))
        result=False
      output.append(calculon.delete_message(message))
    if len(message.mentions)>=2:
      output.append(calculon.send_message(message.channel, '*Calculon looks confused.*'))
      output.append(calculon.delete_message(message))  
      result=False
    return [result, output]

def commandFrame(message):
   butt=calculonDB.checkMark(message.server.id)
   output=list()
   type='frm'
   spoof=butt[1]
   emote=str(message.content).replace("$frame", "")
   if butt[0]:
    payBot=calculonDB.subScore(message.server.id, message.author.id, 1)
    if payBot:
      output.append(calculon.send_message(message.channel,'*%s %s*' % (spoof, emote)))
    else:
      return [False, output]
    output.append(calculon.delete_message(message))
   else: 
    return [False, output]
   return [True, output]

def commandCheck(message):
    member=''
    output=list()
    if len(message.mentions)==0:
      print('inside len==0 loop')
      memberScore=calculonDB.checkScore(message.server.id, message.author.id)
      member=message.author
    elif len(message.mentions)==1:
      userID=message.mentions[0].id
      memberScore=calculonDB.checkScore(message.server.id, userID)
      member=message.mentions[0]
    else:
      return [False, output]
    card=embedModels.createScoreEmbed(member, memberScore, calculon.user)   
    output.append(calculon.send_message(message.channel, '', embed=card))
    return [True, output] 

def commandGive(message):
  output=list()
  parser='\$give\s(\d+|a\sblowjob|some\sanal)\s<@.+'
  if len(message.mentions) !=1:
    output.append(calculon.send_message(message.channel, "Too litte or too many people mentioned.")) 
    return [False, output] 
  donor=message.author
  recipient=message.mentions[0]
  serverID=message.server.id
  amount=re.search(parser, message.content)
  if amount is None:
    output.append(calculon.send_message(message.channel, "That's not something you can give.")) 
    return [False, output] 
  else:
    amount=amount.group(1)
  if amount=='a blowjob' or amount=='some anal':
      newMsgContent='%s *gives* %s *%s*.\n **Tasty!**' % (donor.mention, recipient.mention, amount)
      output.append(calculon.send_message(message.channel,newMsgContent))
      return [True, output]
  payment=calculonDB.subScore(serverID, donor.id, int(amount))
  result=''
  if payment: 
    donation=calculonDB.addScore(serverID, recipient.id, amount)
    newMsgContent='%s *gave* %s *%i points!*' % (donor.mention, recipient.mention, int(amount))
    result=True
  else:
    newMsgContent="%s*, you don't have %i points to be giving away!*" % (donor.mention, amount)
    result=False
  output.append(calculon.send_message(message.channel, newMsgContent))
  return [result, output]

def commandVote(message): 
  output=list()
  result=''
  return [result, output]

def commandMute(message, logChannel):
  output=list()
  parser='\$mute\s(on|off|check)\s.+' 
  srvr=message.server.id
  author=message.author.id
  isAdmin=calculonDB.checkAdmin(srvr, author)
  member=message.mentions[0]
  subCmd=re.search(parser, message.content)
  if subCmd is None: 
    return [False, output]
  else: 
    subCmd=subCmd.group(1)
  if isAdmin is False and subCmd != 'check':
    msgContent='**This functionality is limited to bot admins**' 
    output.append(calculon.send_message(message.channel, msgContent))
    card=embedModels.createAlertEmbed(message, 'mute')
    output.append(calculon.send_message(logChannel, '', embed=card))
    return [False, output]
  result=''
  if len(message.mentions) != 1:
    return [False, output]
  elif subCmd=='on':
    muteUser=calculonDB.setMuted(srvr, member.id, True)
    if muteUser:
      msgContent='**%s has been muted.**' % member.mention
      output.append(calculon.send_message(message.channel, msgContent))
      result=True
    else:
      msgContent='**bot admins cannot be muted!**' 
      output.append(calculon.send_message(message.channel, msgContent))
      result=False
  elif subCmd=='off':
    muteUser=calculonDB.setMuted(srvr, member.id, False)
    if muteUser: 
      msgContent='**%s has been un-muted, behave yourself %s.**' % (member.mention, member.mention)
      output.append(calculon.send_message(message.channel, msgContent))
      result=True
  elif subCmd=='check':
      chck=calculonDB.checkMuted(srvr, member.id) 
      if chck:
        msgContent='*%s is currently muted by bot admins.*' % member.mention 
      elif chck==False: 
        msgContent='*%s is not muted.*' % member.mention
      output.append(calculon.send_message(message.channel, msgContent))
      result=True
  return [Result, output]

def commandBlowup(message): 
  output=list()
  result=''
  return [result, output]

def commandRedose(message): 
  output=list()
  result=''
  return [result, output]
calculon=Bot(command_prefix='!')

@calculon.event
async def on_ready():
    print("Client logged in")
    print(calculon.user.id)

@calculon.event
async def on_message(message):
  serverLogChannel=calculonDB.getLogging(message.server)
  await calculon.process_commands(message)
  if message.author.bot==False:
   print(message.channel.id)
   srvr=calculonDB.checkServer(message.server.id)
   usr=calculonDB.checkUser(message.author)
   mods=calculonDB.checkModules(srvr.serverID)
   if mods.mute:
     if calculonDB.checkMuted(srvr.serverID, usr.discordID): 
       logfile=embedModels.createDeletedEmbed(message, calculon.user)
       server=message.server
       await calculon.delete_message(message)
       await calculon.send_message(serverLogChannel, '', embed=logfile)
       return
   print('%s, %s, %s' % (str(usr), str(message.content), str(message.channel)))
   command_message=message
   if message.content.startswith('$flip') and mods.flip:
     newScript=commandFlip(message)
   elif message.content.startswith('$emote ') and mods.emote:
     newScript=commandEmote(message)
   elif message.content.startswith('$mark') and mods.mark:
     newScript=commandMark(message)
   elif message.content.startswith('$frame ') and mods.frame:
     newScript=commandFrame(message)
   elif message.content.startswith('$$$'):
     newScript=commandCheck(message)
   elif message.content.startswith('$give ') and mods.give:
     newScript=commandGive(message)
   elif message.content.startswith('$vote') and mods.vote:
     newScript=commandVote(message)
   elif message.content.startswith('$mute ') and mods.mute:
     newScript=commandMute(message, serverLogChannel)
   elif message.content.startswith('$blowup') and mods.blowup:
     newScript=commandBlowup(message)
   elif message.content.startswith('$redose' ) and mods.redose:
     newScript=commandBlowup(message)
   else:
     return    
   for action in newScript[1]:
     await action
   card=embedModels.createLogEmbed(message,newScript[0]) 
   await calculon.send_message(serverLogChannel, '', embed=card)
  return

@calculon.command(pass_context=True)
async def hello(*args):
    await calculon.say("Acting!")
    return

@calculon.command(pass_context=True)
async def setAdmin(msg, content:str):
    msg=msg.message
    serverLogChannel=calculonDB.getLogging(msg.server)
    global owner
    subs={
      'set' : True, 
      'unset' : False
      }
    parser='\!setAdmin\s(set|unset)\s\<@'
    print('post-parser')
    subCmd=re.search(parser, msg.content)
    if subCmd is not None: 
      cmd=subCmd.group(1)
      mbr=msg.mentions[0].id
      usr=msg.author.id
      print('%s, %s, %s' % (cmd, mbr, usr))
      if calculonDB.checkAdmin(msg.server.id, usr):
        if mbr is not owner:
          print('admin-accessed and !owner')
          if calculonDB.setAdmin(msg.server.id, mbr, subs[cmd]):
            print('set as admin')
            await calculon.say("Ok.")
          else:  
            await calculon.say("Ok.")
        if serverLogChannel:
            card=embedModels.createAdminEmbed(msg, cmd='setAdmin', result=True)
            await calculon.send_message(serverLogChannel, '', embed=card)
        return True    
      else: 
        if serverLogChannel:
            card=embedModels.createAlertEmbed(msg, cmd='setAdmin')
            await calculon.send_message(serverLogChannel, '', embed=card)
        return False
    await calculon.say("Command not processed")
    if serverLogChannel:
        card=embedModels.createAdminEmbed(message, cmd='setAdmin', result=True)
        await calculon.send_message(serverLogChannel, '', embed=card)
    return True

@calculon.command(pass_context=True)
async def ap(msg, amount=0):
    msg=msg.message
    usr=msg.author.id
    srv=msg.server.id
    serverLogChannel=calculonDB.getLogging(msg.server)
    if calculonDB.checkAdmin(srv, usr):
        if isinstance(amount, int):
          amnt=amount
        else:
          amount=0       
        if calculonDB.addScore(srv, usr, amount): 
          await calculon.say("added %i points to your score" % amount)               
          if serverLogChannel:
            card=embedModels.createAdminEmbed(msg, cmd='addPoints', result=True)
            await calculon.send_message(serverLogChannel, '', embed=card)
          return True    
    else: 
        if serverLogChannel:
            card=embedModels.createAlertEmbed(message, cmd='addPoints')
            await calculon.send_message(serverLogChannel, '', embed=card)
        await calculon.say("Command not processed")
        return False 
    return False

@calculon.command(pass_context=True)
async def test(msg):
    msg=msg.message
    serverLogChannel=calculonDB.getLogging(msg.server)
    usr=msg.author.id
    srv=msg.server.id
    scores=calculonDB.checkScore(srv, usr)
    embd=embedModels.createScoreEmbed(msg.author, scores, calculon.user)
    await calculon.send_message(msg.channel, '', embed=embd)
    if serverLogChannel:
        card=embedModels.createAlertEmbed(msg, cmd='setAdmin')
        await calculon.send_message(serverLogChannel, '', embed=card)
     
 
print(token)   
calculon.run(token)
