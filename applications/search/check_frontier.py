import logging
import logging.handlers
import os
import sys
import argparse
import uuid

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))

from datamodel.search.Rajeevr1AmanikanPpanigra_datamodel import Rajeevr1AmanikanPpanigraLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Deleter, Getter
from spacetime.connectors.spacetime import ObjectlessSpacetimeConnection
from rtypes.dataframe.dataframe_client import dataframe_client
from spacetime.client.frame import ClientFrame
from applications.search.crawler_frame import CrawlerFrame

logger = logging.getLogger(__name__)
LOG_HEADER = "[CHECKFRONTIER]"

@Getter(Rajeevr1AmanikanPpanigraLink)
class CheckFrontierFrame(IApplication):

    def __init__(self, frame):
        self.app_id = "Rajeevr1AmanikanPpanigra"
        self.frame = frame


    def initialize(self):
        pass

    def update(self):
        ls = self.frame.get(Rajeevr1AmanikanPpanigraLink)
        with open("frontier_summary.txt", "w") as f:
            f.write("url\tdownload_complete\n")
            for l in ls:
                try:
                    f.write("%s\t%s\n" % (l.url, "complete" if l.download_complete else "incomplete"))
                except UnicodeError:
                    print "Unicode error when writing to file for url: ", l.url, "status: ", "complete" if l.download_complete else "incomplete"
        print "Wrote the status to frontier_summary.txt"
        self.done = True

    def shutdown(self):
        pass

logger = None

class Simulation(object):
    '''
    classdocs
    '''
    def __init__(self, address, port):
        '''
        Constructor
        '''
        objectless_connector = ObjectlessSpacetimeConnection(
            "CheckFrontier_Rajeevr1AmanikanPpanigra".format(CrawlerFrame.app_id),
            address = "http://" + address + ":" + str(port) + "/")
        frame_c = ClientFrame(
            objectless_connector,
            dataframe_client(),
            time_step=1000)

        frame_c.attach_app(CheckFrontierFrame(frame_c))
        frame_c.run_main()

def SetupLoggers():
    global logger
    logger = logging.getLogger()
    logging.info("testing before")
    logger.setLevel(logging.DEBUG)

    #logfile = os.path.join(os.path.dirname(__file__), "../../logs/CADIS.log")
    #flog = logging.handlers.RotatingFileHandler(logfile, maxBytes=10*1024*1024, backupCount=50, mode='w')
    #flog.setFormatter(logging.Formatter('%(levelname)s [%(name)s] %(message)s'))
    #logger.addHandler(flog)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    clog = logging.StreamHandler()
    clog.addFilter(logging.Filter(name='CRAWLER'))
    clog.setFormatter(logging.Formatter('[%(name)s] %(message)s'))
    clog.setLevel(logging.DEBUG)
    logger.addHandler(clog)

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default="127.0.0.1", help='Address of the distributing server')
    parser.add_argument('-p', '--port', type=int, default=12000, help='Port used by the distributing server')
    args = parser.parse_args()
    SetupLoggers()
    sim = Simulation(args.address, args.port)
