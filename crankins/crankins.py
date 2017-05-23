#!/usr/bin/python3

import discord
from unisettings import Settings
from discord.ext.commands import Bot


global unisettings
unisettings=Settings()

global server1, server2



client = discord.Client()

@client.event
async def on_message(message):
    global unisettings
    if message.author.id==unisettings['owner'] and message.content.startswith('b!servers'):
        print('beggining obj collection')
        unisettings['server1']=client.get_server(unisettings['srvr1'])
        unisettings['server2']=client.get_server(unisettings['srvr2'])
        unisettings['stage']=1
        print('completed obj collection')
    if message.author.id==unisettings['owner'] and message.content.startswith('b!clear') and unisettings['stage']==1:
        print('initiating wipe')
        channels=list() 
        for channel in unisettings['server2'].channels:
            channels.append(channel)
        for channel in channels:
            print('removing channel %s' % channel.name)
            if channel.is_default==False:
                print('removing')
                await client.delete_channel(channel)
        roles=list()        
        for role in unisettings['server2'].roles:
          roles.append(role)
        for role in roles:
            if role.is_everyone is False and role.name not in ('ninja'):
                print('deleting role %s' % role.name)
                await client.delete_role(unisettings['server2'], role)
        unisettings['stage']=2
    if message.author.id==unisettings['owner'] and message.content.startswith('b!build') and unisettings['stage']==2:
        roleList=sorted(unisettings['server1'].roles, key=lambda role: role.position)    
        for role in roleList:
            print('creating role %s' % role)
            if role.is_everyone is False and role.name not in ('ninja', 'satan'):
                newRole=await client.create_role(unisettings['server2'], name=role.name, colour=role.colour, permissions=role.permissions, 
                                           hoist=role.hoist, mentionable=role.mentionable)
                await client.move_role(unisettings['server2'], newRole, role.position)
                
        channel1Default=discord.utils.get(unisettings['server1'].channels, is_default=True)        
        channel2Default=discord.utils.get(unisettings['server2'].channels, is_default=True)
       
        roleList=list()
        every1=discord.utils.get(unisettings['server1'].roles, is_everyone=True)
        chanl=list()
        for chan in unisettings['server1'].channels:              
          chanl.append(chan)
        chan1=chanl
        chanl.remove(channel1Default)
        chanl=sorted(chanl, key=lambda channel: channel.position)
        print(chanl)         
        nchan=list()
        newChannel=channel2Default
        await client.edit_channel(newChannel, name=channel1Default.name, type=channel1Default.type)
        for role in unisettings['server1'].roles:
            roleList.append(role)
        roleList.remove(every1)
        for role in roleList:
          for overWrites in channel1Default.overwrites:
                perms=channel1Default.overwrites_for(role)
                if perms is not None: 
                    role2=discord.utils.get(unisettings['server2'].roles, name=role.name, colour=role.colour)
                    print(role2.id)
                    print(role2.position)
                    print(role2.name)
                await client.edit_channel_permissions(newChannel, role2, perms)
        for channel in chanl:
            newChannel=await client.create_channel(unisettings['server2'], name=channel.name, type=channel.type)
            for role in unisettings['server1'].roles:
                    perms=channel.overwrites_for(role)
                    if perms is not None: 
                        role2=discord.utils.get(unisettings['server2'].roles, name=role.name, colour=role.colour)
                        await client.edit_channel_permissions(newChannel, role2, perms)
        chan1=sorted(chan1, key=lambda channel: channel.position)
        for channel in chan1: 
            if channel.type is discord.ChannelType.text:
                newChannel=discord.utils.get(unisettings['server2'].channels, name=channel.name, type=channel.type)
                await client.move_channel(newChannel, channel.position)
        unisettings['stage']=3
                
#             print('creating new channel %s' % channel.name)                
#             newChannel=await client.create_channel(unisettings['server2'], channel.name, type=channel.type)
#                 
#                 
#                 newChannel=await client.edit_channel(channel2Default, name=channel1Default.name, type=channel1Default.type)
#             for oW  in channel1Default.overwrites:
#                 perms=channel.overwrites_for(role)
#                 if perms is not None: 
#                     role2=discord.utils.get(unisettings['server1'].roles, name=role.name, colour=role.colour)
#                     print(role2)
#                     if role2:
#                         await client.edit_channel_permissions(newChannel,role2, perms)
#             print('moving channel %s to position %i' % (channel.name, channel.position))            
#             if channel.type is not discord.ChannelType.voice:
#                     await client.move_channel(newChannel,channel.position)

        
      #  await client.edit_channel(channel2Default, name=channel1Default.name, type= channel1Default.type)
     #   for oW in channel1Default.overwrites:
     ##           perms=channel.overwrites_for(role)
      #####          if perms is not None: 
           #         role2=discord.utils.get(unisettings['server2'].roles, name=role.name, colour=role.colour)
          #          if role2 is not None:
          #                await client.edit_channel_permissions(channel2Default,role2, perms)             
     #   await client.move_channel(channel2Default, channel1Default.position)

        

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(unisettings['token'])