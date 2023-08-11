import logging
import time
import heapq

from typing import Dict
from threading import Thread
from sqlalchemy.orm.session import Session
from data.models import Room
from mud_parser.verb import VerbResponse

class Event:
    """
    Container for event information to be sent to clients
    """
    def __init__(self, response: VerbResponse, timestamp: int=None):
        self.response = response
        self.timestamp = timestamp if timestamp else time.time()

class EventQueue:
    """
    Event queue for passing messages to unlinked connections
    """
    def __init__(self):
        self._queue = []

    def push_event(self, event: Event, block=False):
        """
        Add an event to the queue and optionally block until its popped
        """
        if isinstance(event, Event):
            heapq.heappush(self._queue, (event.timestamp, event))
        else:
            raise TypeError(f'event must be of type Event')
        
        if block:
            while event in self._queue:
                time.sleep(0.1)

    def _pop_event(self) -> Event:
        return heapq.heappop(self._queue)[1]
    
    def _peek_time(self) -> int:
        try:
            return self._queue[0][0]
        except IndexError:
            return float('inf')
        
    def _execute_event(self,
                       event: Event,
                       session: Session,
                       authenticated_client_threads: Dict[str, Thread]):
            """
            Execute a single event
            """
            if event.response.room_id:
                target_ids = Room.get_occupants(session, event.room_id)
                for id in target_ids:
                    if event.response.target_id:
                        authenticated_client_threads[event.response.target_id].send_message(event.message_you)
                    try:
                        authenticated_client_threads[id].send_message(event.message_they)
                    except KeyError as e:
                        logging.info(e)
            elif event.response.target_id:
                authenticated_client_threads[event.response.target_id].send_message(event.message_you)
            else:
                for thread in authenticated_client_threads.values():
                    thread.send_message(event.message_they)

    
    def execute_events(self, session: Session, authenticated_client_threads: Dict[str, Thread]):
        """
        Execute all events set to execute at the current time or earlier
        """
        event_time = self._peek_time()
        while event_time <= time.time():
            event = self._pop_event()
            self._execute_event(event, session, authenticated_client_threads)
            event_time = self._peek_time()
            
