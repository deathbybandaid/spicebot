#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals, absolute_import, print_function, division

# sopel imports
import sopel.module
from sopel.config.types import StaticSection, ValidatedAttribute, ListAttribute

import sopel_modules.SpiceBot as SpiceBot

import spicemanip

import time


class SpiceBot_Channels_MainSection(StaticSection):
    announcenew = ValidatedAttribute('announcenew', default=False)
    joinall = ValidatedAttribute('joinall', default=False)
    operadmin = ValidatedAttribute('operadmin', default=False)
    chanignore = ListAttribute('chanignore')


def configure(config):
    config.define_section("SpiceBot_Channels", SpiceBot_Channels_MainSection, validate=False)
    config.SpiceBot_Channels.configure_setting('announcenew', 'SpiceBot_Channels Announce New Channels')
    config.SpiceBot_Channels.configure_setting('joinall', 'SpiceBot_Channels JOIN New Channels')
    config.SpiceBot_Channels.configure_setting('operadmin', 'SpiceBot_Channels OPER ADMIN MODE')
    config.SpiceBot_Channels.configure_setting('chanignore', 'SpiceBot_Channels Ignore JOIN for channels')


def setup(bot):
    SpiceBot.logs.log('SpiceBot_Channels', "Starting setup procedure")
    SpiceBot.events.startup_add([SpiceBot.events.BOT_CHANNELS])
    bot.config.define_section("SpiceBot_Channels", SpiceBot_Channels_MainSection, validate=False)


@sopel.module.event(SpiceBot.events.RPL_WELCOME)
@sopel.module.rule('.*')
def unkickable_bot(bot, trigger):
    if bot.config.SpiceBot_Channels.operadmin:
        bot.write(('SAMODE', bot.nick, '+q'))


@sopel.module.event(SpiceBot.events.RPL_WELCOME)
@sopel.module.rule('.*')
def request_channels_list_initial(bot, trigger):

    SpiceBot.channels.bot_part_empty(bot)

    SpiceBot.logs.log('SpiceBot_Channels', "Sending Request for all server channels")
    SpiceBot.channels.channel_list_request(bot)

    starttime = time.time()

    # wait 60 seconds for initial population of information
    while not SpiceBot.channels.dict['InitialProcess']:
        if time.time() - starttime >= 60:
            SpiceBot.logs.log('SpiceBot_Channels', "Initial Channel list populating Timed Out")
            SpiceBot.channels.dict['InitialProcess'] = True
        else:
            pass

    foundchannelcount = len(SpiceBot.channels.dict['list'].keys())
    SpiceBot.logs.log('SpiceBot_Channels', "Channel listing finished! " + str(foundchannelcount) + " channel(s) found.")

    SpiceBot.channels.join_all_channels(bot)
    SpiceBot.channels.chanadmin_all_channels(bot)

    if "*" in SpiceBot.channels.dict['list'].keys():
        del SpiceBot.channels.dict['list']["*"]

    SpiceBot.channels.bot_part_empty(bot)
    SpiceBot.events.trigger(bot, SpiceBot.events.BOT_CHANNELS, "SpiceBot_Channels")


@sopel.module.event('321')
@sopel.module.rule('.*')
def watch_chanlist_start(bot, trigger):
    SpiceBot.channels.channel_list_recieve_start()


@sopel.module.event('322')
@sopel.module.rule('.*')
def watch_chanlist_populate(bot, trigger):
    SpiceBot.channels.channel_list_recieve_input(trigger)


@sopel.module.event('323')
@sopel.module.rule('.*')
def watch_chanlist_complete(bot, trigger):
    SpiceBot.channels.channel_list_recieve_finish()


@sopel.module.event(SpiceBot.events.BOT_CHANNELS)
@sopel.module.rule('.*')
def trigger_channel_list_recurring(bot, trigger):
    while True:
        time.sleep(1800)
        SpiceBot.channels.bot_part_empty(bot)

        oldlist = list(SpiceBot.channels.dict['list'].keys())
        SpiceBot.channels.channel_list_request(bot)

        while SpiceBot.channels.channel_lock:
            pass

        newlist = [item.lower() for item in oldlist if item.lower() not in list(SpiceBot.channels.dict['list'].keys())]
        if "*" in newlist:
            newlist.remove("*")
        if len(newlist) and bot.config.SpiceBot_Channels.announcenew:
            bot.osd(["The Following channel(s) are new:", spicemanip.main(newlist, 'andlist')], bot.channels.keys())

        SpiceBot.channels.join_all_channels(bot)

        SpiceBot.channels.chanadmin_all_channels(bot)

        if "*" in SpiceBot.channels.dict['list'].keys():
            del SpiceBot.channels.dict['list']["*"]
        SpiceBot.channels.bot_part_empty(bot)