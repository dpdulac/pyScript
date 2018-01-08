#!/usr/bin/env python
# coding:utf-8
""":mod:`confoWipe` -- dummy module
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
import time, os, argparse
tk, sgw, project = tkutil.getTk(fast=True, scriptName='duda')
sg = sgw._sg



#get the arg from user
def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "create a wipe compare for al sequence or selected shots")
    #shot argument
    parser.add_argument('--sq','-sq', type=str, help='seq number')
    parser.add_argument('--p','-p', nargs = '*', dest = 'shots', type=str, help='shot number')
    parser.add_argument('--cf','-cf', action='store_true', help='confo_layout mode')
    parser.add_argument('--ca','-ca', action='store_true', help='confo_anim mode')
    args = parser.parse_args()
    shotNumber = args.shots
    seqNumber = args.sq
    cf = args.cf
    ca = args.ca
    return shotNumber, seqNumber,cf, ca

All = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'GenericMovie'],
            ['published_file_type', 'name_is', 'DwaMovie'],
            ['published_file_type', 'name_is', 'GenericImageSequence'],
            ['published_file_type', 'name_is', 'QCRImageSequence'],
            ['published_file_type', 'name_is', 'PlayblastMovie'],
            {
                'filter_operator':'all',
                'filters':[
                    ['published_file_type', 'name_is', 'QCRMovie'],
                    ['tag_list', 'in','ambientOcc']
                ]

            }
        ]
    }

animFilter = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'PlayblastMovie'],
        ]
    }

animMayaSceneFilter = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'MayaScene'],
        ]
    }

confoLayoutFilter ={
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'PlayblastMovie'],
            {
                'filter_operator':'all',
                'filters':[
                    ['published_file_type', 'name_is', 'QCRMovie'],
                    ['tag_list', 'in','ambientOcc']
                ]

            }
        ]
    }


#main call to SG api extract information from published files
def findShots(selecFilter=[], taskname='anim_main', seq='p00300', shotList=['Not']):
    if shotList[0] == 'Not':
        filterShotlist = ['entity', 'is_not', None]
    else:
        filterShotlist = ['entity.Shot.code', 'in',shotList]
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['task', 'name_is', taskname],
        ['entity', 'is_not', None],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.sg_sequence','name_is', seq],
        filterShotlist,
        selecFilter
    ]

    res = {}
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'version_number', 'path', 'published_file_type'], order=[{'field_name':'version_number','direction':'desc'}]):

        entityName = v['entity']['name']
        if not entityName in res:
            res[entityName] = {}

        fileTypeName = v['published_file_type']['name']
        if not fileTypeName in res[entityName]:
            res[entityName][fileTypeName] = []

        res[entityName][fileTypeName].append(v)
    return res

def extractShot(selectedFilter=[], taskname='anim_main', seq='p00300'):
    res = findShots(selectedFilter,taskname,seq)
    shotsPath={}
    shotName = sorted(res)
    for i in shotName:
        versionNb = 0
        shotsPath[i]=''
        fileType = res[i].keys()
        for j in fileType:
            if res[i][j][0]['version_number'] > versionNb:
                versionNb = res[i][j][0]['version_number']
                shotsPath[i] = res[i][j][0]['path']['local_path']
    return shotsPath

#to find the shot for confo layout
def shotsForConfoLayout(seq = 's0300',filterShotList = ['Not']):
    res = findShots(confoLayoutFilter,'confo_layout',seq,filterShotList)
    shotsPath={}
    shotsPath["taskA"]="confo_layout"
    shotsPath["taskB"]='confo_layout_occ'
    shotsPath['shots']={}
    for shotName, fileTypes in res.items():
        if len(res[shotName]) == 2:
            shotsPath['shots'][shotName]={}
            shotsPath['shots'][shotName]['confo_layout']= res[shotName]['PlayblastMovie'][0]['path']['local_path']
            shotsPath['shots'][shotName]['confo_layout_occ']= res[shotName]['QCRMovie'][0]['path']['local_path']
    return shotsPath

#to find the shot for confo anim
def shotsConfoAnim(seq = 's0300', filterShotList = ['Not']):
    resConf = findShots(confoLayoutFilter,'confo_anim',seq, filterShotList)
    resAnim = findShots(animFilter,'anim_main',seq)
    shotsPath={}
    shotsPath["taskA"]="anim_main"
    shotsPath["taskB"]='confo_anim'
    shotsPath['shots']={}
    setAnim = set(sorted(resAnim.keys()))
    shotInConf = sorted(resConf.keys())
    commonShots = [ x for x in shotInConf if x in setAnim]
    for shotName in commonShots:
        shotsPath['shots'][shotName]={}
        shotsPath['shots'][shotName]['anim_main']= resAnim[shotName]['PlayblastMovie'][0]['path']['local_path']
        shotsPath['shots'][shotName]['confo_anim']= resConf[shotName]['QCRMovie'][0]['path']['local_path']

    return shotsPath





def main():


    shotNumber, seqNumber,cf, ca = get_args()
    listShotName = []
    pathFiles ={}
    #format the seqNumber ans the shotNumber
    seqNumber=seqNumber.zfill(4)
    seqNumber = "s"+seqNumber
    if shotNumber:
        for i in shotNumber:
            listShotName.append(seqNumber+"_p"+ i.zfill(5))
        if ca:
            pathFiles = shotsConfoAnim(seqNumber, listShotName)
        elif cf:
            pathFiles = shotsForConfoLayout(seqNumber, listShotName)
        else:
            pathFiles = shotsConfoAnim(seqNumber, listShotName)
    else:
        if ca:
            pathFiles = shotsConfoAnim(seqNumber)
        elif cf:
            pathFiles = shotsForConfoLayout(seqNumber)
        else:
            pathFiles = shotsConfoAnim(seqNumber)


    commandLine = "rv -pyeval \"from rv import commands;import sys; sys.path.append(\'/s/prods/captain/_sandbox/duda/duda/_scripts/donuts/test_duda\');from lauchRv import createMode; createMode("+str(pathFiles)+")\""

    os.system(commandLine)



main()