"""Kalm OS System Modules"""
__version__ = "4.3.0"

from system.config import *
from system.auth import auth_system
from system.task_manager import TaskManager, network_monitor
from system.file_manager import FileManager
from system.program_detector import ProgramDetector
from system.script_runner import ScriptRunner
from system.virtual_runner import VirtualRunner
from system.registry import get_dns_server, get_proxy_server

__all__ = [
    'auth_system',
    'TaskManager',
    'network_monitor',
    'FileManager',
    'ProgramDetector',
    'ScriptRunner',
    'VirtualRunner',
    'get_dns_server',
    'get_proxy_server',
]