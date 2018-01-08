#!/usr/bin/env python
# coding:utf-8
""":mod:`nukeContactSheet_v002` -- dummy module
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
import os, pprint, errno, argparse, sys

_USER_ = os.environ['USER']
_OUTPATH_ ="/s/prods/captain/_sandbox/" + _USER_ +"/ContactSheet"

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg
import nuke
import nuke.rotopaint as rp


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

#main call to SG api extract information from published files
def findShots(selecFilter={}, taskname='compo_precomp', seq='p00300', shotList=['Not']):
    if shotList[0] == 'Not':
        filterShotlist = ['entity', 'is_not', None]
    else:
        filterShotlist = ['entity.Shot.code', 'not_in',shotList]
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['task', 'name_is', taskname],
        ['entity', 'is_not', None],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.sg_sequence','name_is', seq],
        selecFilter,
        filterShotlist
    ]

    res = {}
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'version_number', 'path', 'published_file_type', 'entity.Shot.sg_cut_in','entity.Shot.sg_cut_out','task'], order=[{'field_name':'created_at','direction':'desc'}]):

        entityName = v['entity']['name']
        if not entityName in res:
            res[entityName] = v
            res[entityName]['imgFormat'] = '.'+ v['path']['content_type'][v['path']['content_type'].find("/")+1:]

    return res

def getAvrageColor(frameNumber=[101,125,150], frame = '/s/prods/captain/sequences/s0300/s0300_p00480/compo/compo_precomp/publish/images/generic/v012/s0300_p00480-s0300_p00480-base-compo_precomp-v012.'):
    nodeList = []
    numberOfFrame = len(frameNumber)
    frameNumber = sorted(frameNumber)
    appendClipNode = nuke.nodes.AppendClip(firstFrame=frameNumber[0])
    nodeList.append(appendClipNode)
    for i in range(numberOfFrame):
        readFile = frame + str(frameNumber[i]).zfill(4)+'.exr'
        readNode = nuke.nodes.Read(file =readFile)
        appendClipNode.setInput(i,readNode)
        nodeList.append(readNode)
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

def isFrameGood(fileIn = "/s/prods/captain/_sandbox/duda/images/sRGBtoSpi_ColorCheckerMikrosWrongColor.exr",dirIn = "/tmp"):
    fileOut = fileIn
    dirFiles = sorted(os.listdir(dirIn))
    incr = 0
    dirIn +="/"
    #check if the file exist
    if not os.path.isfile(fileOut):
        #if not get all the files in order
        #dirFiles = sorted(os.listdir(dirIn))
        #incr = 0
        #check which frame is the closet from the file wanted
        while fileOut > (dirIn + dirFiles[incr]):
            incr += 1
            if incr > len(dirFiles)-1:
                incr -= 1
                if incr < 0:
                    incr = 0
                break
    #extract the number from the frame
        fileOut = dirIn + dirFiles[incr]
    numberOut = int(fileOut[fileOut.find('.')+1:fileOut.rfind('.')])
    return { 'filePath':fileOut, 'frameNumber': numberOut}

#check if directory exist and return the proper path for the file in the writes nodes
def checkDir(path = "/tmp", seq = "s1300"):
    if os.path.isdir(path):
        path += "/" + seq
        if not os.path.isdir(path):
            os.mkdir(path)
        if not os.path.isdir(path + "/JPG"):
            os.mkdir(path + "/JPG")
        if not os.path.isdir(path + "/EXR"):
            os.mkdir(path + "/EXR")
        if not os.path.isdir(path + "/HD"):
            os.mkdir(path + "/HD")
        if not os.path.isdir(path + "/Movie"):
            os.mkdir(path + "/Movie")
    else:
        os.makedirs(path)
        path += "/" + seq
        os.mkdir(path)
        os.mkdir(path + "/JPG")
        os.mkdir(path + "/EXR")
        os.mkdir(path + "/HD")
        os.mkdir(path + "/Movie")
    return {"JPG": path+'/'+seq+"/JPG/"+seq+".jpg","EXR": path+'/'+seq+"/EXR/"+seq+".exr","HD": path+'/'+seq+"/HD/"+seq+"HD.jpg","Movie": path+'/'+seq+"/Movie/"+seq+".mov"}


def createContactSheetAllSequence(shotFrame = 'start',nbColumns = 6,seq ="s0300",taskname='compo_precomp',lightOnly = False):
    #find the shot with exr file(part of lighting step)
    res = findShots(selecFilter=exrFilter,seq=seq,taskname=taskname)
    #if user just want to see the anim in the contact sheet
    if not lightOnly:
        lightingShotFound = []
        for shot in res.keys():
            lightingShotFound.append(shot)
        resAnim = findShots(selecFilter=animFilter,seq=seq,taskname='anim_main',shotList=lightingShotFound)
        resAnim.update(res)
        res = resAnim

    shotPath={}

    #find the directory where to put the output files
    fileOutPath = checkDir(path = _OUTPATH_, seq = seq)

    for entityName in res.keys():
        #add an entry with the shot number
        shotPath[entityName]={}
        print "\n" + entityName
        #store the name of the file without extension as well as the directory name
        rootFrame = res[entityName]['path']['local_path'][:res[entityName]['path']['local_path'].find('%04d')]
        rootDir = rootFrame[:rootFrame.rfind("/")]
        #store the image file format
        shotPath[entityName]['imageFormat'] = res[entityName]['imgFormat']
        #if the first frame is chosen for contactsheet
        if shotFrame == 'mid':
            #take the cut_in frame from shotgun data
            frame = str(int((res[entityName]['entity.Shot.sg_cut_in'] + res[entityName]['entity.Shot.sg_cut_out'])/2)).zfill(4)+shotPath[entityName]['imageFormat']
            tmpFullFile = rootFrame+frame
            #check if the frame exist if not go in the directory and chose the closest frame to the chosen frame in the directory
            fullFile = isFrameGood(fileIn = tmpFullFile,dirIn = rootDir)["filePath"]
            #put the chosen frame in the dictionary to be chosen as a contactsheet frame
            shotPath[entityName]['frame']=fullFile
        elif shotFrame == 'end':
            frame = str(res[entityName]['entity.Shot.sg_cut_out']).zfill(4)+shotPath[entityName]['imageFormat']
            tmpFullFile = rootFrame+frame
            #check if the frame exist if not go in the directory and chose the closest frame to the chosen frame in the directory
            fullFile = isFrameGood(fileIn = tmpFullFile,dirIn = rootDir)["filePath"]
            #put the chosen frame in the dictionary to be chosen as a contactsheet frame
            shotPath[entityName]['frame']=fullFile
        else:
            frame = str(res[entityName]['entity.Shot.sg_cut_in']).zfill(4)+shotPath[entityName]['imageFormat']
            tmpFullFile = rootFrame+frame
            #check if the frame exist if not go in the directory and chose the closest frame to the chosen frame in the directory
            fullFile = isFrameGood(fileIn = tmpFullFile,dirIn = rootDir)["filePath"]
            #put the chosen frame in the dictionary to be chosen as a contactsheet frame
            shotPath[entityName]['frame']=fullFile

        shotPath[entityName]['allFrames']= res[entityName]['path']['local_path'][:res[entityName]['path']['local_path'].find('%04d')]+"""####"""+shotPath[entityName]['imageFormat']
        shotPath[entityName]['rootFrame']= rootFrame
        shotPath[entityName]['version'] = str(res[entityName]['version_number'])
        shotPath[entityName]['task'] = res[entityName]['task']['name']

        #use the cut_in from shotgun or if the corresponding frame doesn't exist use the closest number
        cut_in = res[entityName]['entity.Shot.sg_cut_in']
        checkFrame = shotPath[entityName]['rootFrame']+str(cut_in).zfill(4)+shotPath[entityName]['imageFormat']
        NewcutIn = isFrameGood(fileIn = checkFrame,dirIn = rootDir)["frameNumber"]
        shotPath[entityName]['in']= NewcutIn

        #find the cut_out from shotgun or if the corresponding frame doesn't exist use the closest number
        cut_out = res[entityName]['entity.Shot.sg_cut_out']
        checkFrame = shotPath[entityName]['rootFrame']+str(cut_out).zfill(4)+shotPath[entityName]['imageFormat']
        NewcutOut = isFrameGood(fileIn = checkFrame,dirIn = rootDir)["frameNumber"]
        shotPath[entityName]['out']= NewcutOut

        #determine the mid point of the shot or if the corresponding frame doesn't exist use the closest number
        cut_mid = int((res[entityName]['entity.Shot.sg_cut_in'] + res[entityName]['entity.Shot.sg_cut_out'])/2)
        checkFrame = shotPath[entityName]['rootFrame']+str(cut_mid).zfill(4)+shotPath[entityName]['imageFormat']
        NewcutMid = isFrameGood(fileIn = checkFrame,dirIn = rootDir)["frameNumber"]
        shotPath[entityName]['mid']= NewcutMid

        shotPath[entityName]['averageFrame'] = [NewcutIn,NewcutMid,NewcutOut]
        print shotPath[entityName]['averageFrame']

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
    colorConvertNode = a = nuke.nodes.OCIOColorSpace(in_colorspace="linear",out_colorspace="vd")
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
        #get the average color for the shot for the exr image
        if shotPath[path]['imageFormat'] == '.exr':
            averageColor =getAvrageColor(frameNumber=frameNumber, frame=shotPath[path]['rootFrame'])
            totalAvColor[0]+=averageColor[0]
            totalAvColor[1]+=averageColor[1]
            totalAvColor[2]+=averageColor[2]
        #else if it's coming from anim_main just put black
        else:
            averageColor = [0,0,0]
        readNode = nuke.nodes.Read(file = shotPath[path]['frame'],first=cutIn,last=cutOut, name = "read_"+path)
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

        reformatNode = nuke.nodes.Reformat(type = "to box",box_fixed = True,resize = "none",box_width = 1920, box_height = 1170,black_outside = True,name = "reformat_" + path)
        reformatNode.setInput(0,readNode)
        reformatNode.setXYpos(Xpos, Ypos +90)
        transformNode = nuke.nodes.Transform(name = "transform_"+path)
        transformNode['translate'].setValue([0,-45])
        transformNode.setXYpos(Xpos, Ypos +120)
        transformNode.setInput(0,reformatNode)
        textNode = nuke.nodes.Text2(message=path + "    Task: " + shotPath[path]['task'] + "    Version: " + shotPath[path]['version'],cliptype="no clip",global_font_scale=.8,name="title"+path)
        textNode["box"].setValue([25,1050,1920,1160])
        textNode["font"].setValue('Captain Underpants', 'Regular')
        textNode.setInput(0,transformNode)
        textNode.setXYpos(Xpos, Ypos +150)
        contactSheetNode.setInput(input,textNode)
        input+=1
        Xpos += 125
        shiftX += sizeSquare

    #set the average color for the sequence in the constant node
    avCol = [totalAvColor[0]/nbShot,totalAvColor[1]/nbShot,totalAvColor[2]/nbShot,1]
    constantNode['color'].setValue(avCol)

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
    writeHDNode.setXYpos(centerX + 400, 1050)
    writeMovieNode.setXYpos(centerX + 600, 1050)


#createContactSheetAllSequence('mid',nbColumns = 6,seq ="s0300",taskname='compo_precomp',lightOnly = True)