from roowifi import Roomba
from yapsy.IPlugin import IPlugin
from footman.settings import ROOMBAS
import time


class RoombaPlugin(IPlugin):
    """
    Abstraction of the Roomba plugin.  ROOMBA config setting must name
    available robots.
    """
    def __init__(self):
        IPlugin.__init__(self)
        self.command_priority = 1
        self.voice = None
        self.robots = []
        for r in ROOMBAS:
            self.robots.append({
                'ip_address': r['ip_address'],
                'name': r['name'],
            })

        self.commands = {
            '.*(?P<command>start|dock|clean|stop).*(?P<robot>' + '|'.join([r['name'].lower() for r in self.robots]) +
            '|all).*(robot|roomba).*': [
                {
                    'command': self.command,
                    'args': (None, None,),
                    'kwargs': {},
                    'command_priority': 0,
                }
            ]
        }

    def command(self, command_dict, comm_text, robot_text):
        """
        Give the robot a command
        """

        if comm_text:
            command_text = comm_text
        else:
            command_text = command_dict['command']

        if robot_text:
            robot_id_text = robot_text
        else:
            robot_id_text = command_dict['robot']

        if not self.voice:
            self.instantiate_voice()

        if robot_id_text == 'all' and (command_text == 'start' or command_text == 'clean'):
            self.voice.say({}, 'Launching all robots.')
            for r in self.robots:
                roo = Roomba(r['ip_address'])
                roo.idle()
                roo.clean()
        elif robot_id_text == 'all' and (command_text == 'dock' or command_text == 'stop'):
            self.voice.say({}, 'Docking all robots.')
            for r in self.robots:
                roo = Roomba(r['ip_address'])
                roo.idle()
                roo.dock()
            time.sleep(5)  # allow motors to spin down
            for r in self.robots:
                roo = Roomba(r['ip_address'])
                roo.idle()
                roo.dock()
        elif command_text == 'start' or command_text == 'clean':
            self.voice.say({}, 'Launching the ' + robot_id_text + ' robot.')
            for r in self.robots:
                if r['name'] == robot_id_text:
                    roo = Roomba(r['ip_address'])
                    roo.idle()
                    roo.clean()
        elif command_text == 'dock' or command_text == 'stop':
            self.voice.say({}, 'Docking the ' + robot_id_text + ' robot.')
            for r in self.robots:
                if r['name'] == robot_id_text:
                    roo = Roomba(r['ip_address'])
                    roo.idle()
                    roo.dock()
                    time.sleep(5)  # allow motors to spin down
                    roo.idle()
                    roo.dock()

        return None

    def instantiate_voice(self):
        """
        We need to separately instatiate this so yapsy doesn't get confused.
        """
        from footman.plugins.voice import VoicePlugin
        self.voice = VoicePlugin()
        return None


