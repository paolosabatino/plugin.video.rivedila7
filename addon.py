import re
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import urllib2
import urlparse
import requests
import html5lib
from bs4 import BeautifulSoup


addon = xbmcaddon.Addon()
language = addon.getLocalizedString
handle = int(sys.argv[1])
url_rivedi="http://www.la7.it/rivedila7/0/la7"
url_rivedila7d="http://www.la7.it/rivedila7/0/la7d"
url_programmi="http://www.la7.it/programmi"
url_tutti_programmi="http://www.la7.it/tutti-i-programmi"
url_tgla7d="http://tg.la7.it/listing/tgla7d"
url_live="http://www.la7.it/dirette-tv"
url_base="http://www.la7.it"    
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'}
primapagina=True
pagenum=0
list_programmi=[]
tg_cronache=False
link_global=""
thumb_path = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'images')
fanart_path = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'fanart.jpg')


def parameters_string_to_dict(parameters):
    paramDict = dict(urlparse.parse_qsl(parameters[1:]))
    return paramDict


def show_root_menu():
    ''' Show the plugin root menu '''
    liStyle = xbmcgui.ListItem('[B]'+language(32002)+'[/B]', iconImage=os.path.join(thumb_path, 'direttalivela7.jpg'))
    liStyle.setProperty('fanart_image', fanart_path)
    addDirectoryItem({"mode": "diretta_live"},liStyle)
    liStyle = xbmcgui.ListItem('[B]'+language(32007)+'[/B]', iconImage=os.path.join(thumb_path, 'tgmeteo.jpg'))
    liStyle.setProperty('fanart_image', fanart_path)
    addDirectoryItem({"mode": "tg_meteo"},liStyle)    
    liStyle = xbmcgui.ListItem('[B]'+language(32001)+'[/B]', iconImage=os.path.join(thumb_path, 'rivedila7.jpg'))
    liStyle.setProperty('fanart_image', fanart_path)
    addDirectoryItem({"mode": "rivedi_la7"},liStyle)
    liStyle = xbmcgui.ListItem('[B]'+language(32004)+'[/B]', iconImage=os.path.join(thumb_path, 'rivedila7d.jpg'))
    liStyle.setProperty('fanart_image', fanart_path)
    addDirectoryItem({"mode": "rivedi_la7d"},liStyle)
    liStyle = xbmcgui.ListItem('[B]'+language(32006)+'[/B]', iconImage=os.path.join(thumb_path, 'programmila7la7d.jpg'))
    liStyle.setProperty('fanart_image', fanart_path)
    addDirectoryItem({"mode": "tutti_programmi"},liStyle)

    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def addDirectoryItem(parameters, li):
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)


def addDirectoryItem_nodup(parameters, li, title):
    if title in list_programmi:
        xbmc.log('Prog Duplicato',xbmc.LOGNOTICE)
    else:
        url = sys.argv[0] + '?' + urllib.urlencode(parameters)
        #xbmc.log('LIST: '+str(url),xbmc.LOGNOTICE)
        return xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)


def rivedi_la7():
    req = urllib2.Request(url_rivedi,headers=headers) 
    page=urllib2.urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    giorno=html.find(id="giorni").find_all('div' ,class_='giorno')
    
    if giorno is not None:
        for div in giorno[0:]:
            dateDay=div.find('div',class_='dateDay')
            dateMonth=div.find('div',class_='dateMonth')
            dateRowWeek=div.find('div',class_='dateRowWeek')
            a=div.a.get('href')
            liStyle = xbmcgui.ListItem(dateRowWeek.contents[0]+" "+dateDay.contents[0]+" "+dateMonth.contents[0], iconImage=os.path.join(thumb_path, 'rivedila7.jpg'))
            liStyle.setProperty('fanart_image', fanart_path)
            addDirectoryItem({"mode": "rivedi_la7","giorno": a}, liStyle)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def rivedi_la7d():
    req = urllib2.Request(url_rivedila7d,headers=headers) 
    page=urllib2.urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    giorno=html.find(id="giorni").find_all('div' ,class_='giorno')
    
    if giorno is not None:
        for div in giorno[0:]:
            dateDay=div.find('div',class_='dateDay')
            dateMonth=div.find('div',class_='dateMonth')
            dateRowWeek=div.find('div',class_='dateRowWeek')
            a=div.a.get('href')
            liStyle = xbmcgui.ListItem(dateRowWeek.contents[0]+" "+dateDay.contents[0]+" "+dateMonth.contents[0], iconImage=os.path.join(thumb_path, 'rivedila7d.jpg'))
            liStyle.setProperty('fanart_image', fanart_path)
            addDirectoryItem({"mode": "rivedi_la7d","giorno": a}, liStyle)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def get_video_link(url):
    req = urllib2.Request(url,headers=headers) 
    page=urllib2.urlopen(req)
    html=page.read();
    res=re.findall('m3u8" : "(.*?)"', html)
    if res:
        return res[0]
    else:
        res=re.findall('m3u8: "(.*?)"', html)
        if res:
            return res[0]


