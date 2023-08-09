import logging
import time
import heapq

from typing import Dict
from threading import Thread
from sqlalchemy.orm.session import Session
from data.models import Room

class Event:
    """
    Container for event information to be sent to clients
    """
    def __init__(self, message: str, timestamp: int=None, room_id: int=None):
        self.message = message
        self.timestamp = timestamp if timestamp else time.time()
        self.room_id = room_id

class ServerQueue:
    """
    Event queue for passing messages to unlinked connections
    """
    def __init__(self):
        self._queue = []

    def push_event(self, event: Event):
        if isinstance(event, Event):
            heapq.heappush(self._queue, (event.timestamp, event))
        else:
            raise TypeError(f'event must be of type Event')

    def pop_event(self) -> Event:
        return heapq.heappop(self._queue)[1]
    
    def peek_time(self) -> int:
        try:
            return self._queue[0][0]
        except IndexError:
            return float('inf')
    
    def execute_events(self, session: Session, authenticated_client_threads: Dict[str, Thread]):
        """
        Execute all events set to execute at the current time or earlier
        """
        event_time = self.peek_time()
        while event_time <= time.time():
            event = self.pop_event()
            target_ids = Room.get_occupants(session, event.room_id)
            for id in target_ids:
                try:
                    authenticated_client_threads[id].send_message(event.message)
                except KeyError as e:
                    logging.info(e)
            event_time = self.peek_time()
            
