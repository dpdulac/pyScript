#!/usr/bin/env python
# coding:utf-8
""":mod:`testRv` -- dummy module
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
import time, os, argparse, pprint
tk, sgw, project = tkutil.getTk(fast=True, scriptName='duda')
sg = sgw._sg

animFilter = {
        'filter_operator' : 'any',
        'filters':[
            ['published_file_type', 'name_is', 'PlayblastImageSequence'],
           # ['published_file_type', 'name_is', 'QCRImageSequence']
        ]
    }

exrFilter = {
        'filter_operator' : 'any',
        'filters':[
            #['published_file_type', 'in', ['CompoImageSequence','GenericImageSequence']],
            ['published_file_type', 'name_is', 'CompoImageSequence'],
            ['published_file_type', 'name_is', 'GenericImageSequence'],
        ]
        }

#main call to SG api extract information from published files
def findShots(selecFilter={}, taskname='compo_precomp', seq='s0300', shotList=['Not']):
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
    for v in sg.find('PublishedFile', filters, ['code', 'entity', 'version_number', 'path', 'published_file_type','entity.Shot.custom_entity02_sg_shots_lighting_custom_entity02s'], order=[{'field_name':'version_number','direction':'desc'}]):

        entityName = v['entity']['name']
        if not entityName in res:
            res[entityName] = v
            res[entityName]['imgFormat'] = '.'+ v['path']['content_type'][v['path']['content_type'].find("/")+1:]

    return res

def findMaster(seq='s0300'):
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['sg_parent_sequence','name_is', seq]
    ]

    masters = {}
    for v in sg.find('CustomEntity02', filters, ['sg_shots_lighting','code'], order=[{'field_name':'version_number','direction':'desc'}]):
        masterName = v['code']
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
    return masters




def main():
    res = findShots(selecFilter=exrFilter, taskname='compo_precomp', seq='s1300', shotList=['Not'])
    listShot = []
    for key in sorted(res.keys()):
        listShot.append(key)
    print listShot
    resAnim = findShots(selecFilter=animFilter, taskname='anim_main', seq='s1300',shotList=listShot)
    resAnim.update(res)
    for key in sorted(resAnim.keys()):
        print key,resAnim[key]['entity.Shot.custom_entity02_sg_shots_lighting_custom_entity02s']#[0]['name']
        # for item in resAnim[key]['path'].keys():
        #     print item, resAnim[key]['path'][item]
        # print '\n'

#main()

pprint.pprint(findMaster(seq='s0300'))