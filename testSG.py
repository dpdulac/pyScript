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
import os, pprint, errno, argparse, sys
from sgApi.sgApi import SgApi
import os, pprint, errno, argparse, sys, math

_USER_ = os.environ['USER']

_USER_ = os.environ['USER']
_OUTPATH_ ="/s/prods/captain/_sandbox/" + _USER_ +"/ContactSheet"

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
            if not 'Master' in res:
                res['Master']=masters
        else:
            res['Master'] = []
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

def createShotsInSeq(taskname='compo_precomp', seq='s1300',lightOnly = False,doMasters=True):
    #get the list of shots from the sequence
    shotInSeq = findShotsInSequence(seq=seq,doMasters=doMasters)['Shots']
    print shotInSeq
    exrShotsFound = []
    animShotsFound = []
    #get the shots coming from light step
    res = findShots(selecFilter=exrFilter, taskname=taskname, seq=seq, shotList =shotInSeq)
    for key in res.keys():
        res[key]['step'] = 'lighting'
    for key in sorted(res.keys()):
        exrShotsFound.append(key)
    tmpLightList =  sorted(list(set(shotInSeq).symmetric_difference(set(exrShotsFound))))
    resMovieLight = findShots(selecFilter=compoMovieFilter, taskname=taskname, seq=seq, shotList =tmpLightList)
    res = dict(res, **resMovieLight)
    #if we want all the shots (not just the one coming from Light)
    if not lightOnly:
        exrShotsFound = []
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
    shotList = []
    for key in res.keys():
        shotList.append(key)
    status = findStatusTask(taskname = taskname,shotList = shotList,seq=seq)
    for key in sorted(res.keys()):
        res[key]['status']= status[key]
    return res


def createShotPathDict(res = {},shotFrame = 'start'):
    shotPath = {}
    print"eee"
    for entityName in res.keys():
        rootFrame=''
        #add an entry with the shot number
        shotPath[entityName]={}
        print "\n" + entityName

        if res[entityName]['imgFormat'] == 'quicktime':
            #if the first frame is chosen for contactsheet
            if shotFrame == 'mid':
                #take the cut_in frame from shotgun data
                frame = int((res[entityName]['entity.Shot.sg_cut_in'] + res[entityName]['entity.Shot.sg_cut_out'])/2)
                shotPath[entityName]['frame']=frame - 100
            elif shotFrame == 'end':
                frame = int(res[entityName]['entity.Shot.sg_cut_out'])
                shotPath[entityName]['frame']=frame -100
            else:
                frame = int(res[entityName]['entity.Shot.sg_cut_in'])
                #put the chosen frame in the dictionary to be chosen as a contactsheet frame
                shotPath[entityName]['frame']=1
            #use the cut_in from shotgun or if the corresponding frame doesn't exist use the closest number
            NewcutIn = 1
            shotPath[entityName]['in']= NewcutIn

            #find the cut_out from shotgun or if the corresponding frame doesn't exist use the closest number
            NewcutOut = res[entityName]['entity.Shot.sg_cut_out']
            shotPath[entityName]['out']= NewcutOut -100

            #determine the mid point of the shot or if the corresponding frame doesn't exist use the closest number
            NewcutMid = int((res[entityName]['entity.Shot.sg_cut_in'] + res[entityName]['entity.Shot.sg_cut_out'])/2)
            shotPath[entityName]['mid']= NewcutMid -100

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


        shotPath[entityName]['inputFile']= res[entityName]['path']['local_path']
        shotPath[entityName]['version'] = str(res[entityName]['version_number'])
        shotPath[entityName]['task'] = res[entityName]['task']['name']
        #shotPath[entityName]['status']= res[entityName]['status']
        print res[entityName]['status']
        shotPath[entityName]['sequence']= res[entityName]['entity.Shot.sg_sequence']['name']
        shotPath[entityName]['imageFormat'] = res[entityName]['imgFormat']
        shotPath[entityName]['averageFrame'] = [NewcutIn,NewcutMid,NewcutOut]

    return shotPath

# def getAvrageColor(frameNumber=[101,125,150], frame = '/s/prods/captain/sequences/s0300/s0300_p00480/compo/compo_precomp/publish/images/generic/v012/s0300_p00480-s0300_p00480-base-compo_precomp-v012.'):
#     nodeList = []
#     numberOfFrame = len(frameNumber)
#     frameNumber = sorted(frameNumber)
#     appendClipNode = nuke.nodes.AppendClip(firstFrame=frameNumber[0])
#     nodeList.append(appendClipNode)
#     readNode = nuke.nodes.Read(file =frame,on_error ='nearestframe',first=frameNumber[0],last=frameNumber[-1])
#     nodeList.append(readNode)
#     for i in range(numberOfFrame):
#         frameHold = nuke.nodes.FrameHold(first_frame =frameNumber[i])
#         frameHold.setInput(0,readNode)
#         timeClip = nuke.nodes.TimeClip(first = 1, last = 1)
#         timeClip.setInput(0,frameHold)
#         appendClipNode.setInput(i,timeClip)
#         nodeList.append(frameHold)
#         nodeList.append(timeClip)
#     curveToolNode = nuke.nodes.CurveTool(name = "CurveTool",avgframes=1)
#     curveToolNode['ROI'].setValue([0,0,1968,1080])
#     curveToolNode.setInput(0,appendClipNode)
#     nuke.execute("CurveTool", frameNumber[0], (frameNumber[0]-1) + numberOfFrame)
#     nodeList.append(curveToolNode)
#     col = curveToolNode['intensitydata'].value()
#     #clamp the color to a maximum 1
#     for i in range(len(col)):
#         if col[i] > 1:
#             col[i] = 1
#     for node in nodeList:
#         nuke.delete(node)
#     return col
_USER_ = os.environ['USER']
tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg
sgA = SgApi(sgw=sgw, tk=tk, project=project)


