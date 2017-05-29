#!/usr/bin/python3
import discord
from unisettings import Settings
from discord.ext.commands import Bot
global unisettings
unisettings=Settings()
global server1, server2
def crankinsEmbed(serverOrigin, serverDestination):
  user=serverDestination.cUser
  sCard=discord.Embed()
  sCard.set_author(name=user.name, icon_url=user.avatar_url)
  sCard.title='server copy initiated by: %s' % user.name
  sCard.url='http://google.com'
  sCard.type='rich'
  sCard.color=discord.Color.dark_grey()
  sCard.add_field(name='Origin', value=serverOrigin.name)
  sCard.add_field(name='Channels', value=len(serverOrigin.channels))
  sCard.add_field(name='Roles', value=len(serverOrigin.roles))
  sCard.add_field(name='Destination', value=serverDestination.name)
  sCard.add_field(name='Channels', value=len(serverDestination.channels))
  sCard.add_field(name='Roles', value=len(serverDestination.roles))
  return sCard
def crankinsEmbed2(server, cCount, rCount):
  user=server.cUser
  sCard=discord.Embed()
  sCard.set_author(name=user.name, icon_url=user.avatar_url)
  sCard.title='%s server wiped by: %s' % (server.name, user.name)
  sCard.url='http://google.com'
  sCard.type='rich'
  sCard.color=discord.Color.dark_grey()
  sCard.add_field(name='Channels', value=cCount)
  sCard.add_field(name='Roles', value=rCount)
  return sCard
class serverObject():
    def __init__(self, server):
        self.server=server
        self.id=server.id 
        self.name=server.name
        self.dChannel=discord.utils.get(server.channels, is_default=True)
        self.dRole=discord.utils.get(server.roles, is_everyone=True)
        self.admin=discord.utils.get(server.roles, name='ninja')
        self.sRoles=self.sortroles(server.roles)
        self.saRoles=self.sortroles2(server.roles)
        self.roles=server.roles
        self.channels=server.channels
        self.sChannels=self.sortchannels(server.channels)
        self.saChannels=self.sortchannels2(server.channels)
        self.cUser=discord.utils.get(server.members, id=unisettings['owner'])        
    def sortroles(self, roles):
        roleList=list()
        for role in roles:
            roleList.append(role)
        roleList.remove(self.admin)
        roleList.remove(self.dRole)
        roleList=sorted(roleList, key=lambda role: role.position)
        return roleList
    def sortroles2(self, roles):
        roleList=list()
        for role in roles:
            if role.managed==False: 
                roleList.append(role)
        roleList.remove(self.admin)
        roleList.remove(self.dRole)
        roleList=sorted(roleList, key=lambda role: role.position)
        return roleList
    def sortchannels(self, channels):
        channelList=list()
        for channel in channels:
            if channel.type!=discord.ChannelType.voice:
                channelList.append(channel)
        channelList.remove(self.dChannel)
        channelList=sorted(channelList, key=lambda channel: channel.position)
        return channelList
    def sortchannels2(self, channels):
        channelList=list()
        for channel in channels:
            if channel.type!=discord.ChannelType.voice:
                channelList.append(channel)
        channelList=sorted(channelList, key=lambda channel: channel.position)
        return channelList
def stageOne(message):
    global  server1, server2
    commands=list()
    server1=client.get_server(unisettings['srvr1'])
    server2=client.get_server(unisettings['srvr2'])
    server1=serverObject(server1)
    server2=serverObject(server2)
    commands.append(client.send_message(server2.dChannel, 'beginning obj collection'))
    commands.append(client.send_message(server2.dChannel, 'completed obj collection'))
    objEmbed=crankinsEmbed(server1, server2)
    commands.append(client.send_message(server2.dChannel, '', embed=objEmbed))
    return commands   
def stageTwo(message):
    global server1, server2
    commands=list()
    commands.append(client.send_message(server2.dChannel, 'initiating wipe'))
    cCount=0
    for channel in server2.sChannels:
        commands.append(client.send_message(server2.dChannel, 'removing channel %s' % channel.name))
        commands.append(client.delete_channel(channel))
        cCount=cCount+1
    roles=server2.sRoles
    rCount=0
    for role in roles:
        commands.append(client.send_message(server2.dChannel, 'deleting role %s' %  role.name))
        commands.append(client.delete_role(server2, role))
        rCount=rCount+1
    delEmbed=crankinsEmbed2(server2, cCount, rCount)
    commands.append(client.send_message(server2.dChannel, '', embed=delEmbed))
    unisettings['stage']=2
    return commands    
def getPerms(channel, roles, newRoles):
    permIterator=list()
    for role in roles:
        perms=channel.overwrites_for(role)
        if perms != None: 
            permIterator.append(client.send_message(server2.dChannel, 'copying role permissions for %s role to %s channel.' % (role.name, channel.name)))
            role2=discord.utils.get(server2.roles, name=role.name, colour=role.colour)
            print(channel.name, role2.name, perms)
            permIterator.append(client.edit_channel_permissions(channel, role2, perms))
    return permIterator        
client = discord.Client()
@client.event
async def on_message(message):
    global unisettings, server1, server2
    if message.author.id is unisettings['owner']:
        print('not owner')
        return
    output=False
    if message.content in ['c!1', 'c!1 ']:
        output=stageOne(message)
        unisettings['stage']=1
    elif message.content in ['c!2 ', 'c!2'] and unisettings['stage']==1:
        output=stageTwo(message)
    if output:
        for command in output:
            await command
        return
    if unisettings['stage']==2 and message.content.startswith('c!3' ):
        roleList=server1.sRoles   
        for role in roleList:
            await client.send_message(server2.dChannel,'creating role %s' % role)
            newrole=(await client.create_role(server2.server, name=role.name, colour=role.colour, permissions=role.permissions, 
                                               hoist=role.hoist, mentionable=role.mentionable))
            await client.move_role(server2.server, newrole, role.position)
        await client.send_message(server2.dChannel, 'Syncing default channel %s' % server1.dChannel.name)
        await client.edit_channel(server2.dChannel, name=server1.dChannel.name, type=server1.dChannel.type)
        for role in server1.roles:
            if role.managed==True:
                manRole=discord.utils.get(server2.roles, name=role.name)
                await client.delete_role(server2.server, manRole)                
        perms=getPerms(server2.dChannel, server1.saRoles, server2.roles)
        for perm in perms: 
            await perm
        for channel in server1.sChannels:
            await client.send_message(server2.dChannel, 'creating channel %s' % channel.name)
            newChannel=await client.create_channel(server2.server, name=channel.name, type=channel.type)
            perms=getPerms(newChannel, server1.saRoles, server2.sRoles)
            for perm in perms: 
                await perm         
        for channel in server1.saChannels: 
            newChannel=discord.utils.get(server2.channels, name=channel.name, type=channel.type)
            await client.move_channel(newChannel, channel.position)
        await client.send_message(server2.dChannel, 'Complete')
        unisettings['stage']=3
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
client.run(unisettings['token'])