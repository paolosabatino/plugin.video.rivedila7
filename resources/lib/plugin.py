# -*- coding: utf-8 -*-
import re
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import html5lib
from bs4 import BeautifulSoup

from urllib.request import Request
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.parse import parse_qsl


addon = xbmcaddon.Addon()
language = addon.getLocalizedString
handle = int(sys.argv[1])
url_base = "https://www.la7.it"
url_live = "https://www.la7.it/dirette-tv"
url_tgla7d = "https://tg.la7.it/listing/tgla7d"
url_rivedila7 = "https://www.la7.it/rivedila7/0/la7"
url_rivedila7d = "https://www.la7.it/rivedila7/0/la7d"
url_programmi = "https://www.la7.it/programmi"
url_programmila7d = "https://www.la7.it/programmi-la7d"
url_tutti_programmi = "https://www.la7.it/tutti-i-programmi"
url_teche_la7 = "https://www.la7.it/i-protagonisti"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'}
titolo_global = ''
thumb_global = ''
plot_global = ''
link_global = ''
pagenum = 0
list_programmi = []
tg_cronache = False
filtro_cronache = 'TG LA7 Cronache'
omnibus_news = False
filtro_omnibus = 'Omnibus News'
thumb_path = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'images')
fanart_path = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'fanart.jpg')


def parameters_string_to_dict(parameters):
    paramDict = dict(parse_qsl(parameters[1:]))
    return paramDict


def show_root_menu():
    ''' Show the plugin root menu '''
    liStyle = xbmcgui.ListItem('[B]'+language(32002)+'[/B]')
    liStyle.setArt({ 'thumb': os.path.join(thumb_path, 'direttalivela7.jpg'), 'fanart' : fanart_path })
    addDirectoryItem_nodup({"mode": "diretta_live"},liStyle, folder=False)
    liStyle = xbmcgui.ListItem('[B]'+language(32007)+'[/B]')
    liStyle.setArt({ 'thumb': os.path.join(thumb_path, 'tgmeteo.jpg'), 'fanart' : fanart_path })
    addDirectoryItem_nodup({"mode": "tg_meteo"},liStyle)    
    liStyle = xbmcgui.ListItem('[B]'+language(32001)+'[/B]')
    liStyle.setArt({ 'thumb': os.path.join(thumb_path, 'rivedila7.jpg'), 'fanart' : fanart_path })
    addDirectoryItem_nodup({"mode": "rivedi_la7"},liStyle)
    liStyle = xbmcgui.ListItem('[B]'+language(32004)+'[/B]')
    liStyle.setArt({ 'thumb': os.path.join(thumb_path, 'rivedila7d.jpg'), 'fanart' : fanart_path })
    addDirectoryItem_nodup({"mode": "rivedi_la7d"},liStyle)
    liStyle = xbmcgui.ListItem('[B]'+language(32006)+'[/B]')
    liStyle.setArt({ 'thumb': os.path.join(thumb_path, 'programmila7la7d.jpg'), 'fanart' : fanart_path })
    addDirectoryItem_nodup({"mode": "tutti_programmi"},liStyle)
    liStyle = xbmcgui.ListItem('[B]'+language(32008)+'[/B]')
    liStyle.setArt({ 'thumb': os.path.join(thumb_path, 'techela7.jpg'), 'fanart' : fanart_path })
    addDirectoryItem_nodup({"mode": "teche_la7"},liStyle)


    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def addDirectoryItem_nodup(parameters, li, title=titolo_global, folder=True):
    if title in list_programmi:
        xbmc.log('DUPLICATE TV SHOW',xbmc.LOGNOTICE)
    else:
        url = "%s?%s" % (sys.argv[0], urlencode(parameters, True, encoding='utf-8'))
        #xbmc.log('LIST------: '+str(url),xbmc.LOGNOTICE)
        if not folder:
            li.setInfo('video', {})
            li.setProperty('isPlayable', 'true')
        return xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=folder)


