#!/usr/bin/env python
# vim: ts=4:sw=4:et

import os

from twisted.internet import task, defer

from lowlevel import OMXPlayerDBusManager, OMXPlayer




def sleep(seconds, reactor):

    d = defer.Deferred()
    reactor.callLater(seconds, d.callback, None)
    return d



if __name__ == '__main__':

    import sys

    from twisted.logger import (globalLogBeginner, textFileLogObserver,
        LogLevelFilterPredicate, FilteringLogObserver, LogLevel)


    def setup_logging(debug=False):

        observer = textFileLogObserver(sys.stderr, timeFormat='%H:%M:%S.%f')
        loglevel = LogLevel.debug if debug else LogLevel.info
        predicate = LogLevelFilterPredicate(defaultLogLevel=loglevel)
        predicate.setLogLevelForNamespace(
            'txdbus.client.DBusClientFactory',
            LogLevel.warn,
        )
        observers = [FilteringLogObserver(observer, [predicate])]
        globalLogBeginner.beginLoggingTo(observers)


    @defer.inlineCallbacks
    def start_things(reactor, settings):

        executable = settings['executable']
        ld_lib_path = settings['ld_lib_path']
        dbus_mgr = OMXPlayerDBusManager(reactor, executable, ld_lib_path)

        yield dbus_mgr.connect_to_dbus()

        player1 = OMXPlayer('../videos/0-00.mkv', dbus_mgr, layer=10)
        player2 = OMXPlayer('../videos/2-01.mkv', dbus_mgr, layer=20, alpha=0)
        player3 = OMXPlayer('../videos/3-01.mkv', dbus_mgr, layer=30, alpha=0)

        yield player1.spawn()

        yield sleep(5, reactor)

        yield player2.spawn()

        delay = 0.01
        for alpha in range(1, 256, 15):
            yield player2.set_alpha(alpha)
            yield sleep(delay, reactor)

        yield sleep(2, reactor)

        for alpha in range(254, -1, -15):
            yield player2.set_alpha(alpha)
            yield sleep(delay, reactor)

        yield player2.stop(ignore_failures=False)


        yield sleep(5, reactor)


        yield player3.spawn()

        delay = 0.01
        for alpha in range(1, 256, 15):
            yield player3.set_alpha(alpha)
            yield sleep(delay, reactor)

        yield sleep(4, reactor)

        for alpha in range(254, -1, -5):
            yield player3.set_alpha(alpha)
            yield sleep(delay, reactor)


        yield player3.stop(ignore_failures=False)

        yield sleep(5000, reactor)

        yield player1.stop(ignore_failures=False)


    _DBUS_ENV_VAR_NAME = 'DBUS_SESSION_BUS_ADDRESS'
    if _DBUS_ENV_VAR_NAME not in os.environ:
        print('%s not set. DBus session running?' % _DBUS_ENV_VAR_NAME)
        sys.exit(-1)

    SETTINGS = {
        'executable': '/usr/bin/omxplayer.bin',
        'ld_lib_path': '/usr/lib/omxplayer',
    }

    setup_logging(debug='-d' in sys.argv)
    task.react(start_things, (SETTINGS,))

