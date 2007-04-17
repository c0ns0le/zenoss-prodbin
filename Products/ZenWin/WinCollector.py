#################################################################
#
#   Copyright (c) 2007 Zenoss, Inc. All rights reserved.
#
#################################################################

import sys
import os
import time
from socket import getfqdn
import pythoncom

from twisted.internet import reactor, defer

import Globals
from Products.ZenHub.PBDaemon import FakeRemote, PBDaemon as Base
from Products.ZenHub.services import WmiConfig
from Products.ZenEvents.ZenEventClasses import Heartbeat
from Products.ZenUtils.Driver import drive, driveLater

from StatusTest import StatusTest
from WinServiceTest import WinServiceTest
from WinEventlog import WinEventlog

class WinCollector(Base):

    cycleInterval = 60.
    configCycleInterval = 20.

    initialServices = ['EventService', 'WmiConfig']

    heartbeat = dict(eventClass=Heartbeat,
                     device=getfqdn(),
                     component='zenwin')

    def __init__(self):
        self.heartbeat['component'] = self.agent
        self.wmiprobs = []
        Base.__init__(self)


    def processLoop(self):
        pass


    def startScan(self, unused=None):
        drive(self.scanCycle)


    def scanCycle(self, driver):
        now = time.time()
        try:
            yield self.eventService().callRemote('getWmiConnIssues')
            self.wmiprobs = driver.next()
            self.log.debug("Wmi Probs %r", (self.wmiprobs,))
            self.processLoop()
        except Exception, ex:
            self.log.exception("Error processing main loop")
        delay = time.time() - now
        driveLater(max(0, self.cycleInterval - delay), self.scanCycle)

        
    def buildOptions(self):
        Base.buildOptions(self)
        self.parser.add_option('-d', '--device', 
                               dest='device', 
                               default=None,
                               help="single device to collect")
        self.parser.add_option('--debug', 
                               dest='debug', 
                               default=False,
                               help="turn on additional debugging")


    def configService(self):
        return self.services.get('WmiConfig', FakeRemote())


    def updateDevices(self, cfg):
        pass


    def updateConfig(self, cfg):
        for a, v in cfg.monitor:
            current = getattr(self, a, None)
            if current is not None and current != v:
                self.log.info("Setting %s to %r", a, v);
                setattr(self, a, v)
        self.heartbeat['timeout'] = self.cycleInterval*3
        self.log.debug('Device data: %r' % (cfg.devices,))
        self.updateDevices(cfg.devices)


    def error(self, why):
        why.printTraceback()
        self.log.error(why.getErrorMessage())


    def reconfigure(self):
        try:
            d = self.configService().callRemote('getConfig')
            d.addCallbacks(self.updateConfig, self.error)
        except Exception, ex:
            self.log.exception("Error fetching config")
            return defer.fail(ex)
        reactor.callLater(self.configCycleInterval, self.reconfigure)
        return d

    def connected(self):
        d = self.reconfigure()
        d.addCallback(self.startScan)
