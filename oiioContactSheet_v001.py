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

taskList = ['compo_stereo','compo_comp','light_precomp','light_prelight','confo_render','anim_master','confo_anim','anim_main','confo_layout']

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

def imFilter(taskname = 'compo_precomp'):
    filterDict = {'editing_edt': animFilter,
                  'layout_base': animFilter,
                  'confo_layout':imageFilterConfoLayout,
                  'anim_main': animFilter,
                  'light_lighting':exrFilter,
                  'light_precomp':exrFilter,
                  'compo_comp':exrFilter,
                  'light_prelight': animFilter,
                  'compo_stereo':exrFilter,
                  'confo_render':imageFilterConfoLayout,
                  'anim_master':imageFilterConfoLayout,
                  'confo_anim':imageFilterConfoLayout,

                  }
    return filterDict[taskname]

#main call to SG api extract information from published files
def findShots(taskname='compo_comp', seq='p00300', shotList=[]):
    res = {}
    switchTask = taskList.index(taskname)
    while shotList != [] and switchTask < len(taskList):
        filterType = imFilter(taskList[switchTask])
        filters = [
            ['project', 'is', {'type':'Project', 'id':project.id}],
            ['task', 'name_is', taskList[switchTask]],
            #['entity', 'is_not', None],
            ['entity', 'type_is', 'Shot'],
            ['entity.Shot.sg_sequence','name_is', seq],
            ['entity.Shot.sg_status_list', 'is_not', 'omt'],
            filterType
        ]


        for v in sg.find('PublishedFile', filters, ['code', 'entity','entity.Shot.sg_status_list','entity.Shot.sg_cut_order','version_number', 'path', 'published_file_type', 'entity.Shot.sg_cut_in','entity.Shot.sg_cut_out','task','entity.Shot.sg_sequence','entity.Shot.sg_frames_of_interest'], order=[{'field_name':'version_number','direction':'desc'}]):
            entityName = v['entity']['name']
            if not entityName in res:
                res[entityName] = {}
                res[entityName]['imgFormat'] = '.' + v['path']['content_type'][
                                                     v['path']['content_type'].find("/") + 1:]
                res[entityName]['cutOrder'] = v['entity.Shot.sg_cut_order']
                res[entityName]['fInterest'] = ''
                if v['entity.Shot.sg_frames_of_interest'] == None:
                    res[entityName]['fInterest'] = v['entity.Shot.sg_cut_in']
                else:
                    res[entityName]['fInterest'] = v['entity.Shot.sg_frames_of_interest']
                res[entityName]['cutIn'] = v['entity.Shot.sg_cut_in']
                res[entityName]['cutOut'] = v['entity.Shot.sg_cut_out']
                res[entityName]['cutMid'] = int((v['entity.Shot.sg_cut_in'] + v['entity.Shot.sg_cut_out']) / 2)
                res[entityName]['framePath'] = v['path']['local_path_linux']
                res[entityName]['Task'] = v['task']['name']

        listShotInRes = res.keys()
        shotList = list(set(shotList).difference(listShotInRes))
        print taskList[switchTask]
        switchTask = switchTask + 1

    return res

# def findShotsInList( seq='s1300', shotList=[], taskname = 'compo_comp'):
#     res = {}
#     found = False
#     switchTask = taskList.index(taskname)
#     while found == False:
#         print taskList[switchTask]
#         filterType = imFilter(taskList[switchTask])
#         #print taskList[switchTask]
#         filters = [
#             ['project', 'is', {'type': 'Project', 'id': project.id}],
#             ['entity.Shot.code', 'in', shotList],
#             ['task', 'name_is', taskList[switchTask]],
#             filterType
#         ]
#         for v in sg.find('PublishedFile', filters, ['code', 'entity','entity.Shot.sg_cut_order', 'version_number', 'path', 'published_file_type', 'entity.Shot.sg_cut_in','entity.Shot.sg_cut_out','task','entity.Shot.sg_sequence'], order=[{'field_name':'created_at','direction':'desc'}]):
#             entityName = v['entity']['name']
#             if not entityName in res:
#                 res[entityName] = v
#                 res[entityName]['imgFormat'] = '.' + v['path']['content_type'][v['path']['content_type'].find("/") + 1:]
#                 res[entityName]['cutOrder'] = v['entity.Shot.sg_cut_order']
#             if v == None:
#                 print 'no file in: '+ taskList[switchTask]
#                 found = False
#             else:
#                 found = True
#         switchTask = switchTask + 1
#         if switchTask >= len(taskList):
#             print 'not good'
#             break
#
#     return res

