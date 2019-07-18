import logging
import sys
import json
import lxml
from lxml import html
import requests
from datamodel.search.Rajeevr1AmanikanPpanigra_datamodel import Rajeevr1AmanikanPpanigraLink, Rajeevr1AmanikanPpanigraUnprocessedLink, OneRajeevr1AmanikanPpanigraUnProcessedLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter
from lxml import html,etree
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs, urljoin
from uuid import uuid4

dict={}

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"

@Producer(Rajeevr1AmanikanPpanigraLink)
@GetterSetter(OneRajeevr1AmanikanPpanigraUnProcessedLink)
class CrawlerFrame(IApplication):
    app_id = "Rajeevr1AmanikanPpanigra"
    c = 0
    m = 0
    s = ""
    def __init__(self, frame):
        self.app_id = "Rajeevr1AmanikanPpanigra"
        self.frame = frame


    def initialize(self):
        self.m = 0
        self.count = 0
        self.starttime = time()
        c = 0
        links = self.frame.get_new(OneRajeevr1AmanikanPpanigraUnProcessedLink)
        if len(links) > 0:
            print "Resuming from the previous state."
            self.download_links(links)
        else:
            l = Rajeevr1AmanikanPpanigraLink("http://www.ics.uci.edu/")
            print l.full_url
            self.frame.add(l)

    def update(self):
        unprocessed_links = self.frame.get_new(OneRajeevr1AmanikanPpanigraUnProcessedLink)
        if unprocessed_links:
            self.download_links(unprocessed_links)




    def download_links(self, unprocessed_links):

        for link in unprocessed_links:
            print "Got a link to download:", link.full_url
            downloaded = link.download()
            links = extract_next_links(downloaded)
            url=""

            length = len(links)
            if length > self.m:
                self.m = length
                url= urlparse(link.full_url)
                self.s = url.scheme + '//:' +url.netloc + url.path + url.params + url.query + url.fragment
                print(self.s)
            self.c += 1
            for l in links:
                if is_valid(l):
                    # sub-domain count
                    url = urlparse(l)
                    subd = url.netloc.split('.')
                    if subd[-4] == 'www':
                        sub = subd[-3]
                    else:
                        sub = subd[len(subd) - 4] + "." + subd[len(subd) - 3]
                    if sub in dict:
                        dict[sub] += 1
                    else:
                        dict[sub] = 1
                        print(dict[sub])
                    # max outlink count


                    self.frame.add(Rajeevr1AmanikanPpanigraLink(l))

            if self.c == 10:
                with open("analytics.txt", 'w') as f:
                    print('writing to file')
                    f.write("Maximum outlinks found in webpage is ")
                    f.write(str(self.m))
                    f.write("\n")
                    f.write("The webpage having maximum outlinks is ")
                    print(self.s)
                    f.write(self.s)
                    f.write("\n")
                    f.write("Subdomain names and counts")
                    f.write('\n')
                    for hostdict in dict:
                        json.dump(hostdict,f)
                        f.write("\t")
                        json.dump(dict[hostdict],f)
                        f.write('\n')

                f.close()
                self.shutdown()

    def shutdown(self):
        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")
        sys.exit()


def extract_next_links(rawDataObj):
    outputLinks = []
    '''
    rawDataObj is an object of type UrlResponse declared at L20-30
    datamodel/search/server_datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded.
    The frontier takes care of that.

    Suggested library: lxml

    '''

    print(rawDataObj.url)

    if rawDataObj.error_message is None:
        tree = etree.HTML(rawDataObj.content)
        if tree is not None:
            links = tree.xpath('//a/@href')
            links = map(lambda x: urljoin(rawDataObj.url, x) if x.startswith('http') == False else x, links)
            print("length = ", len(links))
            outputLinks = links
    return outputLinks





def checkforTrap(url):
    directory = filter(lambda i: i != "",url.split("/")) ##Split the url by directories
    original = len(directory) ## Count directories of original url
    filtered = len(set(directory)) ##Have a list of only the UNIQUE directories, many traps just infinitely copy the same directories in url
    if original - filtered > 6: ##Check difference between original list and filtered set.
        return True
    return False

def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    python applications/search/crawler.py -a amazon.ics.uci.edu -p 9400
    '''
    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        return False
    if parsed.netloc in set(["calendar.ics.uci.edu", "archive.ics.uci.edu"]):
        #print("not printing")
        return False
    if parsed.netloc == False:
        return False
    if (url.find("?") != -1 or checkforTrap(url) == True):
        return False
    parts = url.split("/")
    if len(parts) >= 25:  ##I have checked some of the traps this number should be shorter more like 11-15
        return False
    try:
        return ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        return False
