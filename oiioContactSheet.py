#!/usr/bin/env python
# coding:utf-8
""":mod: oiioContactSheet --- Module Title
=================================

   2018.07
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""
from sgtkLib import tkutil, tkm
import os, pprint, errno, argparse, sys, math
import OpenImageIO as oiio

_USER_ = os.environ['USER']
_OUTPATH_ ='/s/prodanim/asterix2/_sandbox/' + _USER_ +"/contactSheet"
_FONT_ = 'LiberationSans-Italic'

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

taskList = ['compo_stereo','compo_comp','light_precomp','light_prelight','confo_render','anim_master','confo_anim','anim_main','layout_base']

animFilter = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'PlayblastImageSequence'],
        ]
    }

imageFilterConfoLayout= {
        'filter_operator' : 'all',
        'filters':[
            ['tag_list', 'name_is','primary'],
            ['published_file_type', 'name_is', 'QCRmovie'],
        ]
    }

exrFilter = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'CompoImageSequence'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
        ]
        }

animMaimFilter= {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }

def imFilter(taskname = 'compo_precomp'):
    filterDict = {'editing_edt': animFilter,
                  'layout_base': animFilter,
                  'confo_layout':imageFilterConfoLayout,
                  'anim_main': animMaimFilter,
                  'light_lighting':exrFilter,
                  'light_precomp':exrFilter,
                  'compo_comp':exrFilter,
                  'light_prelight': exrFilter,
                  'compo_stereo':exrFilter,
                  'confo_render':imageFilterConfoLayout,
                  'anim_master':imageFilterConfoLayout,
                  'confo_anim':imageFilterConfoLayout,

                  }
    return filterDict[taskname]

#main call to SG api extract information from published files
def findShots(taskname='compo_comp', seq='p00300', shotList=[]):
    res = {}
    switchTask = taskList.index(taskname)
    testStatus = True
    while shotList != [] and switchTask < len(taskList):
        filterType = imFilter(taskList[switchTask])
        filters = [
            ['project', 'is', {'type':'Project', 'id':project.id}],
            ['task', 'name_is', taskList[switchTask]],
            #['entity', 'is_not', None],
            ['entity', 'type_is', 'Shot'],
            ['entity.Shot.sg_sequence','name_is', seq],
            ['entity.Shot.sg_status_list', 'is_not', 'omt'],
            filterType
        ]


        for v in sg.find('PublishedFile', filters, ['code', 'entity','entity.Shot.sg_status_list','entity.Shot.sg_cut_order','version_number', 'path', 'published_file_type', 'entity.Shot.sg_cut_in','entity.Shot.sg_cut_out','task','entity.Shot.sg_sequence','entity.Shot.sg_frames_of_interest'], order=[{'field_name':'version_number','direction':'desc'}]):
            entityName = v['entity']['name']
            if not entityName in res:
                imFormat = '.' + v['path']['content_type'][
                                                     v['path']['content_type'].find("/") + 1:]
                res[entityName] = {}
                res[entityName]['imgFormat'] = imFormat
                res[entityName]['cutOrder'] = v['entity.Shot.sg_cut_order']
                res[entityName]['fInterest'] = ''
                if v['entity.Shot.sg_frames_of_interest'] == None:
                    res[entityName]['fInterest'] = v['entity.Shot.sg_cut_in']
                else:
                    res[entityName]['fInterest'] = v['entity.Shot.sg_frames_of_interest']
                if imFormat == '.quicktime':
                    res[entityName]['cutIn'] = 1
                    res[entityName]['cutOut'] = int(v['entity.Shot.sg_cut_out']-v['entity.Shot.sg_cut_in'])
                    res[entityName]['cutMid'] = int((v['entity.Shot.sg_cut_out']-v['entity.Shot.sg_cut_in']) / 2)
                else:
                    res[entityName]['cutIn'] = v['entity.Shot.sg_cut_in']
                    res[entityName]['cutOut'] = v['entity.Shot.sg_cut_out']
                    res[entityName]['cutMid'] = int((v['entity.Shot.sg_cut_in'] + v['entity.Shot.sg_cut_out']) / 2)
                res[entityName]['framePath'] = v['path']['local_path_linux']
                res[entityName]['Task'] = v['task']['name']
                #res[entityName]['status'] =v['entity.Shot.sg_status_list']
        # if testStatus:
        #     filterTask = [
        #         ['project', 'is', {'type': 'Project', 'id': project.id}],
        #         ['content', 'is', taskname],
        #         ['entity', 'type_is', 'Shot'],
        #         ['entity.Shot.sg_sequence', 'name_is', seq],
        #         ['entity.Shot.code', 'in', res.keys()]
        #     ]
        #     for v in sg.find('Task', filterTask, ['code', 'entity', 'sg_status_artistique']):
        #         entityName = v['entity']['name']
        #         try:
        #             res[entityName]['status'] = v['sg_status_artistique']
        #         except:
        #             res[entityName]['status'] = 'None'
        #     testStatus = False

        listShotInRes = sorted(res.keys())
        shotList = list(set(shotList).difference(listShotInRes))
        nbShotInTask = str(listShotInRes).replace('\'','').replace('[','').replace(']','')
        if len(listShotInRes) == 0:
            nbShotInTask = 'None'
        print taskList[switchTask]+': '+ nbShotInTask
        switchTask = switchTask + 1

    filterTask = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['content', 'is', taskname],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.sg_sequence', 'name_is', seq],
        ['entity.Shot.code', 'in', res.keys()]
    ]
    for v in sg.find('Task', filterTask, ['code', 'entity', 'sg_status_artistique']):
        entityName = v['entity']['name']
        try:
            res[entityName]['status'] = v['sg_status_artistique']
        except:
            res[entityName]['status'] = 'None'
    return res

def findShotsInList( seq='s1300', shotList=[], taskname = 'compo_comp'):
    res = {}
    for shot in shotList:
        found = False
        switchTask = taskList.index(taskname)
        while found == False:
            print taskList[switchTask],shot
            filterType = imFilter(taskList[switchTask])
            filters = [
            ['project', 'is', {'type': 'Project', 'id': project.id}],
            ['entity.Shot.code', 'is', shot],
            ['entity.Shot.sg_status_list', 'is_not', 'omt'],
            ['task', 'name_is', taskList[switchTask]],
            filterType
            ]

            fileFound = sg.find('PublishedFile', filters, ['code', 'entity','entity.Shot.sg_status_list','entity.Shot.sg_cut_order','version_number', 'path', 'published_file_type', 'entity.Shot.sg_cut_in','entity.Shot.sg_cut_out','task','entity.Shot.sg_sequence','entity.Shot.sg_frames_of_interest'], order=[{'field_name':'version_number','direction':'desc'}])
            if fileFound == []:
                switchTask = switchTask + 1
            else:
                v = fileFound[0]
                entityName = v['entity']['name']
                if not entityName in res:
                    res[entityName] = v
                    res[entityName]['imgFormat'] = '.' + v['path']['content_type'][
                                                         v['path']['content_type'].find("/") + 1:]
                    res[entityName]['cutOrder'] = v['entity.Shot.sg_cut_order']
                    res[entityName]['fInterest'] =''
                    if v['entity.Shot.sg_frames_of_interest'] == None:
                        res[entityName]['fInterest']=v['entity.Shot.sg_cut_in']
                    else:
                        res[entityName]['fInterest']= v['entity.Shot.sg_frames_of_interest']
                    res[entityName]['cutIn'] = v['entity.Shot.sg_cut_in']
                    res[entityName]['cutOut']= v['entity.Shot.sg_cut_out']
                    res[entityName]['cutMid'] = int((v['entity.Shot.sg_cut_in'] + v['entity.Shot.sg_cut_out'])/2)
                    res[entityName]['framePath'] = v['path']['local_path_linux']

                found = True

            if switchTask >= len(taskList):
                print 'not good'
                break

    return res


def findShotsInSequence(seq='s1300',dict=False):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['code','is',seq]
    ]
    res = {}
    seqShots =[]
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','shots']):
        if not 'Shots' in res:
            tmp = v['shots']
            for item in tmp:
                sg_filter = [['project', 'is', {'type':'Project', 'id':project.id}],
                             ['code', 'is', item['name']]]
                for v in sg.find('Shot', sg_filter, ['code','sg_status_list']):
                    if v['sg_status_list'] != 'omt':
                        seqShots.append(item['name'])
            res['Shots'] = sorted(seqShots)
    if dict:
        return res
    else:
        return sorted(seqShots)

'''order the shot in cut order'''

def getOrder(res = {}):
    shotNb = []
    for key in res.keys():
        shotNb.append(key)
    for j in range(len(shotNb)):
    #initially swapped is false
        swapped = False
        i = 0
        while i<len(res)-1:
        #comparing the adjacent elements
            if res[shotNb[i]]['cutOrder']>res[shotNb[i+1]]['cutOrder']:
                #swapping
                shotNb[i],shotNb[i+1] = shotNb[i+1],shotNb[i]
                #Changing the value of swapped
                swapped = True
            i = i+1
    #if swapped is false then the list is sorted
    #we can stop the loop
        if swapped == False:
            break
    return shotNb

def contactSheet(task='compo_comp', seq = 's0180',res={},format = 'jpg',scale = 'full',shotgunData = True):
    path = _OUTPATH_+'/'+seq+'/'+task+'/'
    if not os.path.isdir(path):
        os.makedirs(path)
    outdir = path+'contactSheet_'+seq+'.'+format

    cutOrderSeq = getOrder(res)

    #import the colorchart
    checkerImage =oiio.ImageBuf('/s/prodanim/asterix2/_sandbox/duda/images/chekerCrop.jpg')
    widthChecker = checkerImage.spec().width
    heightChecker = checkerImage.spec().height

    # list of color average
    averageList = []

    # space in between images
    space =80

    # max width and height for the images
    maxwidth = 2048
    maxheight = 858

    # text sequence number
    text = oiio.ImageBuf(oiio.ImageSpec(int(1.5*maxwidth), int(1.5*maxheight), 3, oiio.FLOAT))
    oiio.ImageBufAlgo.render_text(text, 100, ((maxheight) / 2) +400, seq, 1050, fontname=_FONT_,
                                  textcolor=(1, 1, 1, 1))

    # na color
    na = oiio.ImageBuf(oiio.ImageSpec(200, 200, 3, oiio.FLOAT))
    oiio.ImageBufAlgo.zero(na)
    oiio.ImageBufAlgo.render_text(na, 20, 140, 'Na', 120, fontname=_FONT_,
                                  textcolor=(1, 0, 0, 0))

    # logo
    logo = oiio.ImageBuf('/s/prodanim/asterix2/_source_global/Software/Nuke/scripts/contactSheetDir/logo.jpg')
    widthLogo = logo.spec().width
    heightLogo = logo.spec().height

    # number of row and column for the contactsheet
    nrow = 5
    ncol =13

    # area containing the images of sequence
    widthBufImage = (maxwidth*nrow)+(space*(nrow+1))
    heightBufImage = (maxheight*ncol)+(space*(ncol+1))
    buf = oiio.ImageBuf(oiio.ImageSpec(widthBufImage, heightBufImage, 3, oiio.FLOAT))

    # offset to move the image
    offsetwidth = 0
    offsetheight = 0


    imgh = 0
    nbimage = 0
    cutOrderSeqLen = len(cutOrderSeq)
    a =1
    print 'tendering the frames'
    for i in range(1, ncol + 1):
        if a == 0:
            break
        imgw = 0
        for j in range(1, nrow + 1):
            if nbimage < cutOrderSeqLen and nbimage <= (nrow * ncol):
                shot = cutOrderSeq[nbimage]
                pathFile = res[shot]['framePath']
                fileFromList = []
                if res[shot]['imgFormat'] == '.quicktime':
                    fileFromList = oiio.ImageBuf(pathFile, res[shot]['cutMid'], 0)
                else:
                    if not os.path.isfile(pathFile.replace('%04d',str(res[shot]['cutMid']).zfill(4))):
                        dirPath = pathFile[:pathFile.rfind('/')]
                        dirFiles = sorted(os.listdir(dirPath))
                        fileFromList =oiio.ImageBuf(dirPath + '/' +dirFiles[0])
                    else:
                        fileFromList = oiio.ImageBuf(pathFile.replace('%04d',str(res[shot]['cutMid']).zfill(4)))
            else:
                # fileFromList = text
                a = 0
                break
            fileFromListWidth = fileFromList.spec().width
            fileFromListHeight = fileFromList.spec().height
            if fileFromListWidth > maxwidth or fileFromListHeight > maxheight:
                offsetwidth = (fileFromListWidth - maxwidth) / 2
                offsetheight = (fileFromListHeight - maxheight) / 2
            tmpInfile = oiio.ImageBuf(oiio.ImageSpec(maxwidth, maxheight, 3, oiio.FLOAT))
            oiio.ImageBufAlgo.crop(tmpInfile, fileFromList,
                                   oiio.ROI(offsetwidth, fileFromListWidth - offsetwidth, offsetheight,
                                            fileFromListHeight - offsetheight))
            stats = oiio.PixelStats()
            if res[shot]['imgFormat'] == '.exr' and format != 'exr':
                oiio.ImageBufAlgo.colorconvert(tmpInfile, tmpInfile, 'linear', 'Asterix2_Film')
                oiio.ImageBufAlgo.computePixelStats(tmpInfile, stats)
            averageList.append(stats.avg)
            oiio.ImageBufAlgo.paste(buf, imgw + (j * space), imgh + (i * space), 0, 0, tmpInfile)
            if shotgunData:
                tmpData = oiio.ImageBuf(oiio.ImageSpec(maxwidth, 40, 3, oiio.FLOAT))
                oiio.ImageBufAlgo.zero(tmpData)
                shotText = shot
                taskText =  res[shot]['Task']
                if taskText != task:
                    oiio.ImageBufAlgo.fill(tmpData,(1,0,0,1))
                oiio.ImageBufAlgo.render_text(tmpData,10,30,shotText,35,_FONT_)
                oiio.ImageBufAlgo.render_text(tmpData, maxwidth-400, 30, taskText.upper(), 35, _FONT_)
                if taskText == task:
                    statusCol = (1, 0, 0)
                    if res[shot]['status'] == 'cmpt':
                        statusCol = (0,1,0)
                    oiio.ImageBufAlgo.fill(tmpData,statusCol,oiio.ROI(maxwidth-50,maxwidth-10,0,40))
                oiio.ImageBufAlgo.paste(buf, imgw + (j * space), (imgh-40) + (i * space), 0, 0, tmpData)
            imgw = imgw + maxwidth
            nbimage = nbimage + 1
        imgh = imgh + maxheight

    print 'adding some salt'
    # create the master buffer
    masterBufwidth = widthBufImage+(578*2)
    masterBufHeight = int(masterBufwidth*1.414)
    masterBuf = oiio.ImageBuf(oiio.ImageSpec(masterBufwidth, masterBufHeight, 3, oiio.FLOAT))

    # create the white border
    oiio.ImageBufAlgo.render_box(masterBuf,518,518,masterBufwidth -518,masterBufHeight-518,(1,1,1,0),True)
    oiio.ImageBufAlgo.render_box(masterBuf, 578, 578, masterBufwidth - 578, masterBufHeight - 578, (0, 0, 0, 0), True)

    # paste the buffer contactsheet in the main buffer
    oiio.ImageBufAlgo.paste(masterBuf, 578, 578+(2*maxheight), 0, 0, buf)
    oiio.ImageBufAlgo.render_box(masterBuf,578,(578+(2*maxheight))-60,masterBufwidth-578,578+(2*maxheight),(1,1,1,0),True)
    oiio.ImageBufAlgo.render_box(masterBuf,578,578+heightBufImage+(2*maxheight),masterBufwidth-578,578+heightBufImage+(2*maxheight)+60,(1,1,1,1),True)

    print 'a bit of peper'
    # #paste the sequence number
    oiio.ImageBufAlgo.paste(masterBuf, 840, 120 , 0, 0, logo)

    #
    # create the average color box
    startcolumnBox = 1178+(space)
    endColumnBox = startcolumnBox +200
    startRowBox = 578+(2*space)
    averageScene = (0,0,0)
    for col in averageList:
        if len(col) > 2:
            averageScene = tuple(map(sum,zip(averageScene,col)))
            oiio.ImageBufAlgo.fill(masterBuf,col,oiio.ROI(startRowBox,startRowBox+200,startcolumnBox,endColumnBox))
        else:
            oiio.ImageBufAlgo.paste(masterBuf,startRowBox,startcolumnBox,0,0,na)
        startRowBox = startRowBox+200
        if startRowBox > masterBufwidth-(578+(4*space)+(2*widthChecker)):
            startRowBox = 578 + (2*space)
            startcolumnBox = (1178)+200+int(space*1.5)
            endColumnBox = startcolumnBox + 200

    print 'smoldering the lot'
    # create the box with the average of scene color
    averageScene = tuple([x/cutOrderSeqLen for x in averageScene])
    oiio.ImageBufAlgo.fill(masterBuf, averageScene,
                           oiio.ROI(masterBufwidth-((2*widthChecker)+578+(space*2)), masterBufwidth-(widthChecker+578+(2*space)), 878+space, 878+space+heightChecker))

    # add the checker and seq text
    oiio.ImageBufAlgo.paste(masterBuf,masterBufwidth-(widthChecker+578+space),878+space,0,0,checkerImage)
    oiio.ImageBufAlgo.paste(masterBuf,(578+space)+(masterBufwidth/2)-maxwidth-200,masterBufHeight-(518+space+int(1.5*maxheight)),0,0,text)

    #create the output frame
    output = oiio.ImageBuf()
    if scale == 'half':
        output = oiio.ImageBuf(oiio.ImageSpec(int(masterBufwidth/2), int(masterBufHeight/2), 3, oiio.FLOAT))
        oiio.ImageBufAlgo.resize(output,masterBuf)
    elif scale == 'quarter':
        output = oiio.ImageBuf(oiio.ImageSpec(int(masterBufwidth / 4), int(masterBufHeight / 4), 3, oiio.FLOAT))
        oiio.ImageBufAlgo.resize(output, masterBuf)
    else:
        output = masterBuf

    bitFormat = oiio.UINT8
    if format == 'exr':
        bitFormat = oiio.HALF
    elif format == 'tif':
        bitFormat = oiio.UINT16
    else:
        bitFormat == oiio.UINT8

    output.set_write_format(bitFormat)

    output.write(outdir)

    print 'and Voila!\n'+outdir+' is cooked'

def main():
    seq = 's0030'
    task = 'compo_comp'
    shotList = findShotsInSequence(seq)
    res = findShots(task,seq,shotList)
    contactSheet(task,seq,res,'tif','quarter')
    #pprint.pprint(sg.schema_field_read('Task'))

if __name__ == '__main__':
    main()