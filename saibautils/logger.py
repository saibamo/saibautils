
import inspect
from typing import Optional
from elasticsearch import Elasticsearch
from python_openobserve.openobserve import OpenObserve
from datetime import datetime
from zoneinfo import ZoneInfo

class Logger:
    """
    This class will implement a custom logger.
    """
    
    def __init__(
            self, 
            mode:str, 
            url:Optional[str] = None,
            elastic_key:Optional[str] = None,
            oo_user:Optional[str]=None,
            oo_password:Optional[str]=None,
            index:Optional[str]="logs",
        ) -> None:
        """
        Constructor for the Logger-class
        :param mode: mode of the logger, can be 'console', 'elastic', 'openobserve', 'dual-elastic' or 'dual-observe'
        :type mode: str
        :param url: URL to the ElasticSearch/OpenObserve instance
        :type url: str
        :param elastic_key: API key for the ElasticSearch instance
        :type elastic_key: str
        :param oo_user: the User to authenticate against the openobserve instance
        :type oo_user: str
        :param oo_password: the Password for authentication to the openobserve instance
        :type oo_password: str
        :param index: Index in the ElasticSearch or OpenObserve instance
        :type index: str
        """
        if mode not in ["console", "elastic", "openobserve", "dual-elastic", "dual-observe"]:
            raise ValueError("Mode must be 'console', 'elastic', 'openobserve', 'dual-elastic' or 'dual-observe'")
        if "elastic" in mode and not (url and elastic_key):
            raise ValueError("Elastic parameters need to be provided if mode is set to use Elasticsearch!")
        if "observe" in mode and not ((url and oo_user) and oo_password):
            raise ValueError("OpenObserve parameters need to be provided if mode is set to use OpenObserve!")
        
        self.mode = mode
        if "elastic" in self.mode:
            self.es = Elasticsearch(url, api_key=elastic_key)
        if "observe" in self.mode:
            self.oo = OpenObserve(user=oo_user, password=oo_password, host=url, verify=False)
        self.index = index
      
    
    
    def _log(self, message:str, level:str) -> None:
        """
        Logs a message
        
        :param message: message to be logged
        :type message: str
        """
        
        call_tree = self._get_call_tree()
        
        if self.mode in ["console", "dual"]:
            print(f"{level.upper()}: {message}, {call_tree}")
        if "elastic" in self.mode:
            self.es.index(index=self.index, body={"message": message, "level": level, "call_tree": call_tree, "ts": datetime.now(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%dT%H:%M:%S%z")})
        if "observe" in self.mode:
            log_content = {
                "level": level,
                "message": message,
                "call_tree": call_tree,
                "datetime": datetime.now(ZoneInfo("Europe/Berlin")).isoformat()
            }
            self.oo.index(index=self.index, document=log_content)
            
    def info(self, message:str) -> None:
        """
        Logs an info message
        
        :param message: message to be logged
        :type message: str
        """
       
        self._log(message, "info")
    
    def warning(self, message:str) -> None:
        """
        Logs a warning message
        
        :param message: message to be logged
        :type message: str
        """
        
        self._log(message, "warning")
        
    def error(self, message:str) -> None:
        """
        Logs an error message
        
        :param message: message to be logged
        :type message: str
        """
        
        self._log(message, "error")
        
    def debug(self, message:str) -> None:
        """
        Logs a debug message
        
        :param message: message to be logged
        :type message: str
        """
        
        self._log(message, "debug")
        
        
    
    def _get_call_tree(self) -> str:
        stack = inspect.stack()
        call_hierarchy = []
        for frame_info in stack[1:]:  # Skip the current function
            frame = frame_info.frame
            func_name = frame_info.function
            class_name = frame.f_locals.get('self', None).__class__.__name__ if 'self' in frame.f_locals else None
            # Skip frames from the logger itself
            if func_name in ["<module>","translate_proxy_headers"] or class_name == "<module>":
                continue
            if class_name == self.__class__.__name__:
                continue
            if class_name in ["Thread","ThreadedTaskDispatcher", "HTTPChannel", "WSGITask", "Flask", "StructuredTool"]:
                continue
            if class_name:
                call_hierarchy.append(f"{class_name}.{func_name}")
            else:
                call_hierarchy.append(func_name)
        return " -> ".join(reversed(call_hierarchy))
    
    
