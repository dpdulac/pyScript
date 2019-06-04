#!/usr/bin/env python
# coding:utf-8
""":mod: mayaSelectFaceSet.py --- Module Title
=================================

   2019.06
  :platform: Unix
  :synopsis: module idea
  :author: duda

"""
from mayaSurfacingTools.mayaToKatUtils import mayaKatToolBox as mayaToKat
reload(mayaToKat)
try :
    mayaToKat.close()
except:
    pass
maKat = mayaToKat.mayaToKatToolBox()
maKat.show()