"""
Ceci est un exercice pour presenter l'utilisation de 
"""

import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya
import math


class DvParentSwitchPlug(OpenMayaMPx.MPxNode):

    # Define node properties.
    kname = "dvParentSwitchPlug"
    kplugin_id = OpenMaya.MTypeId(0x90000005)

    # Define node attributes.
    rigMode = OpenMaya.MObject()
    followID = OpenMaya.MObject()
    targetMatrix = OpenMaya.MObject()
    hookMatrix = OpenMaya.MObject()
    parentInverseMatrix = OpenMaya.MObject()

    offsetMatrix = OpenMaya.MObject()

    # OUTPUTS
    xform = OpenMaya.MObject()

    translate = OpenMaya.MObject()
    translateX = OpenMaya.MObject()
    translateY = OpenMaya.MObject()
    translateZ = OpenMaya.MObject()

    rotate = OpenMaya.MObject()
    rotateX = OpenMaya.MObject()
    rotateY = OpenMaya.MObject()
    rotateZ = OpenMaya.MObject()

    scale = OpenMaya.MObject()
    scaleX = OpenMaya.MObject()
    scaleY = OpenMaya.MObject()
    scaleZ = OpenMaya.MObject()

    init_plug = True

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def decompose_matrix(self, mMatrix):
        # Convertir MMatrix en MTransformMatrix
        mTrsfmMtx = OpenMaya.MTransformationMatrix(mMatrix)

        # Valeurs translation
        trans = mTrsfmMtx.translation(OpenMaya.MSpace.kWorld)

        # Valeur rotation Euler en radian
        quat = mTrsfmMtx.rotation()
        angles = quat.asEulerRotation()

        # Extraire scale.
        scale = [1.0, 1.0, 1.0]

        scaleDoubleArray = OpenMaya.MScriptUtil()
        scaleDoubleArray.createFromList([0.0, 0.0, 0.0], 3)
        scaleDoubleArrayPtr = scaleDoubleArray.asDoublePtr()

        mTrsfmMtx.getScale(scaleDoubleArrayPtr, OpenMaya.MSpace.kObject)
        scale[0] = OpenMaya.MScriptUtil().getDoubleArrayItem(
                scaleDoubleArrayPtr,
                0
            )
        scale[1] = OpenMaya.MScriptUtil().getDoubleArrayItem(
                scaleDoubleArrayPtr,
                1
            )
        scale[2] = OpenMaya.MScriptUtil().getDoubleArrayItem(
                scaleDoubleArrayPtr,
                2
            )

        return [trans.x, trans.y, trans.z],\
            [angles.x, angles.y, angles.z],\
            scale

    def compute(self, plug, data):

        # Read plugs.
        rigMode_state = data.inputValue(
                DvParentSwitchPlug.rigMode
            ).asBool()

        follow_id = data.inputValue(
                DvParentSwitchPlug.followID
            ).asInt()

        targetMatrix_mMatrix = data.inputValue(
                DvParentSwitchPlug.targetMatrix
            ).asMatrix()

        hookMatrix_mHandle = data.inputArrayValue(
                DvParentSwitchPlug.hookMatrix
            )
        hookMatrix_counts = hookMatrix_mHandle.elementCount()

        parentInverseMatrix_mMatrix = data.inputValue(
                DvParentSwitchPlug.parentInverseMatrix
            ).asMatrix()

        offsetMatrix_mHandle = data.outputArrayValue(
                DvParentSwitchPlug.offsetMatrix
            )
        offsetMatrix_counts = offsetMatrix_mHandle.elementCount()

        delta = hookMatrix_counts - offsetMatrix_counts

        if delta > 0:
            builderOffsetsMatrixArray = offsetMatrix_mHandle.builder()

            for i in xrange(delta):
                aOffsetsMatrixHandle = builderOffsetsMatrixArray.addElement(
                        offsetMatrix_counts + i
                    )

            offsetMatrix_mHandle.set(builderOffsetsMatrixArray)
            offsetMatrix_mHandle.setClean()

        if rigMode_state:
            offsetMatrix_mHandle = data.outputArrayValue(
                DvParentSwitchPlug.offsetMatrix
            )

            for i in xrange(hookMatrix_counts):
                hookMatrix_mHandle = data.inputArrayValue(
                    DvParentSwitchPlug.hookMatrix
                )
                hookMatrix_mHandle.jumpToElement(i)
                hookMatrix_mMatrix = hookMatrix_mHandle.inputValue().asMatrix()

                offsetMatrix_mHandle.jumpToElement(i)
                offsetMatrix_mMatrix = targetMatrix_mMatrix * \
                    hookMatrix_mMatrix.inverse()

                offsetMatrix_mHandle.outputValue().setMMatrix(
                        offsetMatrix_mMatrix
                    )

        offsetMatrix_mHandle = data.inputArrayValue(
                DvParentSwitchPlug.offsetMatrix
            )

        hookMatrix_mHandle = data.inputArrayValue(
            DvParentSwitchPlug.hookMatrix
        )

        if hookMatrix_counts != 0:
            offsetMatrix_mHandle.jumpToElement(follow_id)
            offsetMatrix_mMatrix = offsetMatrix_mHandle.inputValue().asMatrix()

            hookMatrix_mHandle.jumpToElement(follow_id)
            hookMatrix_mMatrix = hookMatrix_mHandle.inputValue().asMatrix()

            final_mMatrix = offsetMatrix_mMatrix * hookMatrix_mMatrix * \
                parentInverseMatrix_mMatrix

            transforms = self.decompose_matrix(final_mMatrix)
        else:
            transforms = [0, 0, 0], [0, 0, 0], [1, 1, 1]

        # OUTPUTS
        xform_handle = data.outputValue(self.xform)

        # Set output shoulder
        out_tr = xform_handle.child(
                DvParentSwitchPlug.translate
            )
        out_tr.set3Double(
                transforms[0][0],
                transforms[0][1],
                transforms[0][2]
            )

        out_rot = xform_handle.child(
                DvParentSwitchPlug.rotate
            )
        out_rot.set3Double(
                transforms[1][0],
                transforms[1][1],
                transforms[1][2]
            )

        out_scl = xform_handle.child(
                DvParentSwitchPlug.scale
            )
        out_scl.set3Double(
                transforms[2][0],
                transforms[2][1],
                transforms[2][2]
            )

        xform_handle.setClean()

        data.setClean(plug)

        return True


