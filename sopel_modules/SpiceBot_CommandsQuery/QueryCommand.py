# coding=utf-8

from __future__ import unicode_literals, absolute_import, division, print_function

import sopel
import sopel.module

from sopel_modules.SpiceBot_Events.System import bot_events_check
from sopel_modules.SpiceBot_SBTools import sopel_triggerargs, similar_list, letters_in_string


import spicemanip


@sopel.module.rule('^\?(.*)')
def query_detection(bot, trigger):

    while not bot_events_check(bot, '2002'):
        pass

    commands_list = dict()
    for commandstype in bot.memory['SpiceBot_CommandsQuery']['commands'].keys():
        if commandstype != 'rule':
            for com in bot.memory['SpiceBot_CommandsQuery']['commands'][commandstype].keys():
                if com not in commands_list.keys():
                    if commandstype == 'nickname':
                        commands_list[str(bot.nick) + " " + com] = bot.memory['SpiceBot_CommandsQuery']['commands'][commandstype][com]
                    else:
                        commands_list[com] = bot.memory['SpiceBot_CommandsQuery']['commands'][commandstype][com]

    triggerargs, triggercommand = sopel_triggerargs(bot, trigger, 'query_command')

    # command issued, check if valid
    if not triggercommand or not len(triggercommand):
        return

    if not letters_in_string(triggercommand):
        return

    if triggercommand.endswith("+"):

        triggercommand = triggercommand[:-1]
        if not triggercommand or not len(triggercommand):
            return

        if triggercommand not in commands_list.keys():
            closestmatches = similar_list(bot, triggercommand, commands_list.keys(), 10, 'reverse')
            dispmsg = ["Cannot find any alias commands: No valid commands match " + str(triggercommand) + ".",
                        "The following commands match " + str(triggercommand) + ": " + spicemanip.main(closestmatches, 'andlist') + "."]
            bot.notice(dispmsg, trigger.nick)
            return

        realcom = triggercommand
        if "aliasfor" in commands_list[triggercommand].keys():
            realcom = commands_list[triggercommand]["aliasfor"]
        validcomlist = commands_list[realcom]["validcoms"]
        bot.notice("The following commands match " + str(triggercommand) + ": " + spicemanip.main(validcomlist, 'andlist') + ".", trigger.nick)
        return

    if triggercommand.endswith("?"):

        triggercommand = triggercommand[:-1]
        if not triggercommand or not len(triggercommand):
            return

        closestmatches = similar_list(bot, triggercommand, commands_list.keys(), 10, 'reverse')
        if not len(closestmatches):
            bot.notice("Cannot find any similar commands for " + str(triggercommand) + ".", trigger.nick)
        else:
            bot.notice("The following commands may match " + str(triggercommand) + ": " + spicemanip.main(closestmatches, 'andlist') + ".", trigger.nick)
        return

    commandlist = []
    for command in commands_list.keys():
        if command.lower().startswith(triggercommand):
            commandlist.append(command)

    if not len(commandlist):
        bot.notice("No commands start with " + str(triggercommand) + ".", trigger.nick)
    else:
        bot.notice("The following commands start with " + str(triggercommand) + ": " + spicemanip.main(commandlist, 'andlist') + ".", trigger.nick)
