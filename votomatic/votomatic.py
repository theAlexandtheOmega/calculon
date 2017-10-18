#!/usr/bin/python3
import discord, asyncio, random, re, settings, time, textwrap
from votomaticDB import props
from votomaticDB import votes
from votomaticDB import comments
from votomaticDB import timers
from discord.ext.commands import Bot
salt='afgagsfghsdfhssdag'

global BotUser, organicTimer
global settings, pendingBills, mIds, messageDeque
settings=settings.Settings()
messageDeque=list()
pendingBills=list()
mIds=list()
organicTimer=dict()
def log(author, channel):
  return 
votomatic=Bot(command_prefix='vote!')
async def voteEmbed(message, data, votes=list(), arguments=list()):
  images={'active':'https://s3-us-west-2.amazonaws.com/calculonbot/active.png', 
            'pass':'https://s3-us-west-2.amazonaws.com/calculonbot/passed.png',
            'fail':'https://s3-us-west-2.amazonaws.com/calculonbot/failed.png',
            'tied':'https://s3-us-west-2.amazonaws.com/calculonbot/tied.png',
            'abstain':'https://s3-us-west-2.amazonaws.com/calculonbot/abstain.png'}
  colors={'active':discord.Color.blue(),
            'pass':discord.Color.green(),
            'fail':discord.Color.red(),
            'tied':discord.Color.gold(),
            'abstain':discord.Color.purple()}
  aCard=discord.Embed()
  aCard.set_author(name=message.author.name, icon_url=message.author.avatar_url)
  aCard.set_footer(text='%s      vote code:%s'  % ( time.ctime(data.endDate), str(data.id)), icon_url=message.author.avatar_url)
  aCard.title=data.title
 # aCard.description=data.body
  aCard.url='http://google.com'  
  aCard.type='rich'
  aCard.set_image(url=images[data.outcome])
  aCard.color=colors[data.outcome]
  aCard.add_field(name='Information', value=data.body)
  if arguments:
      for argument in arguments:
          user=await votomatic.get_user_info(argument.userID) 
          aCard.add_field(name='%s comments:' % user.name, value=argument.comment)
  aCard.add_field(name='votes', value=' ✅:%i      ❌:%i' % (votes[0], votes[1]))
  #aCard.add_field(name='yay!', value=votes[0])
  #aCard.add_field(name='nay!', value=votes[1])
  #aCard.add_field(name='Vote Ends:', value=time.ctime(data.endDate))
  return aCard
async def editor(edit, id):
    global mIds
    newMsg=await edit
    prop=props.updateProp(id, newMsg.id)
    if newMsg.id not in mIds:
        mIds.append(newMsg.id)
    return newMsg
def schedule_coroutine(target, *, loop=None):
    return asyncio.ensure_future(target, loop)
async def billWatch(bill):
    while True:
        if bill.complete or int(time.time())>bill.endDate:
            break
        print('pulse for ' + str(bill.id))
        await asyncio.sleep(10)
    bill=await closeProp(bill.id)
async def closeProp(id):
    global mIds
    prop=props.getProp(id)
    if prop and prop.complete==False:
        prop=props.closeProp(id)
        channel=votomatic.get_channel(id=prop.channelID)
        message=await votomatic.get_message(channel, prop.messageID)
        counts=votes.getVotes(id)
        if prop.title == '0' and prop.body == '0':
            user=await votomatic.get_user_info(prop.voteOwner)
            result="The vote is in!\n %s's vote on '*%s*' is complete and result is %i for Yes and %i for No." % (user.mention, message.content, counts[0], counts[1])
            await votomatic.clear_reactions(message)
            await destroyAnnounce(message, result, 10)
        else:
            results=await redrawEmbed(message)
            await votomatic.send_message(channel,id, embed=results)
            await votomatic.delete_message(message)
        mIds.remove(message.id)
    return True
async def redrawEmbed(message):
    counts=votes.getVotes(int(message.content))
    cmmnts=comments.getComments(int(message.content))
    pData=props.get(int(message.content))
    refresh=await voteEmbed(message, pData, counts, arguments=cmmnts)
    return refresh
@votomatic.event
async def on_ready():
    global BotUser
    BotUser=await votomatic.get_user_info('313178786692595713')
    await pendingLoop()
 #   asyncio.ensure_future(baName(), loop=None)
    print("Client logged in")
    return
async def pendingLoop():
    global pendingBills, mIds, messageDeque
    bills=props.getPending()
    pendingBills=list()
    if bills != None: 
        for bill in bills:
            message=await votomatic.get_message(votomatic.get_channel(bill.channelID), id=bill.messageID)
            votomatic.messages.append(message)
            print(bill)
            await getOfflineVotes(bill)
            if bill.endDate<int(time.time()):
                mIds.append(bill.messageID) 
                await closeProp(bill.id)
            else:    
                mIds.append(bill.messageID) 
                pendingBills.append(asyncio.ensure_future(billWatch(bill), loop=None))
    return