def play_video(video,live):
    link_video = ''
    regex1 = 'vS = "(.*?)"'
    regex2 = '/content/(.*?).mp4'
    regex3 = 'm3u8: "(.*?)"'
    regex4 = '  <iframe src="(.*?)"'

    req = Request(video,headers=headers)
    page=urlopen(req)
    html=page.read().decode('utf-8')
    if live:
        if re.findall(regex1, html):
            #xbmc.log('REGEX1-----: '+str(re.findall(regex1, html)),xbmc.LOGNOTICE)
            link_video = re.findall(regex1, html)[0]
    else:
        if re.findall(regex2, html):
            #xbmc.log('REGEX2-----: '+str(re.findall(regex2, html)),xbmc.LOGNOTICE)
            link_video = 'https://awsvodpkg.iltrovatore.it/local/hls/,/content/'+re.findall(regex2, html)[0]+'.mp4.urlset/master.m3u8'
            #xbmc.log('LINK2-----: '+str(link_video),xbmc.LOGNOTICE)
        elif re.findall(regex3, html):
            #xbmc.log('REGEX3-----: '+str(re.findall(regex3, html)),xbmc.LOGNOTICE)
            link_video = re.findall(regex3, html)[0]
        elif re.findall(regex4, html):
            #xbmc.log('REGEX4-----: '+str(re.findall(regex4, html)),xbmc.LOGNOTICE)
            iframe = re.findall(regex4, html)[0]
            req2 = Request(iframe,headers=headers)
            page2=urlopen(req2)
            html2=page2.read()
            if re.findall(regex2, html2):
                #xbmc.log('REGEX2-B---: '+str(re.findall(regex2, html)),xbmc.LOGNOTICE)
                link_video = str("https:")+re.findall(regex2, html2)[0]

    listitem =xbmcgui.ListItem(titolo_global)
    listitem.setInfo('video', {'Title': titolo_global})
    if (thumb_global != ""):
        listitem.setArt({ 'thumb': thumb_global})
    listitem.setInfo('video', { 'plot': plot_global })
    if link_video == '':
        xbmc.log('NO VIDEO LINK',xbmc.LOGNOTICE)
        if xbmcgui.Dialog().ok(addon.getAddonInfo('name'), language(32005)):
            exit()
    else:
        listitem.setProperty('inputstreamaddon','inputstream.adaptive')
        listitem.setProperty('inputstream.adaptive.manifest_type','hls')
        listitem.setPath(link_video)
        xbmcplugin.setResolvedUrl(handle, True, listitem)


def rivedi(url, thumb):
    req = Request(url,headers=headers) 
    page=urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    giorno=html.find('div',class_='block block-system').find_all('div',class_=['item item--menu-guida-tv ','item item--menu-guida-tv active '])
    #xbmc.log('GIORNO----------: '+str(giorno),xbmc.LOGNOTICE)
    if giorno:
        for div in reversed(giorno):
            dateDay=div.find('div',class_='giorno-numero').text.encode('utf-8').strip()
            dateMonth=div.find('div',class_='giorno-mese').text.encode('utf-8').strip()
            dateRowWeek=div.find('div',class_='giorno-text').text.encode('utf-8').strip()
            a=div.a.get('href').strip()
            liStyle = xbmcgui.ListItem("%s %s %s" % (dateRowWeek.decode('utf-8'), dateDay.decode('utf-8'), dateMonth.decode('utf-8')))
            liStyle.setArt({ 'thumb': os.path.join(thumb_path, thumb), 'fanart' : fanart_path })
            addDirectoryItem_nodup({"mode": mode,"giorno": a}, liStyle)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)    


