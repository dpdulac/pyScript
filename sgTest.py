#!/usr/bin/env python
# coding:utf-8
""":mod: sgTest.py
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2020.12
   
"""
from sgtkLib import tkutil, tkm
import sys, os
import pprint

_USER_ = os.environ['USER']
_OUTPATH_ = '/s/prodanim/asterix2/_sandbox/' + _USER_ + "/contactSheet"
_FONT_ = 'LiberationSans-Italic'

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

imageFilterConfoLayout = {
    'filter_operator': 'all',
    'filters': [
        ['tag_list', 'name_is', 'primary'],
        ['published_file_type', 'name_is', 'QCRmovie'],
    ]
}

imageFilterAsset = {
    'filter_operator': 'any',
    'filters': [
        ['published_file_type', 'name_is', 'TurntableMovie'],
    ]
}

imageFilterLayoutBase = {
    'filter_operator': 'any',
    'filters': [
        # ['published_file_type', 'name_is', 'GenericMovie'],
        ['published_file_type', 'name_is', 'PlayblastMovie'],
        # ['published_file_type', 'name_is', 'CompoMovie'],
        # ['published_file_type', 'name_is', 'GenericImageSequence'],
        # ['published_file_type', 'name_is', 'PlayblastMovie'],
    ]
}

imageFilterEditing = {
    'filter_operator': 'any',
    'filters': [
        # ['published_file_type', 'name_is', 'GenericMovie'],
        # ['published_file_type', 'name_is', 'DwaMovie'],
        ['published_file_type', 'name_is', 'PlayblastMovie'],
        # ['published_file_type', 'name_is', 'GenericImageSequence'],
        # ['published_file_type', 'name_is', 'PlayblastMovie'],
    ]
}

cameraFiltering = {
    'filter_operator': 'any',
    'filters': [['published_file_type', 'name_is', 'CameraAlembic']],
}


def findAllSequence(all=False):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
    ]
    res = {}
    seqShots = []
    # get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence', filters, ['entity', 'code', 'description']):
        seq = v['code']
        if all:
            if not seq in res:
                res[seq] = {}
            res[seq]['description'] = v['description']
        else:
            if int(seq[:3]) < 800:  # only take the first 3 characters
                if not seq in res:
                    res[seq] = {}
                if v['description'] != None:
                    res[seq]['description'] = v['description']
                else:
                    res[seq]['description'] = 'None'
            else:
                print 'donuts for: ' + seq
    return res

def findShotsTmp(seq='s1300',shotList=[], masterLightDict={'Master'}):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        # ['code', 'is', 'Shot'],
        ['code', 'in', shotList],
        # ['entity.Shot.tag_list', 'name_contains', 'mattepainting'],
    ]
    res = {}
    for v in sg.find('Shot', filters,
                     ['code', 'sg_cut_order', 'sg_frames_of_interest', 'sg_master_layout', 'sg_cameras', 'sg_master_lighting', 'sg_shots_lighting', 'sg_cut_in', 'sg_cut_out'],
                     order=[{'field_name': 'created_at', 'direction': 'desc'}]):
        entityName = v['code']
        if v['sg_cut_order'] > 0:
            if not entityName in res:
                print(v['sg_cameras'])
                res[entityName] = {}
                frameInterest = v['sg_frames_of_interest']
                if frameInterest is not None:
                    frameInterestList = frameInterest.split()
                    addComma = ''
                    listFame = []
                    for i in frameInterestList:
                        if i != frameInterestList[-1]:
                            addComma += i + ','
                        else:
                            addComma += i
                    listFame.append(addComma)
                    res[entityName]['frameInterest'] = listFame
                else:
                    res[entityName]['frameInterest'] = ['101']
                res[entityName]['cutIn'] = v['sg_cut_in']
                res[entityName]['cutOut'] = v['sg_cut_out']
                res[entityName]['cutOrder'] = v['sg_cut_order']
                res[entityName]['masterLayout'] = v['sg_master_layout']['name']
                res[entityName]['masterLighting'] = ''
                res[entityName]['campath'] = findCameraOne(entityName)

    if masterLightDict['Master']:
        master = masterLightDict['Master']
        if len(master.keys()) > 0:
            for key in master.keys():
                for shot in master[key]['subShots']:
                    if shot in res.keys():
                        try:
                            res[shot]
                        except:
                            res[shot]['masterLighting'] = ''
                        else:
                            res[shot]['masterLighting'] = key
                    else:
                        print("Ho nooooooooo !!!! you did it again !!!!", shot)

    return res

