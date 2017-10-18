#!/usr/bin/python3
import discord, asyncio, random, re, settings, time 
from votomaticDB import props
from votomaticDB import votes
from votomaticDB import comments
from votomaticDB import timers
from discord.ext.commands import Bot
salt='afgagsfghsdfhssdag'
global settings, pendingBills, mIds, messageDeque
settings=settings.Settings()
messageDeque=list()
pendingBills=list()
mIds=list()
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
    newMsg=await edit
    print(newMsg.id)
    prop=props.updateProp(id, newMsg.id)
    print(prop.messageID)
    mIds.append(newMsg.id)
    return newMsg
def schedule_coroutine(target, *, loop=None):
    return asyncio.ensure_future(target, loop)
async def billWatch(bill):
    while time.time()<bill.endDate:
        await asyncio.sleep(10)
    bill=await closeProp(bill.id)
async def closeProp(id):
    global mIds
    prop=props.getProp(id)
    if prop and prop.complete==False:
        prop=props.closeProp(id)
        channel=votomatic.get_channel(id=prop.channelID)
        message=await votomatic.get_message(channel, prop.messageID)
        count=votes.getVotes(id)
        results=await redrawEmbed(message)
        this=await votomatic.send_message(channel,id, embed=results)
        mIds.remove(message.id)
    return True
@votomatic.event
async def on_reaction_add(reaction, user):
    print('add_reaction block')
    global mIds
    if user.bot: 
        return False
    vts={'✅':True,
           '❌':False,
           '⭕':'' }
    if reaction.message.id in mIds and reaction.emoji in ['✅', '❌', '⭕']:
        if reaction.emoji in ['⭕']:
            vote=votes.getVote(user.id, int(reaction.message.content))
            if vote:
                votes.deleteVote(vote.id)
        else:
            vote=votes.voteOn(user.id, int(reaction.message.content), vts[reaction.emoji])
        await votomatic.remove_reaction(reaction.message, reaction.emoji, user)
        msgEmbed=await redrawEmbed(reaction.message)
        counts=votes.getVotes(int(reaction.message.content))
        msgEmbed.set_footer
        edit=votomatic.edit_message(reaction.message, reaction.message.content, embed=msgEmbed)
        edited=await editor(edit, reaction.message.content)
        mIds.remove(reaction.message.id)
    return
async def redrawEmbed(message):
    counts=votes.getVotes(int(message.content))
    cmmnts=comments.getComments(int(message.content))
    pData=props.get(int(message.content))
    refresh=await voteEmbed(message, pData, counts, arguments=cmmnts)
    return refresh
@votomatic.event
async def on_ready():
    await pendingLoop()
    print("Client logged in")
    return
async def pendingLoop():
    global pendingBills, mIds, messageDeque
    bills=props.getPending()
    pendingBills=list()
    if bills != None: 
        for bill in bills:
            print(bill)
            mIds.append(bill.messageID) 
            pendingBills.append(await billWatch(bill))
    return
@votomatic.event
async def on_message(message):
    print(message.content)
    if message.author.bot or message.channel.is_private:
        return
    await votomatic.process_commands(message)
    return 
@votomatic.command(pass_context=True)
async def c(msg):
    global mIds
    msg=msg.message
    parser='\s(\d+)\|(.+)'
    parsed=re.search(parser, msg.content)
    if parsed != None: 
        id=parsed.group(1)
        cmnt=parsed.group(2)
    else:
        votomatic.say('*comments should be in the following format:*  vote!comment vote code: this is the body')
        return False
    prop=props.get(int(id))
    message=await votomatic.get_message(msg.channel, id=prop.messageID)
    if message:
        comment=comments.addComment(msg.author.id, msg.author.mention, prop.id, cmnt)
        print(message.content)
        embd=await redrawEmbed(message)
        edit=votomatic.edit_message(message, prop.id, embed=embd)
        edited=await editor(edit, int(id))
        mIds.remove(prop.messageID)
    else:
        print('relevent message object is missing')
@votomatic.command(pass_context=True)
async def e(msg, amount):
    global mIds
    msg=msg.message
    amount=int(amount)
    bill=props.getProp(amount)
    if bill:
        if bill.complete != True and bill.voteOwner==msg.author.id:
            print(mIds)
            print(bill.messageID)
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
    parser='\s(.+)\|(.+)'
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
    print(propMessage.id)
    mIds.append(vData.messageID)
    pendingBills.append(await billWatch(vData))
    return True      
votomatic.run(settings['token'])