def rivedi_giorno():
    req = Request(url_base+giorno,headers=headers) 
    page=urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    guida_tv=html.find(id="content_guida_tv_rivedi").find_all('div',class_='item item--guida-tv')
    if guida_tv:
        for div in guida_tv:
            orario=div.find('div',class_='orario').contents[0].encode('utf-8').strip()
            nome=div.find('div',class_='property').text.encode('utf-8').strip()
            thumb='https:'+div.find('div',class_='bg-img lozad').get('data-background-image')
            plot=div.find('div',class_='occhiello').text.encode('utf-8').strip()
            if div.a:
                urll = div.a.get('href').strip()
                #xbmc.log('------LINK------: '+str(urll),xbmc.LOGNOTICE)
                liStyle = xbmcgui.ListItem("%s %s" % (orario.decode('utf-8'), nome.decode('utf-8')))
                liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
                liStyle.setInfo('video', { 'plot': plot })
                liStyle.setProperty('isPlayable', 'true')
                url2 = "%s?%s" % (sys.argv[0], urlencode({"mode": mode,"play": urll,"titolo": nome,"thumb":thumb,"plot":plot}))
                xbmcplugin.addDirectoryItem(handle=handle, url=url2, listitem=liStyle, isFolder=False)

    xbmcplugin.setContent(handle, 'episodes')
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def programmi_lettera():
    req_p = Request(url_programmi,headers=headers) 
    page_p=urlopen(req_p)
    html_p=BeautifulSoup(page_p,'html5lib') 
    programmi=html_p.find(id='container-programmi-list').find_all('div',class_='list-item')
    #xbmc.log('PROGRAMMI----------: '+str(programmi),xbmc.LOGNOTICE)
    req_pd = Request(url_programmila7d,headers=headers) 
    page_pd=urlopen(req_pd)
    html_pd=BeautifulSoup(page_pd,'html5lib') 
    programmila7d=html_pd.find(id='container-programmi-list').find_all('div',class_='list-item')
    req_tp = Request(url_tutti_programmi,headers=headers) 
    page_tp=urlopen(req_tp)
    html_tp=BeautifulSoup(page_tp,'html5lib') 
    tutti_programmi=html_tp.find_all('div',class_='list-item')

    if programmi or programmila7d or tutti_programmi:
        for dati in programmi:
            if dati.find('div',class_='titolo'):
                titolo=dati.find('div',class_='titolo').text.encode('utf-8').strip()
                #xbmc.log('TITLE1-----: '+str(titolo),xbmc.LOGNOTICE)
                liStyle = xbmcgui.ListItem(titolo.decode('utf-8'))
                url_trovato=dati.a.get('href').strip()
                if url_trovato !='/meteola7' and url_trovato !='/tgla7':
                    if url_trovato == '/facciaafaccia':
                        url_trovato='/faccia-a-faccia'
                    link=url_base+url_trovato
                    #xbmc.log('LINK-----: '+str(link),xbmc.LOGNOTICE)
                    if(len(dati)>0):
                        try:
                            thumb=dati.find('div',class_='image-bg lozad').get('data-background-image')
                        except Exception as e:
                            e = sys.exc_info()[0]
                            xbmc.log('EXCEP THUMB1: '+str(e),xbmc.LOGNOTICE)
                            thumb = None
                        if thumb:
                            liStyle.setArt({ 'thumb': thumb})
                        else:
                            xbmc.log('NO THUMB1',xbmc.LOGNOTICE)     
                    liStyle.setArt({ 'fanart' : fanart_path })
                    addDirectoryItem_nodup({"mode": mode,"link": link}, liStyle, titolo)
                    if not titolo in list_programmi:
                        list_programmi.append(titolo)

        for dati in programmila7d:
            if dati.find('div',class_='titolo'):
                titolo=dati.find('div',class_='titolo').text.encode('utf-8').strip()
                #xbmc.log('TITLE1-----: '+str(titolo),xbmc.LOGNOTICE)
                liStyle = xbmcgui.ListItem(titolo.decode('utf-8'))
                url_trovato=dati.a.get('href').strip()
                if url_trovato !='/meteola7' and url_trovato !='/tgla7':
                    if url_trovato == '/facciaafaccia':
                        url_trovato='/faccia-a-faccia'
                    link=url_base+url_trovato
                    #xbmc.log('LINK-----: '+str(link),xbmc.LOGNOTICE)
                    if(len(dati)>0):
                        try:
                            thumb=dati.find('div',class_='image-bg lozad').get('data-background-image')
                        except Exception as e:
                            e = sys.exc_info()[0]
                            xbmc.log('EXCEP THUMB2: '+str(e),xbmc.LOGNOTICE)
                            thumb = None
                        if thumb:
                            liStyle.setArt({ 'thumb': thumb})
                        else:
                            xbmc.log('NO THUMB2',xbmc.LOGNOTICE)     
                    liStyle.setArt({ 'fanart' : fanart_path })
                    addDirectoryItem_nodup({"mode": mode,"link": link}, liStyle, titolo)
                    if not titolo in list_programmi:
                        list_programmi.append(titolo)


        for dati in tutti_programmi:
            if dati.find('div',class_='titolo'):
                titolo=dati.find('div',class_='titolo').text.encode('utf-8').strip()
                #xbmc.log('TITLE2: '+str(titolo),xbmc.LOGNOTICE)
                liStyle = xbmcgui.ListItem(titolo.decode('utf-8'))
                url_trovato=dati.a.get('href').strip()
                if url_trovato !='/meteola7' and url_trovato !='/tgla7':
                    if url_trovato == '/facciaafaccia':
                        url_trovato='/faccia-a-faccia'
                    link=url_base+url_trovato
                    #xbmc.log('LINK-----: '+str(link),xbmc.LOGNOTICE)
                    if(len(dati)>0):
                        try:
                            thumb=dati.find('div',class_='image-bg lozad').get('data-background-image')
                        except Exception as e:
                            e = sys.exc_info()[0]
                            xbmc.log('EXCEP THUMB3: '+str(e),xbmc.LOGNOTICE)
                            thumb = None
                        if thumb:
                            liStyle.setArt({ 'thumb': thumb})
                        else:
                            xbmc.log('NO THUMB3',xbmc.LOGNOTICE)     
                    liStyle.setArt({ 'fanart' : fanart_path })
                    addDirectoryItem_nodup({"mode": mode,"link": link}, liStyle, titolo)

        #Prog aggiunti manualmente
        programmi = {
            'LA MALA EDUCAXXXION 2': {
                'url': '/la-mala-educaxxxion',
                'img': 'https://kdam.iltrovatore.it/p/103/sp/10300/thumbnail/entry_id/0_j0z82ps2/version/100001/type/5/width/600/height/360/quality/100/name/0_j0z82ps2.jpg'
                },           
            'Ω Video non catalogati 1': {
                'url': '/non-classificati',
                'img': '',
                },
            'Ω Video non catalogati 2': {
                'url': '/film',
                'img': '',
                },
        }
        for programma, program_info in programmi.items():
            titolo = programma
            liStyle = xbmcgui.ListItem(titolo)
            url_trovato = program_info['url']
            link = url_base + url_trovato
            thumb = program_info['img']
            liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
            addDirectoryItem_nodup({"mode": mode,"link": link}, liStyle, titolo)

        xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def programmi_lettera_teche_la7():
    req_teche = Request(url_teche_la7,headers=headers) 
    page_teche=urlopen(req_teche)
    html_teche=BeautifulSoup(page_teche,'html5lib') 
    teche_la7=html_teche.find_all('div',class_='list-item')

    if teche_la7:
        for dati in teche_la7:
            if dati.find('div',class_='titolo'):
                nomicognomi = dati.find('div',class_='titolo').text.encode('utf-8').strip()
                cognominomi = " ".join( reversed(nomicognomi.split(" ")))
                #xbmc.log('NOMI-----: '+str(cognominomi),xbmc.LOGNOTICE)
                liStyle = xbmcgui.ListItem(cognominomi.decode('utf-8'))
                url_trovato=dati.a.get('href').strip()
                link=url_base+url_trovato
                #xbmc.log('LINK-----: '+str(link),xbmc.LOGNOTICE)
                if(len(dati)>0):
                    try:
                        thumb='https:'+dati.find('div',class_='image-bg lozad').get('data-background-image')
                    except Exception as e:
                        e = sys.exc_info()[0]
                        xbmc.log('EXCEP THUMB4: '+str(e),xbmc.LOGNOTICE)
                        thumb = None
                    if thumb:
                        liStyle.setArt({ 'thumb': thumb})
                    else:
                        xbmc.log('NO THUMB4',xbmc.LOGNOTICE)     
                liStyle.setArt({ 'fanart' : fanart_path })
                addDirectoryItem_nodup({"mode": mode,"link": link}, liStyle, cognominomi)

        xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    

