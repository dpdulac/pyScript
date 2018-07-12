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
_OUTPATH_ ="/s/prods/captain/_sandbox/" + _USER_ +"/ContactSheet"

tk, sgw, project = tkutil.getTk(fast=True, scriptName=_USER_)
sg = sgw._sg

taskList = ['compo_comp']

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
    # if shotList[0] == 'Not':
    #     filterShotlist = ['entity', 'is_not', None]
    # else:
    #     filterShotlist = ['entity.Shot.code', 'not_in',shotList]
    filters = [
        ['project', 'is', {'type':'Project', 'id':project.id}],
        ['task', 'name_is', taskname],
        #['entity', 'is_not', None],
        ['entity', 'type_is', 'Shot'],
        ['entity.Shot.sg_sequence','name_is', seq],
        selecFilter,
        #filterShotlist
    ]

    res = {}
    for v in sg.find('PublishedFile', filters, ['code', 'entity','entity.Shot.sg_cut_order', 'version_number', 'path', 'published_file_type', 'entity.Shot.sg_cut_in','entity.Shot.sg_cut_out','task','entity.Shot.sg_sequence'], order=[{'field_name':'created_at','direction':'desc'}]):

        entityName = v['entity']['name']
        if v == None:
            print entityName, 'donuts'
        if not entityName in res:
            res[entityName] = v
            res[entityName]['imgFormat'] = '.'+ v['path']['content_type'][v['path']['content_type'].find("/")+1:]
            print v['entity.Shot.sg_cut_order']

    return res

    def getOrder(res={}):
        order = []
        lengthRes = len(res)
        for i in range(1, lengthRes + 1):
            for key in res.keys():
                if res[key]['cutOrder'] == i:
                    order.append(key)
        return order

