#!/usr/bin/env python
# coding:utf-8
""":mod: testMovOiio
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2021.01
   
"""
import PyOpenColorIO as ocio
import OpenImageIO as oiio

def main():

    mov = '/s/prodanim/ta/_sandbox/duda/render/granMaHouseInt/GranMaIntHouse.mov'

    buf = oiio.ImageBuf(mov)
    nbImages = buf.nsubimages
    mylist = [1,1200,3,400,600, 1439]
    mylist.sort()
    for i in mylist:
        print(i,str(oiio.UINT8))
        buf.read(i)
        oiio.ImageBufAlgo.colorconvert(buf,buf,'srgb8','acescg')
        #buf.set_write_format(oiio.HALF)
        buf.write('/s/prodanim/ta/_sandbox/duda/acescg_testoiio.'+str(i)+'.exr',str(oiio.HALF))


if __name__ == '__main__':
    main()