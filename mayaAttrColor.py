#!/usr/bin/env python
# coding:utf-8
""":mod:`mayaAttrColor` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2017, Mikros Animation"

#add attribute color

import maya.cmds as cmds
import xml.etree.cElementTree as ET
from PyQt4.QtGui import *

def addAttrColorToHi():
    #lst for the shape in the scene
    loShapeList =[]
    loTransList = []
    #dictionary containing the name hi and lo as well as color
    dict ={}
    #select only the transformations
    selections = cmds.ls(tr=True)
    for item in selections:
        #if the name has "lo" in it's name add it to the list
        if item.find("_lo") > 1:
            loTransList.append(item)
    #extract the shape
    for item in loTransList:
        shape = cmds.listRelatives(item, shapes=True)
        if shape != None:
            loShapeList.append(shape[0])

    #find the color of low shape and add attributes to hi shape
    for item in loShapeList:
        #if not a mesh
        if cmds.objectType(item) != 'mesh':
            print ' your not my type ' + item
        else:
        #find the shader
            shadingGrps = cmds.listConnections(item,type='shadingEngine')
            shaders = cmds.ls(cmds.listConnections(shadingGrps),materials=True)
            #get the value of the color
            colorValue = cmds.getAttr(shaders[0]+".color")[0]
            #replace the "_loShape" by "_hi"
            transformHiName = item.replace("_loShape","_hi")
            #replace the "_loShape" by "_hi and get rid of the first part"
            shortName = item[item.rfind(":")+1:].replace("_loShape","_hi")
            #replace "_hi" by "_lo"
            shortNameLo = shortName.replace("_hi","_lo")
            dict[shortName] = {}
            dict[shortNameLo] = {}
            dict[shortName]['color']=colorValue
            dict[shortNameLo]['color']=colorValue
            #test if the transform exist
            try:
                currentTramsform = cmds.select(transformHiName, r = True)
            except :
                print transformHiName + ' does not exist'

            else:
                cmds.select(transformHiName, r = True)
                sel = cmds.ls(sl=True)
                #child = cmds.listRelatives(sel, allDescendents=True, type='transform')
                #try if the color attr is already there
                try:
                    cmds.addAttr(ln = 'color', k = True, uac = True, at = 'float3')
                except:
                   cmds.setAttr(transformHiName+'.color.red',colorValue[0])
                   cmds.setAttr(transformHiName+'.color.green',colorValue[1])
                   cmds.setAttr(transformHiName+'.color.blue',colorValue[2])
                else:
                    name = 'color'
                    cmds.addAttr(ln = name, k = True, uac = True, at = 'float3')
                    cmds.addAttr(ln = 'red', k = True, at = 'float', p = name, dv = colorValue[0] )
                    cmds.addAttr(ln = 'green', k = True, at = 'float', p = name, dv = colorValue[1] )
                    cmds.addAttr(ln = 'blue', k = True, at = 'float', p = name, dv = colorValue[2] )
    return dict

def exportXML(dict={},fileName ='/tmp'):
    root = ET.Element("attributeFile", version="0.1.0")
    for item in dict.keys():
        doc = ET.SubElement(root, "attributeList", location=item)
        ET.SubElement(doc, "attribute", name="red", type="float",value=str(dict[item]["color"][0]))
        ET.SubElement(doc, "attribute", name="green", type="float",value=str(dict[item]["color"][1]))
        ET.SubElement(doc, "attribute", name="blue", type="float",value=str(dict[item]["color"][2]))
    print ET.tostring(root)
    tree = ET.ElementTree(root)
    if fileName.rfind('.xml') < 0:
        fileName += '.xml'
    tree.write(fileName)

# Get filename using QFileDialog
w = QWidget()
filename = str(QFileDialog.getSaveFileName(w, 'Save XML File', '/s/prodanim/asterix2/ '))
print filename
dict = addAttrColorToHi()
exportXML(dict,filename)