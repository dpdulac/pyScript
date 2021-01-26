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

Input = oiio.ImageBuf ("/s/prodanim/ta/assets/Character/huHuman/surface_texturing/surface_texturing/work/textures/testAces/huHuman_longSleevesShirt_smooth_1001_BaseColor.exr")
config = oiio.ImageSpec()
config.set_format(oiio.HALF)
oiio.ImageBufAlgo.colorconvert(Input, Input, 'linear_srgb', 'Utility - sRGB - Texture')
config.attribute ("maketx:highlightcomp", 1)
config.attribute ("maketx:filtername", "lanczos3")
config.attribute ("maketx:opaque_detect", 1)
config.attribute('maketx:forcefloat', 1)
config.attribute('maketx:fileformatname', 'tx')
config.attribute('maketx:incolorspace', 'srgb8')
config.attribute('maketx:outcolorspace', 'acescg')
Input.set_write_format(oiio.HALF)
ok = oiio.ImageBufAlgo.make_texture (oiio.MakeTxTexture, Input,
                                "/s/prodanim/ta/_sandbox/duda/tmp/crap/acescg_testC.tx", config)
if not ok :
    print("error:", oiio.geterror())