def play_video(video,live):
    if live:
        s = requests.Session()
        req = s.get(video,headers=headers)
        html = req.text
        vS = re.findall('var vS = \'(.*?)\';', html)
        try:
            link_video = vS[0]
        except: # catch *all* exceptions
            e = sys.exc_info()[0]
            xbmc.log('EXCEP VIDEO: '+str(e),xbmc.LOGNOTICE)
    else:
        link_video=get_video_link(video)
      
    listitem =xbmcgui.ListItem(titolo_global)
    listitem.setInfo('video', {'Title': titolo_global})
    if (thumb_global != ""):
        listitem.setArt({ 'thumb': thumb_global})
    listitem.setInfo('video', { 'plot': plot_global })
    xbmc.Player().play(link_video, listitem)


def rivedi_la7_giorno():
    req = urllib2.Request(url_base+giorno,headers=headers) 
    page=urllib2.urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    guida_tv=html.find(id="content_guida_tv").find_all('div' ,class_='disponibile')
    if guida_tv is not None:
        for div in guida_tv:
            nome=div.find('div',class_='titolo clearfix').a.contents[0].encode('utf-8')
            thumb=div.find('img')['src']
            try:
                plot=div.find('div',class_='descrizione').p.contents[0]
            except: # catch *all* exceptions
                e = sys.exc_info()[0]
                xbmc.log('EXCEP PLOT_R7: '+str(e),xbmc.LOGNOTICE)
                plot=""
            urll=url_base+div.find('div',class_='titolo').a.get('href')
            orario=div.find('div',class_='orario').contents[0].encode('utf-8')
            liStyle = xbmcgui.ListItem(orario+" "+nome)
            liStyle.setArt({ 'thumb': thumb})
            liStyle.setInfo('video', { 'plot': plot })
            url2 = sys.argv[0] + '?' + urllib.urlencode({"mode": "rivedi_la7","play": urll,"titolo": nome,"thumb":thumb,"plot":plot.encode('utf-8')})
            liStyle.setProperty('fanart_image', fanart_path)
            xbmcplugin.addDirectoryItem(handle=handle, url=url2, listitem=liStyle, isFolder=False)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def rivedi_la7d_giorno():
    req = urllib2.Request(url_base+giorno,headers=headers) 
    page=urllib2.urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    guida_tv=html.find(id="content_guida_tv").find_all('div' ,class_='disponibile')
    if guida_tv is not None:
        for div in guida_tv:
            nome=div.find('div',class_='titolo clearfix').a.contents[0].encode('utf-8')
            thumb=div.find('img')['src']
            try:
                plot=div.find('div',class_='descrizione').p.contents[0]
            except: # catch *all* exceptions
                e = sys.exc_info()[0]
                xbmc.log('EXCEP PLOT_R7d: '+str(e),xbmc.LOGNOTICE)
                plot=""            
            urll=url_base+div.find('div',class_='titolo').a.get('href')
            orario=div.find('div',class_='orario').contents[0].encode('utf-8')
            liStyle = xbmcgui.ListItem(orario+" "+nome)
            liStyle.setArt({ 'thumb': thumb})
            liStyle.setInfo('video', { 'plot': plot })
            url2 = sys.argv[0] + '?' + urllib.urlencode({"mode": "rivedi_la7d","play": urll,"titolo": nome,"thumb":thumb,"plot":plot.encode('utf-8')})
            liStyle.setProperty('fanart_image', fanart_path)
            xbmcplugin.addDirectoryItem(handle=handle, url=url2, listitem=liStyle, isFolder=False)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