def programmi_lettera_tg_meteo():
    titolo = 'TG La7'
    liStyle = xbmcgui.ListItem(titolo)
    url_trovato = '/tgla7'
    link = url_base + url_trovato
    thumb = os.path.join(thumb_path, 'tgla7.jpg')
    liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
    addDirectoryItem_nodup({"mode": mode,"link": link}, liStyle, titolo)
    
    titolo = 'TG La7d'
    liStyle = xbmcgui.ListItem(titolo)
    link = url_tgla7d
    thumb = os.path.join(thumb_path, 'tgla7d.jpg')
    liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
    addDirectoryItem_nodup({"mode": mode,"link": link}, liStyle, titolo)

    # (rimosso temporaneamente per mancanza di contenuti)
    # titolo = 'TG Cronache'
    # liStyle = xbmcgui.ListItem(titolo)
    # link = 'flag_tg_cronache'
    # thumb = os.path.join(thumb_path, 'tgcronache.jpg')
    # liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
    # addDirectoryItem_nodup({"mode": mode,"link": link}, liStyle, titolo)
    
    titolo = 'Omnibus News'
    liStyle = xbmcgui.ListItem(titolo)
    link = 'flag_omnibus_news'
    thumb = os.path.join(thumb_path, 'omnibusnews.jpg')
    liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
    addDirectoryItem_nodup({"mode": mode,"link": link}, liStyle, titolo) 

    titolo = 'Meteo La7'
    liStyle = xbmcgui.ListItem(titolo)
    url_trovato = '/meteola7'
    link = url_base+url_trovato
    thumb = os.path.join(thumb_path, 'meteo.jpg')
    liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
    addDirectoryItem_nodup({"mode": mode,"link": link}, liStyle, titolo)          

    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def video_programma():
    global link_global
    global tg_cronache
    global omnibus_news

    #xbmc.log('LINK GLOBAL----: '+str(link_global),xbmc.LOGNOTICE)
    if link_global == url_base+'/atlantide':
        video_programma_landpage()

    if link_global == 'flag_tg_cronache':
        tg_cronache = True
        link_global = url_base+'/tgla7'
    
    if link_global == 'flag_omnibus_news':
        omnibus_news = True
        link_global = url_base+'/omnibus'
    
    if link_global != url_tgla7d:
        req = Request(link_global+"/rivedila7",headers=headers)
        try:
            page=urlopen(req)
        except Exception as e:
            e = sys.exc_info()[0]
            xbmc.log('EXCEP URL: '+str(e),xbmc.LOGNOTICE)
            if xbmcgui.Dialog().ok(addon.getAddonInfo('name'), language(32005)):
                exit()
        html=BeautifulSoup(page,'html5lib')

        if pagenum == 0:
            # FIRST VIDEO
            if html.find('div',class_='ultima_puntata'):
                first = html.find('div',class_='ultima_puntata')
            elif html.find('div',class_='contenitoreUltimaReplicaLa7d'):
                first = html.find('div',class_='contenitoreUltimaReplicaLa7d')
            elif html.find('div',class_='contenitoreUltimaReplicaNoLuminosa'):
                first = html.find('div',class_='contenitoreUltimaReplicaNoLuminosa')
            else:
                xbmc.log('NO FIRST VIDEO',xbmc.LOGNOTICE)
                if xbmcgui.Dialog().ok(addon.getAddonInfo('name'), language(32005)):
                    exit()
            titolo = first.find('div',class_='title_puntata').text.encode('utf-8').strip()
            
            if tg_cronache == True:
                first_video(first, titolo, titolo.find(filtro_cronache) != -1)
            elif omnibus_news == True:
                first_video(first, titolo, titolo.find(filtro_omnibus) != -1)
            elif link_global == url_base+'/tgla7':
                first_video(first, titolo, titolo.find(filtro_cronache) == -1)
            elif link_global == url_base+'/omnibus':
                first_video(first, titolo, titolo.find(filtro_omnibus) == -1)
            else:
                first_video(first, titolo, True)


            # WEEK VIDEO
            if html.findAll(text=" LA SETTIMANA "):
                video_settimana = html.find('div',class_='home-block__content-carousel container-vetrina').find_all('div',class_='item')
                if video_settimana:
                    get_rows_video(video_settimana)
            else:
                xbmc.log('NO WEEK VIDEO',xbmc.LOGNOTICE)

        # CULT VIDEO
        if html.findAll(text="Puntate Cult"):
            if link_global == url_base+'/chi-sceglie-la-seconda-casa':
                req2 = Request(link_global+"/rivedila7",headers=headers)
            else:
                req2 = Request(link_global+"/rivedila7/archivio?page="+str(pagenum),headers=headers)
            page2 = urlopen(req2)
            html2 = BeautifulSoup(page2,'html5lib')
            video_archivio = html2.find('div',class_='view-content clearfix').find_all('div',class_='views-row')
            if video_archivio:
                get_rows_video(video_archivio)

                if (link_global != url_base+'/tgla7') and (link_global != url_base+'/omnibus'):
                    page=html2.find('li',class_='pager-next')
                    pagenext(page)
    #Tg La7d
    else:
        req = Request(link_global+"?page="+str(pagenum),headers=headers)
        page = urlopen(req)
        html=BeautifulSoup(page,'html5lib')
        video_tgla7d = html.find('div',class_='tgla7-category').find_all('article',class_='tgla7-new clearfix')
        if video_tgla7d:
            get_rows_video_tgla7d(video_tgla7d)
            page=html.find('li',class_='next')
            pagenext(page)
            
    xbmcplugin.setContent(handle, 'episodes')
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    
    
