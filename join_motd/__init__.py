import collections
import os
from datetime import datetime
from typing import List, Optional, Callable, Any, Union, Dict

from mcdreforged.api.all import *


class ServerInfo(Serializable):
	name: str
	description: Optional[str] = None
	category: str = ''

	@classmethod
	def from_object(cls, obj) -> 'ServerInfo':
		if isinstance(obj, cls):
			return obj
		return ServerInfo(name=str(obj))


class Config(Serializable):
	serverName: str = 'HLCC'
	mainServerName: str = 'HLCC'
	serverList: List[Union[str, ServerInfo]] = [
		'Main',
		'Mirror',
		'Creative',
	]
	start_day: Optional[str] = '2025-02-01'


Prefix = '!!joinMOTD'
config: Config
ConfigFilePath = os.path.join('config', 'joinMOTD.json')


def get_day(server: ServerInterface) -> str:
	try:
		startday = datetime.strptime(config.start_day, '%Y-%m-%d')
		now = datetime.now()
		output = now - startday
		return str(output.days)
	except Exception as e:
		server.logger.warning(f'[joinMOTD] Failed to parse start_day: {e}')
		return '?'


def display_motd(server: ServerInterface, reply: Callable[[Union[str, RTextBase]], Any]):
	reply('§7=======§r Welcome back to §e{}§7 =======§r'.format(config.serverName))
	reply('今天是§e{}§r开服的第§e{}§r天'.format(config.mainServerName, get_day(server)))
	reply('§7-------§r Server List §7-------§r')

	server_dict: Dict[str, List[ServerInfo]] = collections.defaultdict(list)
	for entry in config.serverList:
		info = ServerInfo.from_object(entry)
		server_dict[info.category].append(info)
	for category, server_list in server_dict.items():
		header = RText('{}: '.format(category) if len(category) > 0 else '')
		messages = []
		for info in server_list:
			command = '/server {}'.format(info.name)
			hover_text = command
			if info.description is not None:
				hover_text = info.description + '\n' + hover_text
			messages.append(RText('[{}]'.format(info.name)).h(hover_text).c(RAction.run_command, command))
		reply(header + RTextBase.join(' ', messages))


def on_player_joined(server: ServerInterface, player, info):
	display_motd(server, lambda msg: server.tell(player, msg))


def on_load(server: PluginServerInterface, old):
	global config
	config = server.load_config_simple(file_name=ConfigFilePath, in_data_folder=False, target_class=Config)
	server.register_help_message(Prefix, '显示欢迎消息')
	server.register_command(Literal(Prefix).runs(lambda src: display_motd(src.get_server(), src.reply)))
