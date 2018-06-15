#!/usr/bin/env python
# coding:utf-8
""":mod: createContactSheet --- Module Title
=================================

   2018.06
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""

import nuke
from nukeCore.nodes import sequenceGroup

def createNukeFile(res = {}):

    allWriteNode = []
    for key in res.keys():
        if not os.path.isdir(res[key]['outDir']):
            os.makedirs(res[key]['outDir'])
        seq = res[key]['seq']
        task = res[key]['task']
        outFile = res[key]['fileOut']
        format = res[key]['fileType']
        showTask = res[key]['showTask']
        status = res[key]['status']
        name = res[key]['name']
        label= res[key]['showLabel']
        version = res[key]['version']
        cutOrder = res[key]['cutOrder']
        artist = res[key]['artist']
        outDir = res[key]['outDir']
        nbShots = res[key]['nbShots']
        #nbShots = len(findShotsInSequence(seq,False))
        intNb = nbShots/5
        floatNb = nbShots/5.0
        if floatNb-intNb > 0:
            intNb += 1
        sequenceGroupNode = sequenceGroup.create()
        sequenceGroupNode['sequence'].setValue(seq)
        sequenceGroupNode['task'].setValue(task)
        sequenceGroupNode['outputMode'].setValue('contactSheet')
        sequenceGroupNode['Rebuild'].execute()
        sequenceGroupNode['RowCol'].setValue([intNb, 5])
        sequenceGroupNode['Resolution'].setValue([5*2048,intNb*858])
        sequenceGroupNode['showName'].setValue(name)
        sequenceGroupNode['showStatus'].setValue(status)
        sequenceGroupNode['showTask'].setValue(showTask)
        sequenceGroupNode['showLabel'].setValue(label)
        sequenceGroupNode['showVersion'].setValue(version)
        sequenceGroupNode['showArtist'].setValue(artist)
        sequenceGroupNode['showCutOrder'].setValue(cutOrder)

        colorConvertNode = nuke.nodes.OCIOColorSpace(in_colorspace="Linear", out_colorspace="Lut")
        colorConvertNode.setInput(0,sequenceGroupNode)

        if format == 'jpg':
            writeNode = nuke.nodes.Write(name=seq + "WriteLutBurn", colorspace="linear", file_type="jpeg",_jpeg_sub_sampling="4:2:2", file=outFile)
            writeNode['_jpeg_quality'].setValue(0.75)
        else:
            writeNode = nuke.nodes.Write(name = seq + "WriteLutBurn", colorspace = "linear", file_type = "tiff",file =outFile)
            writeNode['datatype'].setValue('16 bit')
        writeNode['use_limit'].setValue(1)
        writeNode.setInput(0,colorConvertNode)
        allWriteNode.append(writeNode)
        nuke.scriptSave(outDir + seq + '_contactSheet.nk')
        # time.sleep(5)
        #nuke.execute(writeNode, 1, 1,1)
    masterNukeFile = '/tmp/tmpContactSheet.nk'
    nuke.filename()
    nuke.scriptSave(masterNukeFile)
    fRange = nuke.FrameRanges('1-1')
    # proc = subprocess.Popen(['rez','env','asterix2NukeBeta','--','nuke', '-x', '/tmp/tmpContactSheet.nk','1,1'], stdout=subprocess.PIPE)
    #os.system('nuke -x '+masterNukeFile+' 1,1')
    nuke.executeMultiple(tuple(allWriteNode), fRange, continueOnError=True)
    for renderNode in allWriteNode:
        nuke.execute(renderNode, 1, 1, 1)
    os.remove(masterNukeFile)
    for key in res.keys():
        rmTmpFile = 'rm '+res[key]['outDir']+'tmp* '
        os.system(rmTmpFile)
    print 'donuts'

def testDict(listSeq=['s0180', 's0010', 's0200', 's0080']):
    nbContactSheet = 1
    res = {}
    for seq in listSeq:
        res['contatSheet' + str(nbContactSheet)] = {
            'status': True,
            'showTask': True,
            'task': 'compo_comp',
            'name': True,
            'seq': seq,
            'artist': True,
            'fileOut': '/s/prodanim/asterix2/_sandbox/duda/contactSheet/' + seq + '/compo_comp/' + seq + '_contactSheet.tif',
            'fileType': 'tif',
            'cutOrder': True,
            'showLabel': True,
            'version': True,
            'outDir': '/s/prodanim/asterix2/_sandbox/duda/contactSheet/' + seq + '/compo_comp/'
        }
        nbContactSheet = nbContactSheet + 1

    return res

def main():
    createNukeFile(testDict())

if __name__ == '__main__':
    main()