def video_programma_teche_la7():
    global link_global

    #xbmc.log('LINK------: '+str(link_global),xbmc.LOGNOTICE)
    req = Request(link_global+"?page="+str(pagenum),headers=headers)
    page = urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    
    if pagenum == 0:
        # PREVIEW VIDEO
        video_preview = html.find('div',class_='vetrina-protagonista')
        if video_preview:
            get_rows_video_techela7_preview(video_preview)

    # ARCHIVIO VIDEO    
    if html.find('div',class_='view-content clearfix'):
        video_techela7 = html.find('div',class_='view-grouping-content').find_all('div',class_='list-item')
        if video_techela7:
            get_rows_video_techela7(video_techela7)
            page=html.find('li',class_='pager-next')
            pagenext(page)
            
    xbmcplugin.setContent(handle, 'episodes')
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def first_video(first, titolo, filtro):
    if filtro:
        thumb='https:'+first.find('div',class_='holder-bg lozad').get('data-background-image')
        data='[I] - ('+first.find('div',class_='scritta_ultima').text.encode('utf-8').strip()+')[/I]'
        try:
            plot=first.find('div',class_='occhiello').text.encode('utf-8').strip()
        except Exception as e:
            e = sys.exc_info()[0]
            xbmc.log('EXCEP PLOT1: '+str(e),xbmc.LOGNOTICE)
            plot=""
        link=url_base+first.find('a').get('href')
        liStyle = xbmcgui.ListItem(titolo+data)
        liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
        liStyle.setInfo('video', { 'plot': plot })
        addDirectoryItem_nodup({"mode": mode,"play": link,"titolo": titolo+data,"thumb":thumb,"plot":plot}, liStyle, folder=False)


