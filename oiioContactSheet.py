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
import os, pprint, errno, argparse, sys, math,subprocess
import OpenImageIO as oiio
from PIL import Image

_USER_ = os.environ['USER']
_OUTPATH_ ='/s/prodanim/asterix2/_sandbox/' + _USER_ +"/contactSheet"
_FONT_ = 'LiberationSans-Italic'

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

_TASKLIST_ = ['compo_stereo','compo_comp','light_precomp','light_prelight','confo_render','anim_master','confo_anim','anim_main','layout_base']
_OUTPUTFORMAT_=['jpg','tif','exr']
_OUTSIZE_ = ["full", "half", "quarter"]

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
    if taskname not in _TASKLIST_:
        taskname = _TASKLIST_[0]
    print 'using : '
    res = {}
    switchTask = _TASKLIST_.index(taskname)
    testStatus = True
    while shotList != [] and switchTask < len(_TASKLIST_):
        filterType = imFilter(_TASKLIST_[switchTask])
        filters = [
            ['project', 'is', {'type':'Project', 'id':project.id}],
            ['task', 'name_is', _TASKLIST_[switchTask]],
            #['entity', 'is_not', None],
            ['entity', 'type_is', 'Shot'],
            ['entity.Shot.sg_sequence','name_is', seq],
            ['entity.Shot.sg_status_list', 'is_not', 'omt'],
            filterType
        ]


        for v in sg.find('PublishedFile', filters, ['code', 'entity','entity.Shot.sg_status_list','entity.Shot.sg_cut_order','version_number', 'path', 'published_file_type', 'entity.Shot.sg_cut_in','entity.Shot.sg_cut_out','task','entity.Shot.sg_sequence','entity.Shot.sg_frames_of_interest'], order=[{'field_name':'version_number','direction':'desc'}]):
            versionNb =v['version_number']
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
                res[entityName]['version']= v['version_number']
                res[entityName]['versionNb'] = {}
                res[entityName]['versionNb'][versionNb] = v['path']['local_path_linux']
            elif versionNb not in res[entityName]['versionNb']:
                res[entityName]['versionNb'][versionNb] = v['path']['local_path_linux']
            else:
                continue

        listShotInRes = sorted(res.keys())
        shotList = list(set(shotList).difference(listShotInRes))
        #nbShotInTask = str(listShotInRes).replace('\'','').replace('[','').replace(']','')
        if len(listShotInRes) == 0:
            nbShotInTask = 'None'
        print '\t'+_TASKLIST_[switchTask]#+': '+ nbShotInTask
        switchTask = switchTask + 1

    # find the artistic status of the main task for each shot
    filterTask = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['content', 'is', taskname],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.sg_sequence', 'name_is', seq],
        ['entity.Shot.code', 'in', res.keys()]
    ]
    for v in sg.find('Task', filterTask, ['code', 'entity', 'sg_status_artistique','version_number']):
        entityName = v['entity']['name']
        try:
            res[entityName]['status'] = v['sg_status_artistique']
        except:
            res[entityName]['status'] = 'None'

    # find all version for the shot in res
    # if findVersions:
    #     for shot in res.keys():
    #         if res[shot]['Task'] == taskname :
    #             versionList = []
    #             filters = [
    #                 ['project', 'is', {'type': 'Project', 'id': project.id}],
    #                 ['entity.Shot.code', 'is', shot],
    #                 ['entity.Shot.sg_status_list', 'is_not', 'omt'],
    #                 ['task', 'name_is', res[shot]['Task']],
    #             ]
    #
    #             fileFound = sg.find('PublishedFile', filters,
    #                                 ['code', 'entity', 'version_number'],order=[{'field_name': 'version_number', 'direction': 'desc'}])
    #             for version in fileFound:
    #                 if str(version['version_number']) not in versionList:
    #                     versionList.append(str(version['version_number']))
    #             res[shot]['versionsList']=versionList
    # pprint.pprint(res)
    return res

def findAllSequence(all = False):
    from sgtkLib import tkutil, tkm
    tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
    sg = sgw._sg

    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
    ]
    seqShots =[]
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','code','description']):
        seq = v['code']
        if all:
            if not seq in seqShots:
                seqShots.append(seq)
        else:
            if int(seq[seq.find('s')+1:]) <9000:
                if not seq in seqShots:
                    seqShots.append(seq)
            else:
                print  seq + ' will not be included'
    seqShots=sorted(seqShots)
    return seqShots

