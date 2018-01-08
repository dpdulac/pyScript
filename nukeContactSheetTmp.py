#!/usr/bin/env python
# coding:utf-8
""":mod:`testSG` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2016, Mikros Image"

from sgtkLib import tkutil, tkm
import os, pprint, errno, argparse, sys, math

_USER_ = os.environ['USER']
_OUTPATH_ ="/s/prods/captain/_sandbox/" + _USER_ +"/ContactSheet"
_NBSHOTMAX_ = 10000
_STARTCOMPFRAME_ = 101

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg



animFilter = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'PlayblastImageSequence'],
        ]
    }

exrFilter = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'CompoImageSequence'],
            ['published_file_type', 'name_is', 'GenericImageSequence'],
        ]
        }

DWAFilter = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }

compoMovieFilter = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'CompoMovie']
        ]
        }

def findStatusTask(taskname = 'compo_precomp',shotList = ['s1300_p00220','s1300_p00200','s1300_p00880','s1300_p00340'],seq='s1300'):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['content', 'is', taskname],
        ['entity', 'is_not', None],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.sg_sequence','name_is', seq],
        ['entity.Shot.code', 'in',shotList]
    ]
    res={}
    for v in sg.find('Task', filters, ['code','entity','sg_status_artistique']):
        entityName = v['entity']['name']
        if not entityName in res:
            res[entityName]= v['sg_status_artistique']
    return res

def findShotsInSequence(seq='1300', doMasters=False):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['code','is',seq]
    ]
    res = {}
    seqShots =[]
    seqMasters = []
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','shots','sg_masters']):
        if not 'Shots' in res:
            tmp = v['shots']
            for item in tmp:
                seqShots.append(item['name'])
            res['Shots'] = seqShots
    if doMasters:
        #extract the masters from the sequence
        tmp = v['sg_masters']
        for item in tmp:
            if item['name'].find('_k')>0:
                    seqMasters.append(item['name'])
        #if masters exist
        if len(seqMasters) > 0:
            filtersMasters = [
                ['project', 'is', {'type':'Project', 'id':project.id}],
                ['code', 'in',seqMasters]
            ]

            masters = {}
            for v in sg.find('CustomEntity02', filtersMasters, ['sg_shots_lighting','code'], order=[{'field_name':'version_number','direction':'desc'}]):
                masterName = v['code']
                if masterName.find('_m')>= 0:
                    print masterName+ ': layout master will not be used'
                else:
                    masters[masterName]={}
                    masterShot = masterName.replace('_k','_p0')
                    linkShots = []
                    for i in range(len(v['sg_shots_lighting'])):
                        if v['sg_shots_lighting'][i]['name'] != masterShot:
                            linkShots.append(v['sg_shots_lighting'][i]['name'])
                    masters[masterName]['masterShot'] = masterShot
                    masters[masterName]['subShots'] = linkShots
                    linkShots.insert(0,masterShot)
                    masters[masterName]['sortedShot'] = linkShots
            #if the master is not in res take it out of the masters dict
            for key in masters.keys():
                if not key in seqShots:
                    print 'master: '+key + ' not ready'
                    masters.pop(key,None)
            if not 'Master' in res:
                res['Master']=masters
        else:
            raise Exception('no Masters')
    return res

def findShots(selecFilter={}, taskname='compo_precomp', seq='s1300', shotList=[]):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'in',shotList],
        ['task', 'name_is', taskname],
        ['entity', 'is_not', None],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.sg_sequence','name_is', seq],
        selecFilter,
    ]

    res = {}
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'version_number', 'path', 'published_file_type', 'entity.Shot.sg_cut_in','entity.Shot.sg_cut_out','task','entity.Shot.sg_sequence'], order=[{'field_name':'created_at','direction':'desc'}]):

        entityName = v['entity']['name']
        if not entityName in res:
            res[entityName] = v
            contentType = v['path']['content_type']
            if contentType is None:
                imgFormat = v['path']['local_path'][v['path']['local_path'].rfind('.')+1:]
                res[entityName]['imgFormat'] = imgFormat
            else:
                imgFormat = v['path']['content_type'][v['path']['content_type'].find("/")+1:]
                if imgFormat == 'quicktime':
                    res[entityName]['imgFormat'] = imgFormat
                else:
                    res[entityName]['imgFormat'] = '.'+ imgFormat
    return res

def createShotsInSeq(taskname='compo_precomp', seq='s1300',lightOnly = False,doMasters=False,masterName='',shotList=[], clampShot=False,useLightDNX=False):
    seqDict = findShotsInSequence(seq=seq,doMasters=doMasters)
    shotInSeq=[]
    if doMasters:
        if masterName == '':
            raise Exception("no master name given")
        else:
            shotInSeq =seqDict['Master'][masterName]['sortedShot']
    #case where a list of shot is given
    elif len(shotList) > 0:
        strShotList =[]
        #convert format from int to Mikros shot format if the list is a list of tupple it take the first element to transform it
        for item in shotList:
            if item.__class__.__name__ == 'tuple':
                strShot = seq + '_p'+ str(item[0]).zfill(5)
                strShotList.append(strShot)
            elif item.__class__.__name__ == 'int':
                strShot = seq + '_p'+ str(item).zfill(5)
                strShotList.append(strShot)
            else:
                raise Exception('the type in the list need to be a tuple or an int')
        shotInSeq = sorted(strShotList)
    else:
        #get the list of shots from the sequence
        shotInSeq = seqDict['Shots']
    exrShotsFound = []
    animShotsFound = []
    if useLightDNX:
        lightFilter=compoMovieFilter
    else:
        lightFilter = exrFilter
    #get the shots coming from light step
    res = findShots(selecFilter=lightFilter, taskname=taskname, seq=seq, shotList =shotInSeq)
    #add the step lightint to dictionary
    for key in res.keys():
        res[key]['step'] = 'lighting'
    if not lightOnly:
        for key in sorted(res.keys()):
            exrShotsFound.append(key)
        #infer the list of shot not found as a exrFile in the whole list of shot for this sequence
        animShotList =  sorted(list(set(shotInSeq).symmetric_difference(set(exrShotsFound))))
        #get the shot coming from anim_main
        resAnim = findShots(selecFilter=animFilter, taskname='anim_main', seq=seq, shotList =animShotList)
        for key in sorted(resAnim.keys()):
            animShotsFound.append(key)
            resAnim[key]['step'] = 'anim'
        #add to res the shot find in anim_main
        res = dict(res, **resAnim)
        #infer the shot not found in anim_main
        DWAShotList = sorted(list(set(animShotList).symmetric_difference(set(animShotsFound))))
        if len(DWAShotList) is not 0:
            resDWA = findShots(selecFilter=DWAFilter, taskname='editing_edt', seq=seq, shotList =DWAShotList)
            for key in resDWA.keys():
                resDWA[key]['step'] = 'anim'
            res = dict(res, **resDWA)

    shotListInSeq = []
    for key in res.keys():
        shotListInSeq.append(key)
    status = findStatusTask(taskname = taskname,shotList = shotListInSeq,seq=seq)
    for key in sorted(res.keys()):
        res[key]['status']= status[key]
    #if the shot number greater than _NBSHOTMAX_ don't put in the contactSheet(i.e in CU shot greater than 10000 are "special shots"
    if clampShot:
        for key in res.keys():
            if int(key[key.rfind('_p')+2:]) > _NBSHOTMAX_:
                res.pop(key)
    return res


def createShotPathDict(res = {},shotFrame = 'start',shotList=[]):
    shotPath = {}
    shotInShotList = {}
    frameInShot = False
    #if the user input a tuple (shot,frame) to precise a particular frame for a shot create a dictionary
    if (shotList)>0:
        for item in shotList:
            if item.__class__.__name__ == 'tuple' and item[0].__class__.__name__ == 'int':
                strShot = seq + '_p'+ str(item[0]).zfill(5)
                shotInShotList[strShot] = item[1]
                frameInShot = True
    for entityName in res.keys():
        rootFrame=''
        #add an entry with the shot number
        shotPath[entityName]={}
        print "\n" + entityName

        #if the media is quicktime the frame range start at 0 instead of 101
        imageFormat = res[entityName]['imgFormat']
        if imageFormat == 'quicktime' or imageFormat == 'mkv':
            #if the first frame is chosen for contactsheet
            if shotFrame == 'mid':
                #take the cut_in frame from shotgun data
                frame = int((res[entityName]['entity.Shot.sg_cut_in'] + res[entityName]['entity.Shot.sg_cut_out'])/2)
                shotPath[entityName]['frame']=frame - _STARTCOMPFRAME_ +1
            elif shotFrame == 'end':
                frame = int(res[entityName]['entity.Shot.sg_cut_out'])
                shotPath[entityName]['frame']=frame -_STARTCOMPFRAME_ +1
            else:
                frame = int(res[entityName]['entity.Shot.sg_cut_in'])
                #put the chosen frame in the dictionary to be chosen as a contactsheet frame
                shotPath[entityName]['frame']=1
            #use the cut_in from shotgun or if the corresponding frame doesn't exist use the closest number
            NewcutIn = 1
            shotPath[entityName]['in']= NewcutIn

            #find the cut_out from shotgun or if the corresponding frame doesn't exist use the closest number
            NewcutOut = res[entityName]['entity.Shot.sg_cut_out']-100
            shotPath[entityName]['out']= NewcutOut

            #determine the mid point of the shot or if the corresponding frame doesn't exist use the closest number
            NewcutMid = int((res[entityName]['entity.Shot.sg_cut_in'] + res[entityName]['entity.Shot.sg_cut_out'])/2) -100
            shotPath[entityName]['mid']= NewcutMid

        else:
            #if the first frame is chosen for contactsheet
            if shotFrame == 'mid':
                #take the cut_in frame from shotgun data
                frame = int((res[entityName]['entity.Shot.sg_cut_in'] + res[entityName]['entity.Shot.sg_cut_out'])/2)
                shotPath[entityName]['frame']=frame
            elif shotFrame == 'end':
                frame = int(res[entityName]['entity.Shot.sg_cut_out'])
                shotPath[entityName]['frame']=frame
            else:
                frame = int(res[entityName]['entity.Shot.sg_cut_in'])
                #put the chosen frame in the dictionary to be chosen as a contactsheet frame
                shotPath[entityName]['frame']=frame
            #use the cut_in from shotgun or if the corresponding frame doesn't exist use the closest number
            NewcutIn = res[entityName]['entity.Shot.sg_cut_in']
            shotPath[entityName]['in']= NewcutIn

            #find the cut_out from shotgun or if the corresponding frame doesn't exist use the closest number
            NewcutOut = res[entityName]['entity.Shot.sg_cut_out']
            shotPath[entityName]['out']= NewcutOut

            #determine the mid point of the shot or if the corresponding frame doesn't exist use the closest number
            NewcutMid = int((res[entityName]['entity.Shot.sg_cut_in'] + res[entityName]['entity.Shot.sg_cut_out'])/2)
            shotPath[entityName]['mid']= NewcutMid

        if frameInShot:
            if entityName in (shotInShotList.keys()):
                if res[entityName]['imgFormat'] == 'quicktime' or res[entityName]['imgFormat'] == 'mkv':
                    shotPath[entityName]['frame'] = shotInShotList[entityName] -100
                else:
                    shotPath[entityName]['frame'] = shotInShotList[entityName]

        shotPath[entityName]['inputFile']= res[entityName]['path']['local_path']
        shotPath[entityName]['version'] = str(res[entityName]['version_number'])
        shotPath[entityName]['task'] = res[entityName]['task']['name']
        shotPath[entityName]['status']= res[entityName]['status']
        shotPath[entityName]['sequence']= res[entityName]['entity.Shot.sg_sequence']['name']
        shotPath[entityName]['imageFormat'] = res[entityName]['imgFormat']
        shotPath[entityName]['averageFrame'] = [NewcutIn,NewcutMid,NewcutOut]
        shotPath[entityName]['step']= res[entityName]['step']

    return shotPath


#######################################################################file checkink/creation #####################################################################################
def checkDir(path = '/tmp'):
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def getNewVersionNumber(path = '/tmp', type = 'jpg'):
    checkDir(path)
    listDir = os.listdir(path)
    movieFile = []
    #only keep file with pattern "type"
    for i in listDir:
        if i.rfind('_v') == 0 and os.path.isdir(path+i):
            movieFile.append(i)
    #if no file found return 0
    if len(movieFile) == 0:
        return '_v001'
    #else return the last movie created
    else:
        movieFile.sort(reverse = True)
        lastFile = movieFile[0]
        start = lastFile.find('_v')+2
        #end = lastFile.rfind('.')
        newNumber = int(lastFile[start:]) +1
        return "_v"+ str(newNumber).zfill(3)

#check if directory exist and return the proper path for the file in the writes nodes
def createFileOutput(path = "/tmp", seq = "s1300", masterName='',createMasterDir=False,createMasterGlobSeq=False):
    #createMasterDir and createMasterGlobSeq cannot be True at the same time
    if createMasterDir and createMasterGlobSeq:
        if masterName is not '':
            createMasterGlobSeq=False
        else:
            createMasterDir=False

    if createMasterDir:
        JPGpath = path+'/'+seq+"/Masters/"+masterName+"/JPG/"
        version = getNewVersionNumber(path=JPGpath,type = 'jpg')
        JPGpath = path+'/'+seq+"/Masters/"+masterName+"/JPG/"+version+"/"
        checkDir(JPGpath)
        JPG = JPGpath+masterName+version+".####.jpg"

        EXRpath = path+'/'+seq+"/Masters/"+masterName+"/EXR/"
        version = getNewVersionNumber(path=EXRpath,type = 'exr')
        EXRpath = path+'/'+seq+"/Masters/"+masterName+"/EXR/"+version+"/"
        checkDir(EXRpath)
        EXR = EXRpath+masterName+version+".####.exr"

        HDpath = path+'/'+seq+"/Masters/"+masterName+"/HD/"
        version = getNewVersionNumber(path=HDpath,type = 'jpg')
        HDpath = path+'/'+seq+"/Masters/"+masterName+"/HD/"+version+"/"
        checkDir(HDpath)
        HD = HDpath+masterName+version+".####.jpg"

        MoviePath = path+'/'+seq+"/Masters/"+masterName+"/Movie/"
        version = getNewVersionNumber(path=MoviePath,type = 'mov')
        MoviePath = path+'/'+seq+"/Masters/"+masterName+"/Movie/"+version+"/"
        checkDir(MoviePath)
        Movie = MoviePath+masterName+version+".mov"

    if createMasterGlobSeq:
        JPGpath = path+'/'+seq+"/Masters/Global/JPG/"
        version = getNewVersionNumber(path=JPGpath,type = 'jpg')
        JPGpath = path+'/'+seq+"/Masters/Global/JPG/"+version+"/"
        checkDir(JPGpath)
        JPG = JPGpath+seq+ version+".####.jpg"

        EXRpath = path+'/'+seq+"/Masters/Global/EXR/"
        version = getNewVersionNumber(path=EXRpath,type = 'exr')
        EXRpath = path+'/'+seq+"/Masters/Global/EXR/"+version+"/"
        checkDir(EXRpath)
        EXR = EXRpath+seq+version+".####.exr"

        HDpath = path+'/'+seq+"/Masters/Global/HD/"
        version = getNewVersionNumber(path=HDpath,type = 'jpg')
        HDpath = path+'/'+seq+"/Masters/Global/HD/"+version+"/"
        checkDir(HDpath)
        HD = HDpath+seq+ "HD" +version+".####.jpg"

        MoviePath = path+'/'+seq+"/Masters/Global/Movie/"
        version = getNewVersionNumber(path=MoviePath,type = 'mov')
        MoviePath = path+'/'+seq+"/Masters/Global/Movie/"+version+"/"
        checkDir(MoviePath)
        Movie = MoviePath+seq+ version+".mov"
    else:
        JPGpath = path+'/'+seq+"/FullContactSheet/JPG/"
        version = getNewVersionNumber(path=JPGpath,type = 'jpg')
        JPGpath = path+'/'+seq+"/FullContactSheet/JPG/"+version+"/"
        checkDir(JPGpath)
        JPG = JPGpath+seq+ version+".####.jpg"

        EXRpath = path+'/'+seq+"/FullContactSheet/EXR/"
        version = getNewVersionNumber(path=EXRpath,type = 'exr')
        EXRpath = path+'/'+seq+"/FullContactSheet/EXR/"+version+"/"
        checkDir(EXRpath)
        EXR = EXRpath+seq+version+".####.exr"

        HDpath = path+'/'+seq+"/FullContactSheet/HD/"
        version = getNewVersionNumber(path=HDpath,type = 'jpg')
        HDpath = path+'/'+seq+"/FullContactSheet/HD/"+version+"/"
        checkDir(HDpath)
        HD = HDpath+seq+ "HD" +version+".####.jpg"

        MoviePath = path+'/'+seq+"/FullContactSheet/Movie/"
        version = getNewVersionNumber(path=MoviePath,type = 'mov')
        MoviePath = path+'/'+seq+"/FullContactSheet/Movie/"+version+"/"
        checkDir(MoviePath)
        Movie = MoviePath+seq+ version+".mov"


    return {"JPG": JPG,"EXR": EXR,"HD": HD,"Movie": Movie}

def getAvrageColor(frameNumber=[101,125,150], frame = '/s/prods/captain/sequences/s0300/s0300_p00480/compo/compo_precomp/publish/images/generic/v012/s0300_p00480-s0300_p00480-base-compo_precomp-v012.'):
    nodeList = []
    numberOfFrame = len(frameNumber)
    frameNumber = sorted(frameNumber)
    appendClipNode = nuke.nodes.AppendClip(firstFrame=frameNumber[0])
    nodeList.append(appendClipNode)
    if frame.find('.mkv') > 0:
        nuke.frame(1)
        readNode = nuke.nodes.Read(file =frame,on_error ='nearestframe',first=1,last=frameNumber[-1])
        print frameNumber
        frameNumber[-1]=int(readNode['last'].getValue())
        print frameNumber, "\n"
    else:
        readNode = nuke.nodes.Read(file =frame,on_error ='nearestframe',first=frameNumber[0],last=frameNumber[-1])
        #readNode = nuke.nodes.Read(file =frame,on_error ='nearestframe')
    nodeList.append(readNode)
    for i in range(numberOfFrame):
        frameHold = nuke.nodes.FrameHold(first_frame =frameNumber[i])
        frameHold.setInput(0,readNode)
        timeClip = nuke.nodes.TimeClip(first = 1, last = 1)
        timeClip.setInput(0,frameHold)
        appendClipNode.setInput(i,timeClip)
        nodeList.append(frameHold)
        nodeList.append(timeClip)
    curveToolNode = nuke.nodes.CurveTool(name = "CurveTool",avgframes=1)
    curveToolNode['ROI'].setValue([0,0,1968,1080])
    curveToolNode.setInput(0,appendClipNode)
    nuke.execute("CurveTool", frameNumber[0], (frameNumber[0]-1) + numberOfFrame)
    nodeList.append(curveToolNode)
    col = curveToolNode['intensitydata'].value()
    #clamp the color to a maximum 1
    for i in range(len(col)):
        if col[i] > 1:
            col[i] = 1
    for node in nodeList:
        nuke.delete(node)
    return col

def createContactSheetAllSequence(shotFrame = 'start',nbColumns = 6,seq ="s1300",taskname='compo_precomp',lightOnly = False, render=True,display = False, HDsplit=False,shotList=[],clampShot=True,useLightDNX=False):
    import nuke
    import nuke.rotopaint as rp
    rootNuke = nuke.root()
    rootNuke['format'].setValue( 'HD_1080' )
    rootNuke['first_frame'].setValue(_STARTCOMPFRAME_)
    rootNuke['last_frame'].setValue(1000)

    #find the shot with exr file(part of lighting step)
    res = createShotsInSeq(taskname=taskname, seq=seq,lightOnly = lightOnly,doMasters=False,shotList=shotList,clampShot=clampShot,useLightDNX=useLightDNX)

    #create the main dict
    shotPath= createShotPathDict(res=res,shotFrame=shotFrame)

    #find the directory where to put the output files
    fileOutPath = createFileOutput(path = _OUTPATH_, seq = seq)

    #number of shot in exr for averaging color
    exrShot = 0
    for shot in res:
        if shotPath[shot]['step'] == 'lighting':
            exrShot+=1
    #number of shot in sequence
    nbShot = len(shotPath.keys())
    #height of contact sheet
    heightContactSheet = (int(nbShot/nbColumns)+1)*1170
    #width of contactsheet
    widthContactSheet = 1920*nbColumns
    #average color for the shot
    averageColor=[]
    #average color for sequence
    totalAvColor=[0.0,0.0,0.0,1]
    # X/Y pos for nodes
    Xpos = 0
    Ypos = 0
    # size of the color swath in the roto node
    sizeSquare = widthContactSheet/nbShot
    if sizeSquare > 500:
        sizeSquare = 500
    # shift for the color swatch
    shiftX = 0
    # input of the contactsheet
    input = 0
    #max and min cut for the sequence
    maxCutOut = 0
    minCutIn = 101

    #variable for HD presentation (i.e contactSheet separated if nbShots > 30
    nbContactSheetHD = 0
    contactSheetHD= []
    nbRowHD=4
    nbColumnsHD = 6
    colTimeRow = nbColumnsHD * nbRowHD
    heightContactSheetHD = nbRowHD * 1170
    widthContactSheetHD = nbColumnsHD * 1920
    if nbShot > colTimeRow:
        nbContactSheetHD = float(nbShot)/float(colTimeRow)
        frac, whole = math.modf(nbContactSheetHD)
        if frac > 0:
            nbContactSheetHD = int(whole + 1)
        else:
            nbContactSheetHD= int(nbContactSheetHD)


    #creation of the roto Node
    rotoNode = nuke.nodes.Roto(name = 'roto',cliptype="no clip")
    rCurves = rotoNode['curves']
    root = rCurves.rootLayer

    #creation of the contactsheet node
    contactSheetNode = nuke.nodes.ContactSheet(name="contactSheet",rows=int(nbShot/nbColumns)+1,columns=nbColumns,roworder="TopBottom",width=widthContactSheet,height=heightContactSheet, center= True,gap = 50)

    #reformat node for the contact sheet
    reformatGlobalNode = nuke.nodes.Reformat(type = "to box",box_fixed = True,resize = "none",box_width = widthContactSheet, box_height = heightContactSheet+2160,black_outside = True,name = "reformatGlobal")
    #text node displaying the sequence number
    textSeqNode = nuke.nodes.Text2(message=seq,cliptype="no clip",global_font_scale=8.5,name="title"+seq)
    textSeqNode["box"].setValue([0,0,2500,1080])
    textSeqNode["font"].setValue('Captain Underpants', 'Regular')
    textSeqNodeTransform = nuke.nodes.Transform(name = "transformSeq_"+seq)
    textSeqNodeTransform['translate'].setValue([200,heightContactSheet+900])
    textSeqNodeTransform.setInput(0,textSeqNode)
    #reformat for the roto node the height is the height of a swatch node
    reformatColAverage = nuke.nodes.Reformat(type="to box",box_fixed=True,resize="none",box_width=widthContactSheet,box_height=sizeSquare,center=False,pbb=True,name="reformatColAverage")
    #constant color for average sequence color
    constantNode = nuke.nodes.Constant(name="averageSeqColor")
    constantNodeTransform = nuke.nodes.Transform(name = "transformConst_"+seq,scale = 0.6)
    constantNodeTransform['translate'].setValue([widthContactSheet-(1920*2),heightContactSheet+1200])
    constantNodeTransform.setInput(0,constantNode)
    #import of the colorChart
    readColorChartNode = nuke.nodes.Read(file="/s/prods/captain/_sandbox/duda/images/sRGBtoSpi_ColorCheckerMikrosWrongColor.exr",name=seq+"_colorChart")
    readColorChartNodeTransform = nuke.nodes.Transform(name = "transformChart_"+seq,scale = 0.85)
    readColorChartNodeTransform['translate'].setValue([widthContactSheet-(1920),heightContactSheet+1080])
    readColorChartNodeTransform.setInput(0,readColorChartNode)

    #merge of all the nodes
    mergeNode = nuke.nodes.Merge2(inputs=[reformatGlobalNode,textSeqNodeTransform],name="merge_"+seq)
    mergeNode.setInput(3,readColorChartNodeTransform)
    mergeNode.setInput(4,reformatColAverage)
    mergeNode.setInput(5,constantNodeTransform)

    #write node
    writeFullNode = nuke.nodes.Write(name = seq + "Write", colorspace = "linear", file_type = "exr",file =fileOutPath["EXR"] )
    writeFullLutBurnNode = nuke.nodes.Write(name = seq + "WriteLutBurn", colorspace = "linear", file_type = "jpeg", _jpeg_sub_sampling = "4:2:2",file =fileOutPath["JPG"])
    writeFullLutBurnNode['_jpeg_quality'].setValue(0.75)
    writeHDNode = nuke.nodes.Write(name = seq + "WriteHD", colorspace = "linear", file_type = "jpeg", _jpeg_sub_sampling = "4:2:2",file =fileOutPath["HD"])
    writeHDNode['_jpeg_quality'].setValue(0.75)
    writeMovieNode = nuke.nodes.Write(name = seq + "WriteMovie", colorspace = "linear", file_type = "mov",file =fileOutPath["Movie"])
    colorConvertNode = nuke.nodes.OCIOColorSpace(in_colorspace="linear",out_colorspace="vd")
    reformatWriteHDNode = nuke.nodes.Reformat(type="to format",resize="fit",center=True,black_outside = True,name="reformatHD_"+seq)
    writeFullLutBurnNode.setInput(0,colorConvertNode)
    writeMovieNode.setInput(0,reformatWriteHDNode)
    colorConvertNode.setInput(0,mergeNode)
    writeFullNode.setInput(0,mergeNode)
    reformatWriteHDNode.setInput(0,colorConvertNode)
    writeHDNode.setInput(0,reformatWriteHDNode)

    for path in sorted(shotPath.keys()):
        frameNumber =[]
        cutIn, cutOut, cutMid = shotPath[path]['in'], shotPath[path]['out'],shotPath[path]['mid']
        frameNumber = shotPath[path]['averageFrame']
        textColor = [0,0,0,1]
        if cutOut > maxCutOut:
            maxCutOut = cutOut
        if cutIn < minCutIn:
            minCutIn = cutIn
        #get the average color only for the shot with exr image
        #if shotPath[path]['imageFormat'] == '.exr':
        if shotPath[path]['step'] == 'lighting':
            averageColor =getAvrageColor(frameNumber=frameNumber, frame=shotPath[path]['inputFile'])
            totalAvColor[0]+=averageColor[0]
            totalAvColor[1]+=averageColor[1]
            totalAvColor[2]+=averageColor[2]
        #else if it's coming from anim_main just put black
        else:
            averageColor = [0,0,0]
        readNode = nuke.nodes.Read(file = shotPath[path]['inputFile'],first=cutIn,last=cutOut, name = "read_"+path,on_error ='nearestframe',after='loop')
        readNode.setXYpos(Xpos, Ypos)
        width = readNode.metadata("input/width")

        shape =rp.Shape(rCurves,type='bezier')
        shape.append([shiftX,sizeSquare])
        shape.append([shiftX + sizeSquare,sizeSquare])
        shape.append([shiftX + sizeSquare,0])
        shape.append([shiftX,0])
        shape.name = 'shape_'+path
        shapeAttr = shape.getAttributes()
        shapeAttr.set('r',averageColor[0])
        shapeAttr.set('g',averageColor[1])
        shapeAttr.set('b',averageColor[2])
        root.append(shape)

        frameHoldNode = nuke.nodes.FrameHold(name="frameHold_"+path,first_frame =shotPath[path]['frame'])
        frameHoldNode.setInput(0,readNode)
        frameHoldNode.setXYpos(Xpos,Ypos +90)
        reformatNode = nuke.nodes.Reformat(type = "to box",box_fixed = True,resize = "none",box_width = 1920, box_height = 1170,black_outside = True,name = "reformat_" + path)
        reformatNode.setInput(0,frameHoldNode)
        reformatNode.setXYpos(Xpos, Ypos +120)
        transformNode = nuke.nodes.Transform(name = "transform_"+path)
        transformNode['translate'].setValue([0,-45])
        transformNode.setXYpos(Xpos, Ypos +150)
        transformNode.setInput(0,reformatNode)
        if shotPath[path]['step'] == 'lighting':
            if shotPath[path]['status'] == 'cmpt':
                textColor = [0,1,0,1]
            else:
                textColor = [1,0,0,1]
        textNode = nuke.nodes.Text2(message=path + "    Task: " + shotPath[path]['task'] + "    Version: " + shotPath[path]['version']+'     Frame: '+ str(shotPath[path]['frame']),cliptype="no clip",global_font_scale=.6,name="title"+path)
        textNode["box"].setValue([25,1050,1920,1160])
        #textNode['color'].setValue(textColor)
        textNode["font"].setValue('Captain Underpants', 'Regular')
        textNode.setInput(0,transformNode)
        textNode.setXYpos(Xpos, Ypos +180)

        statusTextNode = nuke.nodes.Text2(message='g',cliptype="no clip",global_font_scale=.6,name="title"+path)
        statusTextNode["box"].setValue([1836.5,1091.5,1897.5,1152.5])
        statusTextNode['color'].setValue(textColor)
        statusTextNode["font"].setValue('Webdings', 'Regular')
        statusTextNode.setInput(0,textNode)
        statusTextNode.setXYpos(Xpos, Ypos +220)
        contactSheetNode.setInput(input,statusTextNode)
        input+=1
        Xpos += 125
        shiftX += sizeSquare

    #set the comp out frame
    #set the average color for the sequence in the constant node
    if exrShot is not 0:
        avCol = [totalAvColor[0]/exrShot,totalAvColor[1]/exrShot,totalAvColor[2]/exrShot,1]
        constantNode['color'].setValue(avCol)


    #if the user want multiple frames of contactSheet
    if HDsplit and nbShot > colTimeRow :
        inputContactSheet = 0
        contactSheetNumber = 0
        for i in range(nbContactSheetHD):
            contactSheetNodeHD = nuke.nodes.ContactSheet(name="contactSheet"+str(i),rows=nbRowHD,columns=nbColumnsHD,roworder="TopBottom",width=widthContactSheetHD,height=heightContactSheetHD, center= True,gap = 50)
            contactSheetNodeHD["hide_input"].setValue(True)
            contactSheetHD.append(contactSheetNodeHD )
        for item in sorted(shotPath.keys()):
            node = nuke.toNode('title'+item)
            contactSheetHD[contactSheetNumber].setInput(inputContactSheet,node)
            inputContactSheet += 1
            if inputContactSheet > colTimeRow:
                inputContactSheet = 0
                contactSheetNumber += 1
        appendClipNodeContactSheetHD = nuke.nodes.AppendClip(name = "appendClipNodeContactSheetHD_"+seq,firstFrame=_STARTCOMPFRAME_)
        inputContactSheet = 0
        for node in contactSheetHD:
            appendClipNodeContactSheetHD.setInput(inputContactSheet,node)
            inputContactSheet+=1

        readColorChartNodeTransformHD = nuke.nodes.Transform(name = "transformChartHD_"+seq,scale = 0.85)
        readColorChartNodeTransformHD['translate'].setValue([widthContactSheetHD-(1920),heightContactSheetHD+1080])
        readColorChartNodeTransformHD.setInput(0,readColorChartNode)

        textSeqNodeTransformHD = nuke.nodes.Transform(name = "transformSeqHD_"+seq)
        textSeqNodeTransformHD['translate'].setValue([200,heightContactSheetHD+900])
        textSeqNodeTransformHD.setInput(0,textSeqNode)

        constantNodeTransformHD = nuke.nodes.Transform(name = "transformConstHD_"+seq,scale = 0.6)
        constantNodeTransformHD['translate'].setValue([widthContactSheetHD-(1920*2),heightContactSheetHD+1200])
        constantNodeTransformHD.setInput(0,constantNode)

        reformatColAverageHD = nuke.nodes.Reformat(type="to box",box_fixed=True,resize="none",box_width=widthContactSheetHD,box_height=sizeSquare,center=False,pbb=True,name="reformatColAverageHD")
        reformatColAverageHD.setInput(0,rotoNode)

        reformatGlobalNodeHD = nuke.nodes.Reformat(type = "to box",box_fixed = True,resize = "none",box_width = widthContactSheetHD, box_height = heightContactSheetHD+2160,black_outside = True,name = "reformatGlobalHD")
        reformatGlobalNodeHD.setInput(0,appendClipNodeContactSheetHD)

        mergeNodeHD = nuke.nodes.Merge2(inputs=[reformatGlobalNodeHD,textSeqNodeTransformHD],name="merge_"+seq)
        mergeNodeHD.setInput(3,readColorChartNodeTransformHD)
        mergeNodeHD.setInput(4,reformatColAverageHD)
        mergeNodeHD.setInput(5,constantNodeTransformHD)
        #mergeNodeHD["hide_input"].setValue(True)

        pageNumberNodeHD = nuke.nodes.Text2(cliptype="no clip",global_font_scale=3,name="pageNumberHD_"+seq)
        pageNumberNodeHD.setInput(0,mergeNodeHD)
        pageNumberNodeHD["box"].setValue([9576,280,12345,890])
        pageNumberNodeHD["font"].setValue('Captain Underpants', 'Regular')
        pageNumberNodeHD["message"].setValue("Page: [python nuke.frame()-100]/"+str(nbContactSheetHD))

        colorConvertNodeHD = nuke.nodes.OCIOColorSpace(in_colorspace="linear",out_colorspace="vd")
        colorConvertNodeHD.setInput(0,pageNumberNodeHD)

        reformatWriteHDNodeHD = nuke.nodes.Reformat(type="to format",resize="fit",center=True,black_outside = True,name="reformatHD_"+seq)
        reformatWriteHDNodeHD.setInput(0,colorConvertNodeHD)
        writeHDNode = nuke.nodes.Write(name = seq + "WriteHD", colorspace = "linear", file_type = "mov",file =fileOutPath["HD"],mov64_codec='Avid DNxHD Codec',mov64_dnxhd_codec_profile='DNxHD 422 10-bit 220Mbit')
        writeHDNode.setInput(0,reformatWriteHDNodeHD)

        centerXHD = Xpos/2 -600
        shiftX = -125
        for item in contactSheetHD:
            newXPos = shiftX + abs(contactSheetHD.index(item)*shiftX)
            item.setXYpos(centerXHD+newXPos,700)
        appendClipNodeContactSheetHD.setXYpos(centerXHD,750)
        reformatColAverageHD.setXYpos(centerXHD-shiftX,750)
        reformatGlobalNodeHD.setXYpos(centerXHD,800)
        textSeqNodeTransformHD.setXYpos(centerXHD-shiftX,800)
        readColorChartNodeTransformHD.setXYpos(centerXHD+shiftX,800)
        mergeNodeHD.setXYpos(centerXHD,850)
        pageNumberNodeHD.setXYpos(centerXHD,900)
        colorConvertNodeHD.setXYpos(centerXHD,950)
        reformatWriteHDNodeHD.setXYpos(centerXHD,1000)
        writeHDNode.setXYpos(centerXHD,1050)

    #connection and position of the nodes for the comp
    centerX = Xpos/2
    reformatGlobalNode.setInput(0,contactSheetNode)
    contactSheetNode.setXYpos(centerX, 700)
    reformatColAverage.setInput(0,rotoNode)
    reformatColAverage.setXYpos((centerX)-200, 800)
    rotoNode.setXYpos((centerX)-200, 750)
    reformatGlobalNode.setXYpos(centerX, 750)
    textSeqNode.setXYpos((centerX)+200, 750)
    textSeqNodeTransform.setXYpos((centerX)+200, 800)
    readColorChartNode.setXYpos((centerX)+400, 700)
    readColorChartNodeTransform.setXYpos((centerX)+400, 800)
    constantNode.setXYpos(centerX+600, 700)
    constantNodeTransform.setXYpos((centerX)+600, 800)
    mergeNode.setXYpos(centerX, 850)
    colorConvertNode.setXYpos(centerX + 200, 950)
    writeFullNode.setXYpos(centerX, 1050)
    writeFullLutBurnNode.setXYpos(centerX + 200, 1050)
    reformatWriteHDNode.setXYpos(centerX + 400, 1000)
    if not HDsplit:
        writeHDNode.setXYpos(centerX + 400, 1050)
    writeMovieNode.setXYpos(centerX + 600, 1050)

    print type(maxCutOut)
    rootNuke['last_frame'].setValue(maxCutOut)

    #render the frame
    if render:
        nuke.execute(writeFullNode,1,1)
        nuke.execute(writeFullLutBurnNode,1,1)
        if not HDsplit or nbShot < colTimeRow:
            nuke.execute(writeHDNode,1,1)
        else:
            nuke.execute(writeHDNode,1,nbContactSheetHD)

    if display:
        HDpath = fileOutPath["HD"][:fileOutPath["HD"].find(".")]+'*'
        commandLine = "rv "+ HDpath
        os.system(commandLine)
# def main():
#     seq = 's1300'
#     res = createShotsInSeq(taskname='compo_precomp', seq=seq,lightOnly = False,doMasters=True)
#     shotPath = createShotPathDict(res = res,shotFrame = 'start')
#     #res = findShots(selecFilter=exrFilter,seq=seq,taskname=taskname)
#     #shotPath = createShotPathDict(res = res,shotFrame = 'start')
#
#     # shotList = []
#     # for key in shotPath:
#     #     shotList.append(key)
#     # status = findStatusTask(taskname = taskname,shotList = shotList,seq=seq)
#     # for key in shotPath:
#     #     shotPath[key]['status']= status[key]
#     pprint.pprint(shotPath)
#
# if __name__ == '__main__':
#     main()


#createContactSheetAllSequence('mid',nbColumns = 6,seq ="s1300",taskname='compo_precomp',lightOnly = False,HDsplit=False,render=False,shotList=[],clampShot=True,useLightDNX=False)