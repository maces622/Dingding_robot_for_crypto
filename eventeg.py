from queue import Queue,Empty
from threading import Thread
from collections import defaultdict
import time
class event(object):
    def __init__(self,_type:str,data=None):
        self.type=_type
        self.data=data

class eventg(object):
    def __init__(self):
        self._queue=Queue()
        self._thread=Thread(target=self._run)
        self.active=False
        #active::开关
        self._handlers=defaultdict(list)
    def _run(self):
        while self.active:
            try:
                event=self._queue.get(block=True,timeout=1)
                # print(event)
                self._process(event)
            except Empty:
                print("empty")

    def start(self):
        self.active=True
        self._thread.start()

    def put(self,event):
        self._queue.put(event)

    def _process(self, event):
        if event.type in self._handlers:
            for handler in self._handlers[event.type]:
                handler(event)  #

    def register(self, type, handler):
        handler_list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)
    def unregister(self, type: str, handler):
        handler_list = self._handlers[type]
        if handler in handler_list:
            handler_list.remove(handler)
        if not handler_list:
            self._handlers.pop(type)



def on_tick(event):
        print(event.type)
        print(event.data)
if __name__ == '__main__':
    evt_g=eventg()
    evt_g.start()
    evt_g.register('tick',on_tick)
    while True:
        tick=time.time()
        # print(tick)
        evt=event(_type='tick',data={"mark_price":tick})
        evt_g.put(evt)

        time.sleep(3)