# Raggruppamento Programmi per lettera (A-B-C.....)
# def tutti_programmi():
    # req = urllib2.Request(url_tutti_programmi,headers=headers) 
    # page=urllib2.urlopen(req)
    # html=BeautifulSoup(page,'html5lib')        
    # lettere=html.find(id='colSx').find('div',class_='view-content').find_all('h3')
    # if lettere is not None:
        # i=0;
        # for h3 in lettere:
            # liStyle = xbmcgui.ListItem(lettere[i].contents[0])
            # addDirectoryItem({"mode": "tutti_programmi","lettera": lettere[i].contents[0]}, liStyle)
            # i=i+1
        # xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def programmi_lettera():
    req_p = urllib2.Request(url_programmi,headers=headers) 
    page_p=urllib2.urlopen(req_p)
    html_p=BeautifulSoup(page_p,'html5lib') 
    programmi=html_p.find(id='colSx').find_all('div',class_='element_menu')
    req_tp = urllib2.Request(url_tutti_programmi,headers=headers) 
    page_tp=urllib2.urlopen(req_tp)
    html_tp=BeautifulSoup(page_tp,'html5lib') 
    tutti_programmi=html_tp.find(id='colSx').find_all('div',class_='itemTuttiProgrammi')    

    if programmi or tutti_programmi is not None:
        for dati in programmi:
            titolo=dati.find('span',class_='black_overlay').contents[0].encode('utf-8').strip()
            #xbmc.log('TITLE1: '+str(titolo),xbmc.LOGNOTICE)
            list_programmi.append(titolo)
            liStyle = xbmcgui.ListItem(titolo)
            url_trovato=dati.a.get('href')
            if url_trovato != '/meteola7':
                if url_trovato == '/facciaafaccia':
                    url_trovato='/faccia-a-faccia'
                link=url_base+url_trovato
                if(len(dati)>0):
                    try:
                        thumb=dati.find('img')['src']
                    except: # catch *all* exceptions
                        e = sys.exc_info()[0]
                        xbmc.log('EXCEP THUMB1: '+str(e),xbmc.LOGNOTICE)
                        thumb = None
                    if thumb is not None:
                        liStyle.setArt({ 'thumb': thumb})
                    else:
                        xbmc.log('NO THUMB1',xbmc.LOGNOTICE)     
                liStyle.setProperty('fanart_image', fanart_path)
                addDirectoryItem({"mode": "tutti_programmi","link": link}, liStyle)

        for dati in tutti_programmi:
            titolo=dati.find('span',class_='field-content').a.contents[0].encode('utf-8').strip()
            #xbmc.log('TITLE2: '+str(titolo),xbmc.LOGNOTICE)	
            liStyle = xbmcgui.ListItem(titolo)
            url_trovato=dati.find('div',class_='wrapperTestualeProgrammi').a.get('href')
            link=url_base+url_trovato
            img=dati.find('div',class_='wrapperImgProgrammi').find('div',class_='field-content')
            if(len(dati)>0):
                try:
                    thumb=dati.find('img')['src']
                except:
                    e = sys.exc_info()[0]
                    xbmc.log('EXCEP THUMB2: '+str(e),xbmc.LOGNOTICE)
                    thumb = None
                if thumb is not None:
                    liStyle.setArt({ 'thumb': thumb})
                else:
                    xbmc.log('NO THUMB2',xbmc.LOGNOTICE)     
            liStyle.setProperty('fanart_image', fanart_path)
            addDirectoryItem_nodup({"mode": "tutti_programmi","link": link}, liStyle, titolo)

        #Prog aggiunti manualmente
        titolo='Artedi'
        liStyle = xbmcgui.ListItem(titolo)
        url_trovato='/artedi'
        link=url_base+url_trovato
        thumb=url_base+'/sites/default/files/lanci/img/artedi.jpg'
        liStyle.setArt({ 'thumb': thumb})
        liStyle.setProperty('fanart_image', fanart_path)
        addDirectoryItem_nodup({"mode": "tutti_programmi","link": link}, liStyle, titolo)

        xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def programmi_lettera_tg_meteo():

    titolo='TG La7'
    liStyle = xbmcgui.ListItem(titolo)
    url_trovato='/tgla7'
    link=url_base+url_trovato
    thumb=url_base+'/sites/default/files/palinsesto/locandine/palinsesto_tgla7.jpg'
    liStyle.setArt({ 'thumb': thumb})
    liStyle.setProperty('fanart_image', fanart_path)
    addDirectoryItem_nodup({"mode": "tg_meteo","link": link}, liStyle, titolo)
    
    titolo='TG La7 Cronache'
    liStyle = xbmcgui.ListItem(titolo)
    link='flag_tg_cronache'
    thumb='http://kdam.iltrovatore.it/p/103/sp/10300/thumbnail/entry_id/0_6jdqt0jz/version/100000/width/600/name/0_6jdqt0jz.jpg'
    liStyle.setArt({ 'thumb': thumb})
    liStyle.setProperty('fanart_image', fanart_path)
    addDirectoryItem_nodup({"mode": "tg_meteo","link": link}, liStyle, titolo)    
    
    titolo='TG La7d'
    liStyle = xbmcgui.ListItem(titolo)
    link=url_tgla7d
    thumb='http://nkdam.iltrovatore.it/p/110/sp/11000/thumbnail/entry_id/0_wucctmvr/version/100001/width/900/name/0_wucctmvr.jpg'
    liStyle.setArt({ 'thumb': thumb})
    liStyle.setProperty('fanart_image', fanart_path)
    addDirectoryItem_nodup({"mode": "tg_meteo","link": link}, liStyle, titolo)

    titolo='Meteo La7'
    liStyle = xbmcgui.ListItem(titolo)
    url_trovato='/meteola7'
    link=url_base+url_trovato
    thumb=url_base+'/sites/default/files/property/header/home/meteo_header_property_hp_grano.jpg'
    liStyle.setArt({ 'thumb': thumb})
    liStyle.setProperty('fanart_image', fanart_path)
    addDirectoryItem_nodup({"mode": "tg_meteo","link": link}, liStyle, titolo)          

    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
        

