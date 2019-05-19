# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function
"""
This is the SpiceBot events system.

We utilize the Sopel code for event numbers and
self-trigger the bot into performing actions
"""


import sopel
import functools


class BotEvents(object):
    """A dynamic listing of all the notable Bot numeric events.

    Events will be assigned a 4-digit number above 1000.

    This allows you to do, ``@module.event(botevents.BOT_WELCOME)````

    Triggers handled by this module will be processed immediately.
    Others will be placed into a queue.

    Triggers will be logged by ID and content
    """

    def __init__(self):
        self.RPL_WELCOME = '001'  # This is a defined IRC event
        self.BOT_WELCOME = '1001'
        self.BOT_READY = '1002'
        self.BOT_CONNECTED = '1003'
        self.BOT_LOADED = '1004'
        self.defaultevents = [self.BOT_WELCOME, self.BOT_READY, self.BOT_CONNECTED, self.BOT_LOADED]
        self.SpiceBot_Events = {
                                "assigned_IDs": {1000: "Default", 1001: "BOT_WELCOME", 1002: "BOT_READY", 1003: "BOT_CONNECTED", 1004: "BOT_LOADED"},
                                "triggers_recieved": {},
                                "trigger_queue": [],
                                "startup_required": [self.BOT_WELCOME, self.BOT_READY, self.BOT_CONNECTED],
                                }

    def __getattr__(self, name):
        ''' will only get called for undefined attributes '''
        eventnumber = max(list(self.SpiceBot_Events["assigned_IDs"].keys())) + 1
        self.SpiceBot_Events["assigned_IDs"][eventnumber] = str(name)
        setattr(self, name, str(eventnumber))
        return str(eventnumber)

    def trigger(self, bot, number, message="SpiceBot_Events"):
        pretriggerdict = {"number": str(number), "message": message}
        if number in self.defaultevents or self.check(self.BOT_CONNECTED):
            self.dispatch(bot, pretriggerdict)
        else:
            self.SpiceBot_Events["trigger_queue"].append(pretriggerdict)

    def dispatch(self, bot, pretriggerdict):
        number = pretriggerdict["number"]
        message = pretriggerdict["message"]
        pretrigger = sopel.trigger.PreTrigger(
            bot.nick,
            ":SpiceBot_Events " + str(number) + " " + str(bot.nick) + " :" + message
        )
        bot.dispatch(pretrigger)
        self.recieved({"number": number, "message": message})

    def recieved(self, trigger):
        if isinstance(trigger, dict):
            eventnumber = str(trigger["number"])
            message = str(trigger["message"])
        else:
            eventnumber = str(trigger.event)
            message = trigger.args[1]
        if eventnumber not in self.SpiceBot_Events["triggers_recieved"]:
            self.SpiceBot_Events["triggers_recieved"][eventnumber] = []
        self.SpiceBot_Events["triggers_recieved"][eventnumber].append(message)

    def check(self, checklist):
        if not isinstance(checklist, list):
            checklist = [str(checklist)]
        for number in checklist:
            if str(number) not in self.SpiceBot_Events["triggers_recieved"].keys():
                return False
        return True

    def startup_add(self, startlist):
        if not isinstance(startlist, list):
            startlist = [str(startlist)]
        self.SpiceBot_Events["startup_required"].extend(startlist)

    def startup_check(self):
        for number in self.SpiceBot_Events["startup_required"]:
            if str(number) not in self.SpiceBot_Events["triggers_recieved"].keys():
                return False
        return True

    def startup_debug(self):
        not_done = []
        for number in self.SpiceBot_Events["startup_required"]:
            if str(number) not in self.SpiceBot_Events["triggers_recieved"].keys():
                not_done.append(int(number))
        reference_not_done = []
        for item in not_done:
            reference_not_done.append(str(self.SpiceBot_Events["assigned_IDs"][item]))
        return reference_not_done

    def check_ready(self, checklist):
        def actual_decorator(function):
            @functools.wraps(function)
            def _nop(*args, **kwargs):
                while not self.check(checklist):
                    pass
                return function(*args, **kwargs)
            return _nop
        return actual_decorator

    def startup_check_ready(self):
        def actual_decorator(function):
            @functools.wraps(function)
            def _nop(*args, **kwargs):
                while not self.startup_check():
                    pass
                return function(*args, **kwargs)
            return _nop
        return actual_decorator


botevents = BotEvents()
