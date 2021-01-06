#!/usr/bin/env python
# coding:utf-8
""":mod: newTestMovOiio
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2021.01
   
"""
import OpenImageIO as oiio

mov = '/s/prodanim/ta/_sandbox/duda/render/granMaHouseInt/hallwayAA/tst-arnoldStandin-beauty-left.0180.exr'

listFrame = "1"


buf = oiio.ImageBuf(mov)
buf.clear()
buf = oiio.ImageBuf(mov)
nbImages = buf.nsubimages
mylist = listFrame
#buf.read(1200)
buf.write('/s/prodanim/ta/_sandbox/duda/acescg_testoiio.100.jpg',str(oiio.UINT8))
print buf.geterror()
buf.clear()
# for i in mylist:
#     buf = oiio.ImageBuf(mov)
#     buf.read(1200)
#     #oiio.ImageBufAlgo.colorconvert(buf,buf,'srgb8','acescg')
#     print('/s/prodanim/ta/_sandbox/duda/acescg_testoiio.'+str(i)+'.exr')
#     buf.write('/s/prodanim/ta/_sandbox/duda/acescg_testoiio.'+str(i)+'.exr',str(oiio.HALF))