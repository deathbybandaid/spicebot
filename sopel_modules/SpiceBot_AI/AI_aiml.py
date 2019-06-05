# coding=utf-8

from __future__ import unicode_literals, absolute_import, division, print_function

import sopel.module

import sopel_modules.SpiceBot as SpiceBot

import spicemanip


@sopel.module.rule('(.*)')
def bot_command_rule(bot, trigger):

    # TODO add config limits
    # but still allow in privmsg

    if trigger.nick == bot.nick:
        return

    if not len(trigger.args):
        return

    message = str(trigger.args[1]).encode('utf-8', 'replace')

    if is_ascii(message):
        return

    # ignore text coming from a valid prefix
    if str(message).startswith(tuple(bot.config.core.prefix_list)):
        trigger_args, trigger_command = SpiceBot.prerun.trigger_args(message, 'module')
        # patch for people typing "...", maybe other stuff, but this verifies that there is still a command here
        if trigger_command.startswith("."):
            return
        commands_list = []
        for commandstype in SpiceBot.commands.dict['commands'].keys():
            if commandstype not in ['rule', 'nickname']:
                for com in SpiceBot.commands.dict['commands'][commandstype].keys():
                    if com not in commands_list:
                        commands_list.append(com)
        if trigger_command not in commands_list:
            if not SpiceBot.letters_in_string(trigger_command):
                return
            invalid_display = ["I don't seem to have a command for " + str(trigger_command) + "!"]
            # invalid_display.append("If you have a suggestion for this command, you can run .feature ." + str(trigger_command))
            # invalid_display.append("ADD DESCRIPTION HERE!")
            bot.osd(invalid_display, trigger.nick, 'notice')
        return

    if str(message).lower().startswith(str(bot.nick).lower()):
        command_type = 'nickname'
        trigger_args, trigger_command = SpiceBot.prerun.trigger_args(message, 'nickname')
        fulltrigger = spicemanip.main(trigger_args, 0)
        if str(trigger_command).startswith("?"):
            return
        if fulltrigger in SpiceBot.commands.dict['nickrules']:
            return
        if trigger_command in SpiceBot.commands.dict['commands']["nickname"].keys():
            return
    else:
        command_type = 'module'
        trigger_args, trigger_command = SpiceBot.prerun.trigger_args(message, 'module')
        fulltrigger = spicemanip.main(trigger_args, 0)

    returnmessage = SpiceBot.botai.on_message(bot, trigger, message)
    if returnmessage:
        bot.osd(str(returnmessage))
    else:
        if command_type == 'nickname':

            if trigger_args[0].lower() in ["what", "where"] and trigger_args[0].lower() in ["is", "are"]:
                searchterm = spicemanip.main(trigger_args, "3+") or None
                if searchterm:
                    if trigger_args[0].lower() == "where":
                        searchreturn = SpiceBot.googlesearch(searchterm, 'maps')
                    else:
                        searchreturn = SpiceBot.googlesearch(searchterm)
                    if not searchreturn:
                        bot.osd('I cannot find anything about that')
                    else:
                        bot.osd(str(searchreturn))
                return

            closestmatches = SpiceBot.similar_list(trigger_command, SpiceBot.commands.dict['commands']["nickname"].keys(), 3, 'reverse')
            if len(closestmatches):
                closestmatches = spicemanip.main(closestmatches, "andlist")
                bot.osd("I don't know what you are asking me to do! Did you mean: " + str(closestmatches) + "?")
                return
            else:
                bot.osd("I don't know what you are asking me to do!")
                return


def is_ascii(s):
    try:
        s.decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True
