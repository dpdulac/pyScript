#!/usr/bin/env python
# coding:utf-8
""":mod: uberCamInit.py
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: duda
   :date: 2021.05
   
"""
try:
    import uberCam as uberCamKatana
except Exception as exception:
    print('not good...: ', str(exception))
else:
    print('donuts')
    uberCamKatana.getKatanaUberCam()