def findShotsInList( seq='s1300', shotList=[], taskname = 'compo_comp'):
    res = {}
    for shot in shotList:
        found = False
        switchTask = taskList.index(taskname)
        while found == False:
            print taskList[switchTask],shot
            filterType = imFilter(taskList[switchTask])
            filters = [
            ['project', 'is', {'type': 'Project', 'id': project.id}],
            ['entity.Shot.code', 'is', shot],
            ['entity.Shot.sg_status_list', 'is_not', 'omt'],
            ['task', 'name_is', taskList[switchTask]],
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

            if switchTask >= len(taskList):
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

def contactSheet(task='compo_comp', seq = 's0180',res={}):
    # listImages = [
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0010/compo/compo_comp/publish/images/s0080_p0010-base-compo_comp-v026/left/s0080_p0010-base-compo_comp-left.0188.exr',
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0020/compo/compo_comp/publish/images/s0080_p0020-base-compo_comp-v030/left/s0080_p0020-base-compo_comp-left.0101.exr',
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0030/compo/compo_comp/publish/images/s0080_p0030-base-compo_comp-v015/left/s0080_p0030-base-compo_comp-left.0101.exr',
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0040/compo/compo_comp/publish/images/s0080_p0040-base-compo_comp-v020/left/s0080_p0040-base-compo_comp-left.0101.exr',
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0050/compo/compo_comp/publish/images/s0080_p0050-base-compo_comp-v012/left/s0080_p0050-base-compo_comp-left.0115.exr',
    #     '/s/prodanim/asterix2/sequences/s0080/s0080_p0060/compo/compo_comp/publish/images/s0080_p0060-base-compo_comp-v012/left/s0080_p0060-base-compo_comp-left.0101.exr'
    # ]

    cutOrderSeq = getOrder(res)
    listImages = []
    for shot in cutOrderSeq:
        if res[shot]['imgFormat'] == '.quicktime':
            listImages.append(res[shot]['framePath'])
        else:
            listImages.append(res[shot]['framePath'].replace('%04d', str(res[shot]['cutIn']).zfill(4)))
        print shot, listImages[-1], res[shot]['fInterest'], res[shot]['Task']

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

    # na color
    na = oiio.ImageBuf(oiio.ImageSpec(200, 200, 4, oiio.FLOAT))
    oiio.ImageBufAlgo.zero(na)
    oiio.ImageBufAlgo.render_text(na, 20, 140, 'Na', 120, fontname='LiberationSans-Italic',
                                  textcolor=(1, 0, 0, 1))

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
            if nbimage < listImagesLen and nbimage <= (nrow*ncol):
                fileFromList =[]
                if listImages[nbimage].rfind('.mov') > 0:
                    fileFromList = oiio.ImageBuf(listImages[nbimage],1,0)
                else:
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
            stats = oiio.PixelStats()
            if listImages[nbimage].rfind('.exr') > 0:
                oiio.ImageBufAlgo.colorconvert(tmpInfile, tmpInfile, 'linear', 'Asterix2_Film')
                oiio.ImageBufAlgo.computePixelStats(tmpInfile, stats)
            averageList.append(stats.avg)
            oiio.ImageBufAlgo.paste(buf, imgw +(j*space), imgh+(i*space), 0, 0, tmpInfile)

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
        if len(col) > 2:
            averageScene = tuple(map(sum,zip(averageScene,col)))
            oiio.ImageBufAlgo.fill(masterBuf,col,oiio.ROI(startRowBox,startRowBox+200,startcolumnBox,endColumnBox))
        else:
            oiio.ImageBufAlgo.paste(masterBuf,startRowBox,startcolumnBox,0,0,na)
        startRowBox = startRowBox+200
        if startRowBox > masterBufwidth-(578+(4*space)+(2*widthChecker)):
            startRowBox = 578 + (2*space)
            startcolumnBox = (878)+200+int(space*1.5)
            endColumnBox = startcolumnBox + 200

    # create the box with the average of scene color
    averageScene = tuple([x/len(listImages) for x in averageScene])
    oiio.ImageBufAlgo.fill(masterBuf, averageScene,
                           oiio.ROI(masterBufwidth-((2*widthChecker)+578+(space*2)), masterBufwidth-(widthChecker+578+(2*space)), 878+space, 878+space+heightChecker))

    #convert the colorspace
    #oiio.ImageBufAlgo.colorconvert(masterBuf,masterBuf,'linear','Asterix2_Film')
    oiio.ImageBufAlgo.paste(masterBuf,masterBufwidth-(widthChecker+578+space),878+space,0,0,checkerImage)

    masterBuf.set_write_format(oiio.UINT8)

    #draw a shape on image
    #oiio.ImageBufAlgo.render_box(inFile,500,1600,300,1000,(1,1,1,1),True)

    #inFile.write(outFilename)
    masterBuf.write('/s/prodanim/asterix2/_sandbox/duda/paintOver/s0180/p0100/test.jpg')

def main():
    seq = 's0010'
    task = 'compo_comp'
    shotList = findShotsInSequence(seq)
    #res = findShotsInList(seq,shotList,'compo_comp')
    res = findShots(task,seq,shotList)
    #pprint.pprint(res)
    # #pprint.pprint(sg.schema_field_read('Shot'))
    cutOrderSeq = getOrder(res)
    # framePath =[]
    # for shot in cutOrderSeq:
    #     if res[shot]['imgFormat'] == '.quicktime':
    #         framePath.append(res[shot]['framePath'])
    #     else:
    #         framePath.append(res[shot]['framePath'].replace('%04d',str(res[shot]['cutIn']).zfill(4)))
    #     print shot, framePath[-1], res[shot]['fInterest'], res[shot]['Task']
    contactSheet(task,seq,res)

if __name__ == '__main__':
    main()