import os
import subprocess
import shlex

from charms.reactive import hook
from charms.reactive import when
from charms.reactive import relations
from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.unitdata import kv

config = config()
kvdb = kv()


@hook('start')
def start():
    """Start iperf server

    """
    cmd = 'iperf -s -D -p {port}'.format(**config)
    proc = subprocess.Popen(shlex.split(cmd))
    kvdb.set('pid', proc.pid)
    status_set(
        'active',
        'Serving on port {}'.format(config['port']))


@hook('stop')
def stop():
    """Stop iperf server

    """
    pid = kvdb.get('pid')
    if pid:
        try:
            os.kill(pid, 0)
        except:
            pass


@when('config.changed')
def config_changed():
    stop()
    start()
    # tell related units about our new port
    iperf_available(
        relations.RelationBase.from_state('iperf.available'))


@when('iperf.available')
def iperf_available(iperf):
    if iperf:
        iperf.configure(config['port'])