def video_list(div, titolo, filtro):
    if filtro:
        thumb='https:'+div.find('div',class_='bg-img lozad').get('data-background-image')
        #subdata=div.find('a').get('href').encode('utf-8')
        #data='[I] - ('+subdata[24:34]+')[/I]'
        try:
            data='[I] - ('+div.find('div',class_='data').text.encode('utf-8').strip()+')[/I]'
        except Exception as e:
            e = sys.exc_info()[0]
            xbmc.log('EXCEP DATA_1: '+str(e),xbmc.LOGNOTICE)
            data=""
        plot=''
        link=url_base+div.find('a').get('href')
        liStyle = xbmcgui.ListItem(titolo+data)
        liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
        liStyle.setInfo('video', { 'plot': plot })
        addDirectoryItem_nodup({"mode": mode,"play": link,"titolo": titolo+data,"thumb":thumb,"plot":plot}, liStyle, folder=False)


def get_rows_video(video):
    for div in video:
        titolo=div.find('div',class_='title').text.encode('utf-8').strip()
        #xbmc.log('TITOLO: '+str(titolo.find(filtro_cronache)),xbmc.LOGNOTICE)
        if tg_cronache == True:
            video_list(div, titolo, titolo.find(filtro_cronache) != -1)
        elif omnibus_news == True:
            video_list(div, titolo, titolo.find(filtro_omnibus) != -1)
        elif link_global == url_base+'/tgla7':
            video_list(div, titolo, titolo.find(filtro_cronache) == -1)
        elif link_global == url_base+'/omnibus':
            video_list(div, titolo, titolo.find(filtro_omnibus) == -1)
        else:
            video_list(div, titolo, True)


