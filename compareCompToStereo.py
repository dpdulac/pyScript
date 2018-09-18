#!/usr/bin/env python
# coding:utf-8
""":mod: compareCompToStereo --- Module Title
=================================

   2018.09
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""
"""
    Compare the technical aprouved compo_comp shot to the technical aprouved compo_stereo shot (only left eye)
    
"""


import OpenImageIO as oiio
import os, pprint, errno, argparse, sys
from sgtkLib import tkutil, tkm

_USER_ = os.environ['USER']
_OUTPATH_ ='/tmp'
_FONT_ = 'LiberationSans-Italic'

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

def findShots( seq=40, shot = 135):
    # format the input
    seqShot = 's'+str(seq).zfill(4)+'_p'+str(shot).zfill(4)

    # filter forcompo_comp
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.code', 'is', seqShot],
        ['sg_task', 'name_is', 'compo_comp'],
        ['sg_status_list', 'is', 'cmpt'],
    ]

    res = {}
    for v in sg.find('Version', filters,
                     ['code', 'entity', 'sg_tank_version_number', 'sg_path_to_frames','entity.Shot.sg_cut_in', 'entity.Shot.sg_cut_out'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        entityName = v['entity']['name']
        if not entityName in res:
            res['name'] = entityName
            res['framePathCompoComp'] = v['sg_path_to_frames']
            res['cutIn'] = v['entity.Shot.sg_cut_in']
            res['cutOut'] = v['entity.Shot.sg_cut_out']
            tmpVersion = res['framePathCompoComp'][res['framePathCompoComp'].find('-v')+1:]
            res['version compo_comp']= tmpVersion[:tmpVersion.find('/')]

    try:
        res['framePathCompoComp']
    except:
        print("\x1b[0;31;40m"+'no shot for ' + seqShot + ' in compo_stereo marked as cmpt as been found'+"\x1b[0m")
        exit(0)

    # filter for compo_stereo
    filters = [
        ['project', 'is', {'type': 'Project', 'id': project.id}],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.code', 'is', seqShot],
        ['sg_task', 'name_is', 'compo_stereo'],
        ['sg_status_list', 'is', 'cmpt'],
    ]
    for v in sg.find('Version', filters,
                     ['code', 'entity', 'sg_tank_version_number', 'sg_path_to_frames', 'sg_first_frame'],
                     order=[{'field_name': 'version_number', 'direction': 'desc'}]):
        entityName = v['entity']['name']
        if res['name'] == entityName:
            res['framePathCompoStereo'] = v['sg_path_to_frames']
            tmpVersion = res['framePathCompoStereo'][res['framePathCompoStereo'].find('-v') + 1:]
            res['version compo_stereo'] = tmpVersion[:tmpVersion.find('/')]

    try:
        res['framePathCompoStereo']
    except:
        print("\x1b[0;31;40m"+'no shot for ' + seqShot + ' in compo_stereo marked as cmpt as been found'+"\x1b[0m")
        exit(0)

    return res

def compareStereo(res={},rv=False):
    seqA = res['framePathCompoComp']
    seqB = res['framePathCompoStereo']
    cutIn = res['cutIn']
    cutOut = res['cutOut']

    path = _OUTPATH_+'/'+res['name']+'/'
    diff = False
    matchStatus = '\x1b[0;32;40m match\x1b[0m'
    wrongStatus = "\x1b[0;31;40m don't match\x1b[0m"

    print '\n\n\n\x1b[0;32;40m---Starting comparison for shot '+ res['name']+' of '+res['version compo_comp']+ ' compo_comp to '+res['version compo_stereo']+ ' compo_stereo for frame '+ str(cutIn)+' to frame '+str(cutOut)+'---\x1b[0m'

    for imNb in range(cutIn,cutOut+1):
        imLeft = False
        imLestStatus = ''
        frameNb = str(imNb).zfill(4)
        imgA = seqA.replace('%04d',frameNb)
        imgB= seqB.replace('%04d', frameNb)

        # test if images exist
        for im in [imgA,imgB]:
            test = oiio.ImageInput.open(im)
            if not test:
                print "\x1b[0;31;40m",oiio.geterror(),"\x1b[0m"
                exit(0)
        imLeft = doCompare(imgA,imgB,path)
        if imLeft:
            imLestStatus = matchStatus
        else:
            imLestStatus = wrongStatus
            diff = True

        print('for frame nb '+frameNb+ ' the images'+ imLestStatus)

    if rv and diff:
        print path
        os.system('rv '+ path )

def doCompare(imgA='',imgB='',path = ''):

    comp = oiio.CompareResults()

    oiio.ImageBufAlgo.compare(oiio.ImageBuf(imgA), oiio.ImageBuf(imgB), 1/100.0, 1.0, comp)

    if comp.nwarn == 0 and comp.nfail == 0:
        return True
    else:
        if not os.path.isdir(path):
            os.makedirs(path)
        pathFrame = path+ imgA[imgA.rfind('/')+1:imgA.rfind('.exr')]+'.jpg'
        diff=oiio.ImageBuf()
        oiio.ImageBufAlgo.absdiff(diff,oiio.ImageBuf(imgA),oiio.ImageBuf(imgB))
        test = oiio.ImageBuf(oiio.ImageBuf(imgA).spec())
        oiio.ImageBufAlgo.pow(test,diff,(.3,.3,.3,1.0))
        test.write(pathFrame)
        return False

def get_args():
    #Assign description to the help doc
    parser = argparse.ArgumentParser(description = "compare the compo_comp left images to compo_stereo left images for the shot")
    #shot argument
    parser.add_argument('sequences', type=str,nargs='*', help='seq number follow by shot number can have multiple seq. Sequence and shot need to be separated by a - (i.e: 40-130 10-10 180-10)')
    parser.add_argument('--rv', '-rv', action='store_true', help=' do not display the resulting image(s) in rv')
    args = parser.parse_args()
    seqShotNumber = args.sequences
    rv = args.rv
    if len(seqShotNumber) > 1:
        rv = False

    seqShotToDo = []
    for seqShots in seqShotNumber:
        if seqShots.find('-') < 0:
            print "\x1b[0;31;40m usage: sequence number follow by a '-' then shot number (i.e: 430-10)"
            print seqShots+ ' will not be include in the list\x1b[0m'
        else:
            seqShotToDo.append(seqShots)
    try:
        len(seqShotToDo) > 0
    except:

        print 'seq number follow by shot number can have multiple seq. Sequence and shot need to be separated by a - (i.e: 40-130 10-10 180-10)'
        exit(0)

    return seqShotToDo,rv

def main():
    seqShot , rv= get_args()
    for shot in seqShot:
        res = findShots(shot.split('-')[0], shot.split('-')[1])
        #pprint.pprint(res)
        compareStereo(res,rv)

if __name__ == '__main__':
    main()