def creator():
    return OpenMayaMPx.asMPxPtr(DvParentSwitchPlug())


def initialize():
    nAttr = OpenMaya.MFnNumericAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
    cAttr = OpenMaya.MFnCompoundAttribute()
    uAttr = OpenMaya.MFnUnitAttribute()

    # INPUTS
    DvParentSwitchPlug.rigMode = nAttr.create(
            "rigMode",
            "rigmode",
            OpenMaya.MFnNumericData.kBoolean,
            True
        )
    nAttr.setWritable(True)
    nAttr.setStorable(True)
    DvParentSwitchPlug.addAttribute(DvParentSwitchPlug.rigMode)

    DvParentSwitchPlug.followID = nAttr.create(
            "followID",
            "flwid",
            OpenMaya.MFnNumericData.kInt,
            0
        )
    nAttr.setWritable(True)
    nAttr.setStorable(True)
    DvParentSwitchPlug.addAttribute(DvParentSwitchPlug.followID)

    DvParentSwitchPlug.targetMatrix = mAttr.create(
            "targetMatrix",
            "trgtmat"
        )
    mAttr.setStorable(True)
    DvParentSwitchPlug.addAttribute(DvParentSwitchPlug.targetMatrix)

    DvParentSwitchPlug.hookMatrix = mAttr.create(
            "hookMatrix",
            "hookmat"
        )
    mAttr.setArray(True)
    mAttr.setStorable(True)
    DvParentSwitchPlug.addAttribute(DvParentSwitchPlug.hookMatrix)

    DvParentSwitchPlug.parentInverseMatrix = mAttr.create(
            "parentInverseMatrix",
            "pim"
        )
    mAttr.setStorable(False)
    DvParentSwitchPlug.addAttribute(DvParentSwitchPlug.parentInverseMatrix)

    DvParentSwitchPlug.offsetMatrix = mAttr.create(
            "offsetMatrix",
            "offm"
        )
    mAttr.setArray(True)
    mAttr.setStorable(False)
    mAttr.setUsesArrayDataBuilder(True)
    DvParentSwitchPlug.addAttribute(DvParentSwitchPlug.offsetMatrix)

    # OUTPUTS
    # Translate
    DvParentSwitchPlug.translateX = nAttr.create(
        "translateX",
        "tx",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvParentSwitchPlug.translateY = nAttr.create(
        "translateY",
        "ty",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvParentSwitchPlug.translateZ = nAttr.create(
        "translateZ",
        "tz",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvParentSwitchPlug.translate = nAttr.create(
        "translate",   "t",
        DvParentSwitchPlug.translateX,
        DvParentSwitchPlug.translateY,
        DvParentSwitchPlug.translateZ
    )
    nAttr.setStorable(False)

    # Rotate
    DvParentSwitchPlug.rotateX = uAttr.create(
        "rotateX",
        "rx",
        OpenMaya.MFnUnitAttribute.kAngle,
        0.0
    )
    DvParentSwitchPlug.rotateY = uAttr.create(
        "rotateY",
        "ry",
        OpenMaya.MFnUnitAttribute.kAngle,
        0.0
    )
    DvParentSwitchPlug.rotateZ = uAttr.create(
        "rotateZ",
        "rz",
        OpenMaya.MFnUnitAttribute.kAngle,
        0.0
    )
    DvParentSwitchPlug.rotate = nAttr.create(
        "rotate",   "r",
        DvParentSwitchPlug.rotateX,
        DvParentSwitchPlug.rotateY,
        DvParentSwitchPlug.rotateZ
    )
    nAttr.setStorable(False)

    # Scale
    DvParentSwitchPlug.scaleX = nAttr.create(
        "scaleX",
        "sx",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvParentSwitchPlug.scaleY = nAttr.create(
        "scaleY",
        "sy",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvParentSwitchPlug.scaleZ = nAttr.create(
        "scaleZ",
        "sz",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvParentSwitchPlug.scale = nAttr.create(
        "scale",   "s",
        DvParentSwitchPlug.scaleX,
        DvParentSwitchPlug.scaleY,
        DvParentSwitchPlug.scaleZ
    )
    nAttr.setStorable(False)

    DvParentSwitchPlug.xform = cAttr.create("xform", "xf")
    cAttr.addChild(DvParentSwitchPlug.translate)
    cAttr.addChild(DvParentSwitchPlug.rotate)
    cAttr.addChild(DvParentSwitchPlug.scale)
    DvParentSwitchPlug.addAttribute(DvParentSwitchPlug.xform)

    # Attribut affect
    DvParentSwitchPlug.attributeAffects(
            DvParentSwitchPlug.rigMode,
            DvParentSwitchPlug.xform
        )

    DvParentSwitchPlug.attributeAffects(
            DvParentSwitchPlug.targetMatrix,
            DvParentSwitchPlug.xform
        )

    DvParentSwitchPlug.attributeAffects(
            DvParentSwitchPlug.hookMatrix,
            DvParentSwitchPlug.xform
        )

    DvParentSwitchPlug.attributeAffects(
            DvParentSwitchPlug.hookMatrix,
            DvParentSwitchPlug.offsetMatrix
        )

    DvParentSwitchPlug.attributeAffects(
            DvParentSwitchPlug.followID,
            DvParentSwitchPlug.xform
        )

    DvParentSwitchPlug.attributeAffects(
            DvParentSwitchPlug.parentInverseMatrix,
            DvParentSwitchPlug.xform
        )


def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, "damsOLabo", "1.0", "Any")
    try:
        plugin.registerNode(
                DvParentSwitchPlug.kname,
                DvParentSwitchPlug.kplugin_id,
                creator,
                initialize
            )
    except:
        raise RuntimeError, "Failed to register node: '{}'".format(
                DvParentSwitchPlug.kname
            )


def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(DvParentSwitchPlug.kplugin_id)
    except:
        raise RuntimeError, "Failed to register node: '{}'".format(
                DvParentSwitchPlug.kname
            )