def get_rows_video_tgla7d(video):
    for div in video:
        titolo=div.find('div',class_='tgla7-condividi').get('data-title').encode('utf-8').strip()
        thumb_link=div.find('div',class_='tgla7-img').get('style')
        thumb = thumb_link[22:-1]
        try:
            plot=div.find('div',class_='tgla7-descrizione').text.encode('utf-8').strip()
        except Exception as e:
            e = sys.exc_info()[0]
            xbmc.log('EXCEP PLOT_TGLA7d: '+str(e),xbmc.LOGNOTICE)
            plot=""
        link=div.find('div',class_='tgla7-condividi').get('data-share')
        liStyle = xbmcgui.ListItem(titolo.decode('utf-8'))
        liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
        liStyle.setInfo('video', { 'plot': plot })
        addDirectoryItem_nodup({"mode": mode,"play": link,"titolo": titolo,"thumb":thumb,"plot":plot}, liStyle, folder=False)              


def get_rows_video_techela7_preview(video):
    #xbmc.log('TEST-----: '+str(video),xbmc.LOGNOTICE)
    regex5 = 'poster: "(.*?)"'
    html=str(video)
        
    titolo=video.find('a',class_='title').text.encode('utf-8').strip()
    data='[I] - ('+video.find('span',class_='date-display-single').text.encode('utf-8').strip()+')[/I]'
    #xbmc.log('DATA-----: '+str(data),xbmc.LOGNOTICE)
    if re.findall(regex5, html):
        #xbmc.log('REGEX----------: '+str(re.findall(regex5, html)),xbmc.LOGNOTICE)
        thumb = 'https:'+re.findall(regex5, html)[0]
    else:
        thumb=''
    plot=video.find('div',class_='description').text.encode('utf-8').strip()
    link=url_base+video.find('a',class_='title').get('href')
    liStyle = xbmcgui.ListItem("%s%s" % (titolo.decode('utf-8'),data.decode('utf-8')))
    liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
    liStyle.setInfo('video', { 'plot': plot.decode('utf-8') })
    addDirectoryItem_nodup({"mode": mode,"play": link,"titolo": titolo+data,"thumb":thumb,"plot":plot}, liStyle, folder=False)


def get_rows_video_techela7(video):
    for div in video:
        titolo=div.find('div',class_='title').text.encode('utf-8').strip()
        data='[I] - ('+div.find('div',class_='data').text.encode('utf-8').strip()+')[/I]'
        #xbmc.log('DATA-----: '+str(data),xbmc.LOGNOTICE)
        thumb='https:'+div.find('div',class_='bg-img lozad').get('data-background-image')
        plot=""
        link=url_base+div.a.get('href').strip()
        liStyle = xbmcgui.ListItem("%s%s" % (titolo.decode('utf-8'),data.decode('utf-8')))
        liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
        liStyle.setInfo('video', { 'plot': plot.decode('utf-8') })
        addDirectoryItem_nodup({"mode": mode,"play": link,"titolo": titolo+data,"thumb":thumb,"plot":plot}, liStyle, folder=False)


def video_programma_landpage():
    global link_global
    
    #xbmc.log('LINK GLOBAL------: '+str(link_global),xbmc.LOGNOTICE)
    req = Request(link_global,headers=headers)
    page = urlopen(req)
    html=BeautifulSoup(page,'html5lib')
    
    # FIRT VIDEO
    first_video = html.find('div',class_='ultima_puntata')
    if first_video:
        get_rows_video_landpage_preview(first_video)

    # PUNTATE    
    if html.findAll(text="puntate "):
        #xbmc.log('TEST------: '+str(html.find('div',class_='home-block__content-inner')),xbmc.LOGNOTICE)
        video_puntate_1r = html.find('div',class_='home-block__content-inner').select('div[class="item"]')
        video_puntate_2r = html.find('section',class_='home-block home-block--oggi-striscia home-block--fixed').find_all('div',class_='item')
        #xbmc.log('TEST------: '+str(video_puntate_2r),xbmc.LOGNOTICE)
        if video_puntate_1r:
            get_rows_video_landpage(video_puntate_1r)
        if video_puntate_2r:
            get_rows_video_landpage(video_puntate_2r)
            
    xbmcplugin.setContent(handle, 'episodes')
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)


