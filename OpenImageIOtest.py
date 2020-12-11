#!/usr/bin/env python
# coding:utf-8
""":mod:`OpenImageIOtest` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2017, Mikros Animation"

import OpenImageIO as oiio


def find_min_max(filename, output = 'both'):
    inputFile = oiio.ImageInput.open(filename)
    if not inputFile:
        print 'Could not open: "' + filename + '"'
        print '\tError: "', oiio.geterror()
        return
    spec = inputFile.spec()
    nchans = spec.nchannels
    pixels = inputFile.read_image(oiio.FLOAT)
    if not pixels:
        print 'Could not read:', inputFile.geterror()
        return
    inputFile.close() #we're done with the file at this point
    minval = pixels[0:nchans] #initialize to the first pixel value
    maxval = pixels[0:nchans]
    i = 0 #absolute index
    for z in range(spec.depth):
        for y in range(spec.height):
            for x in range(spec.width):
                for c in range(nchans):
                    if pixels[i+c] < minval[c]:
                        minval[c] = pixels[i+c]
                    if pixels[i+c] > maxval[c]:
                        maxval[c] = pixels[i+c]
                i = i + nchans #advance the index
    if output == 'min':
        return minval
    elif output == 'max':
        return maxval
    else:
        return minval,maxval

def findMinMaxSingleChannel(filename, output = 'both'):
    inputFile = oiio.ImageInput.open(filename)
    if not inputFile:
        print 'Could not open: "' + filename + '"'
        print '\tError: "', oiio.geterror()
        return
    spec = inputFile.spec()
    nchans = spec.nchannels
    pixels = inputFile.read_image(oiio.FLOAT)
    if not pixels:
        print 'Could not read:', inputFile.geterror()
        return
    inputFile.close() #we're done with the file at this point
    minval = pixels[0:1] #initialize to the first pixel value
    maxval = pixels[0:1]
    i = 0 #absolute index

    #loops going throught the height and width of the frame
    for y in range(spec.height):
        for x in range(spec.width):
            if output == 'both':
                if pixels[i] < minval[0]:
                    minval[0] = pixels[i]
                if pixels[i] > maxval[0]:
                    maxval[0] = pixels[i]
            elif output == 'min':
                if pixels[i] < minval[0]:
                    minval[0] = pixels[i]
            elif output == 'max':
                if pixels[i] > maxval[0]:
                    maxval[0] = pixels[i]
            else:
                print 'wrong type of ouput'
                return
            i = i + nchans #advance the index
    if output == 'min':
        return minval[0]
    elif output == 'max':
        return maxval[0]
    else:
        return minval[0],maxval[0]

def convertExr(filename = '/s/prodanim/asterix2/_sandbox/duda/paintOver/s0180/p0100/s0180_p0100-base-light_prelight-left.0103.exr'):
    listImages = [
        '/s/prodanim/asterix2/sequences/s0080/s0080_p0010/compo/compo_comp/publish/images/s0080_p0010-base-compo_comp-v026/left/s0080_p0010-base-compo_comp-left.0188.exr',
        '/s/prodanim/asterix2/sequences/s0080/s0080_p0020/compo/compo_comp/publish/images/s0080_p0020-base-compo_comp-v030/left/s0080_p0020-base-compo_comp-left.0101.exr',
        '/s/prodanim/asterix2/sequences/s0080/s0080_p0030/compo/compo_comp/publish/images/s0080_p0030-base-compo_comp-v015/left/s0080_p0030-base-compo_comp-left.0101.exr',
        '/s/prodanim/asterix2/sequences/s0080/s0080_p0040/compo/compo_comp/publish/images/s0080_p0040-base-compo_comp-v020/left/s0080_p0040-base-compo_comp-left.0101.exr',
        '/s/prodanim/asterix2/sequences/s0080/s0080_p0050/compo/compo_comp/publish/images/s0080_p0050-base-compo_comp-v012/left/s0080_p0050-base-compo_comp-left.0115.exr',
        '/s/prodanim/asterix2/sequences/s0080/s0080_p0060/compo/compo_comp/publish/images/s0080_p0060-base-compo_comp-v012/left/s0080_p0060-base-compo_comp-left.0101.exr'
    ]
    checkerImage =oiio.ImageBuf('/s/prodanim/asterix2/_sandbox/duda/images/chekerCrop.jpg')
    widthChecker = checkerImage.spec().width
    heightChecker = checkerImage.spec().height
    outFilename = filename.replace('.exr','.jpg')
    averageList = []
    print outFilename
    space =80
    maxwidth = 2048
    maxheight = 858
    nrow = 5
    # calcul the number of column
    ncol = (len(listImages)/nrow)
    floatncol = (len(listImages)/5.0)
    if floatncol - ncol > 0:
        ncol = ncol +1
    ncol =14
    # inFile = oiio.ImageBuf(filename)
    # inFileMono = oiio.ImageBuf()
    # inFilewidth = inFile.spec().width
    # inFileheight = inFile.spec().height
    offsetwidth = 0
    offsetheight = 0
    widthBufImage = (maxwidth*nrow)+(space*(nrow+1))
    heightBufImage = (maxheight*ncol)+(space*(ncol+1))
    buf = oiio.ImageBuf(oiio.ImageSpec(widthBufImage, heightBufImage, 4, oiio.FLOAT))
    text = oiio.ImageBuf(oiio.ImageSpec(maxwidth,maxheight,4,oiio.FLOAT))
    oiio.ImageBufAlgo.render_text(text,100,(maxheight/2)+200,'s0080',700, fontname='LiberationSans-Italic',textcolor=(1,1,1,1))

    # if inFilewidth > maxwidth:
    #     offsetwidth = (inFilewidth - maxwidth)/2
    # if inFileheight > maxheight:
    #     offsetheight = (inFileheight-maxheight)/2
    # tmpInfile = oiio.ImageBuf(oiio.ImageSpec(maxwidth,maxheight,4,oiio.FLOAT))
    # oiio.ImageBufAlgo.crop(tmpInfile,inFile,oiio.ROI(offsetwidth,inFile.spec().width-offsetwidth,offsetheight,inFile.spec().height-offsetheight))


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
    #masterBufHeight = heightBufImage+240+(2*maxheight)
    masterBufHeight = int(masterBufwidth*1.414)
    masterBuf = oiio.ImageBuf(oiio.ImageSpec(masterBufwidth, masterBufHeight, 4, oiio.FLOAT))

    #create the white border
    oiio.ImageBufAlgo.render_box(masterBuf,518,518,masterBufwidth -518,masterBufHeight-518,(1,1,1,1),True)
    oiio.ImageBufAlgo.render_box(masterBuf, 578, 578, masterBufwidth - 578, masterBufHeight - 578, (0, 0, 0, 1), True)

    # #create the bottom ant top band
    # oiio.ImageBufAlgo.render_box(masterBuf, 120, masterBufHeight-(120+ space+maxheight), masterBufwidth -120, masterBufHeight - 120, (0, 0, 0, 1), True)
    # oiio.ImageBufAlgo.render_box(masterBuf, 120, 120, masterBufwidth - 120, maxheight+ 120, (0, 0, 0, 1), True)
    #
    # #paste the contactsheet images
    oiio.ImageBufAlgo.paste(masterBuf, 578, 578+(2*maxheight), 0, 0, buf)
    oiio.ImageBufAlgo.render_box(masterBuf,578,(578+(2*maxheight))-60,masterBufwidth-578,578+(2*maxheight),(1,1,1,1),True)
    # #paste the sequence number
    oiio.ImageBufAlgo.paste(masterBuf, 840, 120 , 0, 0, text)

    #
    #startcolumnBox = masterBufHeight - (578+space) - (maxheight/2) -100
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

    averageScene = tuple([x/len(listImages) for x in averageScene])
    #oiio.ImageBufAlgo.fill(masterBuf, averageScene, oiio.ROI(578+space, startRowBox, startcolumnBox+200, endColumnBox+200))
    oiio.ImageBufAlgo.fill(masterBuf, averageScene,
                           oiio.ROI(masterBufwidth-((2*widthChecker)+578+(space*2)), masterBufwidth-(widthChecker+578+(2*space)), 878+space, 878+space+heightChecker))

    #convert the colorspace
    oiio.ImageBufAlgo.colorconvert(masterBuf,masterBuf,'linear','Asterix2_Film')
    oiio.ImageBufAlgo.paste(masterBuf,masterBufwidth-(widthChecker+578+space),878+space,0,0,checkerImage)
    #convert to asterix lut
    #oiio.ImageBufAlgo.colorconvert(inFile,inFile,'linear','Asterix2_Film')
    #create a single channel buffer
    #oiio.ImageBufAlgo.channels(inFileMono,inFile,("R",))
    #stats = oiio.PixelStats()
    #get the stats fronm buffer
    #oiio.ImageBufAlgo.computePixelStats(inFileMono,stats)
    #oiio.ImageBufAlgo.computePixelStats(inFile, stats)
    #print stats.avg

    # reelOut = oiio.ImageBuf()
    # oiio.ImageBufAlgo.channels(reelOut,inFile,(0,1,2))

    #oiio.ImageBufAlgo.zero(inFileMono)

    #inFile.set_write_format(oiio.UINT16)
    masterBuf.set_write_format(oiio.UINT8)

    #draw a shape on image
    #oiio.ImageBufAlgo.render_box(inFile,500,1600,300,1000,(1,1,1,1),True)

    #inFile.write(outFilename)
    masterBuf.write('/s/prodanim/asterix2/_sandbox/duda/paintOver/s0180/p0100/test.jpg')

def main():
    #convertExr()
    buf = oiio.ImageBuf('/s/prodanim/ta/_sandbox/duda/render/granMaHouseInt/GranMaIntHouse.mov')
    print buf.nsubimages
    # spec = a.spec()
    # for i in range(len(spec.extra_attribs)):
    #     print spec.extra_attribs[i].name
    # b = a.spec().extra_attribs
    # for i in b:
    #     print a.spec().extra_attribs[i].name
    buf.clear()


if __name__ == '__main__':
    main()