def video_programma():
    global link_global
    global tg_cronache
    #xbmc.log('LINK: '+str(link_global),xbmc.LOGNOTICE)
    if link_global=='flag_tg_cronache':
        tg_cronache=True
        link_global=url_base+'/tgla7'
    if link_global==url_base+'/chi-sceglie-la-seconda-casa':
        req = urllib2.Request(link_global+"/rivedila7",headers=headers)
    elif link_global==url_tgla7d:
        req = urllib2.Request(url_tgla7d+"?page="+str(pagenum),headers=headers)
    elif primapagina==True:
        req = urllib2.Request(link_global+"/rivedila7/archivio",headers=headers)
    else:
        req = urllib2.Request(link_global+"/rivedila7/archivio?page="+str(pagenum),headers=headers)
    try:
        page=urllib2.urlopen(req)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        xbmc.log('EXCEP URL: '+str(e),xbmc.LOGNOTICE)
        if xbmcgui.Dialog().ok(addon.getAddonInfo('name'), language(32005)):
            return
    html=BeautifulSoup(page,'html5lib')

    if link_global != url_tgla7d:
        if pagenum==0:
            firstLa7=html.find('div',class_='contenitoreUltimaReplicaLa7')
            firstLa7d=html.find('div',class_='contenitoreUltimaReplicaLa7d')
            firstLa7old=html.find('div',class_='contenitoreUltimaReplicaNoLuminosa')
            if firstLa7 is not None:
                first=firstLa7
            elif firstLa7d is not None:
                first=firstLa7d
            elif firstLa7old is not None:
                first=firstLa7old
            else:    
                if xbmcgui.Dialog().ok(addon.getAddonInfo('name'), language(32005)):
                    return
            
            if tg_cronache==True:
                titolo=first.find('div',class_='title').text.encode('utf-8')
                if titolo.find('Cronache') != -1:
                    thumb=first.find('div',class_='kaltura-thumb').find('img')['src']
                    data='[I] - ('+first.find('div',class_='dataPuntata').text.encode('utf-8')+')[/I]'
                    try:
                        plot=first.find('div',class_='views-field-field-testo-lancio').find('p').text.encode('utf-8')
                    except: # catch *all* exceptions
                        e = sys.exc_info()[0]
                        xbmc.log('EXCEP PLOT1: '+str(e),xbmc.LOGNOTICE)
                        plot=""
                    link=url_base+first.find('a',class_='clearfix').get('href')
                    liStyle = xbmcgui.ListItem(titolo+data)
                    liStyle.setArt({ 'thumb': thumb})
                    liStyle.setInfo('video', { 'plot': plot })
                    liStyle.setProperty('fanart_image', fanart_path)
                    addDirectoryItem({"mode": "tutti_programmi","play": link,"titolo": titolo+data,"thumb":thumb,"plot":plot}, liStyle)
            else:
                titolo=first.find('div',class_='title').text.encode('utf-8')
                if titolo.find('Cronache') == -1:
                    thumb=first.find('div',class_='kaltura-thumb').find('img')['src']
                    data='[I] - ('+first.find('div',class_='dataPuntata').text.encode('utf-8')+')[/I]'
                    try:
                        plot=first.find('div',class_='views-field-field-testo-lancio').find('p').text.encode('utf-8')
                    except: # catch *all* exceptions
                        e = sys.exc_info()[0]
                        xbmc.log('EXCEP PLOT1: '+str(e),xbmc.LOGNOTICE)
                        plot=""
                    link=url_base+first.find('a',class_='clearfix').get('href')
                    liStyle = xbmcgui.ListItem(titolo+data)
                    liStyle.setArt({ 'thumb': thumb})
                    liStyle.setInfo('video', { 'plot': plot })
                    liStyle.setProperty('fanart_image', fanart_path)
                    addDirectoryItem({"mode": "tutti_programmi","play": link,"titolo": titolo+data,"thumb":thumb,"plot":plot}, liStyle)
                    
            ul=html.find('li',class_='switchBtn settimana')
            if ul is not None and link_global != url_base+'/lispettore-barnaby' and link_global != url_base+'/josephineangegardien':
                req2= urllib2.Request(link_global+"/rivedila7/settimana",headers=headers)
                page2=urllib2.urlopen(req2)
                html2=BeautifulSoup(page2,'html5lib')
                video2=html2.find(id='block-la7it-repliche-la7it-repliche-contenuto-tid').find_all('div',class_='views-row')
                if video2 is not None:
                    get_rows_video(video2)
        video=html.find(id='block-la7it-repliche-la7it-repliche-contenuto-tid').find_all('div',class_='views-row')
        if video is not None:
            get_rows_video(video)
            pagenext=html.find('li',class_='pager-next')
            if pagenext is not None:
                liStyle = xbmcgui.ListItem('[B]'+language(32003)+'[/B]')
                liStyle.setProperty('fanart_image', fanart_path)
                addDirectoryItem({"mode": "tutti_programmi","link":link_global,"page":pagenum+1}, liStyle)
            xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    #Tg La7d
    else:
        video=html.find('div',class_='tgla7-category').find_all('article',class_='tgla7-new clearfix')
        if video is not None:
            get_rows_video_tgla7d(video)
            pagenext=html.find('li',class_='next')
            if pagenext is not None:
                liStyle = xbmcgui.ListItem('[B]'+language(32003)+'[/B]')
                liStyle.setProperty('fanart_image', fanart_path)
                addDirectoryItem({"mode": "tutti_programmi","link":link_global,"page":pagenum+1}, liStyle)
            xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
        else:    
            if xbmcgui.Dialog().ok(addon.getAddonInfo('name'), language(32005)):
                return


