#!/usr/bin/env python
# coding:utf-8
""":mod:`init.py` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "dulacd"
__copyright__ = "Copyright 2016, Mikros Animation"

import sys
import os
import logging

log = logging.getLogger("starPathSetup")

# user name
_USER_ = os.environ['USER']

# add path to KATANA_RESOURCES
os.environ['KATANA_RESOURCES'] += os.pathsep + "/homes/" + _USER_ + "/.katana/"

# set KATANA_HOME
try:
    os.environ["PROD_ROOT"]
except KeyError:
    os.environ["KATANA_HOME"] = "/tmp"
else:
    os.environ["KATANA_HOME"] = os.environ["PROD_ROOT"] + "/_sandbox/" + _USER_

log.info("setting osl")
userPathOSL = "/homes/" + _USER_ + "/.katana/oslShader/compiled"
if os.path.isdir(userPathOSL):
    os.environ['ARNOLD_PLUGIN_PATH'] = userPathOSL + os.pathsep + os.environ['ARNOLD_PLUGIN_PATH']

log.info("setting usd")
katanaRoot = os.environ["KATANA_ROOT"]
if os.path.isdir(katanaRoot + "/plugins/Resources/Usd"):
    os.environ[
        'PYTHONPATH'] += os.pathsep + "/homes/" + _USER_ + "/.katana/Script" + os.pathsep + katanaRoot + "/plugins/Resources/Usd/lib/python"
    os.environ["KATANA_RESOURCES"] += os.pathsep + katanaRoot + "/plugins/Resources/Usd/plugin"
    os.environ["LD_LIBRARY_PATH"] += os.pathsep + katanaRoot + "/plugins/Resources/Usd/lib"

# add the lua path
log.info("setting lua path")
luaPath = "/homes/" + _USER_ + "/.katana/LuaScript/"
if not os.path.isdir(luaPath):
    log.info("Creating: {0}".format(luaPath))
    os.makedirs(luaPath)
try:
    os.environ['LUA_PATH']
except KeyError:
    os.environ['LUA_PATH'] = luaPath + "?.lua"
else:
    log.info("trying to fix the LUA_PATH env variable")
    os.environ[
        'LUA_PATH'] = '/s/apps/packages/mikrosAnim/katanaCore/1.8.0/kCore/lua/?.lua' + os.pathsep + luaPath + "?.lua"

log.info("appending script path")
sys.path.append("/homes/" + _USER_ + "/.katana/Script")
if os.path.isdir("/datas/pyScript"):
    sys.path.append("/datas/pyScript")

envTest = "/homes/" + _USER_ + "/.katana/SuperTools" + os.pathsep + os.environ["KATANA_ROOT"]
os.environ["KATANA_ROOT"] = envTest
print(os.environ["KATANA_ROOT"], "\n\Donuts\nDonuts\nDonutsssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
# load the custom menu once the startup is complete
if _USER_ == "dulacd":
    import katanaSelectFile as david

    david.customMenuCallback()

# import DavidKatanaScript
# from DavidKatanaScript import getBB
# from Katana import NodegraphAPI
# NodegraphAPI.SetExpressionGlobalValue("getBB",getBB)