def get_rows_video_landpage_preview(video):
    #xbmc.log('TEST-----: '+str(video),xbmc.LOGNOTICE)
    titolo = video.find('div',class_='title_puntata').text.encode('utf-8').strip()
    data='[I] - ('+video.find('div',class_='scritta_ultima').text.encode('utf-8').strip()+')[/I]'
    thumb='https:'+video.find('div',class_='holder-bg lozad').get('data-background-image')
    plot=video.find('div',class_='occhiello').text.encode('utf-8').strip()
    link=url_base+video.find('a').get('href')
    liStyle = xbmcgui.ListItem("%s%s" % (titolo.decode('utf-8'), data.decode('utf-8')))
    liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
    liStyle.setInfo('video', { 'plot': plot.decode('utf-8') })
    addDirectoryItem_nodup({"mode": mode,"play": link,"titolo": titolo+data,"thumb":thumb,"plot":plot}, liStyle, folder=False)


def get_rows_video_landpage(video):
    for div in video:
        titolo=div.find('div',class_='title').text.encode('utf-8').strip()
        #xbmc.log('TITOLO-----: '+str(titolo),xbmc.LOGNOTICE)
        data='[I] - ('+div.find('div',class_='data').text.encode('utf-8').strip()+')[/I]'
        thumb='https:'+div.find('div',class_='bg-img lozad').get('data-background-image')
        plot=""
        link=url_base+div.a.get('href').strip()
        liStyle = xbmcgui.ListItem("%s%s" % (titolo.decode('utf-8'), data.decode('utf-8')))
        liStyle.setArt({ 'thumb': thumb, 'fanart' : fanart_path })
        liStyle.setInfo('video', { 'plot': plot.decode('utf-8') })
        addDirectoryItem_nodup({"mode": mode,"play": link,"titolo": titolo+data,"thumb":thumb,"plot":plot}, liStyle, folder=False)


def pagenext(pagenb):
            if pagenb:
                liStyle = xbmcgui.ListItem('[B]'+language(32003)+'[/B]')
                liStyle.setArt({ 'fanart' : fanart_path })
                addDirectoryItem_nodup({"mode": mode,"link":link_global,"page":pagenum+1}, liStyle)




# Main             
params = parameters_string_to_dict(sys.argv[2])
mode = str(params.get("mode", ""))
giorno = str(params.get("giorno", ""))
play=str(params.get("play", ""))
titolo_global=str(params.get("titolo", ""))
thumb_global=str(params.get("thumb", ""))
plot_global=str(params.get("plot", ""))
link_global=str(params.get("link", ""))


if params.get("page", "")=="":
    pagenum=0
else:
    pagenum=int(params.get("page", ""))

if mode=="diretta_live":
    titolo_global=language(32002)
    play_video(url_live,True)    

elif mode=="tg_meteo":
    if play=="":
        if link_global=="":
            programmi_lettera_tg_meteo()
        else:
            video_programma()
    else:
        play_video(play,False)  

elif mode=="rivedi_la7":
    if play=="":
        if giorno=="":
            rivedi(url_rivedila7, 'rivedila7.jpg')
        else:
            rivedi_giorno()
    else:
        play_video(play,False)

elif mode=="rivedi_la7d":
    if play=="":
        if giorno=="":
            rivedi(url_rivedila7d, 'rivedila7d.jpg')
        else:
            rivedi_giorno()
    else:
        play_video(play,False)

elif mode=="tutti_programmi":
    if play=="":
        if link_global=="":
            programmi_lettera()
        else:
            video_programma()
    else:
        play_video(play,False)

elif mode=="teche_la7":
    if play=="":
        if link_global=="":
            programmi_lettera_teche_la7()
        else:
            video_programma_teche_la7()
    else:
        play_video(play,False)

else:
    show_root_menu()
    