def get_rows_video(video):
    if tg_cronache==True:
        for div in video:
            titolo=div.find('div',class_='title').a.text.encode('utf-8')
            #xbmc.log('TITOLO: '+str(titolo.find('Cronache')),xbmc.LOGNOTICE)
            if titolo.find('Cronache') != -1:
                thumb=div.find('div',class_='kaltura-thumb').find('img')['data-src']
                data='[I] - ('+div.find('div',class_='dataPuntata').text.encode('utf-8')+')[/I]'
                plot=div.find('div',class_='views-field-field-testo-lancio').text.encode('utf-8')
                link=url_base+div.find('a',class_='thumbVideo').get('href')
                liStyle = xbmcgui.ListItem(titolo+data)
                liStyle.setArt({ 'thumb': thumb})
                liStyle.setInfo('video', { 'plot': plot })
                liStyle.setProperty('fanart_image', fanart_path)
                addDirectoryItem({"mode": "tutti_programmi","play": link,"titolo": titolo+data,"thumb":thumb,"plot":plot}, liStyle)
    else:
        for div in video:
            titolo=div.find('div',class_='title').a.text.encode('utf-8')
            if titolo.find('Cronache') == -1:
                thumb=div.find('div',class_='kaltura-thumb').find('img')['data-src']            
                data='[I] - ('+div.find('div',class_='dataPuntata').text.encode('utf-8')+')[/I]'
                plot=div.find('div',class_='views-field-field-testo-lancio').text.encode('utf-8')
                link=url_base+div.find('a',class_='thumbVideo').get('href')
                liStyle = xbmcgui.ListItem(titolo+data)
                liStyle.setArt({ 'thumb': thumb})
                liStyle.setInfo('video', { 'plot': plot })
                liStyle.setProperty('fanart_image', fanart_path)
                addDirectoryItem({"mode": "tutti_programmi","play": link,"titolo": titolo+data,"thumb":thumb,"plot":plot}, liStyle)

        
