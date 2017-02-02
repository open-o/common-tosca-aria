#
# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

from __future__ import absolute_import  # so we can import standard 'daemon'

import os


class BackgroundTaskContext(object):
    DEFAULT_ACQUIRE_TIMEOUT = 5
    DEFAULT_DIR = '~'
    DEFAULT_NAME = 'aria_rest'

    def __init__(self, name, rundir):
        self.name = name or self.DEFAULT_NAME
        self.acquire_timeout = self.DEFAULT_ACQUIRE_TIMEOUT
        self.rundir = os.path.abspath(rundir or os.path.expanduser(self.DEFAULT_DIR))
        self.pidfile_path = os.path.join(self.rundir, '{0}.{1}'.format(self.name, 'pid'))
        self.log_path = os.path.join(self.rundir, '{0}.{1}'.format(self.name, 'log'))


try:
    import signal

    from aria.utils.console import (puts, Colored)
    from daemon import DaemonContext
    from daemon.pidfile import TimeoutPIDLockFile
    from daemon.runner import is_pidfile_stale
    from time import sleep

    def start_daemon(context, task, **kwargs):
        pidfile = TimeoutPIDLockFile(context.pidfile_path, context.acquire_timeout)

        if is_pidfile_stale(pidfile):
            pidfile.break_lock()

        if pidfile.is_locked():
            pid = pidfile.read_pid()

            if pid is not None:
                puts(Colored.red('Already running at pid: %d' % pid))
            else:
                puts(Colored.red('Already running'))

            return None

        logfile = open(context.log_path, 'w+t')
        puts(Colored.blue('Starting'))

        with DaemonContext(pidfile=pidfile, stdout=logfile, stderr=logfile):
            task(**kwargs)

    def stop_daemon(context):
        pidfile = TimeoutPIDLockFile(context.pidfile_path, context.acquire_timeout)
        pid = pidfile.read_pid()

        if pid is not None:
            puts(Colored.blue('Stopping pid: %d' % pid))
            os.kill(pid, signal.SIGTERM)

            while pidfile.is_locked():
                puts(Colored.cyan('Waiting...'))
                sleep(0.1)
            puts(Colored.blue('Stopped'))
        else:
            puts(Colored.red('Not running'))


    def status_daemon(context):
        pid = TimeoutPIDLockFile(context.pidfile_path, context.acquire_timeout).read_pid()

        if pid is not None:
            puts(Colored.blue('Running at pid: %d' % pid))
        else:
            puts(Colored.blue('Not running'))

except ImportError as e:

    def start_daemon(context, task, **kwargs):
        puts(Colored.red('Cannot start daemon in this environment, reason: {0}'.format(str(e))))


    def stop_daemon(context):
        puts(Colored.red('Not running'))


    def status_daemon(context):
        puts(Colored.blue('Not running'))