def findShotsInList( seq='s1300', shotList=[], taskname = 'compo_comp'):
    res = {}
    for shot in shotList:
        found = False
        switchTask = _TASKLIST_.index(taskname)
        while found == False:
            print _TASKLIST_[switchTask],shot
            filterType = imFilter(_TASKLIST_[switchTask])
            filters = [
            ['project', 'is', {'type': 'Project', 'id': project.id}],
            ['entity.Shot.code', 'is', shot],
            ['entity.Shot.sg_status_list', 'is_not', 'omt'],
            ['task', 'name_is', _TASKLIST_[switchTask]],
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

            if switchTask >= len(_TASKLIST_):
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

def contactSheet(task='compo_comp', seq = 's0180',res={},format = 'jpg',scale = 'full',shotgunData = True, printFormat = False, nrow =5, pdf =True):

    logoFile = '/s/prodanim/asterix2/_source_global/Software/Nuke/scripts/contactSheetDir/logo.jpg'
    checkerFile = '/s/prodanim/asterix2/_sandbox/duda/images/chekerCrop.jpg'

    path = _OUTPATH_+'/'+seq+'/'+task+'/'
    if not os.path.isdir(path):
        os.makedirs(path)
    outdir = path + 'contactSheet_' + seq + '.' + format
    if printFormat:
        outdir = path + 'contactSheet_print_' + seq + '.' + format

    cutOrderSeq = getOrder(res)

    # space in between images
    space =80

    # max width and height for the images
    maxwidth = 2048
    maxheight = 858

    # logo
    logo = oiio.ImageBuf(logoFile)

    averageList = []

    print 'preparing the sauce'
    # if in print format
    if printFormat:
        # color checker image
        checkerImage = oiio.ImageBuf(checkerFile)
        widthChecker = checkerImage.spec().width
        heightChecker = checkerImage.spec().height
        # na color
        na = oiio.ImageBuf(oiio.ImageSpec(200, 200, 3, oiio.FLOAT))
        oiio.ImageBufAlgo.zero(na)
        oiio.ImageBufAlgo.render_text(na, 20, 140, 'Na', 120, fontname=_FONT_,
                                      textcolor=(1, 0, 0, 0))

        nrow=5
        ncol =13
        # separate the shot number so there is a maximum of 65 shot per page
        imbNb = 1
        nbPage =1
        dictListShot = {}
        for shot in cutOrderSeq:
            imMod = imbNb%65  # (ncol*nrow)
            contactsheet ='contact' + str(nbPage)
            if imMod != 0:
                if not contactsheet in dictListShot:
                    dictListShot[contactsheet]={}
                    dictListShot[contactsheet]['listShot'] = []
                    dictListShot[contactsheet]['masterBuf'] = oiio.ImageBuf()
                    dictListShot[contactsheet]['page'] = nbPage
                    dictListShot[contactsheet]['imagePath']=  path + 'contactSheet_print_' + seq + '_'+str(nbPage).zfill(3)+'.' + format
                dictListShot[contactsheet]['listShot'].append(shot)
            else:
                nbPage = nbPage + 1
                if not contactsheet in dictListShot:
                    dictListShot[contactsheet] = {}
                    dictListShot[contactsheet]['listShot'] = []
                    dictListShot[contactsheet]['masterBuf'] = oiio.ImageBuf()
                    dictListShot[contactsheet]['page'] = nbPage
                    dictListShot[contactsheet]['imagePath'] = path + 'contactSheet_print_' + seq + '_' + str(nbPage).zfill(3) + '.' + format
                dictListShot[contactsheet]['listShot'].append(shot)
            imbNb = imbNb + 1

        # rescale the logo
        tmpLogo = oiio.ImageBuf(oiio.ImageSpec(1558, 1030, 3, oiio.FLOAT))
        oiio.ImageBufAlgo.resize(tmpLogo, logo)
        logo = tmpLogo
        widthLogo = logo.spec().width
        heightLogo = logo.spec().height


        #create the masterBuffer
        for contactSheet in sorted(dictListShot.keys()):
            if contactSheet == 'contact1':
                dictListShot[contactSheet]['masterBuf'], masterBufwidth, masterBufHeight = createMasterBuf(maxwidth=maxwidth, maxheight=maxheight,
                                                                             printFormat=printFormat, nrow=nrow, ncol=ncol,
                                                                             space=space, seq=seq, task=task, topBar=True,
                                                                             bottomBar=True)
                oiio.ImageBufAlgo.paste(dictListShot[contactSheet]['masterBuf'], (masterBufwidth / 2) - (widthLogo / 2), 60, 0, 0, logo)
                #adding page number
                oiio.ImageBufAlgo.render_text(dictListShot[contactSheet]['masterBuf'], masterBufwidth-650,
                                              masterBufHeight -190,
                                              str(dictListShot[contactSheet]['page'])+'/'+str(len(dictListShot.keys())), 250, fontname=_FONT_, textcolor=(1, 1, 1, 1))
                print 'tendering the frames'
                dictListShot[contactSheet]['masterBuf'], averageList = placeImages(res=res, task=task, cutOrderSeq=dictListShot[contactSheet]['listShot'], imgh=578 + (2 * maxheight),
                                                     masterBuf=dictListShot[contactSheet]['masterBuf'], printFormat=printFormat, ncol=ncol, nrow=nrow,
                                                     space=space, maxwidth=maxwidth, maxheight=maxheight,averageList=averageList, shotgunData=shotgunData)
            else:
                dictListShot[contactSheet]['masterBuf'], masterBufwidth, masterBufHeight = createMasterBuf(
                    maxwidth=maxwidth, maxheight=maxheight,
                    printFormat=printFormat, nrow=nrow, ncol=ncol,
                    space=space, seq=seq, task=task, topBar=False,
                    bottomBar=True)
                # adding page number
                oiio.ImageBufAlgo.render_text(dictListShot[contactSheet]['masterBuf'], masterBufwidth - 650,
                                              masterBufHeight - 190,
                                              str(dictListShot[contactSheet]['page']) + '/' + str(
                                                  len(dictListShot.keys())), 250, fontname=_FONT_,
                                              textcolor=(1, 1, 1, 1))
                dictListShot[contactSheet]['masterBuf'], averageList = placeImages(res=res, task=task,
                                                                                   cutOrderSeq=dictListShot[contactSheet]['listShot'],
                                                                                   imgh=578,
                                                                                   masterBuf=dictListShot[contactSheet][
                                                                                       'masterBuf'],
                                                                                   printFormat=printFormat, ncol=ncol,
                                                                                   nrow=nrow,
                                                                                   space=space, maxwidth=maxwidth,
                                                                                   maxheight=maxheight,averageList=averageList,shotgunData=shotgunData)

        # create the average color box
        startcolumnBox = 1178 + (space)
        endColumnBox = startcolumnBox + 200
        startRowBox = 578 + (2 * space)
        averageScene = (0, 0, 0)
        masterBuf = dictListShot['contact1']['masterBuf']
        for col in averageList:
            if len(col) > 2:
                averageScene = tuple(map(sum, zip(averageScene, col)))
                oiio.ImageBufAlgo.fill(masterBuf, col,
                                       oiio.ROI(startRowBox, startRowBox + 200, startcolumnBox, endColumnBox))
            else:
                oiio.ImageBufAlgo.paste(masterBuf, startRowBox, startcolumnBox, 0, 0, na)
            startRowBox = startRowBox + 200
            if startRowBox > masterBufwidth - (578 + (4 * space) + (2 * widthChecker)):
                startRowBox = 578 + (2 * space)
                startcolumnBox = startcolumnBox+ 200 + 10
                endColumnBox = startcolumnBox + 200

        # create the box with the average of scene color
        averageScene = tuple([x / len(cutOrderSeq) for x in averageScene])
        oiio.ImageBufAlgo.fill(masterBuf, averageScene,
                               oiio.ROI(masterBufwidth - ((2 * widthChecker) + 578 + (space * 2)),
                                        masterBufwidth - (widthChecker + 578 + (2 * space)), 878 + space,
                                        878 + space + heightChecker))

        # add the checker and seq text
        oiio.ImageBufAlgo.paste(masterBuf, masterBufwidth - (widthChecker + 578 + space), 878 + space, 0, 0,
                                checkerImage)

        print 'adding some salt\na bit of pepper\nsmoldering the lot'

        # create the outputs frame
        outdir =''
        for key in dictListShot.keys():
            output = oiio.ImageBuf()
            if scale == 'half':
                output = oiio.ImageBuf(oiio.ImageSpec(int(masterBufwidth / 2), int(masterBufHeight / 2), 3, oiio.FLOAT))
                oiio.ImageBufAlgo.resize(output, dictListShot[key]['masterBuf'])
            elif scale == 'quarter':
                output = oiio.ImageBuf(oiio.ImageSpec(int(masterBufwidth / 4), int(masterBufHeight / 4), 3, oiio.FLOAT))
                oiio.ImageBufAlgo.resize(output, dictListShot[key]['masterBuf'])
            else:
                output = dictListShot[key]['masterBuf']

            bitFormat = oiio.UINT8
            if format == 'exr':
                bitFormat = oiio.HALF
            elif format == 'tif':
                bitFormat = oiio.UINT8
            else:
                bitFormat == oiio.UINT8

            output.set_write_format(bitFormat)
            outdir = outdir+ dictListShot[key]['imagePath'] + ', '

            output.write(dictListShot[key]['imagePath'])

            if pdf:
            #listForPdf = []
                for key in dictListShot:
                    infilePath = dictListShot[key]['imagePath']
                    if format != 'jpg':
                        infile = oiio.ImageBuf(infilePath)
                        infile.write(infilePath.replace(format,'jpg'))
                        infilePath = infilePath.replace(format,'jpg')
                #listForPdf.append(dictListShot[key]['imagePath'])
                    pdfFile = Image.open(infilePath)
                    pdfFile.save(infilePath.replace('jpg','pdf'))


    else:
        ncolTmpFloat = float(len(res.keys())/float(nrow))
        ncolTmpInt = int(len(res.keys())/nrow)
        if ncolTmpFloat - ncolTmpInt > 0:
            ncol = ncolTmpInt + 1
        else:
            ncol = ncolTmpInt
        tmpLogo = oiio.ImageBuf(oiio.ImageSpec(2366, 1544, 3, oiio.FLOAT))
        oiio.ImageBufAlgo.resize(tmpLogo, logo)
        logo = tmpLogo
        widthLogo = logo.spec().width
        heightLogo = logo.spec().height
        masterBuf, masterBufwidth, masterBufHeight = createMasterBuf(maxwidth=maxwidth, maxheight=maxheight,
                                                                     printFormat=printFormat, nrow=nrow, ncol=ncol,
                                                                     space=space, seq=seq, task=task, topBar=True,
                                                                     bottomBar=True)
        print 'tendering the frames'
        oiio.ImageBufAlgo.paste(masterBuf, (masterBufwidth / 2) - (widthLogo / 2), 628, 0, 0, logo)
        masterBuf, averageList = placeImages(res=res, task=task, cutOrderSeq=cutOrderSeq, imgh=578 + (2 * maxheight),
                                             masterBuf=masterBuf, printFormat=printFormat, ncol=ncol, nrow=nrow,
                                             space=space, maxwidth=maxwidth, maxheight=maxheight, shotgunData=shotgunData)

        print 'adding some salt\na bit of pepper\nsmoldering the lot'
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

    print 'and Voila!\n'+outdir+' is cooked, \nEnjoy with no moderation!!!!'
    return outdir

def createMasterBuf(maxwidth=2048, maxheight=858, printFormat=True, nrow=5, ncol=13 ,space=40, seq='s0265', task='compo_comp', topBar=True, bottomBar=True):
    # create the master buffer
    # area containing the images of sequence
    widthShotArea = (maxwidth * nrow) + (space * (nrow + 1))
    heightShotArea = (maxheight * ncol) + (space * (ncol + 1))
    masterBufwidth = widthShotArea + (578 * 2)
    masterBufHeight = int(heightShotArea + (4 * maxheight) + (2 * 578))
    if printFormat:
        masterBufHeight = int(masterBufwidth * 1.414)
    masterBuf = oiio.ImageBuf(oiio.ImageSpec(masterBufwidth, masterBufHeight, 3, oiio.FLOAT))
    # create the white border
    oiio.ImageBufAlgo.render_box(masterBuf, 518, 518, masterBufwidth - 518, masterBufHeight - 518, (1, 1, 1, 0), True)
    oiio.ImageBufAlgo.render_box(masterBuf, 578, 578, masterBufwidth - 578, masterBufHeight - 578, (0, 0, 0, 0), True)
    # top bar
    if topBar:
        oiio.ImageBufAlgo.render_box(masterBuf, 578, (578 + (2 * maxheight)) - 60, masterBufwidth - 578,
                                    578 + (2 * maxheight), (1, 1, 1, 0), True)
        # bottom bar
    if bottomBar:
        oiio.ImageBufAlgo.render_box(masterBuf, 578, 578 + heightShotArea + (2 * maxheight), masterBufwidth - 578,
                                     578 + heightShotArea + (2 * maxheight) + 60, (1, 1, 1, 1), True)
    # adding the task,seq number
    oiio.ImageBufAlgo.render_text(masterBuf, int(masterBufwidth / 2) + 200, int(masterBufHeight - (maxheight + 200)),
                                  task.upper(), 400, fontname=_FONT_, textcolor=(1, 1, 1, 1))
    oiio.ImageBufAlgo.render_text(masterBuf, x=int((masterBufwidth / 2) - (1.35 * maxwidth)),
                                  y=int(masterBufHeight - (maxheight + 200)), text=seq, fontsize=1050, fontname=_FONT_,
                                  textcolor=(1, 1, 1, 1))
    return masterBuf,masterBufwidth,masterBufHeight

def placeImages(res = {}, shotgunData = True, task ='compo_comp', cutOrderSeq =[], imgh= 2294, masterBuf = oiio.ImageBuf(), printFormat = False, ncol = 13, nrow = 5, space =40, maxwidth=2048, maxheight=858, averageList = []):
    offsetwidth = 0
    offsetheight = 0
    nbimage = 0
    cutOrderSeqLen = len(cutOrderSeq)
    outLoop = 1
    for i in range(1, ncol + 1):
        if outLoop == 0:
            break
        imgw = 578
        for j in range(1, nrow + 1):
            xPos = imgw + (j * space)  # placement of the image in x
            yPos = imgh + (i * space)  # placement of the image in y
            if nbimage < cutOrderSeqLen and nbimage <= (nrow * ncol):
                shot = cutOrderSeq[nbimage]
                pathFile = res[shot]['framePath']
                fileFromList = oiio.ImageBuf()
                # if it's a quicktime movie
                if res[shot]['imgFormat'] == '.quicktime':
                    fileFromList = oiio.ImageBuf(pathFile, res[shot]['cutMid'], 0)
                else:
                    if not os.path.isfile(pathFile.replace('%04d', str(res[shot]['cutMid']).zfill(4))):
                        dirPath = pathFile[:pathFile.rfind('/')]
                        dirFiles = sorted(os.listdir(dirPath))
                        fileFromList = oiio.ImageBuf(dirPath + '/' + dirFiles[0])
                    else:
                        fileFromList = oiio.ImageBuf(pathFile.replace('%04d', str(res[shot]['cutMid']).zfill(4)))
            else:
                # fileFromList = text
                outLoop = 0
                break
            fileFromListWidth = fileFromList.spec().width
            fileFromListHeight = fileFromList.spec().height
            if fileFromListWidth > maxwidth or fileFromListHeight > maxheight:
                tmpInfile = oiio.ImageBuf(oiio.ImageSpec(maxwidth, maxheight, 3, oiio.FLOAT))
                offsetwidth = (fileFromListWidth - maxwidth) / 2
                offsetheight = (fileFromListHeight - maxheight) / 2
                oiio.ImageBufAlgo.crop(tmpInfile, fileFromList,
                                       oiio.ROI(offsetwidth, fileFromListWidth - offsetwidth, offsetheight,
                                                fileFromListHeight - offsetheight))
                fileFromList = tmpInfile
            stats = oiio.PixelStats()
            if res[shot]['imgFormat'] == '.exr' and format != 'exr':
                oiio.ImageBufAlgo.colorconvert(fileFromList, fileFromList, 'linear', 'Asterix2_Film')
                if printFormat:
                    oiio.ImageBufAlgo.computePixelStats(fileFromList, stats)
            averageList.append(stats.avg)
            oiio.ImageBufAlgo.paste(masterBuf, xPos, yPos, 0, 0, fileFromList)
            # if user want to display shotgun data
            if shotgunData:
                shotText = shot
                taskText = res[shot]['Task']
                if taskText != task:
                    oiio.ImageBufAlgo.fill(masterBuf, (1, 0, 0), oiio.ROI(xPos, xPos + maxwidth, yPos - 40, yPos))
                oiio.ImageBufAlgo.render_text(masterBuf, xPos + 10, yPos - 10, shotText, 35, _FONT_)
                oiio.ImageBufAlgo.render_text(masterBuf, xPos + maxwidth - 450, yPos - 10,
                                              taskText.upper() + '  v' + str(res[shot]['version']), 35, _FONT_)
                if taskText == task:
                    statusCol = (1, 0, 0)
                    if res[shot]['status'] == 'cmpt':
                        statusCol = (0, 1, 0)
                    oiio.ImageBufAlgo.fill(masterBuf, statusCol,
                                           oiio.ROI(xPos + maxwidth - 50, xPos + maxwidth - 10, yPos - 40, yPos))
            imgw = imgw + maxwidth
            nbimage = nbimage + 1
        imgh = imgh + maxheight

    return masterBuf, averageList

def findPrinters():
    tmpPrinterList = subprocess.Popen(['lpstat','-a'],stdout=subprocess.PIPE).communicate()[0]
    printerList = []
    for line in tmpPrinterList.splitlines():
        printerList.append(line[:line.find(' ')])
    return printerList

def playInRv(imagesList=[]):
    rvCommand = 'rv '
    for image in imagesList:
        rvCommand = rvCommand + ' ' + image
    #rvCommand = rvCommand + ' -pyeval "import rv.commands; rv.commands.stop(); print \'donuts\'"'
    os.system(rvCommand)
    #os.system("rvpush py-eval 'rv.commands.stop()'")


def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "create a contactSheet for sequence")
    #shot argument
    parser.add_argument('sequences', type=str,nargs='*', help='seq number(s) you can put multiple sequence separated by a space (i.e: 10 20 200 40)')
    parser.add_argument('--x','-x', action='store_true', help='create the contactSheet without opening the GUI if this arguments is not present or no sequences are pass, the GUI will open')
    parser.add_argument('--t','-t',type=str, help='task name: '+ str(_TASKLIST_) + '\nIf no task is chosen, the default is: comp_precomp')
    parser.add_argument('--f','-f',type=str,help='format for the output image the supported format are: '+str(_OUTPUTFORMAT_) + ' with the default being jpg ')
    parser.add_argument('--nd','-nd', action='store_false', help='do not display metadata')
    parser.add_argument('--s','-s',type=str, help='output image size the argument are "full", "half", "quarter"\nIf no scale is chosen, the default is: quarter')
    parser.add_argument('--pf','-pf', action='store_true', help='output image in print format (A4,A3)')
    parser.add_argument('--ncol','-ncol', type=int, help='number of column for the contactSheet(do not apply in print format)')
    parser.add_argument('--nrv','-nrv', action='store_false', help=' do not display the resulting image(s) in rv')
    args = parser.parse_args()
    seqNumber = args.sequences
    formatedSeq=[]
    if seqNumber is not None and len(seqNumber)>0:
        for seq in seqNumber:
            if seq.find('s') < 0:
                seq = "s"+ seq.zfill(4)
                formatedSeq.append(seq)
    noGui = args.x
    task =args.t
    if task is not None:
        if task not in _TASKLIST_:
            task = 'compo_comp'
    else:
        task = 'compo_comp'
    format = args.f
    if format is not None:
        if format not in _OUTPUTFORMAT_:
            format = 'jpg'
    else:
        format = 'jpg'

    noMeta = args.nd

    outImSize = args.s
    if outImSize is not None:
        if outImSize not in _OUTSIZE_:
            outImSize = 'quarter'
    else:
        outImSize = 'quarter'

    printFormat = args.pf

    nrow = args.ncol
    if nrow is not None:
        if nrow < 3:
            nrow = 5
    else:
        nrow = 5

    nrv = args.nrv

    return formatedSeq, noGui, task, format, noMeta, outImSize, printFormat, nrow,nrv

def main():
    sequences, noGui, task, format,noMeta,outImSize,printFormat, nrow,nrv  = get_args()
    imageList = []
    for seq in sequences:
        shotList = findShotsInSequence(seq)
        res = findShots(task,seq,shotList)
        imageList.append(contactSheet(task, seq, res, format, scale=outImSize, printFormat=printFormat, nrow=nrow,shotgunData=noMeta))
    if nrv:
        print 'serving in rv'
        playInRv(imageList)
    # seq = 's1160'
    # task = 'light_prelight'
    # shotList = findShotsInSequence(seq)
    # res = findShots(task,seq,shotList)
    # contactSheet(task,seq,res,'jpg',scale='quarter',printFormat = False,nrow=10)
    # sequences = findAllSequence()
    # print len(sequences)/8.0
    #for item in range(sequences):


if __name__ == '__main__':
    main()