def get_rows_video_tgla7d(video):
    for div in video:
        titolo=div.find('div',class_='tgla7-condividi').get('data-title').encode('utf-8').strip()
        thumb_link=div.find('div',class_='tgla7-img').get('style')
        thumb = thumb_link[22:-1]
        #xbmc.log('THUMB: '+str(thumb),xbmc.LOGNOTICE)
        plot=div.find('div',class_='tgla7-descrizione').text.encode('utf-8').strip()
        link=div.find('div',class_='tgla7-condividi').get('data-share')
        liStyle = xbmcgui.ListItem(titolo)
        liStyle.setArt({ 'thumb': thumb})
        liStyle.setInfo('video', { 'plot': plot })
        liStyle.setProperty('fanart_image', fanart_path)
        addDirectoryItem({"mode": "tutti_programmi","play": link,"titolo": titolo,"thumb":thumb,"plot":plot}, liStyle)              
        
        
        
        
        
        
# Main             
params = parameters_string_to_dict(sys.argv[2])
mode = str(params.get("mode", ""))
giorno = str(params.get("giorno", ""))
play=str(params.get("play", ""))
titolo_global=str(params.get("titolo", ""))
thumb_global=str(params.get("thumb", ""))
plot_global=str(params.get("plot", ""))
#lettera_global=str(params.get("lettera", ""))
link_global=str(params.get("link", ""))


if params.get("page", "")=="":
    primapagina=True
    pagenum=0;
else:
    primapagina=False
    pagenum=int(params.get("page", ""))

if mode=="diretta_live":
    titolo_global=language(32002)
    thumb_global=""
    play_video(url_live,True)    
    
elif mode=="rivedi_la7":
    if play=="":
        if giorno=="":
            rivedi_la7()
        else:
            rivedi_la7_giorno()
    else:
        play_video(play,False)

elif mode=="rivedi_la7d":
    if play=="":
        if giorno=="":
            rivedi_la7d()
        else:
            rivedi_la7d_giorno()
    else:
        play_video(play,False)

elif mode=="tg_meteo":
    if play=="":
        if link_global=="":
            programmi_lettera_tg_meteo()
        else:
            video_programma()
    else:
        play_video(play,False)        
        
elif mode=="tutti_programmi":
    if play=="":
        if link_global=="":
            # if lettera_global=="":
                # tutti_programmi()
            # else:
            programmi_lettera()
        else:
            video_programma()
    else:
        play_video(play,False)

else:
    show_root_menu()
    



