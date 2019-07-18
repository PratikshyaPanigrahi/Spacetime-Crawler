import lxml
from lxml import html
import requests

page = requests.get('https://www.ics.uci.edu')

tree=lxml.html.fromstring(page.content)
#tree=lxml.html.fromstring(page.text)
#links=tree.cssselect('a')
links = tree.xpath('//a')
out=[]

for i in links:
    if 'href' in i.attrib:
        #print("%s\n" %i)
        print(i.attrib['href'])


#    page = requests.get(rawDataObj.url)
#    tree=lxml.html.fromstring(page.content)
#    if rawDataObj.error_message is None:
#        tree=etree.HTML(rawDataObj.content)
#        if tree is not None:
#            links = tree.xpath('//a/@href')
#            links=map(lambda x: urljoin(rawDataObj.url, x) if x.startswith('http')==False else x,link)
#        for link in links:
#            if 'href' in link.attrib:
#                outputLinks.append(link.attrib['href'])
#    print(links.attrib['href'])
#    return links
#   return outputLinks
