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

#lightshader stuff
# os.environ['LIGHTSHADER'] = "/homes/"+_USER_+"/katanaResources/lightshaderResources"
# _LIGHTSHADER_=os.environ['LIGHTSHADER']
# os.environ['KAT_SHELVES']=_LIGHTSHADER_+"/katana_shelves"
# _KAT_SHELVES_ = os.environ['KAT_SHELVES']
# os.environ['MATLIB']=_LIGHTSHADER_+"/Library"


#add path to KATANA_RESOURCES
# os.environ['KATANA_RESOURCES'] += os.pathsep + "/homes/"+_USER_+"/.katana/UIPlugins"+os.pathsep+_LIGHTSHADER_+"/Resources"+os.pathsep+_KAT_SHELVES_
os.environ['KATANA_RESOURCES'] += os.pathsep + "/homes/"+_USER_+"/.katana/" + os.pathsep + "/datas/KTMaterialXTools/katana/"
#set KATANA_HOME
try :
    os.environ["PROD_ROOT"]
except KeyError:
    os.environ["KATANA_HOME"] ="/tmp"
else:
    os.environ["KATANA_HOME"] = os.environ["PROD_ROOT"]+"/_sandbox/"+ _USER_

#if in arnold-5 add my shaderpath
# pathArnoldPlugin = os.environ["PROD_ROOT"]+"/_sandbox/"+_USER_+"/oslShader"
# if not os.path.isdir(pathArnoldPlugin):
#     print "Creating: "+pathArnoldPlugin
#     os.makedirs(pathArnoldPlugin)
# try:
#     os.environ['ARNOLD_PLUGIN_PATH']
# except KeyError:
#     os.environ['ARNOLD_PLUGIN_PATH'] = pathArnoldPlugin
# else:
#     if os.environ['ARNOLD_PLUGIN_PATH'].find("arnold-5.") > 0:
#         print "using arnold-5"
#         os.environ['ARNOLD_PLUGIN_PATH']+= os.pathsep + pathArnoldPlugin
#         os.environ[
#             'KATANA_RESOURCES'] += os.pathsep + "/homes/" + _USER_ + "/.katana/UIPlugins" + os.pathsep + _LIGHTSHADER_ + "/Resources" + os.pathsep + _KAT_SHELVES_
#     else:
#         print "using Arnold-4"

katanaRoot = os.environ["KATANA_ROOT"]
os.environ['PYTHONPATH'] +=  os.pathsep + "/homes/"+_USER_+"/.katana/Script" + os.pathsep + "/s/apps/packages/cgDev" \
                                                                                            "/pyalembic/1.7.10" \
                                                                                            "/platform-linux/python-2" \
                                                                                            ".7/boost_python-1.61/lib" \
                                                                                            "/python2.7/site-packages" + os.pathsep + "/datas/KTMaterialXTools/python/ " + os.pathsep + "/s/apps/packages/cgDev/materialx/1.37.4/platform-linux/build-release/python-2.7" + os.pathsep + katanaRoot + "/plugins/Resources/Usd/lib/python "
os.environ["KATANA_RESOURCES"] += os.pathsep + katanaRoot + "/plugins/Resources/Usd/plugin"
os.environ["LD_LIBRARY_PATH"] += os.pathsep + katanaRoot + "/plugins/Resources/Usd/lib"
#add the lua path
luaPath = "/homes/"+_USER_+"/.katana/LuaScript/"
if not os.path.isdir(luaPath):
    print "Creating: " + luaPath
    os.makedirs(luaPath)
try:
    os.environ['LUA_PATH']
except KeyError:
    os.environ['LUA_PATH'] = luaPath+"?.lua"
else:
    print 'donuts'
    #os.environ['LUA_PATH'] = luaPath+"?.lua"+os.environ['LUA_PATH']
    os.environ['LUA_PATH'] = '/s/apps/packages/mikrosAnim/katanaCore/1.8.0/kCore/lua/?.lua' +';'+luaPath + "?.lua"

#append my script directory
#sys.path.append("/s/prodanim/asterix2/_sandbox/duda/Katana/Startup")
# sys.path.append("/homes/"+_USER_+"/.katana/UIPlugins")
sys.path.append("/homes/"+_USER_+"/.katana/Script")
# sys.path.append(_LIGHTSHADER_)
# sys.path.append(_LIGHTSHADER_+"/Resources")
# sys.path.append(_KAT_SHELVES_)
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




