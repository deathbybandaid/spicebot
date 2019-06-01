# coding=utf8
from __future__ import unicode_literals, absolute_import, division, print_function
"""
This is the SpiceBot AI system. Based On Chatty cathy
"""

import os
import aiml

from .Logs import logs


class SpiceBot_AI():

    def __init__(self):
        self.dict = {
                    "counts": 0,
                    }
        # Load AIML kernel
        self.aiml_kernel = aiml.Kernel()
        # Learn responses
        import sopel_modules
        for plugin_dir in set(sopel_modules.__path__):
            configsdir = os.path.join(plugin_dir, "SpiceBot_Configs")
            aimldir = os.path.join(configsdir, "aiml")
            aimlstarter = os.path.join(aimldir, "std-startup.xml")
            try:
                self.aiml_kernel.learn(aimlstarter)
                self.aiml_kernel.respond("LOAD AIML B")
                self.dict['counts'] += 1
            except Exception as e:
                logs.log('SpiceBot_AI', "Error loading %s: %s (%s)" % ('aiml', e, aimlstarter))
        logs.log('SpiceBot_AI', "Found " + str(self.dict['counts']) + " " + 'aiml' + " commands.", True)

    def on_message(self, message):
        try:
            aiml_response = self.aiml_kernel.respond(message)
        except WARNING:
            return None
        return aiml_response


botai = SpiceBot_AI()