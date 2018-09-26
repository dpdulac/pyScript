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

__author__ = "duda"
__copyright__ = "Copyright 2016, Mikros Animation"
import sys
import os


# user name
_USER_ = os.environ['USER']

#set KATANA_HOME
os.environ["KATANA_HOME"] = "/s/prods/captain/_sandbox/"+ _USER_

#if in arnold-5 add my shaderpath
pathArnoldPlugin = "/s/prodanim/asterix2/_sandbox/"+_USER_+"/oslShader"
if not os.path.isdir(pathArnoldPlugin):
    os.makedirs(pathArnoldPlugin)
try:
    os.environ['ARNOLD_PLUGIN_PATH']
except KeyError:
    os.environ['ARNOLD_PLUGIN_PATH'] = pathArnoldPlugin
else:
    if os.environ['ARNOLD_PLUGIN_PATH'].find("arnold-5.") > 0:
        print "using arnold-5"
        os.environ['ARNOLD_PLUGIN_PATH']+= os.pathsep + pathArnoldPlugin
    else:
        print "using Arnold-4"

#add path to KATANA_RESOURCES
os.environ['KATANA_RESOURCES'] += os.pathsep + "/homes/"+_USER_+"/.katana/UIPlugins"
os.environ['PYTHONPATH'] +=  os.pathsep + "/homes/"+_USER_+"/.katana/Script"
#add the lua path
luaPath = "/homes/"+_USER_+"/.katana/LuaScript/"
if not os.path.isdir(luaPath):
    os.makedirs(luaPath)
try:
    os.environ['LUA_PATH']
except KeyError:
    os.environ['LUA_PATH'] = luaPath+"?.lua"
else:
    os.environ['LUA_PATH'] += os.pathsep + luaPath+"?.lua"

#append my script directory
#sys.path.append("/s/prodanim/asterix2/_sandbox/duda/Katana/Startup")
sys.path.append("/homes/"+_USER_+"/.katana/UIPlugins")
sys.path.append("/homes/"+_USER_+"/.katana/Script")
sys.path.append("/datas/pyScript")



#append to the pyton path
#os.environ['PYTONPATH']+= os.pathsep + "/homes/duda/.katana/UIPlugins"

#load the custom menu once the startup is complete
import katanaSelectFile as david
david.customMenuCallback()

#open template file
#KatanaFile.Load('/homes/duda/.katana/Template/template.katana')





#sys.path.append("/s/apps/packages/cgDev/pyocio/1.0.8/platform-linux/python-2.7/lib/")

#import PyOpenColorIO as OCIO

#config = OCIO.GetCurrentConfig()
#config_new = config.createEditableCopy()
#config_new.setActiveViews("sRGB")
#OCIO.SetCurrentConfig(config_new)
#print OCIO.GetCurrentConfig().getActiveViews()

#import DavidKatanaScript
#from DavidKatanaScript import getBB
#from Katana import NodegraphAPI
#NodegraphAPI.SetExpressionGlobalValue("getBB",getBB)