async def getOfflineVotes(prop):
    channel=votomatic.get_channel(prop.channelID)
    message=await votomatic.get_message(channel, id=prop.messageID)
    voteChanged=False
    vts={
        '✅':True, 
        '❌':False 
        }
    for vote in ['✅', '❌']:
        print('getOfflineVotes, %s' % vote)
        vote=discord.Reaction(message=message, emoji=vote)
        members=await votomatic.get_reaction_users(vote, limit=100)
        print(members)
        for member in members:
            if member.id != BotUser.id:
                print('getOfflineVotes, member.id != BotUser.id %s' % vote.emoji)
                voteChanged=True
                voted=votes.voteOn(member.id, prop.id, vts[vote.emoji])
                await votomatic.remove_reaction(message=message, emoji=vote.emoji, member=member)
    for vote in ['⭕']:    
        print('getOfflineVotes, %s' % vote)
        vote=discord.Reaction(message=message, emoji=vote)
        members=await votomatic.get_reaction_users(vote, limit=100)
        for member in members:
            if member.id != BotUser.id:
                print('getOfflineVotes, member.id != BotUser.id %s' % vote.emoji)
                voteChanged=True
                curVote=votes.getVote(member.id, prop.id)
                if curVote:
                    votes.deleteVote(curVote.id)                
                await votomatic.remove_reaction(message, emoji=vote.emoji, member=member)
    if voteChanged: 
        print('getOfflineVotes, voteChanged')
        Embed=await redrawEmbed(message)
        await votomatic.edit_message(message, prop.id, embed=Embed)
    return
@votomatic.event
async def on_reaction_add(reaction, user):
    print('add_reaction block')
    global mIds
    if user.bot: 
        return False
    vts={'✅':True,
           '❌':False,
           '⭕':'' }
    announce=''
    if reaction.message.id in mIds and reaction.emoji in ['✅', '❌', '⭕']:
        prop=props.propByMsgID(reaction.message.id)
        vote=votes.getVote(user.id, int(prop.id))
        if reaction.emoji in ['⭕']:
            if vote:
                announce='%s uses %s to clear their vote.' % (user.mention, reaction.emoji)
                votes.deleteVote(vote.id)
            else:
                await votomatic.remove_reaction(reaction.message, reaction.emoji, user)
                return
        else:
            if vote and vote.vote==vts[reaction.emoji]:
                await votomatic.remove_reaction(reaction.message, reaction.emoji, user)
                return
            announce='%s votes %s.' % (user.mention, reaction.emoji)
            vote=votes.voteOn(user.id, prop.id, vts[reaction.emoji])
        await votomatic.remove_reaction(reaction.message, reaction.emoji, user)
        if prop and prop.title != '0':
            msgEmbed=await redrawEmbed(reaction.message)
            edit=votomatic.edit_message(reaction.message, reaction.message.content, embed=msgEmbed)
            edited=await editor(edit, reaction.message.content)
        else:
            asyncio.ensure_future(destroyAnnounce(reaction.message, announce, time=4), loop=None)
    elif reaction.message.id in mIds and reaction.emoji not in ['✅', '❌', '⭕']:
        await votomatic.remove_reaction(reaction.message, reaction.emoji, user)
    return
async def destroyAnnounce(message, content, time=2):
    annce=await votomatic.send_message(message.channel, content=content)
    await asyncio.sleep(time)
    await votomatic.delete_message(annce)
    return
@votomatic.command(pass_context=True)
async def r(msg, amount):
    global mIds
    msg=msg.message
    amount=int(amount)
    bill=props.getProp(amount)
    if bill:
        if bill.title == '0' and bill.body == '0':
            return 
        if bill.complete != True:
            channel=votomatic.get_channel(bill.channelID)
            message=await votomatic.get_message(channel, id=bill.messageID)
            Embed=await redrawEmbed(message)
            newMessage=await votomatic.send_message(channel, message.content, embed=Embed)
            for emoji in ['✅', '❌', '⭕']:
                await votomatic.add_reaction(newMessage, emoji)
            props.updateProp(amount, newMessage.id)
            mIds.remove(message.id)
            await votomatic.delete_message(message)
            mIds.append(newMessage.id)
            if channel != msg.channel: 
                await votomatic.say('vote %i bumped to front of %s' % (bill.id, channel.mention))
        elif bill.complete==True:
            await votomatic.say('Vote already complete!')
    else:
        await votomatic.say('Vote not found/invalid vote code.')
    return True         
@votomatic.command(pass_context=True)
async def c(msg):
    msg=msg.message
    parser='\s(\d+)\|([\w|\n|\s|\W]*)'
    parsed=re.search(parser, msg.content)
    if parsed != None: 
        id=parsed.group(1)
        cmnt=parsed.group(2)
    else:
        votomatic.say('*comments should be in the following format:*  vote!comment vote code: this is the body')
        return False
    prop=props.get(int(id))
    if prop.title==0 and prop.body==0:
        return
    message=await votomatic.get_message(msg.channel, id=prop.messageID)
    wrap=textwrap.wrap(cmnt, 980)
    counter=1
    length=len(wrap)
    cmnts=list()
    for strng in wrap:
        cmnts.append(strng+'\n -=%i/ %i=-' % (counter, length))
        counter=counter+1
    if message:
        for comment in cmnts:
            comments.addComment(msg.author.id, msg.author.mention, prop.id, comment)
        embd=await redrawEmbed(message)
        edit=votomatic.edit_message(message, prop.id, embed=embd)
        await votomatic.delete_message(msg)
        edited=await editor(edit, int(id))
    else:
        return
