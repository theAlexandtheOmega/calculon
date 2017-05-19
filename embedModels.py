#!/usr/bin/python3

import discord

def createScoreEmbed(user, score, botUser):
  sCard=discord.Embed()
  sCard.set_author(name=botUser.name, icon_url=botUser.avatar_url)
  sCard.title='-=<%s>=-' % user.name
  sCard.url='http://google.com'
  sCard.type='rich'
  sCard.color=discord.Color.dark_grey()
  sCard.add_field(name='User', value=user.name)
  sCard.add_field(name='Score', value=score.score)
  return sCard

def createDeletedEmbed(message, botUser):
  dCard=discord.Embed()
  dCard.set_author(name=message.author.name, icon_url=message.author.avatar_url)
  dCard.title='deleted message from %s in %s' % (message.author.name, message.channel)
  dCard.url='http://google.com'  
  dCard.type='rich'
  dCard.color=discord.Color.dark_grey()
  dCard.add_field(name='message content', value=message.content)
  return dCard

def createAdminEmbed(message, cmd, result):
  aCard=discord.Embed()
  aCard.set_author(name=message.author.name, icon_url=message.author.avatar_url)
  aCard.title="Admin command executed"
  aCard.url='http://google.com'  
  aCard.type='rich'
  aCard.color=discord.Color.purple()
  aCard.add_field(name=cmd, value=result)
  aCard.add_field(name='Channel', value=message.channel.name)
  aCard.add_field(name='message content', value=message.content)
  return aCard

def createAlertEmbed(message, cmd):
  aCard=discord.Embed()
  aCard.set_author(name=message.author.name, icon_url=message.author.avatar_url)
  aCard.title="Admin command attempt"
  aCard.url='http://google.com'  
  aCard.type='rich'
  aCard.color=discord.Color.red()
  aCard.add_field(name='Channel', value=message.channel.name)
  aCard.add_field(name=cmd, value="user attempted to use admin command!")
  aCard.add_field(name='message content', value=message.content)
  return aCard
  
def createFlipEmbed(contentString, botUser):
  fCard=discord.Embed()
  fCard.set_author(name=botUser.name, icon_url=botUser.author.avatar_url)
  fCard.title="Coin Toss"
  fCard.url='http://google.com'  
  fCard.type='rich'
  fCard.color=discord.Color.gold()
  fCard.add_field(name='...', value=contentString)
  return fCard

def createLogEmbed(message, result):
  lCard=discord.Embed()
  lCard.set_author(name=message.author.name, icon_url=message.author.avatar_url)
  lCard.title="Bot command executed"
  lCard.url='http://google.com'  
  lCard.type='rich'
  lCard.color=discord.Color.blue()
  lCard.add_field(name='Command Result', value=result)
  lCard.add_field(name='Channel', value=message.channel.name)
  lCard.add_field(name='message content', value=message.content)
  return lCard