def findShots(seq='s1300', shotList=[], masterListDict={'Master'}):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.code', 'in', shotList],
        # ['entity.Shot.tag_list', 'name_contains', 'mattepainting'],
    ]

    res = {}
    for v in sg.find('PublishedFile', filters,
                     ['code', 'entity', 'entity.Shot.sg_cut_order', 'entity.Shot.sg_frames_of_interest',
                      'entity.Shot.sg_master_lighting', 'entity.Shot.sg_shots_lighting', 'entity.Shot.sg_master_layout',
                      'entity.Shot.sg_cut_in', 'entity.Shot.sg_cut_out'],
                     order=[{'field_name': 'created_at', 'direction': 'desc'}]):
        entityName = v['entity']['name']
        if v['entity.Shot.sg_cut_order'] > 0:
            if not entityName in res:
                res[entityName] = {}
                frameInterest = v['entity.Shot.sg_frames_of_interest']
                if frameInterest is not None:
                    frameInterestList = frameInterest.split()
                    addComma = ''
                    listFame = []
                    for i in frameInterestList:
                        if i != frameInterestList[-1]:
                            addComma += i + ','
                        else:
                            addComma += i
                    listFame.append(addComma)
                    res[entityName]['frameInterest'] = listFame
                else:
                    res[entityName]['frameInterest'] = ['101']
                res[entityName]['cutIn'] = v['entity.Shot.sg_cut_in']
                res[entityName]['cutOut'] = v['entity.Shot.sg_cut_out']
                res[entityName]['cutOrder'] = v['entity.Shot.sg_cut_order']
                res[entityName]['masterLayout'] = v['entity.Shot.sg_master_layout']['name']
                res[entityName]['masterLighting'] = ''
    if masterListDict['Master']:
        master = masterListDict['Master']
        if len(master.keys()) > 0:
            for key in master.keys():
                for shot in master[key]['subShots']:
                    try:
                        res[shot]
                    except:
                        pass
                    else:
                        res[shot]['masterLighting'] = key

    return res


