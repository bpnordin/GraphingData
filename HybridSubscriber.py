from origin.client import server, random_data, origin_subscriber,origin_reader
import multiprocessing

class HybridSubscriber(origin_subscriber.Subscriber):

    def __init__(self,config,logger):
        super(HybridSubscriber,self).__init__(config,logger)
        self.data_queue = multiprocessing.Queue()

        


    def get_data(self,stream_id,data,state,log,ctrl):
        return self.data_queue.put((stream_id,data))