imageFilterConfoLayout= {
        'filter_operator' : 'all',
        'filters':[
            ['tag_list', 'name_is','primary'],
            ['published_file_type', 'name_is', 'QCRmovie'],
        ]
    }

imageFilterAsset = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'TurntableMovie'],
        ]
    }

imageFilterLayoutBase = {
        'filter_operator' : 'any',
        'filters':[
            #['published_file_type', 'name_is', 'GenericMovie'],
            ['published_file_type', 'name_is', 'PlayblastMovie'],
            #['published_file_type', 'name_is', 'CompoMovie'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
            #['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }

imageFilterEditing = {
        'filter_operator' : 'any',
        'filters':[
            #['published_file_type', 'name_is', 'GenericMovie'],
            #['published_file_type', 'name_is', 'DwaMovie'],
            ['published_file_type', 'name_is', 'PlayblastMovie'],
            #['published_file_type', 'name_is', 'GenericImageSequence'],
            #['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }



def findAllSequence(all = False):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
    ]
    res = {}
    seqShots =[]
    #get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence',filters,['entity','code','description']):
        seq = v['code']
        if all:
            if not seq in res:
                res[seq] = {}
            res[seq]['description'] = v['description']
        else:
            if int(seq[seq.find('s')+1:]) <9000:
                if not seq in res:
                    res[seq] = {}
                if v['description'] != None:
                    res[seq]['description'] = v['description']
                else:
                    res[seq]['description'] = 'None'
            else:
                print 'donuts for: ' + seq
    return res

def findShots( seq='s1300', shotList=[]):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'in',shotList],
        #['entity.Shot.tag_list', 'name_contains', 'mattepainting'],
    ]

    res = {}
    for v in sg.find('PublishedFile', filters, ['code', 'entity','entity.Shot.sg_cut_order','entity.Shot.sg_frames_of_interest','entity.Shot.sg_cut_in','entity.Shot.sg_cut_out'], order=[{'field_name':'created_at','direction':'desc'}]):
        entityName = v['entity']['name']
        if v['entity.Shot.sg_cut_order'] > 0:
            if not entityName in res:
                res[entityName] ={}
                frameInterest = v['entity.Shot.sg_frames_of_interest']
                if frameInterest is not None:
                    res[entityName]['frameInterest'] = frameInterest.split(',')
                else:
                    res[entityName]['frameInterest'] = ['101']
                res[entityName]['cutIn'] = v['entity.Shot.sg_cut_in']
                res[entityName]['cutOut'] = v['entity.Shot.sg_cut_out']
                res[entityName]['cutOrder']= v['entity.Shot.sg_cut_order']
    return res

def findSingleShot(shot = 's1300_p00300', taskname = 'compo_precomp'):
    filterType = imFilter(taskname)
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['entity.Shot.code', 'is', shot],
        ['task', 'name_is', taskname],
        filterType
    ]
    res = []
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'version_number', 'path', 'published_file_type'], order=[{'field_name':'version_number','direction':'desc'}]):
        res.append(v['path']['local_path'])
    return res

def imFilter(taskname = 'compo_precomp'):
    filterDict = {'editing_edt': imageFilterEditing,
                  'layout_base': imageFilterLayoutBase,
                  'confo_layout':imageFilterConfoLayout,
                  'anim_main': imageFilterLayoutBase,
                  'model_base':imageFilterAsset,
                  'model_hi':imageFilterAsset,
                  'hair_surface':imageFilterAsset,
                  'surface_surfacing':imageFilterAsset
                  }
    return filterDict[taskname]

#get all the shot from the sequence
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
                seqShots.append(item['name'])
            res['Shots'] = sorted(seqShots)
    if dict:
        return res
    else:
        return sorted(seqShots)


def getOrder(res = {}):
    order = []
    lengthRes = len(res)
    for i in range(1,lengthRes+1):
        for key in res.keys():
            if res[key]['cutOrder'] == i:
                order.append(key)
    return order

def main():
    seq = 's0060'
    allShots = findShotsInSequence(seq=seq,dict=False)
    res = findShots( seq='s1300', shotList=allShots)
    for i in getOrder(res):
        print i
    # for key in res.keys():
    #     print key,res[key]['cutOrder']


if __name__ == '__main__':
    main()