# find the masters shot for a sequence looking in SG
def findMasters(seqMasters=[]):
    filtersMasters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['code', 'in', seqMasters]
    ]

    masters = {}
    for v in sg.find('CustomEntity02', filtersMasters, ['sg_shots_lighting', 'code'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        masterName = v['code']
        if masterName.find('_m') >= 0:
            print masterName + ': layout master will not be used'
        else:
            masters[masterName] = {}
            masterShot = masterName.replace('_k', '_')
            linkShots = []
            for i in range(len(v['sg_shots_lighting'])):
                if v['sg_shots_lighting'][i]['name'] != masterShot:
                    linkShots.append(v['sg_shots_lighting'][i]['name'])
            masters[masterName]['masterShot'] = masterShot
            masters[masterName]['subShots'] = linkShots
            linkShots.insert(0, masterShot)
            masters[masterName]['sortedShot'] = linkShots
    return masters


# def findMasterShot(shot = '1300_k0120'):
#     filtersMasters = [
#         ['project', 'is', {'type': 'Project', 'id': project.id}],
#         ['code', 'is', shot],
#         #['code', 'in', seqMasters]
#     ]
#
#     masters = {}
#     for v in sg.find('PublishedFile', filtersMasters, ['sg_shots_lighting', 'code'],
#                      order=[{'field_name': 'version_number', 'direction': 'desc'}]):
#         masterName = v['code']
#         if masterName.find('_m') >= 0:
#             print masterName + ': layout master will not be used'
#         else:
#             masters[masterName] = {}
#             masterShot = masterName.replace('_k', '_')
#             linkShots = []
#             for i in range(len(v['sg_shots_lighting'])):
#                 if v['sg_shots_lighting'][i]['name'] != masterShot:
#                     linkShots.append(v['sg_shots_lighting'][i]['name'])
#             masters[masterName]['masterShot'] = masterShot
#             masters[masterName]['subShots'] = linkShots
#             linkShots.insert(0, masterShot)
#             masters[masterName]['sortedShot'] = linkShots
#     print masters

def findSingleShot(shot='s1300_p00300', taskname='compo_precomp'):
    filterType = imFilter(taskname)
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity.Shot.code', 'is', shot],
        ['task', 'name_is', taskname],
        filterType
    ]
    res = []
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'version_number', 'path', 'published_file_type'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        res.append(v['path']['local_path'])
    return res


def imFilter(taskname='compo_precomp'):
    filterDict = {'editing_edt': imageFilterEditing,
                  'layout_base': imageFilterLayoutBase,
                  'confo_layout': imageFilterConfoLayout,
                  'anim_main': imageFilterLayoutBase,
                  'model_base': imageFilterAsset,
                  'model_hi': imageFilterAsset,
                  'hair_surface': imageFilterAsset,
                  'surface_surfacing': imageFilterAsset
                  }
    return filterDict[taskname]


# get all the shot from the sequence
def findShotsInSequence(seq='s1300', dict=False, doMaster=False):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['code', 'is', seq]
    ]
    res = {}
    master = {}
    masterShot = []
    seqShots = []
    # get all the name of the shots and masters from the sequence
    for v in sg.find('Sequence', filters, ['entity', 'shots', 'sg_masters']):
        if not 'Shots' in res:
            tmp = v['shots']
            for item in tmp:
                seqShots.append(item['name'])
            res['Shots'] = sorted(seqShots)
        # if doMaster:
        tmpMaster = v['sg_masters']
        for item in tmpMaster:
            if item['name'].find('_k') >= 0:
                masterShot.append(item['name'])
        master['Master'] = masterShot
        if len(masterShot) > 0:
            master['Master'] = findMasters(masterShot)

    if dict:
        return res, master
    else:
        return sorted(seqShots), master


# find the camera path
def findCamera(shot='0600_0010'):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity.Shot.code', 'is', shot],
        cameraFiltering
    ]
    res = []
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'path'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        res.append(v['path']['local_path'])
    return res[-1]

def findCameraOne(shot='1375_0010'):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity.Shot.code', 'is', shot],
        cameraFiltering
    ]
    a = sg.find_one('PublishedFile', filters, ['path'],order=[{'field_name':'version_number', 'direction':'desc'}])['path']['local_path']
    return a

quickCameraFiltering = {
    'filter_operator': 'any',
    'filters': [['sg_published_files.code.name', 'name_contains', '.abc']],
}
def quickCam(shot='0700_0010_default'):
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        # ['code', 'is', 'Shot'],
        ['code', 'is', shot],
        # quickCameraFiltering
        # ['entity.Shot.tag_list', 'name_contains', 'mattepainting'],
    ]
    a = sg.find_one('Camera', filters, ['sg_published_files'],order=[{'field_name': 'version_number', 'direction': 'desc'}])['sg_published_files']
    print(a)
    for elem in a:
        if elem['name'].endswith('.abc'):
            print(elem['id'])

def findCameraPath(seq='s1300', dictShots={}, useDict=True):
    if useDict:
        shotInSeq = findShotsInSequence(seq=seq)
        dictShots = findShots(seq, shotInSeq[0], shotInSeq[1])
    for shot in dictShots.keys():
        try:
            camPath = findCamera(shot)
        except AttributeError:
            dictShots.pop(shot, None)
            print "no cam for: " + shot
        else:
            dictShots[shot]['camPath'] = camPath
    # pprint.pprint(dictShots)
    return dictShots

seq='1375'
shotInSeq = findShotsInSequence(seq=seq)
pprint.pprint(findShotsTmp('s1300',shotInSeq[0], shotInSeq[1]))
# quickCam()
# findCameraOne()
# pprint.pprint(dictShots)
# print(dictShot['masterLighting'])
