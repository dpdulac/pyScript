#!/usr/bin/env python
# coding:utf-8
""":mod: testOCIO
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2021.01
   
"""
import PyOpenColorIO as ocio

def findColorSpacesNames():
    config = ocio.GetCurrentConfig()
    colorSpaces = [cs.getName() for cs in config.getColorSpaces()]
    return colorSpaces

print(findColorSpacesNames())