def contactSheet(listImages = [],task='compo_comp', seq = 's0180'):
    # listImages = [
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0010/compo/compo_comp/publish/images/s0080_p0010-base-compo_comp-v026/left/s0080_p0010-base-compo_comp-left.0188.exr',
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0020/compo/compo_comp/publish/images/s0080_p0020-base-compo_comp-v030/left/s0080_p0020-base-compo_comp-left.0101.exr',
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0030/compo/compo_comp/publish/images/s0080_p0030-base-compo_comp-v015/left/s0080_p0030-base-compo_comp-left.0101.exr',
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0040/compo/compo_comp/publish/images/s0080_p0040-base-compo_comp-v020/left/s0080_p0040-base-compo_comp-left.0101.exr',
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0050/compo/compo_comp/publish/images/s0080_p0050-base-compo_comp-v012/left/s0080_p0050-base-compo_comp-left.0115.exr',
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0060/compo/compo_comp/publish/images/s0080_p0060-base-compo_comp-v012/left/s0080_p0060-base-compo_comp-left.0101.exr'
    # ]

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
    text = oiio.ImageBuf(oiio.ImageSpec(maxwidth, maxheight, 4, oiio.FLOAT))
    oiio.ImageBufAlgo.render_text(text, 100, (maxheight / 2) + 200, seq, 700, fontname='LiberationSans-Italic',
                                  textcolor=(1, 1, 1, 1))

    #number of row and column for the contactsheet
    nrow = 5
    ncol =14

    # area containing the images of sequence
    widthBufImage = (maxwidth*nrow)+(space*(nrow+1))
    heightBufImage = (maxheight*ncol)+(space*(ncol+1))
    buf = oiio.ImageBuf(oiio.ImageSpec(widthBufImage, heightBufImage, 4, oiio.FLOAT))

    # offset to move the image
    offsetwidth = 0
    offsetheight = 0


    imgh = 0
    nbimage = 0
    listImagesLen = len(listImages)
    a =1
    for i in range(1,ncol+1):
        if a == 0:
            break
        imgw = 0
        for j in range(1,nrow+1):
            if nbimage < listImagesLen:
                fileFromList = oiio.ImageBuf(listImages[nbimage])
            else:
                #fileFromList = text
                a= 0
                break
            fileFromListWidth = fileFromList.spec().width
            fileFromListHeight = fileFromList.spec().height
            if fileFromListWidth > maxwidth or fileFromListHeight > maxheight:
                offsetwidth = (fileFromListWidth - maxwidth)/2
                offsetheight = (fileFromListHeight - maxheight)/2
            tmpInfile = oiio.ImageBuf(oiio.ImageSpec(maxwidth, maxheight, 4, oiio.FLOAT))
            oiio.ImageBufAlgo.crop(tmpInfile, fileFromList,
                                   oiio.ROI(offsetwidth, fileFromListWidth - offsetwidth, offsetheight,
                                            fileFromListHeight - offsetheight))
            oiio.ImageBufAlgo.paste(buf, imgw +(j*space), imgh+(i*space), 0, 0, tmpInfile)
            stats = oiio.PixelStats()
            oiio.ImageBufAlgo.computePixelStats(tmpInfile, stats)
            averageList.append(stats.avg)
            imgw = imgw + maxwidth
            nbimage = nbimage +1
        imgh = imgh + maxheight

    # create the master buffer
    masterBufwidth = widthBufImage+(578*2)
    masterBufHeight = int(masterBufwidth*1.414)
    masterBuf = oiio.ImageBuf(oiio.ImageSpec(masterBufwidth, masterBufHeight, 4, oiio.FLOAT))

    #create the white border
    oiio.ImageBufAlgo.render_box(masterBuf,518,518,masterBufwidth -518,masterBufHeight-518,(1,1,1,1),True)
    oiio.ImageBufAlgo.render_box(masterBuf, 578, 578, masterBufwidth - 578, masterBufHeight - 578, (0, 0, 0, 1), True)

    # paste the buffer contactsheet in the main buffer
    oiio.ImageBufAlgo.paste(masterBuf, 578, 578+(2*maxheight), 0, 0, buf)
    oiio.ImageBufAlgo.render_box(masterBuf,578,(578+(2*maxheight))-60,masterBufwidth-578,578+(2*maxheight),(1,1,1,1),True)

    # #paste the sequence number
    oiio.ImageBufAlgo.paste(masterBuf, 840, 120 , 0, 0, text)

    #
    # create the average color box
    startcolumnBox = 878+(space)
    endColumnBox = startcolumnBox +200
    startRowBox = 578+(2*space)
    averageScene = (0,0,0)
    for col in averageList:
        averageScene = tuple(map(sum,zip(averageScene,col)))
        oiio.ImageBufAlgo.fill(masterBuf,col,oiio.ROI(startRowBox,startRowBox+200,startcolumnBox,endColumnBox))
        startRowBox = startRowBox+200
        if startRowBox > masterBufwidth-(578+(4*space)+(2*widthChecker)):
            startRowBox = 578 + (space)
            startcolumnBox = (878)+200+int(space*1.5)
            endColumnBox = startcolumnBox + 200

    # create the box with the average of scene color
    averageScene = tuple([x/len(listImages) for x in averageScene])
    oiio.ImageBufAlgo.fill(masterBuf, averageScene,
                           oiio.ROI(masterBufwidth-((2*widthChecker)+578+(space*2)), masterBufwidth-(widthChecker+578+(2*space)), 878+space, 878+space+heightChecker))

    #convert the colorspace
    oiio.ImageBufAlgo.colorconvert(masterBuf,masterBuf,'linear','Asterix2_Film')
    oiio.ImageBufAlgo.paste(masterBuf,masterBufwidth-(widthChecker+578+space),878+space,0,0,checkerImage)

    masterBuf.set_write_format(oiio.UINT8)

    #draw a shape on image
    #oiio.ImageBufAlgo.render_box(inFile,500,1600,300,1000,(1,1,1,1),True)

    #inFile.write(outFilename)
    masterBuf.write('/s/prodanim/asterix2/_sandbox/duda/paintOver/s0180/p0100/test.jpg')

def main():
    seq = 's0010'
    v = findShots(exrFilter,'compo_comp',seq)
    cutOrderSeq = getOrder
    framePath =[]
    for shot in sorted(v.keys()):
        framePath.append(v[shot]['path']['local_path_linux'].replace('%04d',str(v[shot]['entity.Shot.sg_cut_in']).zfill(4)))
        print shot, v[shot]['path']['local_path_linux'].replace('%04d',str(v[shot]['entity.Shot.sg_cut_in']).zfill(4))
    #contactSheet(framePath,seq=seq)

if __name__ == '__main__':
    main()