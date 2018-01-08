#!/usr/bin/env python
# coding:utf-8
#
# David 
#
#
#
#
# scriptForShadingLib.py : 

mappableInterfaceParams = [
#"d_color",
"d_roughness",
#"b_color",
"b_roughness",
"sss_mix",
#"s1_color",
"s1_roughness",
"s1_anisotropy",
"s1_rotation",
"s1_reflectivity",
"s1_edgetint",
#"s2_color",
"s2_roughness",
"s2_anisotropy",
"s2_rotation",
"s2_reflectivity",
"s2_edgetint",
"t_color",
"t_roughness",
"e_color",
"bump",
"normals",
"opacity",
"disp"
]

for param in mappableInterfaceParams:
    # get source to check
    mapParam = "%s_map" % param
    parAttr = GetAttr("material.parameters." + mapParam, inherit=True)
    parVal = ""
    if parAttr:
        parVal = parAttr[0]
    if parVal == "":
        #special treatment for roughness reconnect user intensity if no map
        if param =="s1_roughness"
            SetAttr("material.nodes.Arn_surfaceShader_hi.connections."+ param,["out@s1_roughness_intensity"])
        elif param = "t_color"
            SetAttr("material.nodes.Arn_surfaceShader_hi.connections."+ param,["out@t_color_user"])
        # special treatment for displace
        elif param == "disp":
            SetAttr("material.terminals.arnoldDisplacement", [""])
        # empty filename -> disconnect entry
        else:
            SetAttr("material.nodes.Arn_surfaceShader_hi.connections." + param, ScenegraphAttr.NullAttr())
        # SetAttr("material.nodes.NM_STD_Surface_lo.connections." + param, ScenegraphAttr.NullAttr())
        # SetAttr("material.nodes.NM_STD_Surface_gi.connections." + param, ScenegraphAttr.NullAttr())
