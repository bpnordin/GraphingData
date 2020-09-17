import multiprocessing
import time

def get_data(data_queue):
    data_queue.put("Outgoing data")

def poller_loop(cmd_queue,data_queue):

    while True:
        try:
            cmd = cmd_queue.get_nowait()
            if cmd == "DATA":
                get_data(data_queue)
        except:
            pass
class SubTest():

    def __init__(self,data_queue):
        self.cmd_queue = multiprocessing.Queue()
        self.loop = multiprocessing.Process(target = poller_loop,
                                            args =(self.cmd_queue,data_queue))
        self.loop.start()
        time.sleep(10)
        self.cmd_queue.put("DATA")
    def close(self):
        self.loop.join()
data_queue = multiprocessing.Queue()
subObject = SubTest(data_queue)
print data_queue.get()
subObject.close()

