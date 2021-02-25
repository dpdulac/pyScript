#!/usr/bin/env python
# coding:utf-8
""":mod: oiiomaketxtest
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2021.01
   
"""
import OpenImageIO as oiio


def maketx():
    Input = oiio.ImageBuf(
        "/s/prodanim/ta/assets/Character/huHuman/surface_texturing/surface_texturing/work/textures/testAces/huHuman_longSleevesShirt_smooth_1001_BaseColor.exr")
    config = oiio.ImageSpec()
    config.set_format(oiio.HALF)
    oiio.ImageBufAlgo.colorconvert(Input, Input, 'linear_srgb', 'Utility - sRGB - Texture')
    config.attribute("maketx:highlightcomp", 1)
    config.attribute("maketx:filtername", "lanczos3")
    config.attribute("maketx:opaque_detect", 1)
    config.attribute('maketx:forcefloat', 1)
    config.attribute('maketx:fileformatname', 'tx')
    config.attribute('maketx:incolorspace', 'srgb8')
    config.attribute('maketx:outcolorspace', 'acescg')
    Input.set_write_format(oiio.HALF)
    ok = oiio.ImageBufAlgo.make_texture(oiio.MakeTxTexture, Input,
                                        "/s/prodanim/ta/_sandbox/duda/tmp/crap/acescg_testC.tx", config)
    if not ok:
        print("error:", oiio.geterror())

def openPSD():
    config = oiio.ImageSpec()
    config.attribute("oiio:UnassociatedAlpha", 1)
    inputFile = '/s/prodanim/ta/assets/Mattepaint/ldev_skydome_night/mattepaint/mattepaint_deliver/work/images/photoshop/migeotp_testaces/v003/ldev_skydome_night-mattepaint_deliver-migeotp_testaces-OL_02-v003.tif'
    Input = oiio.ImageBuf('/s/prodanim/ta/assets/Mattepaint/ldev_skydome_night/mattepaint/mattepaint_deliver/work/images/photoshop/migeotp_testaces/v003/ldev_skydome_night-mattepaint_deliver-migeotp_testaces-OL_02-v003.tif')
    Input.specmod().attribute("oiio:UnassociatedAlpha",1)
    OutputName = '/s/prodanim/ta/_sandbox/duda/tmp/crap/donuts'
    BG = oiio.ImageBuf('/s/prodanim/ta/assets/Mattepaint/ldev_skydome_night/mattepaint/mattepaint_deliver/work/images/photoshop/migeotp_testaces/v003/ldev_skydome_night-mattepaint_deliver-migeotp_testaces-BG-v003.tif')
    for i in range(Input.nsubimages):
        config = oiio.ImageSpec()
        config.attribute("oiio:UnassociatedAlpha",1)
        Input.reset(inputFile,i,0,config)
        # RGB = oiio.ImageBuf()
        # Alpha = oiio.ImageBuf()
        # tmp = oiio.ImageBuf()
        # print oiio.ImageBufAlgo.channels(BG, BG, ('R', 'G', 'B', 1.0))
        # print oiio.ImageBufAlgo.over(tmp,Input,BG)
        # print(oiio.geterror())
        #print oiio.ImageBufAlgo.unpremult(Input, Input)
        #print oiio.ImageBufAlgo.channels(RGB, Input, ('R', 'G', 'B', 1.0))
        #print oiio.ImageBufAlgo.channels(Alpha, Input, ('A', ))
        ##print oiio.ImageBufAlgo.colorconvert(tmp, tmp, 'matte_paint', 'acescg')
        #print oiio.ImageBufAlgo.channels(BG, RGB, (0,1,2))
        #print oiio.ImageBufAlgo.channel_append(Input, RGB,Alpha)

        print oiio.ImageBufAlgo.colorconvert(Input, Input, 'scene_linear', 'compositing_linear')
        print oiio.ImageBufAlgo.colorconvert(Input, Input, 'matte_paint', 'compositing_linear')
        Input.specmod().attribute("oiio:ColorSpace", 'acescg')
        #print oiio.ImageBufAlgo.premult(Input, Input)
        #print oiio.ImageBufAlgo.unpremult(Input,Input)
        #print oiio.ImageBufAlgo.premult(Input, Input)
        Input.set_write_format(oiio.FLOAT)
        bla = OutputName + '.'+ str(i).zfill(4) + '.exr'
        Input.write(bla)
        print(bla)



def main():
    # maketx()
    openPSD()


if __name__ == '__main__':
    main()
