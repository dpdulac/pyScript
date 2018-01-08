#!/usr/bin/env python
# coding:utf-8
""":mod:`katanaLocationShadingSetup` -- dummy module
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
"""
# Python built-in modules import

# Third-party modules import

# Mikros modules import

__author__ = "duda"
__copyright__ = "Copyright 2015, Mikros Animation"

from Katana import NodegraphAPI, Utils

from kCore.texturing import textures
from kCore.asset import assetApi
import renderPkg
import kCore.nodegraph as kNg
import kCore.fileIo as kIo

from pprint import pprint
import os

import sceneDescriptor
from corePython import logger
log = logger.getLogger("[shading.setup]")

#example adding 2 tuple
coord = tuple(sum(x) for x in zip(coord, change))

#add Global State Variable
def AddGlobalGraphStateVariable(name, options):
    variablesGroup = NodegraphAPI.GetRootNode().getParameter('variables')
    variableParam = variablesGroup.createChildGroup(name)
    variableParam.createChildNumber('enable', 1)
    variableParam.createChildString('value', options[0])
    optionsParam = variableParam.createChildStringArray('options', len(options))
    for optionParam, optionValue in zip(optionsParam.getChildren(), options):
        optionParam.setValue(optionValue, 0)
    return variableParam.getName()
#AddGlobalGraphStateVariable("camSwitch",["assetCam","userCam"])

def buildLocationShadingSetup(assetId, upTexsets=False, lastTexsets=False, shadingVariant=None, lookfile=False, renderPackage=None):
    """ Generate shading setup from actor_shading assetId

    :param assetId: asset path file
    :type assetId: str.
    :param upTexsets: Update texsets
    :type upTexsets: bool
    :param lastTexsets: Set texsets last version
    :type lastTexsets: bool
    :param shadingVariant: assset shading variant
    :type shadingVariant: str.
    :param lookfile: use lookfile instead of ImportGroup
    :type lookfile: bool
    :param renderPackage: use specific renderPackage version
    :type renderPackage : str
    """
    aApi        = assetApi.getAssetAPI()
    fields      = aApi.getAssetFields(assetId)
    assetType   = fields[assetApi.assetFieldAssetType]
    asset       = fields[assetApi.assetFieldAsset]

    abcAsset = os.path.join(assetId, "%s.sd" % fields[assetApi.assetFieldAsset])
    if not os.path.exists(abcAsset):
        abcName     = "%s.abc" % os.path.basename(aApi.resolvePath(assetId))
        abcAsset    = os.path.join(assetId, abcName)


    if shadingVariant is not None :
        fields[assetApi.assetFieldShadingVariant] = shadingVariant

    location = "/root/world/geo/{assetType}/{asset}".format(    asset=asset,
                                                                assetType=assetType.lower() )

    log.info("| asset %s" % asset)
    log.info("| assetType %s" % assetType)
    log.info("| location %s" % location)
    log.info("| abcAsset %s" % abcAsset)

    rootNode    = NodegraphAPI.GetRootNode()
    nodeList = []

    if assetType in ("Prop", "Character", "Library") :
        actorNode = NodegraphAPI.CreateNode("SceneGenerator", rootNode)
        data = { "root"     :   location,
                 "file"     :   abcAsset}
        kNg.update(nType="SceneGenerator", nId=actorNode.getName(), data=data )
        nodeList.append(actorNode)
    else :
        actorNode = NodegraphAPI.CreateNode("SceneGenerator", rootNode)
        data = { "root"     :   location,
                 "file"     :   abcAsset}
        kNg.update(nType="SceneGenerator", nId=actorNode.getName(), data=data )
        scriptItem=actorNode.setSceneDescriptorScriptItem(abcAsset)
        actorNode.setLookFileVersionRecursively(location="ALL",
                                                scriptItem=scriptItem,
                                                mode="last" )

        rigResolveNode = NodegraphAPI.CreateNode("RigResolve", rootNode)
        rigResolveName = "%s_RigResolve" % asset.title()
        rigResolveNode.setName(rigResolveName)

        lookFileResolveNode = NodegraphAPI.CreateNode("MultiLayerLookFileResolve", rootNode)
        lookFileResolveName = "%s_LookFileResolve" % asset.title()
        lookFileResolveNode.setName(lookFileResolveName)
        nodeList.extend([actorNode, rigResolveNode, lookFileResolveNode])


    actorName   = "%s_Actor" % asset.title()
    actorNode.setName(actorName)

    if lookfile :
        if renderPackage is None :
            renderPackage = getRenderPackageAsset(fields)

        lookFilePath = os.path.join(renderPackage, "lookfile.klf")
        log.info("| lookfile ", lookFilePath)
        groupNode = buildLookFileGroup( assetId,
                                        lookFilePath)
    else :
        groupNode = NodegraphAPI.CreateNode("ImportGroup", rootNode)
        inPort = groupNode.addInputPort( "IN")
        outPort = groupNode.addOutputPort("OUT")
        inPortSend = groupNode.getSendPort("IN")
        outPortReturn = groupNode.getReturnPort("OUT")
        inPortSend.connect(outPortReturn)

    Utils.EventModule.ProcessAllEvents()

    gpName = "%s_Overrides" % asset.title()
    groupNode.setName(gpName)

    nodeList.append(groupNode)

    #nodeList.extend(buildPotentialLocationsOverrideGroup(actorNode))

    kNg.WireInlineNodes(nodeList)
    return nodeList