@votomatic.command(pass_context=True)
async def e(msg, amount):
    global mIds
    msg=msg.message
    amount=int(amount)
    bill=props.getProp(amount)
    if bill.title==0 and bill.body==0:
        return
    if bill:
        if bill.complete != True and bill.voteOwner==msg.author.id:
            bill=await closeProp(bill.id)
        elif bill != True and bill.voteOwner != msg.author.id: 
            user=await votomatic.get_user_info(bill.voteOwner)
            await votomatic.say('Vote can only be closed by %s!' % user.mention)
        elif bill.complete==True:
            await votomatic.say('Vote already complete!')
    else:
        await votomatic.say('Vote not found/invalid vote code.')
    return True     
@votomatic.command(pass_context=True)
async def t(msg, amount):
    message=msg.message
    if amount=='profile':
        output='%s vote timers:\n' % message.author.name
        userTimers=timers.getTimers(message.author.id)
        if userTimers:
            for timer in userTimers:
                channel=votomatic.get_channel(timer.channelID)
                output=output+'%s is set to: %i seconds\n' % (channel.name, timer.duration)
            await votomatic.send_message(message.channel, output)
    elif isinstance(int(amount), int):
        duration=int(amount)
        setTimer=timers.setTimer(message.author.id, message.channel.id, duration)
        await votomatic.send_message(message.channel, 'votes in %s that you start will have a duration of %i seconds' % (message.channel.name, duration))
    else:
        await votomatic.send_message(message.channel, 'usage: vote!t <time in seconds>, vote!t profile')
    return 
@votomatic.command(pass_context=True)
async def s(msg,arg):
    global pendingBills, mIds
    msg=msg.message
    parser='\s(.+)\|([\w|\n|\s|\W]*)'
    parsed=re.search(parser, msg.content)
    if parsed != None: 
        subject=parsed.group(1)
        body=parsed.group(2)
    else:
        votomatic.say('*propositions should be in the following format:*  vote!public this is the title : this is the body')
        return False
    vData=props.makeProp(msg.channel.id, subject, body, msg.author.id)
    embed=await voteEmbed(msg, vData, [0, 0])
    propMessage=await votomatic.send_message(msg.channel, str(vData.id), embed=embed)
    for emoji in ['✅', '❌', '⭕']:
        await votomatic.add_reaction(propMessage, emoji)
    vData=props.updateProp(vData.id, propMessage.id)
    mIds.append(vData.messageID)
    pendingBills.append(asyncio.ensure_future(billWatch(vData), loop=None))
    return True      
@votomatic.event
async def on_message(message):
    if message.author.bot or message.channel.is_private:
        return
    await votomatic.process_commands(message)
    global pendingBills, mIds, organicTimer
    msg=message
    channel=msg.channel
    parser='.*(can vote|put it to a vote|vote on it|[sS]hould [Ii]|[aA]nyone wanna|[aA]nyone else|[dD]o you think|[hH]ave you ever|[sS]hould we).*'
    parsed=re.search(parser, msg.content)
    if parsed != None: 
        if channel.id not in organicTimer.keys() or organicTimer[channel.id]<int(time.time()):
            vData=props.quickProp(msg.id, msg.channel.id, msg.author.id)
            propMessage=msg
            for emoji in ['✅', '❌', '⭕']:
                await votomatic.add_reaction(propMessage, emoji)
            mIds.append(vData.messageID)
            pendingBills.append(asyncio.ensure_future(billWatch(vData), loop=None))
            organicTimer[channel.id]=int(time.time())+180
            return
        else:
            return
    else:
        return
@votomatic.command(pass_context=True)
async def board(msg):
    return
@votomatic.command(pass_context=True)
async def mids():
    print(mIds)











#async def baName():
#     members=list()
#     for server in votomatic.servers:
#         me=server.get_member('223564803224895488')
#         members.append(me)
#     letterName=[('B','2'), 
#                 ('a','1'),
#                 ('n','14')]
#     name='B.a.n.a.n.a'
#     while True: 
#         copy=list(letterName)
#         perm1=random.choice(copy)
#         copy.remove(perm1)
#         perm2=random.choice(copy)
#         name2=name
#         for perm in (perm1, perm2):
#             name2=name2.replace(perm[0], perm[1])
#         for member in members:
#             try:
#                 await votomatic.change_nickname(member, name2)
#             except:
#                 print('that is ok')
#             
#         sleep=random.randint(30, 60)
#         await asyncio.sleep(sleep)
        
        
        
    
votomatic.run(settings['token'])