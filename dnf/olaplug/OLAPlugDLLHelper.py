import os
from ctypes import *


# 接口参数定义
class OLAPlugDLLHelper:
    DLL = "OLAPlug_x64.dll"

    # 回调函数持久化使用
    callbacks = {}

    _dll = WinDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), DLL))
    HotkeyCallback = WINFUNCTYPE(c_int32, c_int32, c_int32)
    MouseCallback = WINFUNCTYPE(None, c_int32, c_int32, c_int32, c_int32)
    MouseWheelCallback = WINFUNCTYPE(None, c_int32, c_int32, c_int32, c_int32)
    MouseMoveCallback = WINFUNCTYPE(None, c_int32, c_int32)
    MouseDragCallback = WINFUNCTYPE(None, c_int32, c_int32)
    DrawGuiButtonCallback = WINFUNCTYPE(None, c_int64)
    DrawGuiMouseCallback = WINFUNCTYPE(None, c_int64, c_int32, c_int32, c_int32)

    _dll.CreateCOLAPlugInterFace.argtypes = []
    _dll.CreateCOLAPlugInterFace.restype = c_int64

    @classmethod
    def CreateCOLAPlugInterFace(cls):
        return cls._dll.CreateCOLAPlugInterFace()

    _dll.DestroyCOLAPlugInterFace.argtypes = [c_int64]
    _dll.DestroyCOLAPlugInterFace.restype = c_int

    @classmethod
    def DestroyCOLAPlugInterFace(cls, instance):
        return cls._dll.DestroyCOLAPlugInterFace(instance)

    _dll.Ver.argtypes = []
    _dll.Ver.restype = c_int64

    @classmethod
    def Ver(cls):
        return cls._dll.Ver()

    _dll.GetPlugInfo.argtypes = [c_int]
    _dll.GetPlugInfo.restype = c_int64

    @classmethod
    def GetPlugInfo(cls, _type):
        return cls._dll.GetPlugInfo(_type)

    _dll.SetPath.argtypes = [c_int64, c_char_p]
    _dll.SetPath.restype = c_int

    @classmethod
    def SetPath(cls, instance, path):
        return cls._dll.SetPath(instance, path.encode("utf-8"))

    _dll.GetPath.argtypes = [c_int64]
    _dll.GetPath.restype = c_int64

    @classmethod
    def GetPath(cls, instance):
        return cls._dll.GetPath(instance)

    _dll.GetMachineCode.argtypes = [c_int64]
    _dll.GetMachineCode.restype = c_int64

    @classmethod
    def GetMachineCode(cls, instance):
        return cls._dll.GetMachineCode(instance)

    _dll.GetBasePath.argtypes = [c_int64]
    _dll.GetBasePath.restype = c_int64

    @classmethod
    def GetBasePath(cls, instance):
        return cls._dll.GetBasePath(instance)

    _dll.Reg.argtypes = [c_char_p, c_char_p, c_char_p]
    _dll.Reg.restype = c_int

    @classmethod
    def Reg(cls, userCode, softCode, featureList):
        return cls._dll.Reg(userCode.encode("utf-8"), softCode.encode("utf-8"), featureList.encode("utf-8"))

    _dll.BindWindow.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_char_p, c_int]
    _dll.BindWindow.restype = c_int

    @classmethod
    def BindWindow(cls, instance, hwnd, display, mouse, keypad, mode):
        return cls._dll.BindWindow(
            instance, hwnd, display.encode("utf-8"), mouse.encode("utf-8"), keypad.encode("utf-8"), mode
        )

    _dll.BindWindowEx.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
    _dll.BindWindowEx.restype = c_int

    @classmethod
    def BindWindowEx(cls, instance, hwnd, display, mouse, keypad, pubstr, mode):
        return cls._dll.BindWindowEx(
            instance,
            hwnd,
            display.encode("utf-8"),
            mouse.encode("utf-8"),
            keypad.encode("utf-8"),
            pubstr.encode("utf-8"),
            mode,
        )

    _dll.UnBindWindow.argtypes = [c_int64]
    _dll.UnBindWindow.restype = c_int

    @classmethod
    def UnBindWindow(cls, instance):
        return cls._dll.UnBindWindow(instance)

    _dll.GetBindWindow.argtypes = [c_int64]
    _dll.GetBindWindow.restype = c_int64

    @classmethod
    def GetBindWindow(cls, instance):
        return cls._dll.GetBindWindow(instance)

    _dll.ReleaseWindowsDll.argtypes = [c_int64, c_int64]
    _dll.ReleaseWindowsDll.restype = c_int

    @classmethod
    def ReleaseWindowsDll(cls, instance, hwnd):
        return cls._dll.ReleaseWindowsDll(instance, hwnd)

    _dll.FreeStringPtr.argtypes = [c_int64]
    _dll.FreeStringPtr.restype = c_int

    @classmethod
    def FreeStringPtr(cls, ptr):
        return cls._dll.FreeStringPtr(ptr)

    _dll.FreeMemoryPtr.argtypes = [c_int64]
    _dll.FreeMemoryPtr.restype = c_int

    @classmethod
    def FreeMemoryPtr(cls, ptr):
        return cls._dll.FreeMemoryPtr(ptr)

    _dll.GetStringSize.argtypes = [c_int64]
    _dll.GetStringSize.restype = c_int

    @classmethod
    def GetStringSize(cls, ptr):
        return cls._dll.GetStringSize(ptr)

    _dll.GetStringFromPtr.argtypes = [c_int64, c_char_p, c_int]
    _dll.GetStringFromPtr.restype = c_int

    @classmethod
    def GetStringFromPtr(cls, ptr, lpString, size):
        return cls._dll.GetStringFromPtr(ptr, lpString.encode("utf-8"), size)

    _dll.Delay.argtypes = [c_int]
    _dll.Delay.restype = c_int

    @classmethod
    def Delay(cls, millisecond):
        return cls._dll.Delay(millisecond)

    _dll.Delays.argtypes = [c_int, c_int]
    _dll.Delays.restype = c_int

    @classmethod
    def Delays(cls, minMillisecond, maxMillisecond):
        return cls._dll.Delays(minMillisecond, maxMillisecond)

    _dll.SetUAC.argtypes = [c_int64, c_int]
    _dll.SetUAC.restype = c_int

    @classmethod
    def SetUAC(cls, instance, enable):
        return cls._dll.SetUAC(instance, enable)

    _dll.CheckUAC.argtypes = [c_int64]
    _dll.CheckUAC.restype = c_int

    @classmethod
    def CheckUAC(cls, instance):
        return cls._dll.CheckUAC(instance)

    _dll.RunApp.argtypes = [c_int64, c_char_p, c_int]
    _dll.RunApp.restype = c_int

    @classmethod
    def RunApp(cls, instance, appPath, mode):
        return cls._dll.RunApp(instance, appPath.encode("utf-8"), mode)

    _dll.ExecuteCmd.argtypes = [c_int64, c_char_p, c_char_p, c_int]
    _dll.ExecuteCmd.restype = c_int64

    @classmethod
    def ExecuteCmd(cls, instance, cmd, current_dir, time_out):
        return cls._dll.ExecuteCmd(instance, cmd.encode("utf-8"), current_dir.encode("utf-8"), time_out)

    _dll.GetConfig.argtypes = [c_int64, c_char_p]
    _dll.GetConfig.restype = c_int64

    @classmethod
    def GetConfig(cls, instance, configKey):
        return cls._dll.GetConfig(instance, configKey.encode("utf-8"))

    _dll.SetConfig.argtypes = [c_int64, c_char_p]
    _dll.SetConfig.restype = c_int

    @classmethod
    def SetConfig(cls, instance, configStr):
        return cls._dll.SetConfig(instance, configStr.encode("utf-8"))

    _dll.SetConfigByKey.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.SetConfigByKey.restype = c_int

    @classmethod
    def SetConfigByKey(cls, instance, key, value):
        return cls._dll.SetConfigByKey(instance, key.encode("utf-8"), value.encode("utf-8"))

    _dll.SendDropFiles.argtypes = [c_int64, c_int64, c_char_p]
    _dll.SendDropFiles.restype = c_int

    @classmethod
    def SendDropFiles(cls, instance, hwnd, file_path):
        return cls._dll.SendDropFiles(instance, hwnd, file_path.encode("utf-8"))

    _dll.SetDefaultEncode.argtypes = [c_int, c_int]
    _dll.SetDefaultEncode.restype = c_int

    @classmethod
    def SetDefaultEncode(cls, inputEncoding, outputEncoding):
        return cls._dll.SetDefaultEncode(inputEncoding, outputEncoding)

    _dll.GetLastError.argtypes = []
    _dll.GetLastError.restype = c_int

    @classmethod
    def GetLastError(cls):
        return cls._dll.GetLastError()

    _dll.GetLastErrorString.argtypes = []
    _dll.GetLastErrorString.restype = c_int64

    @classmethod
    def GetLastErrorString(cls):
        return cls._dll.GetLastErrorString()

    _dll.HideModule.argtypes = [c_int64, c_char_p]
    _dll.HideModule.restype = c_int64

    @classmethod
    def HideModule(cls, instance, moduleName):
        return cls._dll.HideModule(instance, moduleName.encode("utf-8"))

    _dll.UnhideModule.argtypes = [c_int64, c_int64]
    _dll.UnhideModule.restype = c_int

    @classmethod
    def UnhideModule(cls, instance, ctx):
        return cls._dll.UnhideModule(instance, ctx)

    _dll.GetRandomNumber.argtypes = [c_int64, c_int, c_int]
    _dll.GetRandomNumber.restype = c_int

    @classmethod
    def GetRandomNumber(cls, instance, _min, _max):
        return cls._dll.GetRandomNumber(instance, _min, _max)

    _dll.GetRandomDouble.argtypes = [c_int64, c_double, c_double]
    _dll.GetRandomDouble.restype = c_double

    @classmethod
    def GetRandomDouble(cls, instance, _min, _max):
        return cls._dll.GetRandomDouble(instance, _min, _max)

    _dll.ExcludePos.argtypes = [c_int64, c_char_p, c_int, c_int, c_int, c_int, c_int]
    _dll.ExcludePos.restype = c_int64

    @classmethod
    def ExcludePos(cls, instance, _json, _type, x1, y1, x2, y2):
        return cls._dll.ExcludePos(instance, _json.encode("utf-8"), _type, x1, y1, x2, y2)

    _dll.FindNearestPos.argtypes = [c_int64, c_char_p, c_int, c_int, c_int]
    _dll.FindNearestPos.restype = c_int64

    @classmethod
    def FindNearestPos(cls, instance, _json, _type, x, y):
        return cls._dll.FindNearestPos(instance, _json.encode("utf-8"), _type, x, y)

    _dll.SortPosDistance.argtypes = [c_int64, c_char_p, c_int, c_int, c_int]
    _dll.SortPosDistance.restype = c_int64

    @classmethod
    def SortPosDistance(cls, instance, _json, _type, x, y):
        return cls._dll.SortPosDistance(instance, _json.encode("utf-8"), _type, x, y)

    _dll.GetDenseRect.argtypes = [
        c_int64,
        c_int64,
        c_int,
        c_int,
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_int),
    ]
    _dll.GetDenseRect.restype = c_int

    @classmethod
    def GetDenseRect(cls, instance, image, width, height, x1=None, y1=None, x2=None, y2=None):
        x1 = c_int(0)
        y1 = c_int(0)
        x2 = c_int(0)
        y2 = c_int(0)
        result = cls._dll.GetDenseRect(instance, image, width, height, byref(x1), byref(y1), byref(x2), byref(y2))
        return result, x1.value, y1.value, x2.value, y2.value

    _dll.PathPlanning.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int, c_double, c_double]
    _dll.PathPlanning.restype = c_int64

    @classmethod
    def PathPlanning(cls, instance, image, startX, startY, endX, endY, potentialRadius, searchRadius):
        return cls._dll.PathPlanning(instance, image, startX, startY, endX, endY, potentialRadius, searchRadius)

    _dll.CreateGraph.argtypes = [c_int64, c_char_p]
    _dll.CreateGraph.restype = c_int64

    @classmethod
    def CreateGraph(cls, instance, _json):
        return cls._dll.CreateGraph(instance, _json.encode("utf-8"))

    _dll.GetGraph.argtypes = [c_int64, c_int64]
    _dll.GetGraph.restype = c_int64

    @classmethod
    def GetGraph(cls, instance, graphPtr):
        return cls._dll.GetGraph(instance, graphPtr)

    _dll.AddEdge.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_double, c_bool]
    _dll.AddEdge.restype = c_int

    @classmethod
    def AddEdge(cls, instance, graphPtr, _from, to, weight, isDirected):
        return cls._dll.AddEdge(instance, graphPtr, _from.encode("utf-8"), to.encode("utf-8"), weight, isDirected)

    _dll.GetShortestPath.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.GetShortestPath.restype = c_int64

    @classmethod
    def GetShortestPath(cls, instance, graphPtr, _from, to):
        return cls._dll.GetShortestPath(instance, graphPtr, _from.encode("utf-8"), to.encode("utf-8"))

    _dll.GetShortestDistance.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.GetShortestDistance.restype = c_double

    @classmethod
    def GetShortestDistance(cls, instance, graphPtr, _from, to):
        return cls._dll.GetShortestDistance(instance, graphPtr, _from.encode("utf-8"), to.encode("utf-8"))

    _dll.ClearGraph.argtypes = [c_int64, c_int64]
    _dll.ClearGraph.restype = c_int

    @classmethod
    def ClearGraph(cls, instance, graphPtr):
        return cls._dll.ClearGraph(instance, graphPtr)

    _dll.DeleteGraph.argtypes = [c_int64, c_int64]
    _dll.DeleteGraph.restype = c_int

    @classmethod
    def DeleteGraph(cls, instance, graphPtr):
        return cls._dll.DeleteGraph(instance, graphPtr)

    _dll.GetNodeCount.argtypes = [c_int64, c_int64]
    _dll.GetNodeCount.restype = c_int

    @classmethod
    def GetNodeCount(cls, instance, graphPtr):
        return cls._dll.GetNodeCount(instance, graphPtr)

    _dll.GetEdgeCount.argtypes = [c_int64, c_int64]
    _dll.GetEdgeCount.restype = c_int

    @classmethod
    def GetEdgeCount(cls, instance, graphPtr):
        return cls._dll.GetEdgeCount(instance, graphPtr)

    _dll.GetShortestPathToAllNodes.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetShortestPathToAllNodes.restype = c_int64

    @classmethod
    def GetShortestPathToAllNodes(cls, instance, graphPtr, startNode):
        return cls._dll.GetShortestPathToAllNodes(instance, graphPtr, startNode.encode("utf-8"))

    _dll.GetMinimumSpanningTree.argtypes = [c_int64, c_int64]
    _dll.GetMinimumSpanningTree.restype = c_int64

    @classmethod
    def GetMinimumSpanningTree(cls, instance, graphPtr):
        return cls._dll.GetMinimumSpanningTree(instance, graphPtr)

    _dll.GetDirectedPathToAllNodes.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetDirectedPathToAllNodes.restype = c_int64

    @classmethod
    def GetDirectedPathToAllNodes(cls, instance, graphPtr, startNode):
        return cls._dll.GetDirectedPathToAllNodes(instance, graphPtr, startNode.encode("utf-8"))

    _dll.GetMinimumArborescence.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetMinimumArborescence.restype = c_int64

    @classmethod
    def GetMinimumArborescence(cls, instance, graphPtr, root):
        return cls._dll.GetMinimumArborescence(instance, graphPtr, root.encode("utf-8"))

    _dll.CreateGraphFromCoordinates.argtypes = [c_int64, c_char_p, c_bool, c_double, c_bool]
    _dll.CreateGraphFromCoordinates.restype = c_int64

    @classmethod
    def CreateGraphFromCoordinates(cls, instance, _json, connectAll, maxDistance, useEuclideanDistance):
        return cls._dll.CreateGraphFromCoordinates(
            instance, _json.encode("utf-8"), connectAll, maxDistance, useEuclideanDistance
        )

    _dll.AddCoordinateNode.argtypes = [c_int64, c_int64, c_char_p, c_double, c_double, c_bool, c_double, c_bool]
    _dll.AddCoordinateNode.restype = c_int

    @classmethod
    def AddCoordinateNode(cls, instance, graphPtr, name, x, y, connectToExisting, maxDistance, useEuclideanDistance):
        return cls._dll.AddCoordinateNode(
            instance, graphPtr, name.encode("utf-8"), x, y, connectToExisting, maxDistance, useEuclideanDistance
        )

    _dll.GetNodeCoordinates.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetNodeCoordinates.restype = c_int64

    @classmethod
    def GetNodeCoordinates(cls, instance, graphPtr, name):
        return cls._dll.GetNodeCoordinates(instance, graphPtr, name.encode("utf-8"))

    _dll.SetNodeConnection.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_bool, c_double]
    _dll.SetNodeConnection.restype = c_int

    @classmethod
    def SetNodeConnection(cls, instance, graphPtr, _from, to, canConnect, weight):
        return cls._dll.SetNodeConnection(
            instance, graphPtr, _from.encode("utf-8"), to.encode("utf-8"), canConnect, weight
        )

    _dll.GetNodeConnectionStatus.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.GetNodeConnectionStatus.restype = c_int

    @classmethod
    def GetNodeConnectionStatus(cls, instance, graphPtr, _from, to):
        return cls._dll.GetNodeConnectionStatus(instance, graphPtr, _from.encode("utf-8"), to.encode("utf-8"))

    _dll.AsmCall.argtypes = [c_int64, c_int64, c_char_p, c_int, c_int64]
    _dll.AsmCall.restype = c_int64

    @classmethod
    def AsmCall(cls, instance, hwnd, asmStr, _type, baseAddr):
        return cls._dll.AsmCall(instance, hwnd, asmStr.encode("utf-8"), _type, baseAddr)

    _dll.Assemble.argtypes = [c_int64, c_char_p, c_int64, c_int, c_int]
    _dll.Assemble.restype = c_int64

    @classmethod
    def Assemble(cls, instance, asmStr, baseAddr, arch, mode):
        return cls._dll.Assemble(instance, asmStr.encode("utf-8"), baseAddr, arch, mode)

    _dll.Disassemble.argtypes = [c_int64, c_char_p, c_int64, c_int, c_int, c_int]
    _dll.Disassemble.restype = c_int64

    @classmethod
    def Disassemble(cls, instance, asmCode, baseAddr, arch, mode, showType):
        return cls._dll.Disassemble(instance, asmCode.encode("utf-8"), baseAddr, arch, mode, showType)

    _dll.Login.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
    _dll.Login.restype = c_int64

    @classmethod
    def Login(cls, userCode, softCode, featureList, softVersion, dealerCode):
        return cls._dll.Login(
            userCode.encode("utf-8"),
            softCode.encode("utf-8"),
            featureList.encode("utf-8"),
            softVersion.encode("utf-8"),
            dealerCode.encode("utf-8"),
        )

    _dll.Activate.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
    _dll.Activate.restype = c_int64

    @classmethod
    def Activate(cls, userCode, softCode, softVersion, dealerCode, licenseKey):
        return cls._dll.Activate(
            userCode.encode("utf-8"),
            softCode.encode("utf-8"),
            softVersion.encode("utf-8"),
            dealerCode.encode("utf-8"),
            licenseKey.encode("utf-8"),
        )

    _dll.DmaAddDevice.argtypes = [c_int64, c_int]
    _dll.DmaAddDevice.restype = c_int64

    @classmethod
    def DmaAddDevice(cls, instance, vmId):
        return cls._dll.DmaAddDevice(instance, vmId)

    _dll.DmaAddDeviceEx.argtypes = [c_int64, c_char_p]
    _dll.DmaAddDeviceEx.restype = c_int64

    @classmethod
    def DmaAddDeviceEx(cls, instance, connectionString):
        return cls._dll.DmaAddDeviceEx(instance, connectionString.encode("utf-8"))

    _dll.DmaRemoveDevice.argtypes = [c_int64, c_int64]
    _dll.DmaRemoveDevice.restype = c_int

    @classmethod
    def DmaRemoveDevice(cls, instance, deviceId):
        return cls._dll.DmaRemoveDevice(instance, deviceId)

    _dll.DmaGetPidFromName.argtypes = [c_int64, c_int64, c_char_p]
    _dll.DmaGetPidFromName.restype = c_int

    @classmethod
    def DmaGetPidFromName(cls, instance, deviceId, processName):
        return cls._dll.DmaGetPidFromName(instance, deviceId, processName.encode("utf-8"))

    _dll.DmaGetPidList.argtypes = [c_int64, c_int64]
    _dll.DmaGetPidList.restype = c_int64

    @classmethod
    def DmaGetPidList(cls, instance, deviceId):
        return cls._dll.DmaGetPidList(instance, deviceId)

    _dll.DmaGetProcessInfo.argtypes = [c_int64, c_int64, c_int]
    _dll.DmaGetProcessInfo.restype = c_int64

    @classmethod
    def DmaGetProcessInfo(cls, instance, deviceId, pid):
        return cls._dll.DmaGetProcessInfo(instance, deviceId, pid)

    _dll.DmaGetModuleBase.argtypes = [c_int64, c_int64, c_int, c_char_p]
    _dll.DmaGetModuleBase.restype = c_int64

    @classmethod
    def DmaGetModuleBase(cls, instance, deviceId, pid, moduleName):
        return cls._dll.DmaGetModuleBase(instance, deviceId, pid, moduleName.encode("utf-8"))

    _dll.DmaGetModuleSize.argtypes = [c_int64, c_int64, c_int, c_char_p]
    _dll.DmaGetModuleSize.restype = c_int

    @classmethod
    def DmaGetModuleSize(cls, instance, deviceId, pid, moduleName):
        return cls._dll.DmaGetModuleSize(instance, deviceId, pid, moduleName.encode("utf-8"))

    _dll.DmaGetProcAddress.argtypes = [c_int64, c_int64, c_int, c_char_p, c_char_p]
    _dll.DmaGetProcAddress.restype = c_int64

    @classmethod
    def DmaGetProcAddress(cls, instance, deviceId, pid, moduleName, functionName):
        return cls._dll.DmaGetProcAddress(
            instance, deviceId, pid, moduleName.encode("utf-8"), functionName.encode("utf-8")
        )

    _dll.DmaReadInt.argtypes = [c_int64, c_int64, c_int, c_char_p, c_int]
    _dll.DmaReadInt.restype = c_int64

    @classmethod
    def DmaReadInt(cls, instance, deviceId, pid, addr, _type):
        return cls._dll.DmaReadInt(instance, deviceId, pid, addr.encode("utf-8"), _type)

    _dll.DmaReadString.argtypes = [c_int64, c_int64, c_int, c_char_p, c_int, c_int]
    _dll.DmaReadString.restype = c_int64

    @classmethod
    def DmaReadString(cls, instance, deviceId, pid, addr, _type, _len):
        return cls._dll.DmaReadString(instance, deviceId, pid, addr.encode("utf-8"), _type, _len)

    _dll.DmaWriteInt.argtypes = [c_int64, c_int64, c_int, c_char_p, c_int, c_int64]
    _dll.DmaWriteInt.restype = c_int

    @classmethod
    def DmaWriteInt(cls, instance, deviceId, pid, addr, _type, value):
        return cls._dll.DmaWriteInt(instance, deviceId, pid, addr.encode("utf-8"), _type, value)

    _dll.DmaWriteString.argtypes = [c_int64, c_int64, c_int, c_char_p, c_int, c_char_p]
    _dll.DmaWriteString.restype = c_int

    @classmethod
    def DmaWriteString(cls, instance, deviceId, pid, addr, _type, value):
        return cls._dll.DmaWriteString(instance, deviceId, pid, addr.encode("utf-8"), _type, value.encode("utf-8"))

    _dll.DrawGuiCleanup.argtypes = [c_int64]
    _dll.DrawGuiCleanup.restype = c_int

    @classmethod
    def DrawGuiCleanup(cls, instance):
        return cls._dll.DrawGuiCleanup(instance)

    _dll.DrawGuiSetGuiActive.argtypes = [c_int64, c_int]
    _dll.DrawGuiSetGuiActive.restype = c_int

    @classmethod
    def DrawGuiSetGuiActive(cls, instance, active):
        return cls._dll.DrawGuiSetGuiActive(instance, active)

    _dll.DrawGuiIsGuiActive.argtypes = [c_int64]
    _dll.DrawGuiIsGuiActive.restype = c_int

    @classmethod
    def DrawGuiIsGuiActive(cls, instance):
        return cls._dll.DrawGuiIsGuiActive(instance)

    _dll.DrawGuiSetGuiClickThrough.argtypes = [c_int64, c_int]
    _dll.DrawGuiSetGuiClickThrough.restype = c_int

    @classmethod
    def DrawGuiSetGuiClickThrough(cls, instance, enabled):
        return cls._dll.DrawGuiSetGuiClickThrough(instance, enabled)

    _dll.DrawGuiIsGuiClickThrough.argtypes = [c_int64]
    _dll.DrawGuiIsGuiClickThrough.restype = c_int

    @classmethod
    def DrawGuiIsGuiClickThrough(cls, instance):
        return cls._dll.DrawGuiIsGuiClickThrough(instance)

    _dll.DrawGuiRectangle.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_int, c_double]
    _dll.DrawGuiRectangle.restype = c_int64

    @classmethod
    def DrawGuiRectangle(cls, instance, x, y, width, height, mode, lineThickness):
        return cls._dll.DrawGuiRectangle(instance, x, y, width, height, mode, lineThickness)

    _dll.DrawGuiCircle.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_double]
    _dll.DrawGuiCircle.restype = c_int64

    @classmethod
    def DrawGuiCircle(cls, instance, x, y, radius, mode, lineThickness):
        return cls._dll.DrawGuiCircle(instance, x, y, radius, mode, lineThickness)

    _dll.DrawGuiLine.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_double]
    _dll.DrawGuiLine.restype = c_int64

    @classmethod
    def DrawGuiLine(cls, instance, x1, y1, x2, y2, lineThickness):
        return cls._dll.DrawGuiLine(instance, x1, y1, x2, y2, lineThickness)

    _dll.DrawGuiText.argtypes = [c_int64, c_char_p, c_int, c_int, c_char_p, c_int, c_int]
    _dll.DrawGuiText.restype = c_int64

    @classmethod
    def DrawGuiText(cls, instance, text, x, y, fontPath, fontSize, align):
        return cls._dll.DrawGuiText(instance, text.encode("utf-8"), x, y, fontPath.encode("utf-8"), fontSize, align)

    _dll.DrawGuiImage.argtypes = [c_int64, c_char_p, c_int, c_int]
    _dll.DrawGuiImage.restype = c_int64

    @classmethod
    def DrawGuiImage(cls, instance, imagePath, x, y):
        return cls._dll.DrawGuiImage(instance, imagePath.encode("utf-8"), x, y)

    _dll.DrawGuiImagePtr.argtypes = [c_int64, c_int64, c_int, c_int]
    _dll.DrawGuiImagePtr.restype = c_int64

    @classmethod
    def DrawGuiImagePtr(cls, instance, imagePtr, x, y):
        return cls._dll.DrawGuiImagePtr(instance, imagePtr, x, y)

    _dll.DrawGuiWindow.argtypes = [c_int64, c_char_p, c_int, c_int, c_int, c_int, c_int]
    _dll.DrawGuiWindow.restype = c_int64

    @classmethod
    def DrawGuiWindow(cls, instance, title, x, y, width, height, style):
        return cls._dll.DrawGuiWindow(instance, title.encode("utf-8"), x, y, width, height, style)

    _dll.DrawGuiPanel.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int]
    _dll.DrawGuiPanel.restype = c_int64

    @classmethod
    def DrawGuiPanel(cls, instance, parentHandle, x, y, width, height):
        return cls._dll.DrawGuiPanel(instance, parentHandle, x, y, width, height)

    _dll.DrawGuiButton.argtypes = [c_int64, c_int64, c_char_p, c_int, c_int, c_int, c_int]
    _dll.DrawGuiButton.restype = c_int64

    @classmethod
    def DrawGuiButton(cls, instance, parentHandle, text, x, y, width, height):
        return cls._dll.DrawGuiButton(instance, parentHandle, text.encode("utf-8"), x, y, width, height)

    _dll.DrawGuiSetPosition.argtypes = [c_int64, c_int64, c_int, c_int]
    _dll.DrawGuiSetPosition.restype = c_int

    @classmethod
    def DrawGuiSetPosition(cls, instance, handle, x, y):
        return cls._dll.DrawGuiSetPosition(instance, handle, x, y)

    _dll.DrawGuiSetSize.argtypes = [c_int64, c_int64, c_int, c_int]
    _dll.DrawGuiSetSize.restype = c_int

    @classmethod
    def DrawGuiSetSize(cls, instance, handle, width, height):
        return cls._dll.DrawGuiSetSize(instance, handle, width, height)

    _dll.DrawGuiSetColor.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int]
    _dll.DrawGuiSetColor.restype = c_int

    @classmethod
    def DrawGuiSetColor(cls, instance, handle, r, g, b, a):
        return cls._dll.DrawGuiSetColor(instance, handle, r, g, b, a)

    _dll.DrawGuiSetAlpha.argtypes = [c_int64, c_int64, c_int]
    _dll.DrawGuiSetAlpha.restype = c_int

    @classmethod
    def DrawGuiSetAlpha(cls, instance, handle, alpha):
        return cls._dll.DrawGuiSetAlpha(instance, handle, alpha)

    _dll.DrawGuiSetDrawMode.argtypes = [c_int64, c_int64, c_int]
    _dll.DrawGuiSetDrawMode.restype = c_int

    @classmethod
    def DrawGuiSetDrawMode(cls, instance, handle, mode):
        return cls._dll.DrawGuiSetDrawMode(instance, handle, mode)

    _dll.DrawGuiSetLineThickness.argtypes = [c_int64, c_int64, c_double]
    _dll.DrawGuiSetLineThickness.restype = c_int

    @classmethod
    def DrawGuiSetLineThickness(cls, instance, handle, thickness):
        return cls._dll.DrawGuiSetLineThickness(instance, handle, thickness)

    _dll.DrawGuiSetFont.argtypes = [c_int64, c_int64, c_char_p, c_int]
    _dll.DrawGuiSetFont.restype = c_int

    @classmethod
    def DrawGuiSetFont(cls, instance, handle, fontPath, fontSize):
        return cls._dll.DrawGuiSetFont(instance, handle, fontPath.encode("utf-8"), fontSize)

    _dll.DrawGuiSetTextAlign.argtypes = [c_int64, c_int64, c_int]
    _dll.DrawGuiSetTextAlign.restype = c_int

    @classmethod
    def DrawGuiSetTextAlign(cls, instance, handle, align):
        return cls._dll.DrawGuiSetTextAlign(instance, handle, align)

    _dll.DrawGuiSetText.argtypes = [c_int64, c_int64, c_char_p]
    _dll.DrawGuiSetText.restype = c_int

    @classmethod
    def DrawGuiSetText(cls, instance, handle, text):
        return cls._dll.DrawGuiSetText(instance, handle, text.encode("utf-8"))

    _dll.DrawGuiSetWindowTitle.argtypes = [c_int64, c_int64, c_char_p]
    _dll.DrawGuiSetWindowTitle.restype = c_int

    @classmethod
    def DrawGuiSetWindowTitle(cls, instance, handle, title):
        return cls._dll.DrawGuiSetWindowTitle(instance, handle, title.encode("utf-8"))

    _dll.DrawGuiSetWindowStyle.argtypes = [c_int64, c_int64, c_int]
    _dll.DrawGuiSetWindowStyle.restype = c_int

    @classmethod
    def DrawGuiSetWindowStyle(cls, instance, handle, style):
        return cls._dll.DrawGuiSetWindowStyle(instance, handle, style)

    _dll.DrawGuiSetWindowTopMost.argtypes = [c_int64, c_int64, c_int]
    _dll.DrawGuiSetWindowTopMost.restype = c_int

    @classmethod
    def DrawGuiSetWindowTopMost(cls, instance, handle, topMost):
        return cls._dll.DrawGuiSetWindowTopMost(instance, handle, topMost)

    _dll.DrawGuiSetWindowTransparency.argtypes = [c_int64, c_int64, c_int]
    _dll.DrawGuiSetWindowTransparency.restype = c_int

    @classmethod
    def DrawGuiSetWindowTransparency(cls, instance, handle, alpha):
        return cls._dll.DrawGuiSetWindowTransparency(instance, handle, alpha)

    _dll.DrawGuiDeleteObject.argtypes = [c_int64, c_int64]
    _dll.DrawGuiDeleteObject.restype = c_int

    @classmethod
    def DrawGuiDeleteObject(cls, instance, handle):
        return cls._dll.DrawGuiDeleteObject(instance, handle)

    _dll.DrawGuiClearAll.argtypes = [c_int64]
    _dll.DrawGuiClearAll.restype = c_int

    @classmethod
    def DrawGuiClearAll(cls, instance):
        return cls._dll.DrawGuiClearAll(instance)

    _dll.DrawGuiSetVisible.argtypes = [c_int64, c_int64, c_int]
    _dll.DrawGuiSetVisible.restype = c_int

    @classmethod
    def DrawGuiSetVisible(cls, instance, handle, visible):
        return cls._dll.DrawGuiSetVisible(instance, handle, visible)

    _dll.DrawGuiSetZOrder.argtypes = [c_int64, c_int64, c_int]
    _dll.DrawGuiSetZOrder.restype = c_int

    @classmethod
    def DrawGuiSetZOrder(cls, instance, handle, zOrder):
        return cls._dll.DrawGuiSetZOrder(instance, handle, zOrder)

    _dll.DrawGuiSetParent.argtypes = [c_int64, c_int64, c_int64]
    _dll.DrawGuiSetParent.restype = c_int

    @classmethod
    def DrawGuiSetParent(cls, instance, handle, parentHandle):
        return cls._dll.DrawGuiSetParent(instance, handle, parentHandle)

    _dll.DrawGuiSetButtonCallback.argtypes = [c_int64, c_int64, DrawGuiButtonCallback]
    _dll.DrawGuiSetButtonCallback.restype = c_int

    @classmethod
    def DrawGuiSetButtonCallback(cls, instance, handle, callback):
        callback = cls.DrawGuiButtonCallback(callback)
        key = f"DrawGuiSetButtonCallback_{instance}_{handle}"
        cls.callbacks[key] = callback
        return cls._dll.DrawGuiSetButtonCallback(instance, handle, callback)

    _dll.DrawGuiSetMouseCallback.argtypes = [c_int64, c_int64, DrawGuiMouseCallback]
    _dll.DrawGuiSetMouseCallback.restype = c_int

    @classmethod
    def DrawGuiSetMouseCallback(cls, instance, handle, callback):
        callback = cls.DrawGuiMouseCallback(callback)
        key = f"DrawGuiSetMouseCallback_{instance}_{handle}"
        cls.callbacks[key] = callback
        return cls._dll.DrawGuiSetMouseCallback(instance, handle, callback)

    _dll.DrawGuiGetDrawObjectType.argtypes = [c_int64, c_int64]
    _dll.DrawGuiGetDrawObjectType.restype = c_int

    @classmethod
    def DrawGuiGetDrawObjectType(cls, instance, handle):
        return cls._dll.DrawGuiGetDrawObjectType(instance, handle)

    _dll.DrawGuiGetPosition.argtypes = [c_int64, c_int64, POINTER(c_int), POINTER(c_int)]
    _dll.DrawGuiGetPosition.restype = c_int

    @classmethod
    def DrawGuiGetPosition(cls, instance, handle, x=None, y=None):
        x = c_int(0)
        y = c_int(0)
        result = cls._dll.DrawGuiGetPosition(instance, handle, byref(x), byref(y))
        return result, x.value, y.value

    _dll.DrawGuiGetSize.argtypes = [c_int64, c_int64, POINTER(c_int), POINTER(c_int)]
    _dll.DrawGuiGetSize.restype = c_int

    @classmethod
    def DrawGuiGetSize(cls, instance, handle, width=None, height=None):
        width = c_int(0)
        height = c_int(0)
        result = cls._dll.DrawGuiGetSize(instance, handle, byref(width), byref(height))
        return result, width.value, height.value

    _dll.DrawGuiIsPointInObject.argtypes = [c_int64, c_int64, c_int, c_int]
    _dll.DrawGuiIsPointInObject.restype = c_int

    @classmethod
    def DrawGuiIsPointInObject(cls, instance, handle, x, y):
        return cls._dll.DrawGuiIsPointInObject(instance, handle, x, y)

    _dll.SetMemoryMode.argtypes = [c_int64, c_int]
    _dll.SetMemoryMode.restype = c_int

    @classmethod
    def SetMemoryMode(cls, instance, mode):
        return cls._dll.SetMemoryMode(instance, mode)

    _dll.ExportDriver.argtypes = [c_int64, c_char_p, c_int]
    _dll.ExportDriver.restype = c_int

    @classmethod
    def ExportDriver(cls, instance, driver_path, _type):
        return cls._dll.ExportDriver(instance, driver_path.encode("utf-8"), _type)

    _dll.LoadDriver.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.LoadDriver.restype = c_int

    @classmethod
    def LoadDriver(cls, instance, driver_name, driver_path):
        return cls._dll.LoadDriver(instance, driver_name.encode("utf-8"), driver_path.encode("utf-8"))

    _dll.UnloadDriver.argtypes = [c_int64, c_char_p]
    _dll.UnloadDriver.restype = c_int

    @classmethod
    def UnloadDriver(cls, instance, driver_name):
        return cls._dll.UnloadDriver(instance, driver_name.encode("utf-8"))

    _dll.DriverTest.argtypes = [c_int64]
    _dll.DriverTest.restype = c_int

    @classmethod
    def DriverTest(cls, instance):
        return cls._dll.DriverTest(instance)

    _dll.LoadPdb.argtypes = [c_int64]
    _dll.LoadPdb.restype = c_int

    @classmethod
    def LoadPdb(cls, instance):
        return cls._dll.LoadPdb(instance)

    _dll.HideProcess.argtypes = [c_int64, c_int64, c_int]
    _dll.HideProcess.restype = c_int

    @classmethod
    def HideProcess(cls, instance, pid, enable):
        return cls._dll.HideProcess(instance, pid, enable)

    _dll.ProtectProcess.argtypes = [c_int64, c_int64, c_int]
    _dll.ProtectProcess.restype = c_int

    @classmethod
    def ProtectProcess(cls, instance, pid, enable):
        return cls._dll.ProtectProcess(instance, pid, enable)

    _dll.ProtectProcess2.argtypes = [c_int64, c_int64, c_int]
    _dll.ProtectProcess2.restype = c_int

    @classmethod
    def ProtectProcess2(cls, instance, pid, enable):
        return cls._dll.ProtectProcess2(instance, pid, enable)

    _dll.AddProtectPID.argtypes = [c_int64, c_int64, c_int64, c_int64]
    _dll.AddProtectPID.restype = c_int

    @classmethod
    def AddProtectPID(cls, instance, pid, mode, allow_pid):
        return cls._dll.AddProtectPID(instance, pid, mode, allow_pid)

    _dll.RemoveProtectPID.argtypes = [c_int64, c_int64]
    _dll.RemoveProtectPID.restype = c_int

    @classmethod
    def RemoveProtectPID(cls, instance, pid):
        return cls._dll.RemoveProtectPID(instance, pid)

    _dll.AddAllowPID.argtypes = [c_int64, c_int64]
    _dll.AddAllowPID.restype = c_int

    @classmethod
    def AddAllowPID(cls, instance, pid):
        return cls._dll.AddAllowPID(instance, pid)

    _dll.RemoveAllowPID.argtypes = [c_int64, c_int64]
    _dll.RemoveAllowPID.restype = c_int

    @classmethod
    def RemoveAllowPID(cls, instance, pid):
        return cls._dll.RemoveAllowPID(instance, pid)

    _dll.FakeProcess.argtypes = [c_int64, c_int64, c_int64]
    _dll.FakeProcess.restype = c_int

    @classmethod
    def FakeProcess(cls, instance, pid, fake_pid):
        return cls._dll.FakeProcess(instance, pid, fake_pid)

    _dll.ProtectWindow.argtypes = [c_int64, c_int64, c_int]
    _dll.ProtectWindow.restype = c_int

    @classmethod
    def ProtectWindow(cls, instance, hwnd, flag):
        return cls._dll.ProtectWindow(instance, hwnd, flag)

    _dll.KeOpenProcess.argtypes = [c_int64, c_int64, POINTER(c_int64)]
    _dll.KeOpenProcess.restype = c_int

    @classmethod
    def KeOpenProcess(cls, instance, pid, process_handle=None):
        process_handle = c_int64(0)
        result = cls._dll.KeOpenProcess(instance, pid, byref(process_handle))
        return result, process_handle.value

    _dll.KeOpenThread.argtypes = [c_int64, c_int64, POINTER(c_int64)]
    _dll.KeOpenThread.restype = c_int

    @classmethod
    def KeOpenThread(cls, instance, thread_id, thread_handle=None):
        thread_handle = c_int64(0)
        result = cls._dll.KeOpenThread(instance, thread_id, byref(thread_handle))
        return result, thread_handle.value

    _dll.StartSecurityGuard.argtypes = [c_int64]
    _dll.StartSecurityGuard.restype = c_int

    @classmethod
    def StartSecurityGuard(cls, instance):
        return cls._dll.StartSecurityGuard(instance)

    _dll.ProtectFileTestDriver.argtypes = [c_int64]
    _dll.ProtectFileTestDriver.restype = c_int

    @classmethod
    def ProtectFileTestDriver(cls, instance):
        return cls._dll.ProtectFileTestDriver(instance)

    _dll.ProtectFileEnableDriver.argtypes = [c_int64]
    _dll.ProtectFileEnableDriver.restype = c_int

    @classmethod
    def ProtectFileEnableDriver(cls, instance):
        return cls._dll.ProtectFileEnableDriver(instance)

    _dll.ProtectFileDisableDriver.argtypes = [c_int64]
    _dll.ProtectFileDisableDriver.restype = c_int

    @classmethod
    def ProtectFileDisableDriver(cls, instance):
        return cls._dll.ProtectFileDisableDriver(instance)

    _dll.ProtectFileStartFilter.argtypes = [c_int64]
    _dll.ProtectFileStartFilter.restype = c_int

    @classmethod
    def ProtectFileStartFilter(cls, instance):
        return cls._dll.ProtectFileStartFilter(instance)

    _dll.ProtectFileStopFilter.argtypes = [c_int64]
    _dll.ProtectFileStopFilter.restype = c_int

    @classmethod
    def ProtectFileStopFilter(cls, instance):
        return cls._dll.ProtectFileStopFilter(instance)

    _dll.ProtectFileAddProtectedPath.argtypes = [c_int64, c_char_p, c_int, c_int]
    _dll.ProtectFileAddProtectedPath.restype = c_int

    @classmethod
    def ProtectFileAddProtectedPath(cls, instance, path, mode, is_directory):
        return cls._dll.ProtectFileAddProtectedPath(instance, path.encode("utf-8"), mode, is_directory)

    _dll.ProtectFileRemoveProtectedPath.argtypes = [c_int64, c_char_p]
    _dll.ProtectFileRemoveProtectedPath.restype = c_int

    @classmethod
    def ProtectFileRemoveProtectedPath(cls, instance, path):
        return cls._dll.ProtectFileRemoveProtectedPath(instance, path.encode("utf-8"))

    _dll.ProtectFileClearProtectedPaths.argtypes = [c_int64]
    _dll.ProtectFileClearProtectedPaths.restype = c_int

    @classmethod
    def ProtectFileClearProtectedPaths(cls, instance):
        return cls._dll.ProtectFileClearProtectedPaths(instance)

    _dll.ProtectFileQueryProtectedPath.argtypes = [c_int64, c_char_p, POINTER(c_int)]
    _dll.ProtectFileQueryProtectedPath.restype = c_int

    @classmethod
    def ProtectFileQueryProtectedPath(cls, instance, path, mode=None):
        mode = c_int(0)
        result = cls._dll.ProtectFileQueryProtectedPath(instance, path.encode("utf-8"), byref(mode))
        return result, mode.value

    _dll.ProtectFileAddWhitelist.argtypes = [c_int64, c_int64]
    _dll.ProtectFileAddWhitelist.restype = c_int

    @classmethod
    def ProtectFileAddWhitelist(cls, instance, pid):
        return cls._dll.ProtectFileAddWhitelist(instance, pid)

    _dll.ProtectFileRemoveWhitelist.argtypes = [c_int64, c_int64]
    _dll.ProtectFileRemoveWhitelist.restype = c_int

    @classmethod
    def ProtectFileRemoveWhitelist(cls, instance, pid):
        return cls._dll.ProtectFileRemoveWhitelist(instance, pid)

    _dll.ProtectFileClearWhitelist.argtypes = [c_int64]
    _dll.ProtectFileClearWhitelist.restype = c_int

    @classmethod
    def ProtectFileClearWhitelist(cls, instance):
        return cls._dll.ProtectFileClearWhitelist(instance)

    _dll.ProtectFileQueryWhitelist.argtypes = [c_int64, c_int64]
    _dll.ProtectFileQueryWhitelist.restype = c_int

    @classmethod
    def ProtectFileQueryWhitelist(cls, instance, pid):
        return cls._dll.ProtectFileQueryWhitelist(instance, pid)

    _dll.ProtectFileAddBlacklist.argtypes = [c_int64, c_int64]
    _dll.ProtectFileAddBlacklist.restype = c_int

    @classmethod
    def ProtectFileAddBlacklist(cls, instance, pid):
        return cls._dll.ProtectFileAddBlacklist(instance, pid)

    _dll.ProtectFileRemoveBlacklist.argtypes = [c_int64, c_int64]
    _dll.ProtectFileRemoveBlacklist.restype = c_int

    @classmethod
    def ProtectFileRemoveBlacklist(cls, instance, pid):
        return cls._dll.ProtectFileRemoveBlacklist(instance, pid)

    _dll.ProtectFileClearBlacklist.argtypes = [c_int64]
    _dll.ProtectFileClearBlacklist.restype = c_int

    @classmethod
    def ProtectFileClearBlacklist(cls, instance):
        return cls._dll.ProtectFileClearBlacklist(instance)

    _dll.ProtectFileQueryBlacklist.argtypes = [c_int64, c_int64]
    _dll.ProtectFileQueryBlacklist.restype = c_int

    @classmethod
    def ProtectFileQueryBlacklist(cls, instance, pid):
        return cls._dll.ProtectFileQueryBlacklist(instance, pid)

    _dll.VipProtectEnableDriver.argtypes = [c_int64]
    _dll.VipProtectEnableDriver.restype = c_int

    @classmethod
    def VipProtectEnableDriver(cls, instance):
        return cls._dll.VipProtectEnableDriver(instance)

    _dll.VipProtectDisableDriver.argtypes = [c_int64]
    _dll.VipProtectDisableDriver.restype = c_int

    @classmethod
    def VipProtectDisableDriver(cls, instance):
        return cls._dll.VipProtectDisableDriver(instance)

    _dll.VipProtectAddProtect.argtypes = [c_int64, c_int64, c_char_p, c_int, c_int]
    _dll.VipProtectAddProtect.restype = c_int

    @classmethod
    def VipProtectAddProtect(cls, instance, pid, path, mode, permission):
        return cls._dll.VipProtectAddProtect(instance, pid, path.encode("utf-8"), mode, permission)

    _dll.VipProtectRemoveProtect.argtypes = [c_int64, c_int64, c_char_p]
    _dll.VipProtectRemoveProtect.restype = c_int

    @classmethod
    def VipProtectRemoveProtect(cls, instance, pid, path):
        return cls._dll.VipProtectRemoveProtect(instance, pid, path.encode("utf-8"))

    _dll.VipProtectClearAll.argtypes = [c_int64]
    _dll.VipProtectClearAll.restype = c_int

    @classmethod
    def VipProtectClearAll(cls, instance):
        return cls._dll.VipProtectClearAll(instance)

    _dll.VipProtectAddWhitelist.argtypes = [c_int64, c_int64, c_char_p]
    _dll.VipProtectAddWhitelist.restype = c_int

    @classmethod
    def VipProtectAddWhitelist(cls, instance, pid, path):
        return cls._dll.VipProtectAddWhitelist(instance, pid, path.encode("utf-8"))

    _dll.VipProtectRemoveWhitelist.argtypes = [c_int64, c_int64, c_char_p]
    _dll.VipProtectRemoveWhitelist.restype = c_int

    @classmethod
    def VipProtectRemoveWhitelist(cls, instance, pid, path):
        return cls._dll.VipProtectRemoveWhitelist(instance, pid, path.encode("utf-8"))

    _dll.VipProtectClearWhitelist.argtypes = [c_int64]
    _dll.VipProtectClearWhitelist.restype = c_int

    @classmethod
    def VipProtectClearWhitelist(cls, instance):
        return cls._dll.VipProtectClearWhitelist(instance)

    _dll.VipProtectAddBlacklist.argtypes = [c_int64, c_int64, c_char_p]
    _dll.VipProtectAddBlacklist.restype = c_int

    @classmethod
    def VipProtectAddBlacklist(cls, instance, pid, path):
        return cls._dll.VipProtectAddBlacklist(instance, pid, path.encode("utf-8"))

    _dll.VipProtectRemoveBlacklist.argtypes = [c_int64, c_int64, c_char_p]
    _dll.VipProtectRemoveBlacklist.restype = c_int

    @classmethod
    def VipProtectRemoveBlacklist(cls, instance, pid, path):
        return cls._dll.VipProtectRemoveBlacklist(instance, pid, path.encode("utf-8"))

    _dll.VipProtectClearBlacklist.argtypes = [c_int64]
    _dll.VipProtectClearBlacklist.restype = c_int

    @classmethod
    def VipProtectClearBlacklist(cls, instance):
        return cls._dll.VipProtectClearBlacklist(instance)

    _dll.GenerateRSAKey.argtypes = [c_int64, c_char_p, c_char_p, c_int, c_int]
    _dll.GenerateRSAKey.restype = c_int

    @classmethod
    def GenerateRSAKey(cls, instance, publicKeyPath, privateKeyPath, _type, keySize):
        return cls._dll.GenerateRSAKey(
            instance, publicKeyPath.encode("utf-8"), privateKeyPath.encode("utf-8"), _type, keySize
        )

    _dll.ConvertRSAPublicKey.argtypes = [c_int64, c_char_p, c_int, c_int]
    _dll.ConvertRSAPublicKey.restype = c_int64

    @classmethod
    def ConvertRSAPublicKey(cls, instance, publicKey, inputType, outputType):
        return cls._dll.ConvertRSAPublicKey(instance, publicKey.encode("utf-8"), inputType, outputType)

    _dll.ConvertRSAPrivateKey.argtypes = [c_int64, c_char_p, c_int, c_int]
    _dll.ConvertRSAPrivateKey.restype = c_int64

    @classmethod
    def ConvertRSAPrivateKey(cls, instance, privateKey, inputType, outputType):
        return cls._dll.ConvertRSAPrivateKey(instance, privateKey.encode("utf-8"), inputType, outputType)

    _dll.EncryptWithRsa.argtypes = [c_int64, c_char_p, c_char_p, c_int]
    _dll.EncryptWithRsa.restype = c_int64

    @classmethod
    def EncryptWithRsa(cls, instance, message, publicKey, paddingType):
        return cls._dll.EncryptWithRsa(instance, message.encode("utf-8"), publicKey.encode("utf-8"), paddingType)

    _dll.DecryptWithRsa.argtypes = [c_int64, c_char_p, c_char_p, c_int]
    _dll.DecryptWithRsa.restype = c_int64

    @classmethod
    def DecryptWithRsa(cls, instance, cipher, privateKey, paddingType):
        return cls._dll.DecryptWithRsa(instance, cipher.encode("utf-8"), privateKey.encode("utf-8"), paddingType)

    _dll.SignWithRsa.argtypes = [c_int64, c_char_p, c_char_p, c_int, c_int]
    _dll.SignWithRsa.restype = c_int64

    @classmethod
    def SignWithRsa(cls, instance, message, privateCer, shaType, paddingType):
        return cls._dll.SignWithRsa(instance, message.encode("utf-8"), privateCer.encode("utf-8"), shaType, paddingType)

    _dll.VerifySignWithRsa.argtypes = [c_int64, c_char_p, c_char_p, c_int, c_int, c_char_p]
    _dll.VerifySignWithRsa.restype = c_int

    @classmethod
    def VerifySignWithRsa(cls, instance, message, signature, shaType, paddingType, publicCer):
        return cls._dll.VerifySignWithRsa(
            instance,
            message.encode("utf-8"),
            signature.encode("utf-8"),
            shaType,
            paddingType,
            publicCer.encode("utf-8"),
        )

    _dll.AESEncrypt.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.AESEncrypt.restype = c_int64

    @classmethod
    def AESEncrypt(cls, instance, source, key):
        return cls._dll.AESEncrypt(instance, source.encode("utf-8"), key.encode("utf-8"))

    _dll.AESDecrypt.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.AESDecrypt.restype = c_int64

    @classmethod
    def AESDecrypt(cls, instance, source, key):
        return cls._dll.AESDecrypt(instance, source.encode("utf-8"), key.encode("utf-8"))

    _dll.AESEncryptEx.argtypes = [c_int64, c_char_p, c_char_p, c_char_p, c_int, c_int]
    _dll.AESEncryptEx.restype = c_int64

    @classmethod
    def AESEncryptEx(cls, instance, source, key, iv, mode, paddingType):
        return cls._dll.AESEncryptEx(
            instance, source.encode("utf-8"), key.encode("utf-8"), iv.encode("utf-8"), mode, paddingType
        )

    _dll.AESDecryptEx.argtypes = [c_int64, c_char_p, c_char_p, c_char_p, c_int, c_int]
    _dll.AESDecryptEx.restype = c_int64

    @classmethod
    def AESDecryptEx(cls, instance, source, key, iv, mode, paddingType):
        return cls._dll.AESDecryptEx(
            instance, source.encode("utf-8"), key.encode("utf-8"), iv.encode("utf-8"), mode, paddingType
        )

    _dll.MD5Encrypt.argtypes = [c_int64, c_char_p]
    _dll.MD5Encrypt.restype = c_int64

    @classmethod
    def MD5Encrypt(cls, instance, source):
        return cls._dll.MD5Encrypt(instance, source.encode("utf-8"))

    _dll.SHAHash.argtypes = [c_int64, c_char_p, c_int]
    _dll.SHAHash.restype = c_int64

    @classmethod
    def SHAHash(cls, instance, source, shaType):
        return cls._dll.SHAHash(instance, source.encode("utf-8"), shaType)

    _dll.HMAC.argtypes = [c_int64, c_char_p, c_char_p, c_int]
    _dll.HMAC.restype = c_int64

    @classmethod
    def HMAC(cls, instance, source, key, shaType):
        return cls._dll.HMAC(instance, source.encode("utf-8"), key.encode("utf-8"), shaType)

    _dll.GenerateRandomBytes.argtypes = [c_int64, c_int, c_int]
    _dll.GenerateRandomBytes.restype = c_int64

    @classmethod
    def GenerateRandomBytes(cls, instance, length, _type):
        return cls._dll.GenerateRandomBytes(instance, length, _type)

    _dll.GenerateGuid.argtypes = [c_int64, c_int]
    _dll.GenerateGuid.restype = c_int64

    @classmethod
    def GenerateGuid(cls, instance, _type):
        return cls._dll.GenerateGuid(instance, _type)

    _dll.Base64Encode.argtypes = [c_int64, c_char_p]
    _dll.Base64Encode.restype = c_int64

    @classmethod
    def Base64Encode(cls, instance, source):
        return cls._dll.Base64Encode(instance, source.encode("utf-8"))

    _dll.Base64Decode.argtypes = [c_int64, c_char_p]
    _dll.Base64Decode.restype = c_int64

    @classmethod
    def Base64Decode(cls, instance, source):
        return cls._dll.Base64Decode(instance, source.encode("utf-8"))

    _dll.PBKDF2.argtypes = [c_int64, c_char_p, c_char_p, c_int, c_int, c_int]
    _dll.PBKDF2.restype = c_int64

    @classmethod
    def PBKDF2(cls, instance, password, salt, iterations, keyLength, shaType):
        return cls._dll.PBKDF2(instance, password.encode("utf-8"), salt.encode("utf-8"), iterations, keyLength, shaType)

    _dll.MD5File.argtypes = [c_int64, c_char_p]
    _dll.MD5File.restype = c_int64

    @classmethod
    def MD5File(cls, instance, filePath):
        return cls._dll.MD5File(instance, filePath.encode("utf-8"))

    _dll.SHAFile.argtypes = [c_int64, c_char_p, c_int]
    _dll.SHAFile.restype = c_int64

    @classmethod
    def SHAFile(cls, instance, filePath, shaType):
        return cls._dll.SHAFile(instance, filePath.encode("utf-8"), shaType)

    _dll.CreateFolder.argtypes = [c_int64, c_char_p]
    _dll.CreateFolder.restype = c_int

    @classmethod
    def CreateFolder(cls, instance, path):
        return cls._dll.CreateFolder(instance, path.encode("utf-8"))

    _dll.DeleteFolder.argtypes = [c_int64, c_char_p]
    _dll.DeleteFolder.restype = c_int

    @classmethod
    def DeleteFolder(cls, instance, path):
        return cls._dll.DeleteFolder(instance, path.encode("utf-8"))

    _dll.GetFolderList.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.GetFolderList.restype = c_int64

    @classmethod
    def GetFolderList(cls, instance, path, baseDir):
        return cls._dll.GetFolderList(instance, path.encode("utf-8"), baseDir.encode("utf-8"))

    _dll.IsDirectory.argtypes = [c_int64, c_char_p]
    _dll.IsDirectory.restype = c_int

    @classmethod
    def IsDirectory(cls, instance, path):
        return cls._dll.IsDirectory(instance, path.encode("utf-8"))

    _dll.IsFile.argtypes = [c_int64, c_char_p]
    _dll.IsFile.restype = c_int

    @classmethod
    def IsFile(cls, instance, path):
        return cls._dll.IsFile(instance, path.encode("utf-8"))

    _dll.CreateFile.argtypes = [c_int64, c_char_p]
    _dll.CreateFile.restype = c_int

    @classmethod
    def CreateFile(cls, instance, path):
        return cls._dll.CreateFile(instance, path.encode("utf-8"))

    _dll.DeleteFile.argtypes = [c_int64, c_char_p]
    _dll.DeleteFile.restype = c_int

    @classmethod
    def DeleteFile(cls, instance, path):
        return cls._dll.DeleteFile(instance, path.encode("utf-8"))

    _dll.CopyFile.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.CopyFile.restype = c_int

    @classmethod
    def CopyFile(cls, instance, src, dst):
        return cls._dll.CopyFile(instance, src.encode("utf-8"), dst.encode("utf-8"))

    _dll.MoveFile.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.MoveFile.restype = c_int

    @classmethod
    def MoveFile(cls, instance, src, dst):
        return cls._dll.MoveFile(instance, src.encode("utf-8"), dst.encode("utf-8"))

    _dll.RenameFile.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.RenameFile.restype = c_int

    @classmethod
    def RenameFile(cls, instance, src, dst):
        return cls._dll.RenameFile(instance, src.encode("utf-8"), dst.encode("utf-8"))

    _dll.GetFileSize.argtypes = [c_int64, c_char_p]
    _dll.GetFileSize.restype = c_int64

    @classmethod
    def GetFileSize(cls, instance, path):
        return cls._dll.GetFileSize(instance, path.encode("utf-8"))

    _dll.GetFileList.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.GetFileList.restype = c_int64

    @classmethod
    def GetFileList(cls, instance, path, baseDir):
        return cls._dll.GetFileList(instance, path.encode("utf-8"), baseDir.encode("utf-8"))

    _dll.GetFileName.argtypes = [c_int64, c_char_p, c_int]
    _dll.GetFileName.restype = c_int64

    @classmethod
    def GetFileName(cls, instance, path, withExtension):
        return cls._dll.GetFileName(instance, path.encode("utf-8"), withExtension)

    _dll.ToAbsolutePath.argtypes = [c_int64, c_char_p]
    _dll.ToAbsolutePath.restype = c_int64

    @classmethod
    def ToAbsolutePath(cls, instance, path):
        return cls._dll.ToAbsolutePath(instance, path.encode("utf-8"))

    _dll.ToRelativePath.argtypes = [c_int64, c_char_p]
    _dll.ToRelativePath.restype = c_int64

    @classmethod
    def ToRelativePath(cls, instance, path):
        return cls._dll.ToRelativePath(instance, path.encode("utf-8"))

    _dll.FileOrDirectoryExists.argtypes = [c_int64, c_char_p]
    _dll.FileOrDirectoryExists.restype = c_int

    @classmethod
    def FileOrDirectoryExists(cls, instance, path):
        return cls._dll.FileOrDirectoryExists(instance, path.encode("utf-8"))

    _dll.ReadFileString.argtypes = [c_int64, c_char_p, c_int]
    _dll.ReadFileString.restype = c_int64

    @classmethod
    def ReadFileString(cls, instance, filePath, encoding):
        return cls._dll.ReadFileString(instance, filePath.encode("utf-8"), encoding)

    _dll.ReadBytesFromFile.argtypes = [c_int64, c_char_p, c_int, c_int64]
    _dll.ReadBytesFromFile.restype = c_int64

    @classmethod
    def ReadBytesFromFile(cls, instance, filePath, offset, size):
        return cls._dll.ReadBytesFromFile(instance, filePath.encode("utf-8"), offset, size)

    _dll.WriteBytesToFile.argtypes = [c_int64, c_char_p, c_int64, c_int]
    _dll.WriteBytesToFile.restype = c_int

    @classmethod
    def WriteBytesToFile(cls, instance, filePath, dataAddr, dataSize):
        return cls._dll.WriteBytesToFile(instance, filePath.encode("utf-8"), dataAddr, dataSize)

    _dll.WriteStringToFile.argtypes = [c_int64, c_char_p, c_char_p, c_int]
    _dll.WriteStringToFile.restype = c_int

    @classmethod
    def WriteStringToFile(cls, instance, filePath, data, encoding):
        return cls._dll.WriteStringToFile(instance, filePath.encode("utf-8"), data.encode("utf-8"), encoding)

    _dll.StartHotkeyHook.argtypes = [c_int64]
    _dll.StartHotkeyHook.restype = c_int

    @classmethod
    def StartHotkeyHook(cls, instance):
        return cls._dll.StartHotkeyHook(instance)

    _dll.StopHotkeyHook.argtypes = [c_int64]
    _dll.StopHotkeyHook.restype = c_int

    @classmethod
    def StopHotkeyHook(cls, instance):
        return cls._dll.StopHotkeyHook(instance)

    _dll.RegisterHotkey.argtypes = [c_int64, c_int, c_int, HotkeyCallback]
    _dll.RegisterHotkey.restype = c_int

    @classmethod
    def RegisterHotkey(cls, instance, keycode, modifiers, callback):
        callback = cls.HotkeyCallback(callback)
        key = f"RegisterHotkey_{instance}_{keycode}_{modifiers}"
        cls.callbacks[key] = callback
        return cls._dll.RegisterHotkey(instance, keycode, modifiers, callback)

    _dll.UnregisterHotkey.argtypes = [c_int64, c_int, c_int]
    _dll.UnregisterHotkey.restype = c_int

    @classmethod
    def UnregisterHotkey(cls, instance, keycode, modifiers):
        return cls._dll.UnregisterHotkey(instance, keycode, modifiers)

    _dll.RegisterMouseButton.argtypes = [c_int64, c_int, c_int, MouseCallback]
    _dll.RegisterMouseButton.restype = c_int

    @classmethod
    def RegisterMouseButton(cls, instance, button, _type, callback):
        callback = cls.MouseCallback(callback)
        key = f"RegisterMouseButton_{instance}_{button}_{_type}"
        cls.callbacks[key] = callback
        return cls._dll.RegisterMouseButton(instance, button, _type, callback)

    _dll.UnregisterMouseButton.argtypes = [c_int64, c_int, c_int]
    _dll.UnregisterMouseButton.restype = c_int

    @classmethod
    def UnregisterMouseButton(cls, instance, button, _type):
        return cls._dll.UnregisterMouseButton(instance, button, _type)

    _dll.RegisterMouseWheel.argtypes = [c_int64, MouseWheelCallback]
    _dll.RegisterMouseWheel.restype = c_int

    @classmethod
    def RegisterMouseWheel(cls, instance, callback):
        callback = cls.MouseWheelCallback(callback)
        key = f"RegisterMouseWheel_{instance}"
        cls.callbacks[key] = callback
        return cls._dll.RegisterMouseWheel(instance, callback)

    _dll.UnregisterMouseWheel.argtypes = [c_int64]
    _dll.UnregisterMouseWheel.restype = c_int

    @classmethod
    def UnregisterMouseWheel(cls, instance):
        return cls._dll.UnregisterMouseWheel(instance)

    _dll.RegisterMouseMove.argtypes = [c_int64, MouseMoveCallback]
    _dll.RegisterMouseMove.restype = c_int

    @classmethod
    def RegisterMouseMove(cls, instance, callback):
        callback = cls.MouseMoveCallback(callback)
        key = f"RegisterMouseMove_{instance}"
        cls.callbacks[key] = callback
        return cls._dll.RegisterMouseMove(instance, callback)

    _dll.UnregisterMouseMove.argtypes = [c_int64]
    _dll.UnregisterMouseMove.restype = c_int

    @classmethod
    def UnregisterMouseMove(cls, instance):
        return cls._dll.UnregisterMouseMove(instance)

    _dll.RegisterMouseDrag.argtypes = [c_int64, MouseDragCallback]
    _dll.RegisterMouseDrag.restype = c_int

    @classmethod
    def RegisterMouseDrag(cls, instance, callback):
        callback = cls.MouseDragCallback(callback)
        key = f"RegisterMouseDrag_{instance}"
        cls.callbacks[key] = callback
        return cls._dll.RegisterMouseDrag(instance, callback)

    _dll.UnregisterMouseDrag.argtypes = [c_int64]
    _dll.UnregisterMouseDrag.restype = c_int

    @classmethod
    def UnregisterMouseDrag(cls, instance):
        return cls._dll.UnregisterMouseDrag(instance)

    _dll.Inject.argtypes = [c_int64, c_int64, c_char_p, c_int, c_int]
    _dll.Inject.restype = c_int

    @classmethod
    def Inject(cls, instance, hwnd, dll_path, _type, bypassGuard):
        return cls._dll.Inject(instance, hwnd, dll_path.encode("utf-8"), _type, bypassGuard)

    _dll.InjectFromUrl.argtypes = [c_int64, c_int64, c_char_p, c_int, c_int]
    _dll.InjectFromUrl.restype = c_int

    @classmethod
    def InjectFromUrl(cls, instance, hwnd, url, _type, bypassGuard):
        return cls._dll.InjectFromUrl(instance, hwnd, url.encode("utf-8"), _type, bypassGuard)

    _dll.InjectFromBuffer.argtypes = [c_int64, c_int64, c_int64, c_int, c_int, c_int]
    _dll.InjectFromBuffer.restype = c_int

    @classmethod
    def InjectFromBuffer(cls, instance, hwnd, bufferAddr, bufferSize, _type, bypassGuard):
        return cls._dll.InjectFromBuffer(instance, hwnd, bufferAddr, bufferSize, _type, bypassGuard)

    _dll.JsonCreateObject.argtypes = []
    _dll.JsonCreateObject.restype = c_int64

    @classmethod
    def JsonCreateObject(cls):
        return cls._dll.JsonCreateObject()

    _dll.JsonCreateArray.argtypes = []
    _dll.JsonCreateArray.restype = c_int64

    @classmethod
    def JsonCreateArray(cls):
        return cls._dll.JsonCreateArray()

    _dll.JsonParse.argtypes = [c_char_p, POINTER(c_int)]
    _dll.JsonParse.restype = c_int64

    @classmethod
    def JsonParse(cls, _str, err=None):
        err = c_int(0)
        result = cls._dll.JsonParse(_str.encode("utf-8"), byref(err))
        return result, err.value

    _dll.JsonStringify.argtypes = [c_int64, c_int, POINTER(c_int)]
    _dll.JsonStringify.restype = c_int64

    @classmethod
    def JsonStringify(cls, obj, indent, err=None):
        err = c_int(0)
        result = cls._dll.JsonStringify(obj, indent, byref(err))
        return result, err.value

    _dll.JsonFree.argtypes = [c_int64]
    _dll.JsonFree.restype = c_int

    @classmethod
    def JsonFree(cls, obj):
        return cls._dll.JsonFree(obj)

    _dll.JsonGetValue.argtypes = [c_int64, c_char_p, POINTER(c_int)]
    _dll.JsonGetValue.restype = c_int64

    @classmethod
    def JsonGetValue(cls, obj, key, err=None):
        err = c_int(0)
        result = cls._dll.JsonGetValue(obj, key.encode("utf-8"), byref(err))
        return result, err.value

    _dll.JsonGetArrayItem.argtypes = [c_int64, c_int, POINTER(c_int)]
    _dll.JsonGetArrayItem.restype = c_int64

    @classmethod
    def JsonGetArrayItem(cls, arr, index, err=None):
        err = c_int(0)
        result = cls._dll.JsonGetArrayItem(arr, index, byref(err))
        return result, err.value

    _dll.JsonGetString.argtypes = [c_int64, c_char_p, POINTER(c_int)]
    _dll.JsonGetString.restype = c_int64

    @classmethod
    def JsonGetString(cls, obj, key, err=None):
        err = c_int(0)
        result = cls._dll.JsonGetString(obj, key.encode("utf-8"), byref(err))
        return result, err.value

    _dll.JsonGetNumber.argtypes = [c_int64, c_char_p, POINTER(c_int)]
    _dll.JsonGetNumber.restype = c_double

    @classmethod
    def JsonGetNumber(cls, obj, key, err=None):
        err = c_int(0)
        result = cls._dll.JsonGetNumber(obj, key.encode("utf-8"), byref(err))
        return result, err.value

    _dll.JsonGetBool.argtypes = [c_int64, c_char_p, POINTER(c_int)]
    _dll.JsonGetBool.restype = c_int

    @classmethod
    def JsonGetBool(cls, obj, key, err=None):
        err = c_int(0)
        result = cls._dll.JsonGetBool(obj, key.encode("utf-8"), byref(err))
        return result, err.value

    _dll.JsonGetSize.argtypes = [c_int64, POINTER(c_int)]
    _dll.JsonGetSize.restype = c_int

    @classmethod
    def JsonGetSize(cls, obj, err=None):
        err = c_int(0)
        result = cls._dll.JsonGetSize(obj, byref(err))
        return result, err.value

    _dll.JsonSetValue.argtypes = [c_int64, c_char_p, c_int64]
    _dll.JsonSetValue.restype = c_int

    @classmethod
    def JsonSetValue(cls, obj, key, value):
        return cls._dll.JsonSetValue(obj, key.encode("utf-8"), value)

    _dll.JsonArrayAppend.argtypes = [c_int64, c_int64]
    _dll.JsonArrayAppend.restype = c_int

    @classmethod
    def JsonArrayAppend(cls, arr, value):
        return cls._dll.JsonArrayAppend(arr, value)

    _dll.JsonSetString.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.JsonSetString.restype = c_int

    @classmethod
    def JsonSetString(cls, obj, key, value):
        return cls._dll.JsonSetString(obj, key.encode("utf-8"), value.encode("utf-8"))

    _dll.JsonSetNumber.argtypes = [c_int64, c_char_p, c_double]
    _dll.JsonSetNumber.restype = c_int

    @classmethod
    def JsonSetNumber(cls, obj, key, value):
        return cls._dll.JsonSetNumber(obj, key.encode("utf-8"), value)

    _dll.JsonSetBool.argtypes = [c_int64, c_char_p, c_int]
    _dll.JsonSetBool.restype = c_int

    @classmethod
    def JsonSetBool(cls, obj, key, value):
        return cls._dll.JsonSetBool(obj, key.encode("utf-8"), value)

    _dll.JsonDeleteKey.argtypes = [c_int64, c_char_p]
    _dll.JsonDeleteKey.restype = c_int

    @classmethod
    def JsonDeleteKey(cls, obj, key):
        return cls._dll.JsonDeleteKey(obj, key.encode("utf-8"))

    _dll.JsonClear.argtypes = [c_int64]
    _dll.JsonClear.restype = c_int

    @classmethod
    def JsonClear(cls, obj):
        return cls._dll.JsonClear(obj)

    _dll.ParseMatchImageJson.argtypes = [
        c_char_p,
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_double),
        POINTER(c_double),
        POINTER(c_int),
    ]
    _dll.ParseMatchImageJson.restype = c_int

    @classmethod
    def ParseMatchImageJson(
        cls, _str, matchState=None, x=None, y=None, width=None, height=None, matchVal=None, angle=None, index=None
    ):
        matchState = c_int(0)
        x = c_int(0)
        y = c_int(0)
        width = c_int(0)
        height = c_int(0)
        matchVal = c_double(0)
        angle = c_double(0)
        index = c_int(0)
        result = cls._dll.ParseMatchImageJson(
            _str.encode("utf-8"),
            byref(matchState),
            byref(x),
            byref(y),
            byref(width),
            byref(height),
            byref(matchVal),
            byref(angle),
            byref(index),
        )
        return (
            result,
            matchState.value,
            x.value,
            y.value,
            width.value,
            height.value,
            matchVal.value,
            angle.value,
            index.value,
        )

    _dll.GetMatchImageAllCount.argtypes = [c_char_p]
    _dll.GetMatchImageAllCount.restype = c_int

    @classmethod
    def GetMatchImageAllCount(cls, _str):
        return cls._dll.GetMatchImageAllCount(_str.encode("utf-8"))

    _dll.ParseMatchImageAllJson.argtypes = [
        c_char_p,
        c_int,
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_double),
        POINTER(c_double),
        POINTER(c_int),
    ]
    _dll.ParseMatchImageAllJson.restype = c_int

    @classmethod
    def ParseMatchImageAllJson(
        cls,
        _str,
        parseIndex,
        matchState=None,
        x=None,
        y=None,
        width=None,
        height=None,
        matchVal=None,
        angle=None,
        index=None,
    ):
        matchState = c_int(0)
        x = c_int(0)
        y = c_int(0)
        width = c_int(0)
        height = c_int(0)
        matchVal = c_double(0)
        angle = c_double(0)
        index = c_int(0)
        result = cls._dll.ParseMatchImageAllJson(
            _str.encode("utf-8"),
            parseIndex,
            byref(matchState),
            byref(x),
            byref(y),
            byref(width),
            byref(height),
            byref(matchVal),
            byref(angle),
            byref(index),
        )
        return (
            result,
            matchState.value,
            x.value,
            y.value,
            width.value,
            height.value,
            matchVal.value,
            angle.value,
            index.value,
        )

    _dll.GetResultCount.argtypes = [c_char_p]
    _dll.GetResultCount.restype = c_int

    @classmethod
    def GetResultCount(cls, resultStr):
        return cls._dll.GetResultCount(resultStr.encode("utf-8"))

    _dll.GenerateMouseTrajectory.argtypes = [c_int64, c_int, c_int, c_int, c_int]
    _dll.GenerateMouseTrajectory.restype = c_int64

    @classmethod
    def GenerateMouseTrajectory(cls, instance, startX, startY, endX, endY):
        return cls._dll.GenerateMouseTrajectory(instance, startX, startY, endX, endY)

    _dll.KeyDown.argtypes = [c_int64, c_int]
    _dll.KeyDown.restype = c_int

    @classmethod
    def KeyDown(cls, instance, vk_code):
        return cls._dll.KeyDown(instance, vk_code)

    _dll.KeyUp.argtypes = [c_int64, c_int]
    _dll.KeyUp.restype = c_int

    @classmethod
    def KeyUp(cls, instance, vk_code):
        return cls._dll.KeyUp(instance, vk_code)

    _dll.KeyPress.argtypes = [c_int64, c_int]
    _dll.KeyPress.restype = c_int

    @classmethod
    def KeyPress(cls, instance, vk_code):
        return cls._dll.KeyPress(instance, vk_code)

    _dll.LeftDown.argtypes = [c_int64]
    _dll.LeftDown.restype = c_int

    @classmethod
    def LeftDown(cls, instance):
        return cls._dll.LeftDown(instance)

    _dll.LeftUp.argtypes = [c_int64]
    _dll.LeftUp.restype = c_int

    @classmethod
    def LeftUp(cls, instance):
        return cls._dll.LeftUp(instance)

    _dll.MoveTo.argtypes = [c_int64, c_int, c_int]
    _dll.MoveTo.restype = c_int

    @classmethod
    def MoveTo(cls, instance, x, y):
        return cls._dll.MoveTo(instance, x, y)

    _dll.MoveToWithoutSimulator.argtypes = [c_int64, c_int, c_int]
    _dll.MoveToWithoutSimulator.restype = c_int

    @classmethod
    def MoveToWithoutSimulator(cls, instance, x, y):
        return cls._dll.MoveToWithoutSimulator(instance, x, y)

    _dll.RightClick.argtypes = [c_int64]
    _dll.RightClick.restype = c_int

    @classmethod
    def RightClick(cls, instance):
        return cls._dll.RightClick(instance)

    _dll.RightDoubleClick.argtypes = [c_int64]
    _dll.RightDoubleClick.restype = c_int

    @classmethod
    def RightDoubleClick(cls, instance):
        return cls._dll.RightDoubleClick(instance)

    _dll.RightDown.argtypes = [c_int64]
    _dll.RightDown.restype = c_int

    @classmethod
    def RightDown(cls, instance):
        return cls._dll.RightDown(instance)

    _dll.RightUp.argtypes = [c_int64]
    _dll.RightUp.restype = c_int

    @classmethod
    def RightUp(cls, instance):
        return cls._dll.RightUp(instance)

    _dll.GetCursorShape.argtypes = [c_int64]
    _dll.GetCursorShape.restype = c_int64

    @classmethod
    def GetCursorShape(cls, instance):
        return cls._dll.GetCursorShape(instance)

    _dll.GetCursorImage.argtypes = [c_int64]
    _dll.GetCursorImage.restype = c_int64

    @classmethod
    def GetCursorImage(cls, instance):
        return cls._dll.GetCursorImage(instance)

    _dll.KeyPressStr.argtypes = [c_int64, c_char_p, c_int]
    _dll.KeyPressStr.restype = c_int

    @classmethod
    def KeyPressStr(cls, instance, keyStr, delay):
        return cls._dll.KeyPressStr(instance, keyStr.encode("utf-8"), delay)

    _dll.SendString.argtypes = [c_int64, c_int64, c_char_p]
    _dll.SendString.restype = c_int

    @classmethod
    def SendString(cls, instance, hwnd, _str):
        return cls._dll.SendString(instance, hwnd, _str.encode("utf-8"))

    _dll.SendStringEx.argtypes = [c_int64, c_int64, c_int64, c_int, c_int]
    _dll.SendStringEx.restype = c_int

    @classmethod
    def SendStringEx(cls, instance, hwnd, addr, _len, _type):
        return cls._dll.SendStringEx(instance, hwnd, addr, _len, _type)

    _dll.KeyPressChar.argtypes = [c_int64, c_char_p]
    _dll.KeyPressChar.restype = c_int

    @classmethod
    def KeyPressChar(cls, instance, keyStr):
        return cls._dll.KeyPressChar(instance, keyStr.encode("utf-8"))

    _dll.KeyDownChar.argtypes = [c_int64, c_char_p]
    _dll.KeyDownChar.restype = c_int

    @classmethod
    def KeyDownChar(cls, instance, keyStr):
        return cls._dll.KeyDownChar(instance, keyStr.encode("utf-8"))

    _dll.KeyUpChar.argtypes = [c_int64, c_char_p]
    _dll.KeyUpChar.restype = c_int

    @classmethod
    def KeyUpChar(cls, instance, keyStr):
        return cls._dll.KeyUpChar(instance, keyStr.encode("utf-8"))

    _dll.MoveR.argtypes = [c_int64, c_int, c_int]
    _dll.MoveR.restype = c_int

    @classmethod
    def MoveR(cls, instance, rx, ry):
        return cls._dll.MoveR(instance, rx, ry)

    _dll.MiddleClick.argtypes = [c_int64]
    _dll.MiddleClick.restype = c_int

    @classmethod
    def MiddleClick(cls, instance):
        return cls._dll.MiddleClick(instance)

    _dll.MoveToEx.argtypes = [c_int64, c_int, c_int, c_int, c_int]
    _dll.MoveToEx.restype = c_int64

    @classmethod
    def MoveToEx(cls, instance, x, y, w, h):
        return cls._dll.MoveToEx(instance, x, y, w, h)

    _dll.GetCursorPos.argtypes = [c_int64, POINTER(c_int), POINTER(c_int)]
    _dll.GetCursorPos.restype = c_int

    @classmethod
    def GetCursorPos(cls, instance, x=None, y=None):
        x = c_int(0)
        y = c_int(0)
        result = cls._dll.GetCursorPos(instance, byref(x), byref(y))
        return result, x.value, y.value

    _dll.MiddleUp.argtypes = [c_int64]
    _dll.MiddleUp.restype = c_int

    @classmethod
    def MiddleUp(cls, instance):
        return cls._dll.MiddleUp(instance)

    _dll.MiddleDown.argtypes = [c_int64]
    _dll.MiddleDown.restype = c_int

    @classmethod
    def MiddleDown(cls, instance):
        return cls._dll.MiddleDown(instance)

    _dll.MiddleDoubleClick.argtypes = [c_int64]
    _dll.MiddleDoubleClick.restype = c_int

    @classmethod
    def MiddleDoubleClick(cls, instance):
        return cls._dll.MiddleDoubleClick(instance)

    _dll.LeftClick.argtypes = [c_int64]
    _dll.LeftClick.restype = c_int

    @classmethod
    def LeftClick(cls, instance):
        return cls._dll.LeftClick(instance)

    _dll.LeftDoubleClick.argtypes = [c_int64]
    _dll.LeftDoubleClick.restype = c_int

    @classmethod
    def LeftDoubleClick(cls, instance):
        return cls._dll.LeftDoubleClick(instance)

    _dll.WheelUp.argtypes = [c_int64]
    _dll.WheelUp.restype = c_int

    @classmethod
    def WheelUp(cls, instance):
        return cls._dll.WheelUp(instance)

    _dll.WheelDown.argtypes = [c_int64]
    _dll.WheelDown.restype = c_int

    @classmethod
    def WheelDown(cls, instance):
        return cls._dll.WheelDown(instance)

    _dll.WaitKey.argtypes = [c_int64, c_int, c_int]
    _dll.WaitKey.restype = c_int

    @classmethod
    def WaitKey(cls, instance, vk_code, time_out):
        return cls._dll.WaitKey(instance, vk_code, time_out)

    _dll.EnableMouseAccuracy.argtypes = [c_int64, c_int]
    _dll.EnableMouseAccuracy.restype = c_int

    @classmethod
    def EnableMouseAccuracy(cls, instance, enable):
        return cls._dll.EnableMouseAccuracy(instance, enable)

    _dll.DoubleToData.argtypes = [c_int64, c_double]
    _dll.DoubleToData.restype = c_int64

    @classmethod
    def DoubleToData(cls, instance, double_value):
        return cls._dll.DoubleToData(instance, double_value)

    _dll.FloatToData.argtypes = [c_int64, c_float]
    _dll.FloatToData.restype = c_int64

    @classmethod
    def FloatToData(cls, instance, float_value):
        return cls._dll.FloatToData(instance, float_value)

    _dll.StringToData.argtypes = [c_int64, c_char_p, c_int]
    _dll.StringToData.restype = c_int64

    @classmethod
    def StringToData(cls, instance, string_value, _type):
        return cls._dll.StringToData(instance, string_value.encode("utf-8"), _type)

    _dll.Int64ToInt32.argtypes = [c_int64, c_int64]
    _dll.Int64ToInt32.restype = c_int

    @classmethod
    def Int64ToInt32(cls, instance, v):
        return cls._dll.Int64ToInt32(instance, v)

    _dll.Int32ToInt64.argtypes = [c_int64, c_int]
    _dll.Int32ToInt64.restype = c_int64

    @classmethod
    def Int32ToInt64(cls, instance, v):
        return cls._dll.Int32ToInt64(instance, v)

    _dll.FindData.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.FindData.restype = c_int64

    @classmethod
    def FindData(cls, instance, hwnd, addr_range, data):
        return cls._dll.FindData(instance, hwnd, addr_range.encode("utf-8"), data.encode("utf-8"))

    _dll.FindDataEx.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_int, c_int, c_int]
    _dll.FindDataEx.restype = c_int64

    @classmethod
    def FindDataEx(cls, instance, hwnd, addr_range, data, step, multi_thread, mode):
        return cls._dll.FindDataEx(
            instance, hwnd, addr_range.encode("utf-8"), data.encode("utf-8"), step, multi_thread, mode
        )

    _dll.FindDouble.argtypes = [c_int64, c_int64, c_char_p, c_double, c_double]
    _dll.FindDouble.restype = c_int64

    @classmethod
    def FindDouble(cls, instance, hwnd, addr_range, double_value_min, double_value_max):
        return cls._dll.FindDouble(instance, hwnd, addr_range.encode("utf-8"), double_value_min, double_value_max)

    _dll.FindDoubleEx.argtypes = [c_int64, c_int64, c_char_p, c_double, c_double, c_int, c_int, c_int]
    _dll.FindDoubleEx.restype = c_int64

    @classmethod
    def FindDoubleEx(cls, instance, hwnd, addr_range, double_value_min, double_value_max, step, multi_thread, mode):
        return cls._dll.FindDoubleEx(
            instance, hwnd, addr_range.encode("utf-8"), double_value_min, double_value_max, step, multi_thread, mode
        )

    _dll.FindFloat.argtypes = [c_int64, c_int64, c_char_p, c_float, c_float]
    _dll.FindFloat.restype = c_int64

    @classmethod
    def FindFloat(cls, instance, hwnd, addr_range, float_value_min, float_value_max):
        return cls._dll.FindFloat(instance, hwnd, addr_range.encode("utf-8"), float_value_min, float_value_max)

    _dll.FindFloatEx.argtypes = [c_int64, c_int64, c_char_p, c_float, c_float, c_int, c_int, c_int]
    _dll.FindFloatEx.restype = c_int64

    @classmethod
    def FindFloatEx(cls, instance, hwnd, addr_range, float_value_min, float_value_max, step, multi_thread, mode):
        return cls._dll.FindFloatEx(
            instance, hwnd, addr_range.encode("utf-8"), float_value_min, float_value_max, step, multi_thread, mode
        )

    _dll.FindInt.argtypes = [c_int64, c_int64, c_char_p, c_int64, c_int64, c_int]
    _dll.FindInt.restype = c_int64

    @classmethod
    def FindInt(cls, instance, hwnd, addr_range, int_value_min, int_value_max, _type):
        return cls._dll.FindInt(instance, hwnd, addr_range.encode("utf-8"), int_value_min, int_value_max, _type)

    _dll.FindIntEx.argtypes = [c_int64, c_int64, c_char_p, c_int64, c_int64, c_int, c_int, c_int, c_int]
    _dll.FindIntEx.restype = c_int64

    @classmethod
    def FindIntEx(cls, instance, hwnd, addr_range, int_value_min, int_value_max, _type, step, multi_thread, mode):
        return cls._dll.FindIntEx(
            instance, hwnd, addr_range.encode("utf-8"), int_value_min, int_value_max, _type, step, multi_thread, mode
        )

    _dll.FindString.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_int]
    _dll.FindString.restype = c_int64

    @classmethod
    def FindString(cls, instance, hwnd, addr_range, string_value, _type):
        return cls._dll.FindString(instance, hwnd, addr_range.encode("utf-8"), string_value.encode("utf-8"), _type)

    _dll.FindStringEx.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_int, c_int, c_int, c_int]
    _dll.FindStringEx.restype = c_int64

    @classmethod
    def FindStringEx(cls, instance, hwnd, addr_range, string_value, _type, step, multi_thread, mode):
        return cls._dll.FindStringEx(
            instance, hwnd, addr_range.encode("utf-8"), string_value.encode("utf-8"), _type, step, multi_thread, mode
        )

    _dll.ReadData.argtypes = [c_int64, c_int64, c_char_p, c_int]
    _dll.ReadData.restype = c_int64

    @classmethod
    def ReadData(cls, instance, hwnd, addr, _len):
        return cls._dll.ReadData(instance, hwnd, addr.encode("utf-8"), _len)

    _dll.ReadDataAddr.argtypes = [c_int64, c_int64, c_int64, c_int]
    _dll.ReadDataAddr.restype = c_int64

    @classmethod
    def ReadDataAddr(cls, instance, hwnd, addr, _len):
        return cls._dll.ReadDataAddr(instance, hwnd, addr, _len)

    _dll.ReadDataAddrToBin.argtypes = [c_int64, c_int64, c_int64, c_int]
    _dll.ReadDataAddrToBin.restype = c_int64

    @classmethod
    def ReadDataAddrToBin(cls, instance, hwnd, addr, _len):
        return cls._dll.ReadDataAddrToBin(instance, hwnd, addr, _len)

    _dll.ReadDataToBin.argtypes = [c_int64, c_int64, c_char_p, c_int]
    _dll.ReadDataToBin.restype = c_int64

    @classmethod
    def ReadDataToBin(cls, instance, hwnd, addr, _len):
        return cls._dll.ReadDataToBin(instance, hwnd, addr.encode("utf-8"), _len)

    _dll.ReadDouble.argtypes = [c_int64, c_int64, c_char_p]
    _dll.ReadDouble.restype = c_double

    @classmethod
    def ReadDouble(cls, instance, hwnd, addr):
        return cls._dll.ReadDouble(instance, hwnd, addr.encode("utf-8"))

    _dll.ReadDoubleAddr.argtypes = [c_int64, c_int64, c_int64]
    _dll.ReadDoubleAddr.restype = c_double

    @classmethod
    def ReadDoubleAddr(cls, instance, hwnd, addr):
        return cls._dll.ReadDoubleAddr(instance, hwnd, addr)

    _dll.ReadFloat.argtypes = [c_int64, c_int64, c_char_p]
    _dll.ReadFloat.restype = c_float

    @classmethod
    def ReadFloat(cls, instance, hwnd, addr):
        return cls._dll.ReadFloat(instance, hwnd, addr.encode("utf-8"))

    _dll.ReadFloatAddr.argtypes = [c_int64, c_int64, c_int64]
    _dll.ReadFloatAddr.restype = c_float

    @classmethod
    def ReadFloatAddr(cls, instance, hwnd, addr):
        return cls._dll.ReadFloatAddr(instance, hwnd, addr)

    _dll.ReadInt.argtypes = [c_int64, c_int64, c_char_p, c_int]
    _dll.ReadInt.restype = c_int64

    @classmethod
    def ReadInt(cls, instance, hwnd, addr, _type):
        return cls._dll.ReadInt(instance, hwnd, addr.encode("utf-8"), _type)

    _dll.ReadIntAddr.argtypes = [c_int64, c_int64, c_int64, c_int]
    _dll.ReadIntAddr.restype = c_int64

    @classmethod
    def ReadIntAddr(cls, instance, hwnd, addr, _type):
        return cls._dll.ReadIntAddr(instance, hwnd, addr, _type)

    _dll.ReadString.argtypes = [c_int64, c_int64, c_char_p, c_int, c_int]
    _dll.ReadString.restype = c_int64

    @classmethod
    def ReadString(cls, instance, hwnd, addr, _type, _len):
        return cls._dll.ReadString(instance, hwnd, addr.encode("utf-8"), _type, _len)

    _dll.ReadStringAddr.argtypes = [c_int64, c_int64, c_int64, c_int, c_int]
    _dll.ReadStringAddr.restype = c_int64

    @classmethod
    def ReadStringAddr(cls, instance, hwnd, addr, _type, _len):
        return cls._dll.ReadStringAddr(instance, hwnd, addr, _type, _len)

    _dll.WriteData.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.WriteData.restype = c_int

    @classmethod
    def WriteData(cls, instance, hwnd, addr, data):
        return cls._dll.WriteData(instance, hwnd, addr.encode("utf-8"), data.encode("utf-8"))

    _dll.WriteDataFromBin.argtypes = [c_int64, c_int64, c_char_p, c_int64, c_int]
    _dll.WriteDataFromBin.restype = c_int

    @classmethod
    def WriteDataFromBin(cls, instance, hwnd, addr, data, _len):
        return cls._dll.WriteDataFromBin(instance, hwnd, addr.encode("utf-8"), data, _len)

    _dll.WriteDataAddr.argtypes = [c_int64, c_int64, c_int64, c_char_p]
    _dll.WriteDataAddr.restype = c_int

    @classmethod
    def WriteDataAddr(cls, instance, hwnd, addr, data):
        return cls._dll.WriteDataAddr(instance, hwnd, addr, data.encode("utf-8"))

    _dll.WriteDataAddrFromBin.argtypes = [c_int64, c_int64, c_int64, c_int64, c_int]
    _dll.WriteDataAddrFromBin.restype = c_int

    @classmethod
    def WriteDataAddrFromBin(cls, instance, hwnd, addr, data, _len):
        return cls._dll.WriteDataAddrFromBin(instance, hwnd, addr, data, _len)

    _dll.WriteDouble.argtypes = [c_int64, c_int64, c_char_p, c_double]
    _dll.WriteDouble.restype = c_int

    @classmethod
    def WriteDouble(cls, instance, hwnd, addr, double_value):
        return cls._dll.WriteDouble(instance, hwnd, addr.encode("utf-8"), double_value)

    _dll.WriteDoubleAddr.argtypes = [c_int64, c_int64, c_int64, c_double]
    _dll.WriteDoubleAddr.restype = c_int

    @classmethod
    def WriteDoubleAddr(cls, instance, hwnd, addr, double_value):
        return cls._dll.WriteDoubleAddr(instance, hwnd, addr, double_value)

    _dll.WriteFloat.argtypes = [c_int64, c_int64, c_char_p, c_float]
    _dll.WriteFloat.restype = c_int

    @classmethod
    def WriteFloat(cls, instance, hwnd, addr, float_value):
        return cls._dll.WriteFloat(instance, hwnd, addr.encode("utf-8"), float_value)

    _dll.WriteFloatAddr.argtypes = [c_int64, c_int64, c_int64, c_float]
    _dll.WriteFloatAddr.restype = c_int

    @classmethod
    def WriteFloatAddr(cls, instance, hwnd, addr, float_value):
        return cls._dll.WriteFloatAddr(instance, hwnd, addr, float_value)

    _dll.WriteInt.argtypes = [c_int64, c_int64, c_char_p, c_int, c_int64]
    _dll.WriteInt.restype = c_int

    @classmethod
    def WriteInt(cls, instance, hwnd, addr, _type, value):
        return cls._dll.WriteInt(instance, hwnd, addr.encode("utf-8"), _type, value)

    _dll.WriteIntAddr.argtypes = [c_int64, c_int64, c_int64, c_int, c_int64]
    _dll.WriteIntAddr.restype = c_int

    @classmethod
    def WriteIntAddr(cls, instance, hwnd, addr, _type, value):
        return cls._dll.WriteIntAddr(instance, hwnd, addr, _type, value)

    _dll.WriteString.argtypes = [c_int64, c_int64, c_char_p, c_int, c_char_p]
    _dll.WriteString.restype = c_int

    @classmethod
    def WriteString(cls, instance, hwnd, addr, _type, value):
        return cls._dll.WriteString(instance, hwnd, addr.encode("utf-8"), _type, value.encode("utf-8"))

    _dll.WriteStringAddr.argtypes = [c_int64, c_int64, c_int64, c_int, c_char_p]
    _dll.WriteStringAddr.restype = c_int

    @classmethod
    def WriteStringAddr(cls, instance, hwnd, addr, _type, value):
        return cls._dll.WriteStringAddr(instance, hwnd, addr, _type, value.encode("utf-8"))

    _dll.SetMemoryHwndAsProcessId.argtypes = [c_int64, c_int]
    _dll.SetMemoryHwndAsProcessId.restype = c_int

    @classmethod
    def SetMemoryHwndAsProcessId(cls, instance, enable):
        return cls._dll.SetMemoryHwndAsProcessId(instance, enable)

    _dll.FreeProcessMemory.argtypes = [c_int64, c_int64]
    _dll.FreeProcessMemory.restype = c_int

    @classmethod
    def FreeProcessMemory(cls, instance, hwnd):
        return cls._dll.FreeProcessMemory(instance, hwnd)

    _dll.GetModuleBaseAddr.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetModuleBaseAddr.restype = c_int64

    @classmethod
    def GetModuleBaseAddr(cls, instance, hwnd, module_name):
        return cls._dll.GetModuleBaseAddr(instance, hwnd, module_name.encode("utf-8"))

    _dll.GetModuleSize.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetModuleSize.restype = c_int

    @classmethod
    def GetModuleSize(cls, instance, hwnd, module_name):
        return cls._dll.GetModuleSize(instance, hwnd, module_name.encode("utf-8"))

    _dll.GetRemoteApiAddress.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.GetRemoteApiAddress.restype = c_int64

    @classmethod
    def GetRemoteApiAddress(cls, instance, hwnd, module_name, fun_name):
        return cls._dll.GetRemoteApiAddress(instance, hwnd, module_name.encode("utf-8"), fun_name.encode("utf-8"))

    _dll.VirtualAllocEx.argtypes = [c_int64, c_int64, c_int64, c_int, c_int]
    _dll.VirtualAllocEx.restype = c_int64

    @classmethod
    def VirtualAllocEx(cls, instance, hwnd, addr, size, _type):
        return cls._dll.VirtualAllocEx(instance, hwnd, addr, size, _type)

    _dll.VirtualFreeEx.argtypes = [c_int64, c_int64, c_int64]
    _dll.VirtualFreeEx.restype = c_int

    @classmethod
    def VirtualFreeEx(cls, instance, hwnd, addr):
        return cls._dll.VirtualFreeEx(instance, hwnd, addr)

    _dll.VirtualProtectEx.argtypes = [c_int64, c_int64, c_int64, c_int, c_int, POINTER(c_int)]
    _dll.VirtualProtectEx.restype = c_int

    @classmethod
    def VirtualProtectEx(cls, instance, hwnd, addr, size, newProtect, oldProtect=None):
        oldProtect = c_int(0)
        result = cls._dll.VirtualProtectEx(instance, hwnd, addr, size, newProtect, byref(oldProtect))
        return result, oldProtect.value

    _dll.VirtualQueryEx.argtypes = [c_int64, c_int64, c_int64, c_int64]
    _dll.VirtualQueryEx.restype = c_int64

    @classmethod
    def VirtualQueryEx(cls, instance, hwnd, addr, pmbi):
        return cls._dll.VirtualQueryEx(instance, hwnd, addr, pmbi)

    _dll.CreateRemoteThread.argtypes = [c_int64, c_int64, c_int64, c_int64, c_int, POINTER(c_int64)]
    _dll.CreateRemoteThread.restype = c_int64

    @classmethod
    def CreateRemoteThread(cls, instance, hwnd, lpStartAddress, lpParameter, dwCreationFlags, lpThreadId=None):
        lpThreadId = c_int64(0)
        result = cls._dll.CreateRemoteThread(
            instance, hwnd, lpStartAddress, lpParameter, dwCreationFlags, byref(lpThreadId)
        )
        return result, lpThreadId.value

    _dll.CloseHandle.argtypes = [c_int64, c_int64]
    _dll.CloseHandle.restype = c_int

    @classmethod
    def CloseHandle(cls, instance, handle):
        return cls._dll.CloseHandle(instance, handle)

    _dll.HookRemoteApi.argtypes = [c_int64, c_int64, c_int64, c_int64, c_int64]
    _dll.HookRemoteApi.restype = c_int

    @classmethod
    def HookRemoteApi(cls, instance, hwnd, targetAddr, size, hook_proc):
        return cls._dll.HookRemoteApi(instance, hwnd, targetAddr, size, hook_proc)

    _dll.UnhookRemoteApi.argtypes = [c_int64, c_int64, c_int64]
    _dll.UnhookRemoteApi.restype = c_int

    @classmethod
    def UnhookRemoteApi(cls, instance, hwnd, targetAddr):
        return cls._dll.UnhookRemoteApi(instance, hwnd, targetAddr)

    _dll.Ocr.argtypes = [c_int64, c_int, c_int, c_int, c_int]
    _dll.Ocr.restype = c_int64

    @classmethod
    def Ocr(cls, instance, x1, y1, x2, y2):
        return cls._dll.Ocr(instance, x1, y1, x2, y2)

    _dll.OcrFromPtr.argtypes = [c_int64, c_int64]
    _dll.OcrFromPtr.restype = c_int64

    @classmethod
    def OcrFromPtr(cls, instance, ptr):
        return cls._dll.OcrFromPtr(instance, ptr)

    _dll.OcrFromBmpData.argtypes = [c_int64, c_int64, c_int]
    _dll.OcrFromBmpData.restype = c_int64

    @classmethod
    def OcrFromBmpData(cls, instance, ptr, size):
        return cls._dll.OcrFromBmpData(instance, ptr, size)

    _dll.OcrDetails.argtypes = [c_int64, c_int, c_int, c_int, c_int]
    _dll.OcrDetails.restype = c_int64

    @classmethod
    def OcrDetails(cls, instance, x1, y1, x2, y2):
        return cls._dll.OcrDetails(instance, x1, y1, x2, y2)

    _dll.OcrFromPtrDetails.argtypes = [c_int64, c_int64]
    _dll.OcrFromPtrDetails.restype = c_int64

    @classmethod
    def OcrFromPtrDetails(cls, instance, ptr):
        return cls._dll.OcrFromPtrDetails(instance, ptr)

    _dll.OcrFromBmpDataDetails.argtypes = [c_int64, c_int64, c_int]
    _dll.OcrFromBmpDataDetails.restype = c_int64

    @classmethod
    def OcrFromBmpDataDetails(cls, instance, ptr, size):
        return cls._dll.OcrFromBmpDataDetails(instance, ptr, size)

    _dll.OcrV5.argtypes = [c_int64, c_int, c_int, c_int, c_int]
    _dll.OcrV5.restype = c_int64

    @classmethod
    def OcrV5(cls, instance, x1, y1, x2, y2):
        return cls._dll.OcrV5(instance, x1, y1, x2, y2)

    _dll.OcrV5Details.argtypes = [c_int64, c_int, c_int, c_int, c_int]
    _dll.OcrV5Details.restype = c_int64

    @classmethod
    def OcrV5Details(cls, instance, x1, y1, x2, y2):
        return cls._dll.OcrV5Details(instance, x1, y1, x2, y2)

    _dll.OcrV5FromPtr.argtypes = [c_int64, c_int64]
    _dll.OcrV5FromPtr.restype = c_int64

    @classmethod
    def OcrV5FromPtr(cls, instance, ptr):
        return cls._dll.OcrV5FromPtr(instance, ptr)

    _dll.OcrV5FromPtrDetails.argtypes = [c_int64, c_int64]
    _dll.OcrV5FromPtrDetails.restype = c_int64

    @classmethod
    def OcrV5FromPtrDetails(cls, instance, ptr):
        return cls._dll.OcrV5FromPtrDetails(instance, ptr)

    _dll.GetOcrConfig.argtypes = [c_int64, c_char_p]
    _dll.GetOcrConfig.restype = c_int64

    @classmethod
    def GetOcrConfig(cls, instance, configKey):
        return cls._dll.GetOcrConfig(instance, configKey.encode("utf-8"))

    _dll.SetOcrConfig.argtypes = [c_int64, c_char_p]
    _dll.SetOcrConfig.restype = c_int

    @classmethod
    def SetOcrConfig(cls, instance, configStr):
        return cls._dll.SetOcrConfig(instance, configStr.encode("utf-8"))

    _dll.SetOcrConfigByKey.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.SetOcrConfigByKey.restype = c_int

    @classmethod
    def SetOcrConfigByKey(cls, instance, key, value):
        return cls._dll.SetOcrConfigByKey(instance, key.encode("utf-8"), value.encode("utf-8"))

    _dll.OcrFromDict.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_char_p, c_double]
    _dll.OcrFromDict.restype = c_int64

    @classmethod
    def OcrFromDict(cls, instance, x1, y1, x2, y2, colorJson, dict_name, matchVal):
        return cls._dll.OcrFromDict(
            instance, x1, y1, x2, y2, colorJson.encode("utf-8"), dict_name.encode("utf-8"), matchVal
        )

    _dll.OcrFromDictDetails.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_char_p, c_double]
    _dll.OcrFromDictDetails.restype = c_int64

    @classmethod
    def OcrFromDictDetails(cls, instance, x1, y1, x2, y2, colorJson, dict_name, matchVal):
        return cls._dll.OcrFromDictDetails(
            instance, x1, y1, x2, y2, colorJson.encode("utf-8"), dict_name.encode("utf-8"), matchVal
        )

    _dll.OcrFromDictPtr.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_double]
    _dll.OcrFromDictPtr.restype = c_int64

    @classmethod
    def OcrFromDictPtr(cls, instance, ptr, colorJson, dict_name, matchVal):
        return cls._dll.OcrFromDictPtr(instance, ptr, colorJson.encode("utf-8"), dict_name.encode("utf-8"), matchVal)

    _dll.OcrFromDictPtrDetails.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_double]
    _dll.OcrFromDictPtrDetails.restype = c_int64

    @classmethod
    def OcrFromDictPtrDetails(cls, instance, ptr, colorJson, dict_name, matchVal):
        return cls._dll.OcrFromDictPtrDetails(
            instance, ptr, colorJson.encode("utf-8"), dict_name.encode("utf-8"), matchVal
        )

    _dll.FindStr.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_char_p,
        c_char_p,
        c_double,
        POINTER(c_int),
        POINTER(c_int),
    ]
    _dll.FindStr.restype = c_int

    @classmethod
    def FindStr(cls, instance, x1, y1, x2, y2, _str, colorJson, _dict, matchVal, outX=None, outY=None):
        outX = c_int(0)
        outY = c_int(0)
        result = cls._dll.FindStr(
            instance,
            x1,
            y1,
            x2,
            y2,
            _str.encode("utf-8"),
            colorJson.encode("utf-8"),
            _dict.encode("utf-8"),
            matchVal,
            byref(outX),
            byref(outY),
        )
        return result, outX.value, outY.value

    _dll.FindStrDetail.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_char_p, c_char_p, c_double]
    _dll.FindStrDetail.restype = c_int64

    @classmethod
    def FindStrDetail(cls, instance, x1, y1, x2, y2, _str, colorJson, _dict, matchVal):
        return cls._dll.FindStrDetail(
            instance, x1, y1, x2, y2, _str.encode("utf-8"), colorJson.encode("utf-8"), _dict.encode("utf-8"), matchVal
        )

    _dll.FindStrAll.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_char_p, c_char_p, c_double]
    _dll.FindStrAll.restype = c_int64

    @classmethod
    def FindStrAll(cls, instance, x1, y1, x2, y2, _str, colorJson, _dict, matchVal):
        return cls._dll.FindStrAll(
            instance, x1, y1, x2, y2, _str.encode("utf-8"), colorJson.encode("utf-8"), _dict.encode("utf-8"), matchVal
        )

    _dll.FindStrFromPtr.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_char_p, c_double]
    _dll.FindStrFromPtr.restype = c_int64

    @classmethod
    def FindStrFromPtr(cls, instance, source, _str, colorJson, _dict, matchVal):
        return cls._dll.FindStrFromPtr(
            instance, source, _str.encode("utf-8"), colorJson.encode("utf-8"), _dict.encode("utf-8"), matchVal
        )

    _dll.FindStrFromPtrAll.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_char_p, c_double]
    _dll.FindStrFromPtrAll.restype = c_int64

    @classmethod
    def FindStrFromPtrAll(cls, instance, source, _str, colorJson, _dict, matchVal):
        return cls._dll.FindStrFromPtrAll(
            instance, source, _str.encode("utf-8"), colorJson.encode("utf-8"), _dict.encode("utf-8"), matchVal
        )

    _dll.FastNumberOcrFromPtr.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_double]
    _dll.FastNumberOcrFromPtr.restype = c_int

    @classmethod
    def FastNumberOcrFromPtr(cls, instance, source, numbers, colorJson, matchVal):
        return cls._dll.FastNumberOcrFromPtr(
            instance, source, numbers.encode("utf-8"), colorJson.encode("utf-8"), matchVal
        )

    _dll.FastNumberOcr.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_char_p, c_double]
    _dll.FastNumberOcr.restype = c_int

    @classmethod
    def FastNumberOcr(cls, instance, x1, y1, x2, y2, numbers, colorJson, matchVal):
        return cls._dll.FastNumberOcr(
            instance, x1, y1, x2, y2, numbers.encode("utf-8"), colorJson.encode("utf-8"), matchVal
        )

    _dll.ImportTxtDict.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.ImportTxtDict.restype = c_int

    @classmethod
    def ImportTxtDict(cls, instance, dictName, dictPath):
        return cls._dll.ImportTxtDict(instance, dictName.encode("utf-8"), dictPath.encode("utf-8"))

    _dll.ExportTxtDict.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.ExportTxtDict.restype = c_int

    @classmethod
    def ExportTxtDict(cls, instance, dictName, dictPath):
        return cls._dll.ExportTxtDict(instance, dictName.encode("utf-8"), dictPath.encode("utf-8"))

    _dll.Capture.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p]
    _dll.Capture.restype = c_int

    @classmethod
    def Capture(cls, instance, x1, y1, x2, y2, file):
        return cls._dll.Capture(instance, x1, y1, x2, y2, file.encode("utf-8"))

    _dll.GetScreenDataBmp.argtypes = [c_int64, c_int, c_int, c_int, c_int, POINTER(c_int64), POINTER(c_int)]
    _dll.GetScreenDataBmp.restype = c_int

    @classmethod
    def GetScreenDataBmp(cls, instance, x1, y1, x2, y2, data=None, dataLen=None):
        data = c_int64(0)
        dataLen = c_int(0)
        result = cls._dll.GetScreenDataBmp(instance, x1, y1, x2, y2, byref(data), byref(dataLen))
        return result, data.value, dataLen.value

    _dll.GetScreenData.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        POINTER(c_int64),
        POINTER(c_int),
        POINTER(c_int),
    ]
    _dll.GetScreenData.restype = c_int

    @classmethod
    def GetScreenData(cls, instance, x1, y1, x2, y2, data=None, dataLen=None, stride=None):
        data = c_int64(0)
        dataLen = c_int(0)
        stride = c_int(0)
        result = cls._dll.GetScreenData(instance, x1, y1, x2, y2, byref(data), byref(dataLen), byref(stride))
        return result, data.value, dataLen.value, stride.value

    _dll.GetScreenDataPtr.argtypes = [c_int64, c_int, c_int, c_int, c_int]
    _dll.GetScreenDataPtr.restype = c_int64

    @classmethod
    def GetScreenDataPtr(cls, instance, x1, y1, x2, y2):
        return cls._dll.GetScreenDataPtr(instance, x1, y1, x2, y2)

    _dll.CaptureGif.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_int, c_int]
    _dll.CaptureGif.restype = c_int

    @classmethod
    def CaptureGif(cls, instance, x1, y1, x2, y2, file, delay, time):
        return cls._dll.CaptureGif(instance, x1, y1, x2, y2, file.encode("utf-8"), delay, time)

    _dll.LockDisplay.argtypes = [c_int64, c_int]
    _dll.LockDisplay.restype = c_int

    @classmethod
    def LockDisplay(cls, instance, enable):
        return cls._dll.LockDisplay(instance, enable)

    _dll.SetSnapCacheTime.argtypes = [c_int64, c_int]
    _dll.SetSnapCacheTime.restype = c_int

    @classmethod
    def SetSnapCacheTime(cls, instance, cacheTime):
        return cls._dll.SetSnapCacheTime(instance, cacheTime)

    _dll.GetImageData.argtypes = [c_int64, c_int64, POINTER(c_int64), POINTER(c_int), POINTER(c_int)]
    _dll.GetImageData.restype = c_int

    @classmethod
    def GetImageData(cls, instance, imgPtr, data=None, size=None, stride=None):
        data = c_int64(0)
        size = c_int(0)
        stride = c_int(0)
        result = cls._dll.GetImageData(instance, imgPtr, byref(data), byref(size), byref(stride))
        return result, data.value, size.value, stride.value

    _dll.MatchImageFromPath.argtypes = [c_int64, c_char_p, c_char_p, c_double, c_int, c_double, c_double]
    _dll.MatchImageFromPath.restype = c_int64

    @classmethod
    def MatchImageFromPath(cls, instance, source, templ, matchVal, _type, angle, scale):
        return cls._dll.MatchImageFromPath(
            instance, source.encode("utf-8"), templ.encode("utf-8"), matchVal, _type, angle, scale
        )

    _dll.MatchImageFromPathAll.argtypes = [c_int64, c_char_p, c_char_p, c_double, c_int, c_double, c_double]
    _dll.MatchImageFromPathAll.restype = c_int64

    @classmethod
    def MatchImageFromPathAll(cls, instance, source, templ, matchVal, _type, angle, scale):
        return cls._dll.MatchImageFromPathAll(
            instance, source.encode("utf-8"), templ.encode("utf-8"), matchVal, _type, angle, scale
        )

    _dll.MatchImagePtrFromPath.argtypes = [c_int64, c_int64, c_char_p, c_double, c_int, c_double, c_double]
    _dll.MatchImagePtrFromPath.restype = c_int64

    @classmethod
    def MatchImagePtrFromPath(cls, instance, source, templ, matchVal, _type, angle, scale):
        return cls._dll.MatchImagePtrFromPath(instance, source, templ.encode("utf-8"), matchVal, _type, angle, scale)

    _dll.MatchImagePtrFromPathAll.argtypes = [c_int64, c_int64, c_char_p, c_double, c_int, c_double, c_double]
    _dll.MatchImagePtrFromPathAll.restype = c_int64

    @classmethod
    def MatchImagePtrFromPathAll(cls, instance, source, templ, matchVal, _type, angle, scale):
        return cls._dll.MatchImagePtrFromPathAll(instance, source, templ.encode("utf-8"), matchVal, _type, angle, scale)

    _dll.GetColor.argtypes = [c_int64, c_int, c_int]
    _dll.GetColor.restype = c_int64

    @classmethod
    def GetColor(cls, instance, x, y):
        return cls._dll.GetColor(instance, x, y)

    _dll.GetColorPtr.argtypes = [c_int64, c_int64, c_int, c_int]
    _dll.GetColorPtr.restype = c_int64

    @classmethod
    def GetColorPtr(cls, instance, source, x, y):
        return cls._dll.GetColorPtr(instance, source, x, y)

    _dll.CopyImage.argtypes = [c_int64, c_int64]
    _dll.CopyImage.restype = c_int64

    @classmethod
    def CopyImage(cls, instance, sourcePtr):
        return cls._dll.CopyImage(instance, sourcePtr)

    _dll.FreeImagePath.argtypes = [c_int64, c_char_p]
    _dll.FreeImagePath.restype = c_int

    @classmethod
    def FreeImagePath(cls, instance, path):
        return cls._dll.FreeImagePath(instance, path.encode("utf-8"))

    _dll.FreeImageAll.argtypes = [c_int64]
    _dll.FreeImageAll.restype = c_int

    @classmethod
    def FreeImageAll(cls, instance):
        return cls._dll.FreeImageAll(instance)

    _dll.LoadImage.argtypes = [c_int64, c_char_p]
    _dll.LoadImage.restype = c_int64

    @classmethod
    def LoadImage(cls, instance, path):
        return cls._dll.LoadImage(instance, path.encode("utf-8"))

    _dll.LoadImageFromBmpData.argtypes = [c_int64, c_int64, c_int]
    _dll.LoadImageFromBmpData.restype = c_int64

    @classmethod
    def LoadImageFromBmpData(cls, instance, data, dataSize):
        return cls._dll.LoadImageFromBmpData(instance, data, dataSize)

    _dll.LoadImageFromRGBData.argtypes = [c_int64, c_int, c_int, c_int64, c_int]
    _dll.LoadImageFromRGBData.restype = c_int64

    @classmethod
    def LoadImageFromRGBData(cls, instance, width, height, scan0, stride):
        return cls._dll.LoadImageFromRGBData(instance, width, height, scan0, stride)

    _dll.FreeImagePtr.argtypes = [c_int64, c_int64]
    _dll.FreeImagePtr.restype = c_int

    @classmethod
    def FreeImagePtr(cls, instance, screenPtr):
        return cls._dll.FreeImagePtr(instance, screenPtr)

    _dll.MatchWindowsFromPtr.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int64,
        c_double,
        c_int,
        c_double,
        c_double,
    ]
    _dll.MatchWindowsFromPtr.restype = c_int64

    @classmethod
    def MatchWindowsFromPtr(cls, instance, x1, y1, x2, y2, templ, matchVal, _type, angle, scale):
        return cls._dll.MatchWindowsFromPtr(instance, x1, y1, x2, y2, templ, matchVal, _type, angle, scale)

    _dll.MatchImageFromPtr.argtypes = [c_int64, c_int64, c_int64, c_double, c_int, c_double, c_double]
    _dll.MatchImageFromPtr.restype = c_int64

    @classmethod
    def MatchImageFromPtr(cls, instance, source, templ, matchVal, _type, angle, scale):
        return cls._dll.MatchImageFromPtr(instance, source, templ, matchVal, _type, angle, scale)

    _dll.MatchImageFromPtrAll.argtypes = [c_int64, c_int64, c_int64, c_double, c_int, c_double, c_double]
    _dll.MatchImageFromPtrAll.restype = c_int64

    @classmethod
    def MatchImageFromPtrAll(cls, instance, source, templ, matchVal, _type, angle, scale):
        return cls._dll.MatchImageFromPtrAll(instance, source, templ, matchVal, _type, angle, scale)

    _dll.MatchWindowsFromPtrAll.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int64,
        c_double,
        c_int,
        c_double,
        c_double,
    ]
    _dll.MatchWindowsFromPtrAll.restype = c_int64

    @classmethod
    def MatchWindowsFromPtrAll(cls, instance, x1, y1, x2, y2, templ, matchVal, _type, angle, scale):
        return cls._dll.MatchWindowsFromPtrAll(instance, x1, y1, x2, y2, templ, matchVal, _type, angle, scale)

    _dll.MatchWindowsFromPath.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_double,
        c_int,
        c_double,
        c_double,
    ]
    _dll.MatchWindowsFromPath.restype = c_int64

    @classmethod
    def MatchWindowsFromPath(cls, instance, x1, y1, x2, y2, templ, matchVal, _type, angle, scale):
        return cls._dll.MatchWindowsFromPath(
            instance, x1, y1, x2, y2, templ.encode("utf-8"), matchVal, _type, angle, scale
        )

    _dll.MatchWindowsFromPathAll.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_double,
        c_int,
        c_double,
        c_double,
    ]
    _dll.MatchWindowsFromPathAll.restype = c_int64

    @classmethod
    def MatchWindowsFromPathAll(cls, instance, x1, y1, x2, y2, templ, matchVal, _type, angle, scale):
        return cls._dll.MatchWindowsFromPathAll(
            instance, x1, y1, x2, y2, templ.encode("utf-8"), matchVal, _type, angle, scale
        )

    _dll.MatchWindowsThresholdFromPtr.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_int64,
        c_double,
        c_double,
        c_double,
    ]
    _dll.MatchWindowsThresholdFromPtr.restype = c_int64

    @classmethod
    def MatchWindowsThresholdFromPtr(cls, instance, x1, y1, x2, y2, colorJson, templ, matchVal, angle, scale):
        return cls._dll.MatchWindowsThresholdFromPtr(
            instance, x1, y1, x2, y2, colorJson.encode("utf-8"), templ, matchVal, angle, scale
        )

    _dll.MatchWindowsThresholdFromPtrAll.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_int64,
        c_double,
        c_double,
        c_double,
    ]
    _dll.MatchWindowsThresholdFromPtrAll.restype = c_int64

    @classmethod
    def MatchWindowsThresholdFromPtrAll(cls, instance, x1, y1, x2, y2, colorJson, templ, matchVal, angle, scale):
        return cls._dll.MatchWindowsThresholdFromPtrAll(
            instance, x1, y1, x2, y2, colorJson.encode("utf-8"), templ, matchVal, angle, scale
        )

    _dll.MatchWindowsThresholdFromPath.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_char_p,
        c_double,
        c_double,
        c_double,
    ]
    _dll.MatchWindowsThresholdFromPath.restype = c_int64

    @classmethod
    def MatchWindowsThresholdFromPath(cls, instance, x1, y1, x2, y2, colorJson, templ, matchVal, angle, scale):
        return cls._dll.MatchWindowsThresholdFromPath(
            instance, x1, y1, x2, y2, colorJson.encode("utf-8"), templ.encode("utf-8"), matchVal, angle, scale
        )

    _dll.MatchWindowsThresholdFromPathAll.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_char_p,
        c_double,
        c_double,
        c_double,
    ]
    _dll.MatchWindowsThresholdFromPathAll.restype = c_int64

    @classmethod
    def MatchWindowsThresholdFromPathAll(cls, instance, x1, y1, x2, y2, colorJson, templ, matchVal, angle, scale):
        return cls._dll.MatchWindowsThresholdFromPathAll(
            instance, x1, y1, x2, y2, colorJson.encode("utf-8"), templ.encode("utf-8"), matchVal, angle, scale
        )

    _dll.ShowMatchWindow.argtypes = [c_int64, c_int]
    _dll.ShowMatchWindow.restype = c_int

    @classmethod
    def ShowMatchWindow(cls, instance, flag):
        return cls._dll.ShowMatchWindow(instance, flag)

    _dll.CalculateSSIM.argtypes = [c_int64, c_int64, c_int64]
    _dll.CalculateSSIM.restype = c_double

    @classmethod
    def CalculateSSIM(cls, instance, image1, image2):
        return cls._dll.CalculateSSIM(instance, image1, image2)

    _dll.CalculateHistograms.argtypes = [c_int64, c_int64, c_int64]
    _dll.CalculateHistograms.restype = c_double

    @classmethod
    def CalculateHistograms(cls, instance, image1, image2):
        return cls._dll.CalculateHistograms(instance, image1, image2)

    _dll.CalculateMSE.argtypes = [c_int64, c_int64, c_int64]
    _dll.CalculateMSE.restype = c_double

    @classmethod
    def CalculateMSE(cls, instance, image1, image2):
        return cls._dll.CalculateMSE(instance, image1, image2)

    _dll.SaveImageFromPtr.argtypes = [c_int64, c_int64, c_char_p]
    _dll.SaveImageFromPtr.restype = c_int

    @classmethod
    def SaveImageFromPtr(cls, instance, ptr, path):
        return cls._dll.SaveImageFromPtr(instance, ptr, path.encode("utf-8"))

    _dll.ReSize.argtypes = [c_int64, c_int64, c_int, c_int]
    _dll.ReSize.restype = c_int64

    @classmethod
    def ReSize(cls, instance, ptr, width, height):
        return cls._dll.ReSize(instance, ptr, width, height)

    _dll.FindColor.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_char_p,
        c_int,
        POINTER(c_int),
        POINTER(c_int),
    ]
    _dll.FindColor.restype = c_int

    @classmethod
    def FindColor(cls, instance, x1, y1, x2, y2, color1, color2, _dir, x=None, y=None):
        x = c_int(0)
        y = c_int(0)
        result = cls._dll.FindColor(
            instance, x1, y1, x2, y2, color1.encode("utf-8"), color2.encode("utf-8"), _dir, byref(x), byref(y)
        )
        return result, x.value, y.value

    _dll.FindColorList.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_char_p]
    _dll.FindColorList.restype = c_int64

    @classmethod
    def FindColorList(cls, instance, x1, y1, x2, y2, color1, color2):
        return cls._dll.FindColorList(instance, x1, y1, x2, y2, color1.encode("utf-8"), color2.encode("utf-8"))

    _dll.FindColorEx.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_int, POINTER(c_int), POINTER(c_int)]
    _dll.FindColorEx.restype = c_int

    @classmethod
    def FindColorEx(cls, instance, x1, y1, x2, y2, colorJson, _dir, x=None, y=None):
        x = c_int(0)
        y = c_int(0)
        result = cls._dll.FindColorEx(instance, x1, y1, x2, y2, colorJson.encode("utf-8"), _dir, byref(x), byref(y))
        return result, x.value, y.value

    _dll.FindColorListEx.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p]
    _dll.FindColorListEx.restype = c_int64

    @classmethod
    def FindColorListEx(cls, instance, x1, y1, x2, y2, colorJson):
        return cls._dll.FindColorListEx(instance, x1, y1, x2, y2, colorJson.encode("utf-8"))

    _dll.FindMultiColor.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_char_p,
        c_double,
        c_int,
        POINTER(c_int),
        POINTER(c_int),
    ]
    _dll.FindMultiColor.restype = c_int

    @classmethod
    def FindMultiColor(cls, instance, x1, y1, x2, y2, colorJson, pointJson, sim, _dir, x=None, y=None):
        x = c_int(0)
        y = c_int(0)
        result = cls._dll.FindMultiColor(
            instance,
            x1,
            y1,
            x2,
            y2,
            colorJson.encode("utf-8"),
            pointJson.encode("utf-8"),
            sim,
            _dir,
            byref(x),
            byref(y),
        )
        return result, x.value, y.value

    _dll.FindMultiColorList.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_char_p, c_double]
    _dll.FindMultiColorList.restype = c_int64

    @classmethod
    def FindMultiColorList(cls, instance, x1, y1, x2, y2, colorJson, pointJson, sim):
        return cls._dll.FindMultiColorList(
            instance, x1, y1, x2, y2, colorJson.encode("utf-8"), pointJson.encode("utf-8"), sim
        )

    _dll.FindMultiColorFromPtr.argtypes = [
        c_int64,
        c_int64,
        c_char_p,
        c_char_p,
        c_double,
        c_int,
        POINTER(c_int),
        POINTER(c_int),
    ]
    _dll.FindMultiColorFromPtr.restype = c_int

    @classmethod
    def FindMultiColorFromPtr(cls, instance, ptr, colorJson, pointJson, sim, _dir, x=None, y=None):
        x = c_int(0)
        y = c_int(0)
        result = cls._dll.FindMultiColorFromPtr(
            instance, ptr, colorJson.encode("utf-8"), pointJson.encode("utf-8"), sim, _dir, byref(x), byref(y)
        )
        return result, x.value, y.value

    _dll.FindMultiColorListFromPtr.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_double]
    _dll.FindMultiColorListFromPtr.restype = c_int64

    @classmethod
    def FindMultiColorListFromPtr(cls, instance, ptr, colorJson, pointJson, sim):
        return cls._dll.FindMultiColorListFromPtr(
            instance, ptr, colorJson.encode("utf-8"), pointJson.encode("utf-8"), sim
        )

    _dll.GetImageSize.argtypes = [c_int64, c_int64, POINTER(c_int), POINTER(c_int)]
    _dll.GetImageSize.restype = c_int

    @classmethod
    def GetImageSize(cls, instance, ptr, width=None, height=None):
        width = c_int(0)
        height = c_int(0)
        result = cls._dll.GetImageSize(instance, ptr, byref(width), byref(height))
        return result, width.value, height.value

    _dll.FindColorBlock.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_int,
        c_int,
        c_int,
        POINTER(c_int),
        POINTER(c_int),
    ]
    _dll.FindColorBlock.restype = c_int

    @classmethod
    def FindColorBlock(cls, instance, x1, y1, x2, y2, colorList, count, width, height, x=None, y=None):
        x = c_int(0)
        y = c_int(0)
        result = cls._dll.FindColorBlock(
            instance, x1, y1, x2, y2, colorList.encode("utf-8"), count, width, height, byref(x), byref(y)
        )
        return result, x.value, y.value

    _dll.FindColorBlockPtr.argtypes = [c_int64, c_int64, c_char_p, c_int, c_int, c_int, POINTER(c_int), POINTER(c_int)]
    _dll.FindColorBlockPtr.restype = c_int

    @classmethod
    def FindColorBlockPtr(cls, instance, ptr, colorList, count, width, height, x=None, y=None):
        x = c_int(0)
        y = c_int(0)
        result = cls._dll.FindColorBlockPtr(
            instance, ptr, colorList.encode("utf-8"), count, width, height, byref(x), byref(y)
        )
        return result, x.value, y.value

    _dll.FindColorBlockList.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_int, c_int, c_int, c_int]
    _dll.FindColorBlockList.restype = c_int64

    @classmethod
    def FindColorBlockList(cls, instance, x1, y1, x2, y2, colorList, count, width, height, _type):
        return cls._dll.FindColorBlockList(
            instance, x1, y1, x2, y2, colorList.encode("utf-8"), count, width, height, _type
        )

    _dll.FindColorBlockListPtr.argtypes = [c_int64, c_int64, c_char_p, c_int, c_int, c_int, c_int]
    _dll.FindColorBlockListPtr.restype = c_int64

    @classmethod
    def FindColorBlockListPtr(cls, instance, ptr, colorList, count, width, height, _type):
        return cls._dll.FindColorBlockListPtr(instance, ptr, colorList.encode("utf-8"), count, width, height, _type)

    _dll.FindColorBlockEx.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_int,
        c_int,
        c_int,
        c_int,
        POINTER(c_int),
        POINTER(c_int),
    ]
    _dll.FindColorBlockEx.restype = c_int

    @classmethod
    def FindColorBlockEx(cls, instance, x1, y1, x2, y2, colorList, count, width, height, _dir, x=None, y=None):
        x = c_int(0)
        y = c_int(0)
        result = cls._dll.FindColorBlockEx(
            instance, x1, y1, x2, y2, colorList.encode("utf-8"), count, width, height, _dir, byref(x), byref(y)
        )
        return result, x.value, y.value

    _dll.FindColorBlockPtrEx.argtypes = [
        c_int64,
        c_int64,
        c_char_p,
        c_int,
        c_int,
        c_int,
        c_int,
        POINTER(c_int),
        POINTER(c_int),
    ]
    _dll.FindColorBlockPtrEx.restype = c_int

    @classmethod
    def FindColorBlockPtrEx(cls, instance, ptr, colorList, count, width, height, _dir, x=None, y=None):
        x = c_int(0)
        y = c_int(0)
        result = cls._dll.FindColorBlockPtrEx(
            instance, ptr, colorList.encode("utf-8"), count, width, height, _dir, byref(x), byref(y)
        )
        return result, x.value, y.value

    _dll.FindColorBlockListEx.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int,
    ]
    _dll.FindColorBlockListEx.restype = c_int64

    @classmethod
    def FindColorBlockListEx(cls, instance, x1, y1, x2, y2, colorList, count, width, height, _type, _dir):
        return cls._dll.FindColorBlockListEx(
            instance, x1, y1, x2, y2, colorList.encode("utf-8"), count, width, height, _type, _dir
        )

    _dll.FindColorBlockListPtrEx.argtypes = [c_int64, c_int64, c_char_p, c_int, c_int, c_int, c_int, c_int]
    _dll.FindColorBlockListPtrEx.restype = c_int64

    @classmethod
    def FindColorBlockListPtrEx(cls, instance, ptr, colorList, count, width, height, _type, _dir):
        return cls._dll.FindColorBlockListPtrEx(
            instance, ptr, colorList.encode("utf-8"), count, width, height, _type, _dir
        )

    _dll.GetColorNum.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p]
    _dll.GetColorNum.restype = c_int

    @classmethod
    def GetColorNum(cls, instance, x1, y1, x2, y2, colorList):
        return cls._dll.GetColorNum(instance, x1, y1, x2, y2, colorList.encode("utf-8"))

    _dll.GetColorNumPtr.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetColorNumPtr.restype = c_int

    @classmethod
    def GetColorNumPtr(cls, instance, ptr, colorList):
        return cls._dll.GetColorNumPtr(instance, ptr, colorList.encode("utf-8"))

    _dll.Cropped.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int]
    _dll.Cropped.restype = c_int64

    @classmethod
    def Cropped(cls, instance, image, x1, y1, x2, y2):
        return cls._dll.Cropped(instance, image, x1, y1, x2, y2)

    _dll.GetThresholdImageFromMultiColorPtr.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetThresholdImageFromMultiColorPtr.restype = c_int64

    @classmethod
    def GetThresholdImageFromMultiColorPtr(cls, instance, ptr, colorJson):
        return cls._dll.GetThresholdImageFromMultiColorPtr(instance, ptr, colorJson.encode("utf-8"))

    _dll.GetThresholdImageFromMultiColor.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p]
    _dll.GetThresholdImageFromMultiColor.restype = c_int64

    @classmethod
    def GetThresholdImageFromMultiColor(cls, instance, x1, y1, x2, y2, colorJson):
        return cls._dll.GetThresholdImageFromMultiColor(instance, x1, y1, x2, y2, colorJson.encode("utf-8"))

    _dll.IsSameImage.argtypes = [c_int64, c_int64, c_int64]
    _dll.IsSameImage.restype = c_int

    @classmethod
    def IsSameImage(cls, instance, ptr, ptr2):
        return cls._dll.IsSameImage(instance, ptr, ptr2)

    _dll.ShowImage.argtypes = [c_int64, c_int64]
    _dll.ShowImage.restype = c_int

    @classmethod
    def ShowImage(cls, instance, ptr):
        return cls._dll.ShowImage(instance, ptr)

    _dll.ShowImageFromFile.argtypes = [c_int64, c_char_p]
    _dll.ShowImageFromFile.restype = c_int

    @classmethod
    def ShowImageFromFile(cls, instance, file):
        return cls._dll.ShowImageFromFile(instance, file.encode("utf-8"))

    _dll.SetColorsToNewColor.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.SetColorsToNewColor.restype = c_int64

    @classmethod
    def SetColorsToNewColor(cls, instance, ptr, colorJson, color):
        return cls._dll.SetColorsToNewColor(instance, ptr, colorJson.encode("utf-8"), color.encode("utf-8"))

    _dll.RemoveOtherColors.argtypes = [c_int64, c_int64, c_char_p]
    _dll.RemoveOtherColors.restype = c_int64

    @classmethod
    def RemoveOtherColors(cls, instance, ptr, colorJson):
        return cls._dll.RemoveOtherColors(instance, ptr, colorJson.encode("utf-8"))

    _dll.DrawRectangle.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int, c_int, c_char_p]
    _dll.DrawRectangle.restype = c_int64

    @classmethod
    def DrawRectangle(cls, instance, ptr, x1, y1, x2, y2, thickness, color):
        return cls._dll.DrawRectangle(instance, ptr, x1, y1, x2, y2, thickness, color.encode("utf-8"))

    _dll.DrawCircle.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int, c_char_p]
    _dll.DrawCircle.restype = c_int64

    @classmethod
    def DrawCircle(cls, instance, ptr, x, y, radius, thickness, color):
        return cls._dll.DrawCircle(instance, ptr, x, y, radius, thickness, color.encode("utf-8"))

    _dll.DrawFillPoly.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.DrawFillPoly.restype = c_int64

    @classmethod
    def DrawFillPoly(cls, instance, ptr, pointJson, color):
        return cls._dll.DrawFillPoly(instance, ptr, pointJson.encode("utf-8"), color.encode("utf-8"))

    _dll.DecodeQRCode.argtypes = [c_int64, c_int64]
    _dll.DecodeQRCode.restype = c_int64

    @classmethod
    def DecodeQRCode(cls, instance, ptr):
        return cls._dll.DecodeQRCode(instance, ptr)

    _dll.CreateQRCode.argtypes = [c_int64, c_char_p, c_int]
    _dll.CreateQRCode.restype = c_int64

    @classmethod
    def CreateQRCode(cls, instance, _str, pixelsPerModule):
        return cls._dll.CreateQRCode(instance, _str.encode("utf-8"), pixelsPerModule)

    _dll.CreateQRCodeEx.argtypes = [c_int64, c_char_p, c_int, c_int, c_int, c_int, c_int]
    _dll.CreateQRCodeEx.restype = c_int64

    @classmethod
    def CreateQRCodeEx(cls, instance, _str, pixelsPerModule, version, correction_level, mode, structure_number):
        return cls._dll.CreateQRCodeEx(
            instance, _str.encode("utf-8"), pixelsPerModule, version, correction_level, mode, structure_number
        )

    _dll.MatchAnimationFromPtr.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int64,
        c_double,
        c_int,
        c_double,
        c_double,
        c_int,
        c_int,
        c_int,
    ]
    _dll.MatchAnimationFromPtr.restype = c_int64

    @classmethod
    def MatchAnimationFromPtr(
        cls, instance, x1, y1, x2, y2, templ, matchVal, _type, angle, scale, delay, time, threadCount
    ):
        return cls._dll.MatchAnimationFromPtr(
            instance, x1, y1, x2, y2, templ, matchVal, _type, angle, scale, delay, time, threadCount
        )

    _dll.MatchAnimationFromPath.argtypes = [
        c_int64,
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_double,
        c_int,
        c_double,
        c_double,
        c_int,
        c_int,
        c_int,
    ]
    _dll.MatchAnimationFromPath.restype = c_int64

    @classmethod
    def MatchAnimationFromPath(
        cls, instance, x1, y1, x2, y2, templ, matchVal, _type, angle, scale, delay, time, threadCount
    ):
        return cls._dll.MatchAnimationFromPath(
            instance, x1, y1, x2, y2, templ.encode("utf-8"), matchVal, _type, angle, scale, delay, time, threadCount
        )

    _dll.RemoveImageDiff.argtypes = [c_int64, c_int64, c_int64]
    _dll.RemoveImageDiff.restype = c_int64

    @classmethod
    def RemoveImageDiff(cls, instance, image1, image2):
        return cls._dll.RemoveImageDiff(instance, image1, image2)

    _dll.GetImageBmpData.argtypes = [c_int64, c_int64, POINTER(c_int64), POINTER(c_int)]
    _dll.GetImageBmpData.restype = c_int

    @classmethod
    def GetImageBmpData(cls, instance, imgPtr, data=None, size=None):
        data = c_int64(0)
        size = c_int(0)
        result = cls._dll.GetImageBmpData(instance, imgPtr, byref(data), byref(size))
        return result, data.value, size.value

    _dll.GetImagePngData.argtypes = [c_int64, c_int64, POINTER(c_int64), POINTER(c_int)]
    _dll.GetImagePngData.restype = c_int

    @classmethod
    def GetImagePngData(cls, instance, imgPtr, data=None, size=None):
        data = c_int64(0)
        size = c_int(0)
        result = cls._dll.GetImagePngData(instance, imgPtr, byref(data), byref(size))
        return result, data.value, size.value

    _dll.FreeImageData.argtypes = [c_int64, c_int64]
    _dll.FreeImageData.restype = c_int

    @classmethod
    def FreeImageData(cls, instance, screenPtr):
        return cls._dll.FreeImageData(instance, screenPtr)

    _dll.ScalePixels.argtypes = [c_int64, c_int64, c_int]
    _dll.ScalePixels.restype = c_int64

    @classmethod
    def ScalePixels(cls, instance, ptr, pixelsPerModule):
        return cls._dll.ScalePixels(instance, ptr, pixelsPerModule)

    _dll.CreateImage.argtypes = [c_int64, c_int, c_int, c_char_p]
    _dll.CreateImage.restype = c_int64

    @classmethod
    def CreateImage(cls, instance, width, height, color):
        return cls._dll.CreateImage(instance, width, height, color.encode("utf-8"))

    _dll.SetPixel.argtypes = [c_int64, c_int64, c_int, c_int, c_char_p]
    _dll.SetPixel.restype = c_int

    @classmethod
    def SetPixel(cls, instance, image, x, y, color):
        return cls._dll.SetPixel(instance, image, x, y, color.encode("utf-8"))

    _dll.SetPixelList.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.SetPixelList.restype = c_int

    @classmethod
    def SetPixelList(cls, instance, image, points, color):
        return cls._dll.SetPixelList(instance, image, points.encode("utf-8"), color.encode("utf-8"))

    _dll.ConcatImage.argtypes = [c_int64, c_int64, c_int64, c_int, c_char_p, c_int]
    _dll.ConcatImage.restype = c_int64

    @classmethod
    def ConcatImage(cls, instance, image1, image2, gap, color, _dir):
        return cls._dll.ConcatImage(instance, image1, image2, gap, color.encode("utf-8"), _dir)

    _dll.CoverImage.argtypes = [c_int64, c_int64, c_int64, c_int, c_int, c_double]
    _dll.CoverImage.restype = c_int64

    @classmethod
    def CoverImage(cls, instance, image1, image2, x, y, alpha):
        return cls._dll.CoverImage(instance, image1, image2, x, y, alpha)

    _dll.RotateImage.argtypes = [c_int64, c_int64, c_double]
    _dll.RotateImage.restype = c_int64

    @classmethod
    def RotateImage(cls, instance, image, angle):
        return cls._dll.RotateImage(instance, image, angle)

    _dll.ImageToBase64.argtypes = [c_int64, c_int64]
    _dll.ImageToBase64.restype = c_int64

    @classmethod
    def ImageToBase64(cls, instance, image):
        return cls._dll.ImageToBase64(instance, image)

    _dll.Base64ToImage.argtypes = [c_int64, c_char_p]
    _dll.Base64ToImage.restype = c_int64

    @classmethod
    def Base64ToImage(cls, instance, base64):
        return cls._dll.Base64ToImage(instance, base64.encode("utf-8"))

    _dll.Hex2ARGB.argtypes = [c_int64, c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    _dll.Hex2ARGB.restype = c_int

    @classmethod
    def Hex2ARGB(cls, instance, hex, a=None, r=None, g=None, b=None):
        a = c_int(0)
        r = c_int(0)
        g = c_int(0)
        b = c_int(0)
        result = cls._dll.Hex2ARGB(instance, hex.encode("utf-8"), byref(a), byref(r), byref(g), byref(b))
        return result, a.value, r.value, g.value, b.value

    _dll.Hex2RGB.argtypes = [c_int64, c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    _dll.Hex2RGB.restype = c_int

    @classmethod
    def Hex2RGB(cls, instance, hex, r=None, g=None, b=None):
        r = c_int(0)
        g = c_int(0)
        b = c_int(0)
        result = cls._dll.Hex2RGB(instance, hex.encode("utf-8"), byref(r), byref(g), byref(b))
        return result, r.value, g.value, b.value

    _dll.ARGB2Hex.argtypes = [c_int64, c_int, c_int, c_int, c_int]
    _dll.ARGB2Hex.restype = c_int64

    @classmethod
    def ARGB2Hex(cls, instance, a, r, g, b):
        return cls._dll.ARGB2Hex(instance, a, r, g, b)

    _dll.RGB2Hex.argtypes = [c_int64, c_int, c_int, c_int]
    _dll.RGB2Hex.restype = c_int64

    @classmethod
    def RGB2Hex(cls, instance, r, g, b):
        return cls._dll.RGB2Hex(instance, r, g, b)

    _dll.Hex2HSV.argtypes = [c_int64, c_char_p]
    _dll.Hex2HSV.restype = c_int64

    @classmethod
    def Hex2HSV(cls, instance, hex):
        return cls._dll.Hex2HSV(instance, hex.encode("utf-8"))

    _dll.RGB2HSV.argtypes = [c_int64, c_int, c_int, c_int]
    _dll.RGB2HSV.restype = c_int64

    @classmethod
    def RGB2HSV(cls, instance, r, g, b):
        return cls._dll.RGB2HSV(instance, r, g, b)

    _dll.CmpColor.argtypes = [c_int64, c_int, c_int, c_char_p, c_char_p]
    _dll.CmpColor.restype = c_int

    @classmethod
    def CmpColor(cls, instance, x1, y1, colorStart, colorEnd):
        return cls._dll.CmpColor(instance, x1, y1, colorStart.encode("utf-8"), colorEnd.encode("utf-8"))

    _dll.CmpColorPtr.argtypes = [c_int64, c_int64, c_int, c_int, c_char_p, c_char_p]
    _dll.CmpColorPtr.restype = c_int

    @classmethod
    def CmpColorPtr(cls, instance, ptr, x, y, colorStart, colorEnd):
        return cls._dll.CmpColorPtr(instance, ptr, x, y, colorStart.encode("utf-8"), colorEnd.encode("utf-8"))

    _dll.CmpColorEx.argtypes = [c_int64, c_int, c_int, c_char_p]
    _dll.CmpColorEx.restype = c_int

    @classmethod
    def CmpColorEx(cls, instance, x1, y1, colorJson):
        return cls._dll.CmpColorEx(instance, x1, y1, colorJson.encode("utf-8"))

    _dll.CmpColorPtrEx.argtypes = [c_int64, c_int64, c_int, c_int, c_char_p]
    _dll.CmpColorPtrEx.restype = c_int

    @classmethod
    def CmpColorPtrEx(cls, instance, ptr, x, y, colorJson):
        return cls._dll.CmpColorPtrEx(instance, ptr, x, y, colorJson.encode("utf-8"))

    _dll.CmpColorHexEx.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.CmpColorHexEx.restype = c_int

    @classmethod
    def CmpColorHexEx(cls, instance, hex, colorJson):
        return cls._dll.CmpColorHexEx(instance, hex.encode("utf-8"), colorJson.encode("utf-8"))

    _dll.CmpColorHex.argtypes = [c_int64, c_char_p, c_char_p, c_char_p]
    _dll.CmpColorHex.restype = c_int

    @classmethod
    def CmpColorHex(cls, instance, hex, colorStart, colorEnd):
        return cls._dll.CmpColorHex(instance, hex.encode("utf-8"), colorStart.encode("utf-8"), colorEnd.encode("utf-8"))

    _dll.GetConnectedComponents.argtypes = [c_int64, c_int64, c_char_p, c_int]
    _dll.GetConnectedComponents.restype = c_int64

    @classmethod
    def GetConnectedComponents(cls, instance, ptr, points, tolerance):
        return cls._dll.GetConnectedComponents(instance, ptr, points.encode("utf-8"), tolerance)

    _dll.DetectPointerDirection.argtypes = [c_int64, c_int64, c_int, c_int]
    _dll.DetectPointerDirection.restype = c_double

    @classmethod
    def DetectPointerDirection(cls, instance, ptr, x, y):
        return cls._dll.DetectPointerDirection(instance, ptr, x, y)

    _dll.DetectPointerDirectionByFeatures.argtypes = [c_int64, c_int64, c_int64, c_int, c_int, c_bool]
    _dll.DetectPointerDirectionByFeatures.restype = c_double

    @classmethod
    def DetectPointerDirectionByFeatures(cls, instance, ptr, templatePtr, x, y, useTemplate):
        return cls._dll.DetectPointerDirectionByFeatures(instance, ptr, templatePtr, x, y, useTemplate)

    _dll.FastMatch.argtypes = [c_int64, c_int64, c_int64, c_double, c_int, c_double, c_double]
    _dll.FastMatch.restype = c_int64

    @classmethod
    def FastMatch(cls, instance, ptr, templatePtr, matchVal, _type, angle, scale):
        return cls._dll.FastMatch(instance, ptr, templatePtr, matchVal, _type, angle, scale)

    _dll.FastROI.argtypes = [c_int64, c_int64]
    _dll.FastROI.restype = c_int64

    @classmethod
    def FastROI(cls, instance, ptr):
        return cls._dll.FastROI(instance, ptr)

    _dll.GetROIRegion.argtypes = [c_int64, c_int64, POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    _dll.GetROIRegion.restype = c_int

    @classmethod
    def GetROIRegion(cls, instance, ptr, x1=None, y1=None, x2=None, y2=None):
        x1 = c_int(0)
        y1 = c_int(0)
        x2 = c_int(0)
        y2 = c_int(0)
        result = cls._dll.GetROIRegion(instance, ptr, byref(x1), byref(y1), byref(x2), byref(y2))
        return result, x1.value, y1.value, x2.value, y2.value

    _dll.GetForegroundPoints.argtypes = [c_int64, c_int64]
    _dll.GetForegroundPoints.restype = c_int64

    @classmethod
    def GetForegroundPoints(cls, instance, ptr):
        return cls._dll.GetForegroundPoints(instance, ptr)

    _dll.ConvertColor.argtypes = [c_int64, c_int64, c_int]
    _dll.ConvertColor.restype = c_int64

    @classmethod
    def ConvertColor(cls, instance, ptr, _type):
        return cls._dll.ConvertColor(instance, ptr, _type)

    _dll.Threshold.argtypes = [c_int64, c_int64, c_double, c_double, c_int]
    _dll.Threshold.restype = c_int64

    @classmethod
    def Threshold(cls, instance, ptr, thresh, maxVal, _type):
        return cls._dll.Threshold(instance, ptr, thresh, maxVal, _type)

    _dll.RemoveIslands.argtypes = [c_int64, c_int64, c_int]
    _dll.RemoveIslands.restype = c_int64

    @classmethod
    def RemoveIslands(cls, instance, ptr, minArea):
        return cls._dll.RemoveIslands(instance, ptr, minArea)

    _dll.MorphGradient.argtypes = [c_int64, c_int64, c_int]
    _dll.MorphGradient.restype = c_int64

    @classmethod
    def MorphGradient(cls, instance, ptr, kernelSize):
        return cls._dll.MorphGradient(instance, ptr, kernelSize)

    _dll.MorphTophat.argtypes = [c_int64, c_int64, c_int]
    _dll.MorphTophat.restype = c_int64

    @classmethod
    def MorphTophat(cls, instance, ptr, kernelSize):
        return cls._dll.MorphTophat(instance, ptr, kernelSize)

    _dll.MorphBlackhat.argtypes = [c_int64, c_int64, c_int]
    _dll.MorphBlackhat.restype = c_int64

    @classmethod
    def MorphBlackhat(cls, instance, ptr, kernelSize):
        return cls._dll.MorphBlackhat(instance, ptr, kernelSize)

    _dll.Dilation.argtypes = [c_int64, c_int64, c_int]
    _dll.Dilation.restype = c_int64

    @classmethod
    def Dilation(cls, instance, ptr, kernelSize):
        return cls._dll.Dilation(instance, ptr, kernelSize)

    _dll.Erosion.argtypes = [c_int64, c_int64, c_int]
    _dll.Erosion.restype = c_int64

    @classmethod
    def Erosion(cls, instance, ptr, kernelSize):
        return cls._dll.Erosion(instance, ptr, kernelSize)

    _dll.GaussianBlur.argtypes = [c_int64, c_int64, c_int]
    _dll.GaussianBlur.restype = c_int64

    @classmethod
    def GaussianBlur(cls, instance, ptr, kernelSize):
        return cls._dll.GaussianBlur(instance, ptr, kernelSize)

    _dll.Sharpen.argtypes = [c_int64, c_int64]
    _dll.Sharpen.restype = c_int64

    @classmethod
    def Sharpen(cls, instance, ptr):
        return cls._dll.Sharpen(instance, ptr)

    _dll.CannyEdge.argtypes = [c_int64, c_int64, c_int]
    _dll.CannyEdge.restype = c_int64

    @classmethod
    def CannyEdge(cls, instance, ptr, kernelSize):
        return cls._dll.CannyEdge(instance, ptr, kernelSize)

    _dll.Flip.argtypes = [c_int64, c_int64, c_int]
    _dll.Flip.restype = c_int64

    @classmethod
    def Flip(cls, instance, ptr, flipCode):
        return cls._dll.Flip(instance, ptr, flipCode)

    _dll.MorphOpen.argtypes = [c_int64, c_int64, c_int]
    _dll.MorphOpen.restype = c_int64

    @classmethod
    def MorphOpen(cls, instance, ptr, kernelSize):
        return cls._dll.MorphOpen(instance, ptr, kernelSize)

    _dll.MorphClose.argtypes = [c_int64, c_int64, c_int]
    _dll.MorphClose.restype = c_int64

    @classmethod
    def MorphClose(cls, instance, ptr, kernelSize):
        return cls._dll.MorphClose(instance, ptr, kernelSize)

    _dll.Skeletonize.argtypes = [c_int64, c_int64]
    _dll.Skeletonize.restype = c_int64

    @classmethod
    def Skeletonize(cls, instance, ptr):
        return cls._dll.Skeletonize(instance, ptr)

    _dll.ImageStitchFromPath.argtypes = [c_int64, c_char_p, POINTER(c_int64)]
    _dll.ImageStitchFromPath.restype = c_int64

    @classmethod
    def ImageStitchFromPath(cls, instance, path, trajectory=None):
        trajectory = c_int64(0)
        result = cls._dll.ImageStitchFromPath(instance, path.encode("utf-8"), byref(trajectory))
        return result, trajectory.value

    _dll.ImageStitchCreate.argtypes = [c_int64]
    _dll.ImageStitchCreate.restype = c_int64

    @classmethod
    def ImageStitchCreate(cls, instance):
        return cls._dll.ImageStitchCreate(instance)

    _dll.ImageStitchAppend.argtypes = [c_int64, c_int64, c_int64]
    _dll.ImageStitchAppend.restype = c_int

    @classmethod
    def ImageStitchAppend(cls, instance, imageStitch, image):
        return cls._dll.ImageStitchAppend(instance, imageStitch, image)

    _dll.ImageStitchGetResult.argtypes = [c_int64, c_int64, POINTER(c_int64)]
    _dll.ImageStitchGetResult.restype = c_int64

    @classmethod
    def ImageStitchGetResult(cls, instance, imageStitch, trajectory=None):
        trajectory = c_int64(0)
        result = cls._dll.ImageStitchGetResult(instance, imageStitch, byref(trajectory))
        return result, trajectory.value

    _dll.ImageStitchFree.argtypes = [c_int64, c_int64]
    _dll.ImageStitchFree.restype = c_int

    @classmethod
    def ImageStitchFree(cls, instance, imageStitch):
        return cls._dll.ImageStitchFree(instance, imageStitch)

    _dll.BitPacking.argtypes = [c_int64, c_int64]
    _dll.BitPacking.restype = c_int64

    @classmethod
    def BitPacking(cls, instance, image):
        return cls._dll.BitPacking(instance, image)

    _dll.BitUnpacking.argtypes = [c_int64, c_char_p]
    _dll.BitUnpacking.restype = c_int64

    @classmethod
    def BitUnpacking(cls, instance, imageStr):
        return cls._dll.BitUnpacking(instance, imageStr.encode("utf-8"))

    _dll.SetImageCache.argtypes = [c_int]
    _dll.SetImageCache.restype = c_int

    @classmethod
    def SetImageCache(cls, enable):
        return cls._dll.SetImageCache(enable)

    _dll.FindImageFromPtr.argtypes = [c_int64, c_int64, c_int64, c_char_p, c_double, c_int]
    _dll.FindImageFromPtr.restype = c_int64

    @classmethod
    def FindImageFromPtr(cls, instance, source, templ, deltaColor, matchVal, _dir):
        return cls._dll.FindImageFromPtr(instance, source, templ, deltaColor.encode("utf-8"), matchVal, _dir)

    _dll.FindImageFromPtrAll.argtypes = [c_int64, c_int64, c_int64, c_char_p, c_double]
    _dll.FindImageFromPtrAll.restype = c_int64

    @classmethod
    def FindImageFromPtrAll(cls, instance, source, templ, deltaColor, matchVal):
        return cls._dll.FindImageFromPtrAll(instance, source, templ, deltaColor.encode("utf-8"), matchVal)

    _dll.FindImageFromPath.argtypes = [c_int64, c_char_p, c_char_p, c_char_p, c_double, c_int]
    _dll.FindImageFromPath.restype = c_int64

    @classmethod
    def FindImageFromPath(cls, instance, source, templ, deltaColor, matchVal, _dir):
        return cls._dll.FindImageFromPath(
            instance, source.encode("utf-8"), templ.encode("utf-8"), deltaColor.encode("utf-8"), matchVal, _dir
        )

    _dll.FindImageFromPathAll.argtypes = [c_int64, c_char_p, c_char_p, c_char_p, c_double]
    _dll.FindImageFromPathAll.restype = c_int64

    @classmethod
    def FindImageFromPathAll(cls, instance, source, templ, deltaColor, matchVal):
        return cls._dll.FindImageFromPathAll(
            instance, source.encode("utf-8"), templ.encode("utf-8"), deltaColor.encode("utf-8"), matchVal
        )

    _dll.FindWindowsFromPtr.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_int64, c_char_p, c_double, c_int]
    _dll.FindWindowsFromPtr.restype = c_int64

    @classmethod
    def FindWindowsFromPtr(cls, instance, x1, y1, x2, y2, templ, deltaColor, matchVal, _dir):
        return cls._dll.FindWindowsFromPtr(instance, x1, y1, x2, y2, templ, deltaColor.encode("utf-8"), matchVal, _dir)

    _dll.FindWindowsFromPtrAll.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_int64, c_char_p, c_double]
    _dll.FindWindowsFromPtrAll.restype = c_int64

    @classmethod
    def FindWindowsFromPtrAll(cls, instance, x1, y1, x2, y2, templ, deltaColor, matchVal):
        return cls._dll.FindWindowsFromPtrAll(instance, x1, y1, x2, y2, templ, deltaColor.encode("utf-8"), matchVal)

    _dll.FindWindowsFromPath.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_char_p, c_double, c_int]
    _dll.FindWindowsFromPath.restype = c_int64

    @classmethod
    def FindWindowsFromPath(cls, instance, x1, y1, x2, y2, templ, deltaColor, matchVal, _dir):
        return cls._dll.FindWindowsFromPath(
            instance, x1, y1, x2, y2, templ.encode("utf-8"), deltaColor.encode("utf-8"), matchVal, _dir
        )

    _dll.FindWindowsFromPathAll.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_char_p, c_char_p, c_double]
    _dll.FindWindowsFromPathAll.restype = c_int64

    @classmethod
    def FindWindowsFromPathAll(cls, instance, x1, y1, x2, y2, templ, deltaColor, matchVal):
        return cls._dll.FindWindowsFromPathAll(
            instance, x1, y1, x2, y2, templ.encode("utf-8"), deltaColor.encode("utf-8"), matchVal
        )

    _dll.RegistryOpenKey.argtypes = [c_int64, c_int, c_char_p]
    _dll.RegistryOpenKey.restype = c_int64

    @classmethod
    def RegistryOpenKey(cls, instance, rootKey, subKey):
        return cls._dll.RegistryOpenKey(instance, rootKey, subKey.encode("utf-8"))

    _dll.RegistryCreateKey.argtypes = [c_int64, c_int, c_char_p]
    _dll.RegistryCreateKey.restype = c_int64

    @classmethod
    def RegistryCreateKey(cls, instance, rootKey, subKey):
        return cls._dll.RegistryCreateKey(instance, rootKey, subKey.encode("utf-8"))

    _dll.RegistryCloseKey.argtypes = [c_int64, c_int64]
    _dll.RegistryCloseKey.restype = c_int

    @classmethod
    def RegistryCloseKey(cls, instance, key):
        return cls._dll.RegistryCloseKey(instance, key)

    _dll.RegistryKeyExists.argtypes = [c_int64, c_int, c_char_p]
    _dll.RegistryKeyExists.restype = c_int

    @classmethod
    def RegistryKeyExists(cls, instance, rootKey, subKey):
        return cls._dll.RegistryKeyExists(instance, rootKey, subKey.encode("utf-8"))

    _dll.RegistryDeleteKey.argtypes = [c_int64, c_int, c_char_p, c_int]
    _dll.RegistryDeleteKey.restype = c_int

    @classmethod
    def RegistryDeleteKey(cls, instance, rootKey, subKey, recursive):
        return cls._dll.RegistryDeleteKey(instance, rootKey, subKey.encode("utf-8"), recursive)

    _dll.RegistrySetString.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.RegistrySetString.restype = c_int

    @classmethod
    def RegistrySetString(cls, instance, key, valueName, value):
        return cls._dll.RegistrySetString(instance, key, valueName.encode("utf-8"), value.encode("utf-8"))

    _dll.RegistryGetString.argtypes = [c_int64, c_int64, c_char_p]
    _dll.RegistryGetString.restype = c_int64

    @classmethod
    def RegistryGetString(cls, instance, key, valueName):
        return cls._dll.RegistryGetString(instance, key, valueName.encode("utf-8"))

    _dll.RegistrySetDword.argtypes = [c_int64, c_int64, c_char_p, c_int]
    _dll.RegistrySetDword.restype = c_int

    @classmethod
    def RegistrySetDword(cls, instance, key, valueName, value):
        return cls._dll.RegistrySetDword(instance, key, valueName.encode("utf-8"), value)

    _dll.RegistryGetDword.argtypes = [c_int64, c_int64, c_char_p]
    _dll.RegistryGetDword.restype = c_int

    @classmethod
    def RegistryGetDword(cls, instance, key, valueName):
        return cls._dll.RegistryGetDword(instance, key, valueName.encode("utf-8"))

    _dll.RegistrySetQword.argtypes = [c_int64, c_int64, c_char_p, c_int64]
    _dll.RegistrySetQword.restype = c_int

    @classmethod
    def RegistrySetQword(cls, instance, key, valueName, value):
        return cls._dll.RegistrySetQword(instance, key, valueName.encode("utf-8"), value)

    _dll.RegistryGetQword.argtypes = [c_int64, c_int64, c_char_p]
    _dll.RegistryGetQword.restype = c_int64

    @classmethod
    def RegistryGetQword(cls, instance, key, valueName):
        return cls._dll.RegistryGetQword(instance, key, valueName.encode("utf-8"))

    _dll.RegistryDeleteValue.argtypes = [c_int64, c_int64, c_char_p]
    _dll.RegistryDeleteValue.restype = c_int

    @classmethod
    def RegistryDeleteValue(cls, instance, key, valueName):
        return cls._dll.RegistryDeleteValue(instance, key, valueName.encode("utf-8"))

    _dll.RegistryEnumSubKeys.argtypes = [c_int64, c_int64]
    _dll.RegistryEnumSubKeys.restype = c_int64

    @classmethod
    def RegistryEnumSubKeys(cls, instance, key):
        return cls._dll.RegistryEnumSubKeys(instance, key)

    _dll.RegistryEnumValues.argtypes = [c_int64, c_int64]
    _dll.RegistryEnumValues.restype = c_int64

    @classmethod
    def RegistryEnumValues(cls, instance, key):
        return cls._dll.RegistryEnumValues(instance, key)

    _dll.RegistrySetEnvironmentVariable.argtypes = [c_int64, c_char_p, c_char_p, c_int]
    _dll.RegistrySetEnvironmentVariable.restype = c_int

    @classmethod
    def RegistrySetEnvironmentVariable(cls, instance, name, value, systemWide):
        return cls._dll.RegistrySetEnvironmentVariable(
            instance, name.encode("utf-8"), value.encode("utf-8"), systemWide
        )

    _dll.RegistryGetEnvironmentVariable.argtypes = [c_int64, c_char_p, c_int]
    _dll.RegistryGetEnvironmentVariable.restype = c_int64

    @classmethod
    def RegistryGetEnvironmentVariable(cls, instance, name, systemWide):
        return cls._dll.RegistryGetEnvironmentVariable(instance, name.encode("utf-8"), systemWide)

    _dll.RegistryGetUserRegistryPath.argtypes = [c_int64]
    _dll.RegistryGetUserRegistryPath.restype = c_int64

    @classmethod
    def RegistryGetUserRegistryPath(cls, instance):
        return cls._dll.RegistryGetUserRegistryPath(instance)

    _dll.RegistryGetSystemRegistryPath.argtypes = [c_int64]
    _dll.RegistryGetSystemRegistryPath.restype = c_int64

    @classmethod
    def RegistryGetSystemRegistryPath(cls, instance):
        return cls._dll.RegistryGetSystemRegistryPath(instance)

    _dll.RegistryBackupToFile.argtypes = [c_int64, c_int, c_char_p, c_char_p]
    _dll.RegistryBackupToFile.restype = c_int

    @classmethod
    def RegistryBackupToFile(cls, instance, rootKey, subKey, filePath):
        return cls._dll.RegistryBackupToFile(instance, rootKey, subKey.encode("utf-8"), filePath.encode("utf-8"))

    _dll.RegistryRestoreFromFile.argtypes = [c_int64, c_char_p]
    _dll.RegistryRestoreFromFile.restype = c_int

    @classmethod
    def RegistryRestoreFromFile(cls, instance, filePath):
        return cls._dll.RegistryRestoreFromFile(instance, filePath.encode("utf-8"))

    _dll.RegistryCompareKeys.argtypes = [c_int64, c_int, c_char_p, c_int, c_char_p]
    _dll.RegistryCompareKeys.restype = c_int64

    @classmethod
    def RegistryCompareKeys(cls, instance, rootKey1, subKey1, rootKey2, subKey2):
        return cls._dll.RegistryCompareKeys(
            instance, rootKey1, subKey1.encode("utf-8"), rootKey2, subKey2.encode("utf-8")
        )

    _dll.RegistrySearchKeys.argtypes = [c_int64, c_int, c_char_p, c_char_p, c_int]
    _dll.RegistrySearchKeys.restype = c_int64

    @classmethod
    def RegistrySearchKeys(cls, instance, rootKey, searchPath, searchPattern, recursive):
        return cls._dll.RegistrySearchKeys(
            instance, rootKey, searchPath.encode("utf-8"), searchPattern.encode("utf-8"), recursive
        )

    _dll.RegistryGetInstalledSoftware.argtypes = [c_int64]
    _dll.RegistryGetInstalledSoftware.restype = c_int64

    @classmethod
    def RegistryGetInstalledSoftware(cls, instance):
        return cls._dll.RegistryGetInstalledSoftware(instance)

    _dll.RegistryGetWindowsVersion.argtypes = [c_int64]
    _dll.RegistryGetWindowsVersion.restype = c_int64

    @classmethod
    def RegistryGetWindowsVersion(cls, instance):
        return cls._dll.RegistryGetWindowsVersion(instance)

    _dll.CreateDatabase.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.CreateDatabase.restype = c_int64

    @classmethod
    def CreateDatabase(cls, instance, dbName, password):
        return cls._dll.CreateDatabase(instance, dbName.encode("utf-8"), password.encode("utf-8"))

    _dll.OpenDatabase.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.OpenDatabase.restype = c_int64

    @classmethod
    def OpenDatabase(cls, instance, dbName, password):
        return cls._dll.OpenDatabase(instance, dbName.encode("utf-8"), password.encode("utf-8"))

    _dll.OpenMemoryDatabase.argtypes = [c_int64, c_int64, c_int, c_char_p]
    _dll.OpenMemoryDatabase.restype = c_int64

    @classmethod
    def OpenMemoryDatabase(cls, instance, address, size, password):
        return cls._dll.OpenMemoryDatabase(instance, address, size, password.encode("utf-8"))

    _dll.GetDatabaseError.argtypes = [c_int64, c_int64]
    _dll.GetDatabaseError.restype = c_int64

    @classmethod
    def GetDatabaseError(cls, instance, db):
        return cls._dll.GetDatabaseError(instance, db)

    _dll.CloseDatabase.argtypes = [c_int64, c_int64]
    _dll.CloseDatabase.restype = c_int

    @classmethod
    def CloseDatabase(cls, instance, db):
        return cls._dll.CloseDatabase(instance, db)

    _dll.GetAllTableNames.argtypes = [c_int64, c_int64]
    _dll.GetAllTableNames.restype = c_int64

    @classmethod
    def GetAllTableNames(cls, instance, db):
        return cls._dll.GetAllTableNames(instance, db)

    _dll.GetTableInfo.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetTableInfo.restype = c_int64

    @classmethod
    def GetTableInfo(cls, instance, db, tableName):
        return cls._dll.GetTableInfo(instance, db, tableName.encode("utf-8"))

    _dll.GetTableInfoDetail.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetTableInfoDetail.restype = c_int64

    @classmethod
    def GetTableInfoDetail(cls, instance, db, tableName):
        return cls._dll.GetTableInfoDetail(instance, db, tableName.encode("utf-8"))

    _dll.ExecuteSql.argtypes = [c_int64, c_int64, c_char_p]
    _dll.ExecuteSql.restype = c_int

    @classmethod
    def ExecuteSql(cls, instance, db, sql):
        return cls._dll.ExecuteSql(instance, db, sql.encode("utf-8"))

    _dll.ExecuteScalar.argtypes = [c_int64, c_int64, c_char_p]
    _dll.ExecuteScalar.restype = c_int

    @classmethod
    def ExecuteScalar(cls, instance, db, sql):
        return cls._dll.ExecuteScalar(instance, db, sql.encode("utf-8"))

    _dll.ExecuteReader.argtypes = [c_int64, c_int64, c_char_p]
    _dll.ExecuteReader.restype = c_int64

    @classmethod
    def ExecuteReader(cls, instance, db, sql):
        return cls._dll.ExecuteReader(instance, db, sql.encode("utf-8"))

    _dll.Read.argtypes = [c_int64, c_int64]
    _dll.Read.restype = c_int

    @classmethod
    def Read(cls, instance, stmt):
        return cls._dll.Read(instance, stmt)

    _dll.GetDataCount.argtypes = [c_int64, c_int64]
    _dll.GetDataCount.restype = c_int

    @classmethod
    def GetDataCount(cls, instance, stmt):
        return cls._dll.GetDataCount(instance, stmt)

    _dll.GetColumnCount.argtypes = [c_int64, c_int64]
    _dll.GetColumnCount.restype = c_int

    @classmethod
    def GetColumnCount(cls, instance, stmt):
        return cls._dll.GetColumnCount(instance, stmt)

    _dll.GetColumnName.argtypes = [c_int64, c_int64, c_int]
    _dll.GetColumnName.restype = c_int64

    @classmethod
    def GetColumnName(cls, instance, stmt, iCol):
        return cls._dll.GetColumnName(instance, stmt, iCol)

    _dll.GetColumnIndex.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetColumnIndex.restype = c_int

    @classmethod
    def GetColumnIndex(cls, instance, stmt, columnName):
        return cls._dll.GetColumnIndex(instance, stmt, columnName.encode("utf-8"))

    _dll.GetColumnType.argtypes = [c_int64, c_int64, c_int]
    _dll.GetColumnType.restype = c_int

    @classmethod
    def GetColumnType(cls, instance, stmt, iCol):
        return cls._dll.GetColumnType(instance, stmt, iCol)

    _dll.Finalize.argtypes = [c_int64, c_int64]
    _dll.Finalize.restype = c_int

    @classmethod
    def Finalize(cls, instance, stmt):
        return cls._dll.Finalize(instance, stmt)

    _dll.GetDouble.argtypes = [c_int64, c_int64, c_int]
    _dll.GetDouble.restype = c_double

    @classmethod
    def GetDouble(cls, instance, stmt, iCol):
        return cls._dll.GetDouble(instance, stmt, iCol)

    _dll.GetInt32.argtypes = [c_int64, c_int64, c_int]
    _dll.GetInt32.restype = c_int

    @classmethod
    def GetInt32(cls, instance, stmt, iCol):
        return cls._dll.GetInt32(instance, stmt, iCol)

    _dll.GetInt64.argtypes = [c_int64, c_int64, c_int]
    _dll.GetInt64.restype = c_int64

    @classmethod
    def GetInt64(cls, instance, stmt, iCol):
        return cls._dll.GetInt64(instance, stmt, iCol)

    _dll.GetString.argtypes = [c_int64, c_int64, c_int]
    _dll.GetString.restype = c_int64

    @classmethod
    def GetString(cls, instance, stmt, iCol):
        return cls._dll.GetString(instance, stmt, iCol)

    _dll.GetDoubleByColumnName.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetDoubleByColumnName.restype = c_double

    @classmethod
    def GetDoubleByColumnName(cls, instance, stmt, columnName):
        return cls._dll.GetDoubleByColumnName(instance, stmt, columnName.encode("utf-8"))

    _dll.GetInt32ByColumnName.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetInt32ByColumnName.restype = c_int

    @classmethod
    def GetInt32ByColumnName(cls, instance, stmt, columnName):
        return cls._dll.GetInt32ByColumnName(instance, stmt, columnName.encode("utf-8"))

    _dll.GetInt64ByColumnName.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetInt64ByColumnName.restype = c_int64

    @classmethod
    def GetInt64ByColumnName(cls, instance, stmt, columnName):
        return cls._dll.GetInt64ByColumnName(instance, stmt, columnName.encode("utf-8"))

    _dll.GetStringByColumnName.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetStringByColumnName.restype = c_int64

    @classmethod
    def GetStringByColumnName(cls, instance, stmt, columnName):
        return cls._dll.GetStringByColumnName(instance, stmt, columnName.encode("utf-8"))

    _dll.InitOlaDatabase.argtypes = [c_int64, c_int64]
    _dll.InitOlaDatabase.restype = c_int

    @classmethod
    def InitOlaDatabase(cls, instance, db):
        return cls._dll.InitOlaDatabase(instance, db)

    _dll.InitOlaImageFromDir.argtypes = [c_int64, c_int64, c_char_p, c_int]
    _dll.InitOlaImageFromDir.restype = c_int

    @classmethod
    def InitOlaImageFromDir(cls, instance, db, _dir, cover):
        return cls._dll.InitOlaImageFromDir(instance, db, _dir.encode("utf-8"), cover)

    _dll.RemoveOlaImageFromDir.argtypes = [c_int64, c_int64, c_char_p]
    _dll.RemoveOlaImageFromDir.restype = c_int

    @classmethod
    def RemoveOlaImageFromDir(cls, instance, db, _dir):
        return cls._dll.RemoveOlaImageFromDir(instance, db, _dir.encode("utf-8"))

    _dll.ExportOlaImageDir.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.ExportOlaImageDir.restype = c_int

    @classmethod
    def ExportOlaImageDir(cls, instance, db, _dir, exportDir):
        return cls._dll.ExportOlaImageDir(instance, db, _dir.encode("utf-8"), exportDir.encode("utf-8"))

    _dll.ImportOlaImage.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_int]
    _dll.ImportOlaImage.restype = c_int

    @classmethod
    def ImportOlaImage(cls, instance, db, _dir, fileName, cover):
        return cls._dll.ImportOlaImage(instance, db, _dir.encode("utf-8"), fileName.encode("utf-8"), cover)

    _dll.GetOlaImage.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.GetOlaImage.restype = c_int64

    @classmethod
    def GetOlaImage(cls, instance, db, _dir, fileName):
        return cls._dll.GetOlaImage(instance, db, _dir.encode("utf-8"), fileName.encode("utf-8"))

    _dll.RemoveOlaImage.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.RemoveOlaImage.restype = c_int

    @classmethod
    def RemoveOlaImage(cls, instance, db, _dir, fileName):
        return cls._dll.RemoveOlaImage(instance, db, _dir.encode("utf-8"), fileName.encode("utf-8"))

    _dll.SetDbConfig.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.SetDbConfig.restype = c_int

    @classmethod
    def SetDbConfig(cls, instance, db, key, value):
        return cls._dll.SetDbConfig(instance, db, key.encode("utf-8"), value.encode("utf-8"))

    _dll.GetDbConfig.argtypes = [c_int64, c_int64, c_char_p]
    _dll.GetDbConfig.restype = c_int64

    @classmethod
    def GetDbConfig(cls, instance, db, key):
        return cls._dll.GetDbConfig(instance, db, key.encode("utf-8"))

    _dll.RemoveDbConfig.argtypes = [c_int64, c_int64, c_char_p]
    _dll.RemoveDbConfig.restype = c_int

    @classmethod
    def RemoveDbConfig(cls, instance, db, key):
        return cls._dll.RemoveDbConfig(instance, db, key.encode("utf-8"))

    _dll.SetDbConfigEx.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.SetDbConfigEx.restype = c_int

    @classmethod
    def SetDbConfigEx(cls, instance, key, value):
        return cls._dll.SetDbConfigEx(instance, key.encode("utf-8"), value.encode("utf-8"))

    _dll.GetDbConfigEx.argtypes = [c_int64, c_char_p]
    _dll.GetDbConfigEx.restype = c_int64

    @classmethod
    def GetDbConfigEx(cls, instance, key):
        return cls._dll.GetDbConfigEx(instance, key.encode("utf-8"))

    _dll.RemoveDbConfigEx.argtypes = [c_int64, c_char_p]
    _dll.RemoveDbConfigEx.restype = c_int

    @classmethod
    def RemoveDbConfigEx(cls, instance, key):
        return cls._dll.RemoveDbConfigEx(instance, key.encode("utf-8"))

    _dll.InitDictFromDir.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_int]
    _dll.InitDictFromDir.restype = c_int

    @classmethod
    def InitDictFromDir(cls, instance, db, dict_name, dict_path, cover):
        return cls._dll.InitDictFromDir(instance, db, dict_name.encode("utf-8"), dict_path.encode("utf-8"), cover)

    _dll.InitDictFromTxt.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_int]
    _dll.InitDictFromTxt.restype = c_int

    @classmethod
    def InitDictFromTxt(cls, instance, db, dict_name, dict_path, cover):
        return cls._dll.InitDictFromTxt(instance, db, dict_name.encode("utf-8"), dict_path.encode("utf-8"), cover)

    _dll.ImportDictWord.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_int]
    _dll.ImportDictWord.restype = c_int

    @classmethod
    def ImportDictWord(cls, instance, db, dict_name, pic_file_name, cover):
        return cls._dll.ImportDictWord(instance, db, dict_name.encode("utf-8"), pic_file_name.encode("utf-8"), cover)

    _dll.ExportDict.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.ExportDict.restype = c_int

    @classmethod
    def ExportDict(cls, instance, db, dict_name, export_dir):
        return cls._dll.ExportDict(instance, db, dict_name.encode("utf-8"), export_dir.encode("utf-8"))

    _dll.RemoveDict.argtypes = [c_int64, c_int64, c_char_p]
    _dll.RemoveDict.restype = c_int

    @classmethod
    def RemoveDict(cls, instance, db, dict_name):
        return cls._dll.RemoveDict(instance, db, dict_name.encode("utf-8"))

    _dll.RemoveDictWord.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.RemoveDictWord.restype = c_int

    @classmethod
    def RemoveDictWord(cls, instance, db, dict_name, word):
        return cls._dll.RemoveDictWord(instance, db, dict_name.encode("utf-8"), word.encode("utf-8"))

    _dll.GetDictImage.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_int, c_int]
    _dll.GetDictImage.restype = c_int64

    @classmethod
    def GetDictImage(cls, instance, db, dict_name, word, gap, _dir):
        return cls._dll.GetDictImage(instance, db, dict_name.encode("utf-8"), word.encode("utf-8"), gap, _dir)

    _dll.OpenVideo.argtypes = [c_int64, c_char_p]
    _dll.OpenVideo.restype = c_int64

    @classmethod
    def OpenVideo(cls, instance, videoPath):
        return cls._dll.OpenVideo(instance, videoPath.encode("utf-8"))

    _dll.OpenCamera.argtypes = [c_int64, c_int]
    _dll.OpenCamera.restype = c_int64

    @classmethod
    def OpenCamera(cls, instance, deviceIndex):
        return cls._dll.OpenCamera(instance, deviceIndex)

    _dll.CloseVideo.argtypes = [c_int64, c_int64]
    _dll.CloseVideo.restype = c_int

    @classmethod
    def CloseVideo(cls, instance, videoHandle):
        return cls._dll.CloseVideo(instance, videoHandle)

    _dll.IsVideoOpened.argtypes = [c_int64, c_int64]
    _dll.IsVideoOpened.restype = c_int

    @classmethod
    def IsVideoOpened(cls, instance, videoHandle):
        return cls._dll.IsVideoOpened(instance, videoHandle)

    _dll.GetVideoInfo.argtypes = [c_int64, c_int64]
    _dll.GetVideoInfo.restype = c_int64

    @classmethod
    def GetVideoInfo(cls, instance, videoHandle):
        return cls._dll.GetVideoInfo(instance, videoHandle)

    _dll.GetVideoWidth.argtypes = [c_int64, c_int64]
    _dll.GetVideoWidth.restype = c_int

    @classmethod
    def GetVideoWidth(cls, instance, videoHandle):
        return cls._dll.GetVideoWidth(instance, videoHandle)

    _dll.GetVideoHeight.argtypes = [c_int64, c_int64]
    _dll.GetVideoHeight.restype = c_int

    @classmethod
    def GetVideoHeight(cls, instance, videoHandle):
        return cls._dll.GetVideoHeight(instance, videoHandle)

    _dll.GetVideoFPS.argtypes = [c_int64, c_int64]
    _dll.GetVideoFPS.restype = c_double

    @classmethod
    def GetVideoFPS(cls, instance, videoHandle):
        return cls._dll.GetVideoFPS(instance, videoHandle)

    _dll.GetVideoTotalFrames.argtypes = [c_int64, c_int64]
    _dll.GetVideoTotalFrames.restype = c_int

    @classmethod
    def GetVideoTotalFrames(cls, instance, videoHandle):
        return cls._dll.GetVideoTotalFrames(instance, videoHandle)

    _dll.GetVideoDuration.argtypes = [c_int64, c_int64]
    _dll.GetVideoDuration.restype = c_double

    @classmethod
    def GetVideoDuration(cls, instance, videoHandle):
        return cls._dll.GetVideoDuration(instance, videoHandle)

    _dll.GetCurrentFrameIndex.argtypes = [c_int64, c_int64]
    _dll.GetCurrentFrameIndex.restype = c_int

    @classmethod
    def GetCurrentFrameIndex(cls, instance, videoHandle):
        return cls._dll.GetCurrentFrameIndex(instance, videoHandle)

    _dll.GetCurrentTimestamp.argtypes = [c_int64, c_int64]
    _dll.GetCurrentTimestamp.restype = c_double

    @classmethod
    def GetCurrentTimestamp(cls, instance, videoHandle):
        return cls._dll.GetCurrentTimestamp(instance, videoHandle)

    _dll.ReadNextFrame.argtypes = [c_int64, c_int64]
    _dll.ReadNextFrame.restype = c_int64

    @classmethod
    def ReadNextFrame(cls, instance, videoHandle):
        return cls._dll.ReadNextFrame(instance, videoHandle)

    _dll.ReadFrameAtIndex.argtypes = [c_int64, c_int64, c_int]
    _dll.ReadFrameAtIndex.restype = c_int64

    @classmethod
    def ReadFrameAtIndex(cls, instance, videoHandle, frameIndex):
        return cls._dll.ReadFrameAtIndex(instance, videoHandle, frameIndex)

    _dll.ReadFrameAtTime.argtypes = [c_int64, c_int64, c_double]
    _dll.ReadFrameAtTime.restype = c_int64

    @classmethod
    def ReadFrameAtTime(cls, instance, videoHandle, timestamp):
        return cls._dll.ReadFrameAtTime(instance, videoHandle, timestamp)

    _dll.ReadCurrentFrame.argtypes = [c_int64, c_int64]
    _dll.ReadCurrentFrame.restype = c_int64

    @classmethod
    def ReadCurrentFrame(cls, instance, videoHandle):
        return cls._dll.ReadCurrentFrame(instance, videoHandle)

    _dll.SeekToFrame.argtypes = [c_int64, c_int64, c_int]
    _dll.SeekToFrame.restype = c_int

    @classmethod
    def SeekToFrame(cls, instance, videoHandle, frameIndex):
        return cls._dll.SeekToFrame(instance, videoHandle, frameIndex)

    _dll.SeekToTime.argtypes = [c_int64, c_int64, c_double]
    _dll.SeekToTime.restype = c_int

    @classmethod
    def SeekToTime(cls, instance, videoHandle, timestamp):
        return cls._dll.SeekToTime(instance, videoHandle, timestamp)

    _dll.SeekToBeginning.argtypes = [c_int64, c_int64]
    _dll.SeekToBeginning.restype = c_int

    @classmethod
    def SeekToBeginning(cls, instance, videoHandle):
        return cls._dll.SeekToBeginning(instance, videoHandle)

    _dll.SeekToEnd.argtypes = [c_int64, c_int64]
    _dll.SeekToEnd.restype = c_int

    @classmethod
    def SeekToEnd(cls, instance, videoHandle):
        return cls._dll.SeekToEnd(instance, videoHandle)

    _dll.ExtractFramesToFiles.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_char_p, c_char_p, c_int]
    _dll.ExtractFramesToFiles.restype = c_int

    @classmethod
    def ExtractFramesToFiles(
        cls, instance, videoHandle, startFrame, endFrame, step, outputDir, imageFormat, jpegQuality
    ):
        return cls._dll.ExtractFramesToFiles(
            instance,
            videoHandle,
            startFrame,
            endFrame,
            step,
            outputDir.encode("utf-8"),
            imageFormat.encode("utf-8"),
            jpegQuality,
        )

    _dll.ExtractFramesByInterval.argtypes = [c_int64, c_int64, c_double, c_char_p, c_char_p]
    _dll.ExtractFramesByInterval.restype = c_int

    @classmethod
    def ExtractFramesByInterval(cls, instance, videoHandle, intervalSeconds, outputDir, imageFormat):
        return cls._dll.ExtractFramesByInterval(
            instance, videoHandle, intervalSeconds, outputDir.encode("utf-8"), imageFormat.encode("utf-8")
        )

    _dll.ExtractKeyFrames.argtypes = [c_int64, c_int64, c_double, c_int, c_char_p, c_char_p]
    _dll.ExtractKeyFrames.restype = c_int

    @classmethod
    def ExtractKeyFrames(cls, instance, videoHandle, threshold, maxFrames, outputDir, imageFormat):
        return cls._dll.ExtractKeyFrames(
            instance, videoHandle, threshold, maxFrames, outputDir.encode("utf-8"), imageFormat.encode("utf-8")
        )

    _dll.SaveCurrentFrame.argtypes = [c_int64, c_int64, c_char_p, c_int]
    _dll.SaveCurrentFrame.restype = c_int

    @classmethod
    def SaveCurrentFrame(cls, instance, videoHandle, outputPath, quality):
        return cls._dll.SaveCurrentFrame(instance, videoHandle, outputPath.encode("utf-8"), quality)

    _dll.SaveFrameAtIndex.argtypes = [c_int64, c_int64, c_int, c_char_p, c_int]
    _dll.SaveFrameAtIndex.restype = c_int

    @classmethod
    def SaveFrameAtIndex(cls, instance, videoHandle, frameIndex, outputPath, quality):
        return cls._dll.SaveFrameAtIndex(instance, videoHandle, frameIndex, outputPath.encode("utf-8"), quality)

    _dll.FrameToBase64.argtypes = [c_int64, c_int64, c_char_p]
    _dll.FrameToBase64.restype = c_int64

    @classmethod
    def FrameToBase64(cls, instance, videoHandle, format):
        return cls._dll.FrameToBase64(instance, videoHandle, format.encode("utf-8"))

    _dll.CalculateFrameSimilarity.argtypes = [c_int64, c_int64, c_int64]
    _dll.CalculateFrameSimilarity.restype = c_double

    @classmethod
    def CalculateFrameSimilarity(cls, instance, frame1, frame2):
        return cls._dll.CalculateFrameSimilarity(instance, frame1, frame2)

    _dll.GetVideoInfoFromPath.argtypes = [c_int64, c_char_p]
    _dll.GetVideoInfoFromPath.restype = c_int64

    @classmethod
    def GetVideoInfoFromPath(cls, instance, videoPath):
        return cls._dll.GetVideoInfoFromPath(instance, videoPath.encode("utf-8"))

    _dll.IsValidVideoFile.argtypes = [c_int64, c_char_p]
    _dll.IsValidVideoFile.restype = c_int

    @classmethod
    def IsValidVideoFile(cls, instance, videoPath):
        return cls._dll.IsValidVideoFile(instance, videoPath.encode("utf-8"))

    _dll.ExtractSingleFrame.argtypes = [c_int64, c_char_p, c_int]
    _dll.ExtractSingleFrame.restype = c_int64

    @classmethod
    def ExtractSingleFrame(cls, instance, videoPath, frameIndex):
        return cls._dll.ExtractSingleFrame(instance, videoPath.encode("utf-8"), frameIndex)

    _dll.ExtractThumbnail.argtypes = [c_int64, c_char_p]
    _dll.ExtractThumbnail.restype = c_int64

    @classmethod
    def ExtractThumbnail(cls, instance, videoPath):
        return cls._dll.ExtractThumbnail(instance, videoPath.encode("utf-8"))

    _dll.ConvertVideo.argtypes = [c_int64, c_char_p, c_char_p, c_char_p, c_double]
    _dll.ConvertVideo.restype = c_int

    @classmethod
    def ConvertVideo(cls, instance, inputPath, outputPath, codec, fps):
        return cls._dll.ConvertVideo(
            instance, inputPath.encode("utf-8"), outputPath.encode("utf-8"), codec.encode("utf-8"), fps
        )

    _dll.ResizeVideo.argtypes = [c_int64, c_char_p, c_char_p, c_int, c_int]
    _dll.ResizeVideo.restype = c_int

    @classmethod
    def ResizeVideo(cls, instance, inputPath, outputPath, width, height):
        return cls._dll.ResizeVideo(instance, inputPath.encode("utf-8"), outputPath.encode("utf-8"), width, height)

    _dll.TrimVideo.argtypes = [c_int64, c_char_p, c_char_p, c_double, c_double]
    _dll.TrimVideo.restype = c_int

    @classmethod
    def TrimVideo(cls, instance, inputPath, outputPath, startTime, endTime):
        return cls._dll.TrimVideo(instance, inputPath.encode("utf-8"), outputPath.encode("utf-8"), startTime, endTime)

    _dll.CreateVideoFromImages.argtypes = [c_int64, c_char_p, c_char_p, c_double, c_char_p]
    _dll.CreateVideoFromImages.restype = c_int

    @classmethod
    def CreateVideoFromImages(cls, instance, imageDir, outputPath, fps, codec):
        return cls._dll.CreateVideoFromImages(
            instance, imageDir.encode("utf-8"), outputPath.encode("utf-8"), fps, codec.encode("utf-8")
        )

    _dll.DetectSceneChanges.argtypes = [c_int64, c_char_p, c_double]
    _dll.DetectSceneChanges.restype = c_int64

    @classmethod
    def DetectSceneChanges(cls, instance, videoPath, threshold):
        return cls._dll.DetectSceneChanges(instance, videoPath.encode("utf-8"), threshold)

    _dll.CalculateAverageBrightness.argtypes = [c_int64, c_char_p]
    _dll.CalculateAverageBrightness.restype = c_double

    @classmethod
    def CalculateAverageBrightness(cls, instance, videoPath):
        return cls._dll.CalculateAverageBrightness(instance, videoPath.encode("utf-8"))

    _dll.DetectMotion.argtypes = [c_int64, c_char_p, c_double]
    _dll.DetectMotion.restype = c_int64

    @classmethod
    def DetectMotion(cls, instance, videoPath, threshold):
        return cls._dll.DetectMotion(instance, videoPath.encode("utf-8"), threshold)

    _dll.SetWindowState.argtypes = [c_int64, c_int64, c_int]
    _dll.SetWindowState.restype = c_int

    @classmethod
    def SetWindowState(cls, instance, hwnd, state):
        return cls._dll.SetWindowState(instance, hwnd, state)

    _dll.FindWindow.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.FindWindow.restype = c_int64

    @classmethod
    def FindWindow(cls, instance, class_name, title):
        return cls._dll.FindWindow(instance, class_name.encode("utf-8"), title.encode("utf-8"))

    _dll.GetClipboard.argtypes = [c_int64]
    _dll.GetClipboard.restype = c_int64

    @classmethod
    def GetClipboard(cls, instance):
        return cls._dll.GetClipboard(instance)

    _dll.SetClipboard.argtypes = [c_int64, c_char_p]
    _dll.SetClipboard.restype = c_int

    @classmethod
    def SetClipboard(cls, instance, text):
        return cls._dll.SetClipboard(instance, text.encode("utf-8"))

    _dll.SendPaste.argtypes = [c_int64, c_int64]
    _dll.SendPaste.restype = c_int

    @classmethod
    def SendPaste(cls, instance, hwnd):
        return cls._dll.SendPaste(instance, hwnd)

    _dll.GetWindow.argtypes = [c_int64, c_int64, c_int]
    _dll.GetWindow.restype = c_int64

    @classmethod
    def GetWindow(cls, instance, hwnd, flag):
        return cls._dll.GetWindow(instance, hwnd, flag)

    _dll.GetWindowTitle.argtypes = [c_int64, c_int64]
    _dll.GetWindowTitle.restype = c_int64

    @classmethod
    def GetWindowTitle(cls, instance, hwnd):
        return cls._dll.GetWindowTitle(instance, hwnd)

    _dll.GetWindowClass.argtypes = [c_int64, c_int64]
    _dll.GetWindowClass.restype = c_int64

    @classmethod
    def GetWindowClass(cls, instance, hwnd):
        return cls._dll.GetWindowClass(instance, hwnd)

    _dll.GetWindowRect.argtypes = [c_int64, c_int64, POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    _dll.GetWindowRect.restype = c_int

    @classmethod
    def GetWindowRect(cls, instance, hwnd, x1=None, y1=None, x2=None, y2=None):
        x1 = c_int(0)
        y1 = c_int(0)
        x2 = c_int(0)
        y2 = c_int(0)
        result = cls._dll.GetWindowRect(instance, hwnd, byref(x1), byref(y1), byref(x2), byref(y2))
        return result, x1.value, y1.value, x2.value, y2.value

    _dll.GetWindowProcessPath.argtypes = [c_int64, c_int64]
    _dll.GetWindowProcessPath.restype = c_int64

    @classmethod
    def GetWindowProcessPath(cls, instance, hwnd):
        return cls._dll.GetWindowProcessPath(instance, hwnd)

    _dll.GetWindowState.argtypes = [c_int64, c_int64, c_int]
    _dll.GetWindowState.restype = c_int

    @classmethod
    def GetWindowState(cls, instance, hwnd, flag):
        return cls._dll.GetWindowState(instance, hwnd, flag)

    _dll.GetForegroundWindow.argtypes = [c_int64]
    _dll.GetForegroundWindow.restype = c_int64

    @classmethod
    def GetForegroundWindow(cls, instance):
        return cls._dll.GetForegroundWindow(instance)

    _dll.GetWindowProcessId.argtypes = [c_int64, c_int64]
    _dll.GetWindowProcessId.restype = c_int

    @classmethod
    def GetWindowProcessId(cls, instance, hwnd):
        return cls._dll.GetWindowProcessId(instance, hwnd)

    _dll.GetClientSize.argtypes = [c_int64, c_int64, POINTER(c_int), POINTER(c_int)]
    _dll.GetClientSize.restype = c_int

    @classmethod
    def GetClientSize(cls, instance, hwnd, width=None, height=None):
        width = c_int(0)
        height = c_int(0)
        result = cls._dll.GetClientSize(instance, hwnd, byref(width), byref(height))
        return result, width.value, height.value

    _dll.GetMousePointWindow.argtypes = [c_int64]
    _dll.GetMousePointWindow.restype = c_int64

    @classmethod
    def GetMousePointWindow(cls, instance):
        return cls._dll.GetMousePointWindow(instance)

    _dll.GetSpecialWindow.argtypes = [c_int64, c_int]
    _dll.GetSpecialWindow.restype = c_int64

    @classmethod
    def GetSpecialWindow(cls, instance, flag):
        return cls._dll.GetSpecialWindow(instance, flag)

    _dll.GetClientRect.argtypes = [c_int64, c_int64, POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    _dll.GetClientRect.restype = c_int

    @classmethod
    def GetClientRect(cls, instance, hwnd, x1=None, y1=None, x2=None, y2=None):
        x1 = c_int(0)
        y1 = c_int(0)
        x2 = c_int(0)
        y2 = c_int(0)
        result = cls._dll.GetClientRect(instance, hwnd, byref(x1), byref(y1), byref(x2), byref(y2))
        return result, x1.value, y1.value, x2.value, y2.value

    _dll.SetWindowText.argtypes = [c_int64, c_int64, c_char_p]
    _dll.SetWindowText.restype = c_int

    @classmethod
    def SetWindowText(cls, instance, hwnd, title):
        return cls._dll.SetWindowText(instance, hwnd, title.encode("utf-8"))

    _dll.SetWindowSize.argtypes = [c_int64, c_int64, c_int, c_int]
    _dll.SetWindowSize.restype = c_int

    @classmethod
    def SetWindowSize(cls, instance, hwnd, width, height):
        return cls._dll.SetWindowSize(instance, hwnd, width, height)

    _dll.SetClientSize.argtypes = [c_int64, c_int64, c_int, c_int]
    _dll.SetClientSize.restype = c_int

    @classmethod
    def SetClientSize(cls, instance, hwnd, width, height):
        return cls._dll.SetClientSize(instance, hwnd, width, height)

    _dll.SetWindowTransparent.argtypes = [c_int64, c_int64, c_int]
    _dll.SetWindowTransparent.restype = c_int

    @classmethod
    def SetWindowTransparent(cls, instance, hwnd, alpha):
        return cls._dll.SetWindowTransparent(instance, hwnd, alpha)

    _dll.FindWindowEx.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.FindWindowEx.restype = c_int64

    @classmethod
    def FindWindowEx(cls, instance, parent, class_name, title):
        return cls._dll.FindWindowEx(instance, parent, class_name.encode("utf-8"), title.encode("utf-8"))

    _dll.FindWindowByProcess.argtypes = [c_int64, c_char_p, c_char_p, c_char_p]
    _dll.FindWindowByProcess.restype = c_int64

    @classmethod
    def FindWindowByProcess(cls, instance, process_name, class_name, title):
        return cls._dll.FindWindowByProcess(
            instance, process_name.encode("utf-8"), class_name.encode("utf-8"), title.encode("utf-8")
        )

    _dll.MoveWindow.argtypes = [c_int64, c_int64, c_int, c_int]
    _dll.MoveWindow.restype = c_int

    @classmethod
    def MoveWindow(cls, instance, hwnd, x, y):
        return cls._dll.MoveWindow(instance, hwnd, x, y)

    _dll.GetScaleFromWindows.argtypes = [c_int64, c_int64]
    _dll.GetScaleFromWindows.restype = c_double

    @classmethod
    def GetScaleFromWindows(cls, instance, hwnd):
        return cls._dll.GetScaleFromWindows(instance, hwnd)

    _dll.GetWindowDpiAwarenessScale.argtypes = [c_int64, c_int64]
    _dll.GetWindowDpiAwarenessScale.restype = c_double

    @classmethod
    def GetWindowDpiAwarenessScale(cls, instance, hwnd):
        return cls._dll.GetWindowDpiAwarenessScale(instance, hwnd)

    _dll.EnumProcess.argtypes = [c_int64, c_char_p]
    _dll.EnumProcess.restype = c_int64

    @classmethod
    def EnumProcess(cls, instance, name):
        return cls._dll.EnumProcess(instance, name.encode("utf-8"))

    _dll.EnumWindow.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_int]
    _dll.EnumWindow.restype = c_int64

    @classmethod
    def EnumWindow(cls, instance, parent, title, className, _filter):
        return cls._dll.EnumWindow(instance, parent, title.encode("utf-8"), className.encode("utf-8"), _filter)

    _dll.EnumWindowByProcess.argtypes = [c_int64, c_char_p, c_char_p, c_char_p, c_int]
    _dll.EnumWindowByProcess.restype = c_int64

    @classmethod
    def EnumWindowByProcess(cls, instance, process_name, title, class_name, _filter):
        return cls._dll.EnumWindowByProcess(
            instance, process_name.encode("utf-8"), title.encode("utf-8"), class_name.encode("utf-8"), _filter
        )

    _dll.EnumWindowByProcessId.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_int]
    _dll.EnumWindowByProcessId.restype = c_int64

    @classmethod
    def EnumWindowByProcessId(cls, instance, pid, title, class_name, _filter):
        return cls._dll.EnumWindowByProcessId(instance, pid, title.encode("utf-8"), class_name.encode("utf-8"), _filter)

    _dll.EnumWindowSuper.argtypes = [c_int64, c_char_p, c_int, c_int, c_char_p, c_int, c_int, c_int]
    _dll.EnumWindowSuper.restype = c_int64

    @classmethod
    def EnumWindowSuper(cls, instance, spec1, flag1, type1, spec2, flag2, type2, sort):
        return cls._dll.EnumWindowSuper(
            instance, spec1.encode("utf-8"), flag1, type1, spec2.encode("utf-8"), flag2, type2, sort
        )

    _dll.GetPointWindow.argtypes = [c_int64, c_int, c_int]
    _dll.GetPointWindow.restype = c_int64

    @classmethod
    def GetPointWindow(cls, instance, x, y):
        return cls._dll.GetPointWindow(instance, x, y)

    _dll.GetProcessInfo.argtypes = [c_int64, c_int64]
    _dll.GetProcessInfo.restype = c_int64

    @classmethod
    def GetProcessInfo(cls, instance, pid):
        return cls._dll.GetProcessInfo(instance, pid)

    _dll.ShowTaskBarIcon.argtypes = [c_int64, c_int64, c_int]
    _dll.ShowTaskBarIcon.restype = c_int

    @classmethod
    def ShowTaskBarIcon(cls, instance, hwnd, show):
        return cls._dll.ShowTaskBarIcon(instance, hwnd, show)

    _dll.FindWindowByProcessId.argtypes = [c_int64, c_int64, c_char_p, c_char_p]
    _dll.FindWindowByProcessId.restype = c_int64

    @classmethod
    def FindWindowByProcessId(cls, instance, process_id, className, title):
        return cls._dll.FindWindowByProcessId(instance, process_id, className.encode("utf-8"), title.encode("utf-8"))

    _dll.GetWindowThreadId.argtypes = [c_int64, c_int64]
    _dll.GetWindowThreadId.restype = c_int64

    @classmethod
    def GetWindowThreadId(cls, instance, hwnd):
        return cls._dll.GetWindowThreadId(instance, hwnd)

    _dll.FindWindowSuper.argtypes = [c_int64, c_char_p, c_int, c_int, c_char_p, c_int, c_int]
    _dll.FindWindowSuper.restype = c_int64

    @classmethod
    def FindWindowSuper(cls, instance, spec1, flag1, type1, spec2, flag2, type2):
        return cls._dll.FindWindowSuper(
            instance, spec1.encode("utf-8"), flag1, type1, spec2.encode("utf-8"), flag2, type2
        )

    _dll.ClientToScreen.argtypes = [c_int64, c_int64, POINTER(c_int), POINTER(c_int)]
    _dll.ClientToScreen.restype = c_int

    @classmethod
    def ClientToScreen(cls, instance, hwnd, x, y):
        x = c_int(x)
        y = c_int(y)
        result = cls._dll.ClientToScreen(instance, hwnd, byref(x), byref(y))
        return result, x.value, y.value

    _dll.ScreenToClient.argtypes = [c_int64, c_int64, POINTER(c_int), POINTER(c_int)]
    _dll.ScreenToClient.restype = c_int

    @classmethod
    def ScreenToClient(cls, instance, hwnd, x, y):
        x = c_int(x)
        y = c_int(y)
        result = cls._dll.ScreenToClient(instance, hwnd, byref(x), byref(y))
        return result, x.value, y.value

    _dll.GetForegroundFocus.argtypes = [c_int64]
    _dll.GetForegroundFocus.restype = c_int64

    @classmethod
    def GetForegroundFocus(cls, instance):
        return cls._dll.GetForegroundFocus(instance)

    _dll.SetWindowDisplay.argtypes = [c_int64, c_int64, c_int]
    _dll.SetWindowDisplay.restype = c_int

    @classmethod
    def SetWindowDisplay(cls, instance, hwnd, affinity):
        return cls._dll.SetWindowDisplay(instance, hwnd, affinity)

    _dll.IsDisplayDead.argtypes = [c_int64, c_int, c_int, c_int, c_int, c_int]
    _dll.IsDisplayDead.restype = c_int

    @classmethod
    def IsDisplayDead(cls, instance, x1, y1, x2, y2, time):
        return cls._dll.IsDisplayDead(instance, x1, y1, x2, y2, time)

    _dll.GetWindowsFps.argtypes = [c_int64, c_int, c_int, c_int, c_int]
    _dll.GetWindowsFps.restype = c_int

    @classmethod
    def GetWindowsFps(cls, instance, x1, y1, x2, y2):
        return cls._dll.GetWindowsFps(instance, x1, y1, x2, y2)

    _dll.TerminateProcess.argtypes = [c_int64, c_int64]
    _dll.TerminateProcess.restype = c_int

    @classmethod
    def TerminateProcess(cls, instance, pid):
        return cls._dll.TerminateProcess(instance, pid)

    _dll.TerminateProcessTree.argtypes = [c_int64, c_int64]
    _dll.TerminateProcessTree.restype = c_int

    @classmethod
    def TerminateProcessTree(cls, instance, pid):
        return cls._dll.TerminateProcessTree(instance, pid)

    _dll.GetCommandLine.argtypes = [c_int64, c_int64]
    _dll.GetCommandLine.restype = c_int64

    @classmethod
    def GetCommandLine(cls, instance, hwnd):
        return cls._dll.GetCommandLine(instance, hwnd)

    _dll.CheckFontSmooth.argtypes = [c_int64]
    _dll.CheckFontSmooth.restype = c_int

    @classmethod
    def CheckFontSmooth(cls, instance):
        return cls._dll.CheckFontSmooth(instance)

    _dll.SetFontSmooth.argtypes = [c_int64, c_int]
    _dll.SetFontSmooth.restype = c_int

    @classmethod
    def SetFontSmooth(cls, instance, enable):
        return cls._dll.SetFontSmooth(instance, enable)

    _dll.EnableDebugPrivilege.argtypes = [c_int64]
    _dll.EnableDebugPrivilege.restype = c_int

    @classmethod
    def EnableDebugPrivilege(cls, instance):
        return cls._dll.EnableDebugPrivilege(instance)

    _dll.SystemStart.argtypes = [c_int64, c_char_p, c_char_p]
    _dll.SystemStart.restype = c_int

    @classmethod
    def SystemStart(cls, instance, applicationName, commandLine):
        return cls._dll.SystemStart(instance, applicationName.encode("utf-8"), commandLine.encode("utf-8"))

    _dll.CreateChildProcess.argtypes = [c_int64, c_char_p, c_char_p, c_char_p, c_int, c_int]
    _dll.CreateChildProcess.restype = c_int

    @classmethod
    def CreateChildProcess(cls, instance, applicationName, commandLine, currentDirectory, showType, parentProcessId):
        return cls._dll.CreateChildProcess(
            instance,
            applicationName.encode("utf-8"),
            commandLine.encode("utf-8"),
            currentDirectory.encode("utf-8"),
            showType,
            parentProcessId,
        )

    _dll.YoloLoadModel.argtypes = [c_int64, c_char_p, c_char_p, c_char_p, c_char_p, c_int, c_int, c_int]
    _dll.YoloLoadModel.restype = c_int64

    @classmethod
    def YoloLoadModel(
        cls, instance, modelPath, outputPath, names_label, password, modelType, inferenceType, inferenceDevice
    ):
        return cls._dll.YoloLoadModel(
            instance,
            modelPath.encode("utf-8"),
            outputPath.encode("utf-8"),
            names_label.encode("utf-8"),
            password.encode("utf-8"),
            modelType,
            inferenceType,
            inferenceDevice,
        )

    _dll.YoloReleaseModel.argtypes = [c_int64, c_int64]
    _dll.YoloReleaseModel.restype = c_int

    @classmethod
    def YoloReleaseModel(cls, instance, modelHandle):
        return cls._dll.YoloReleaseModel(instance, modelHandle)

    _dll.YoloLoadModelMemory.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int]
    _dll.YoloLoadModelMemory.restype = c_int64

    @classmethod
    def YoloLoadModelMemory(cls, instance, memoryAddr, size, modelType, inferenceType, inferenceDevice):
        return cls._dll.YoloLoadModelMemory(instance, memoryAddr, size, modelType, inferenceType, inferenceDevice)

    _dll.YoloInfer.argtypes = [c_int64, c_int64, c_int64]
    _dll.YoloInfer.restype = c_int64

    @classmethod
    def YoloInfer(cls, instance, handle, imagePtr):
        return cls._dll.YoloInfer(instance, handle, imagePtr)

    _dll.YoloIsModelValid.argtypes = [c_int64, c_int64]
    _dll.YoloIsModelValid.restype = c_int

    @classmethod
    def YoloIsModelValid(cls, instance, modelHandle):
        return cls._dll.YoloIsModelValid(instance, modelHandle)

    _dll.YoloListModels.argtypes = [c_int64]
    _dll.YoloListModels.restype = c_int64

    @classmethod
    def YoloListModels(cls, instance):
        return cls._dll.YoloListModels(instance)

    _dll.YoloGetModelInfo.argtypes = [c_int64, c_int64]
    _dll.YoloGetModelInfo.restype = c_int64

    @classmethod
    def YoloGetModelInfo(cls, instance, modelHandle):
        return cls._dll.YoloGetModelInfo(instance, modelHandle)

    _dll.YoloSetModelConfig.argtypes = [c_int64, c_int64, c_char_p]
    _dll.YoloSetModelConfig.restype = c_int

    @classmethod
    def YoloSetModelConfig(cls, instance, modelHandle, configJson):
        return cls._dll.YoloSetModelConfig(instance, modelHandle, configJson.encode("utf-8"))

    _dll.YoloGetModelConfig.argtypes = [c_int64, c_int64]
    _dll.YoloGetModelConfig.restype = c_int64

    @classmethod
    def YoloGetModelConfig(cls, instance, modelHandle):
        return cls._dll.YoloGetModelConfig(instance, modelHandle)

    _dll.YoloWarmup.argtypes = [c_int64, c_int64, c_int]
    _dll.YoloWarmup.restype = c_int

    @classmethod
    def YoloWarmup(cls, instance, modelHandle, iterations):
        return cls._dll.YoloWarmup(instance, modelHandle, iterations)

    _dll.YoloDetect.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int, c_char_p, c_double, c_double, c_int]
    _dll.YoloDetect.restype = c_int64

    @classmethod
    def YoloDetect(cls, instance, modelHandle, x1, y1, x2, y2, classes, confidence, iou, maxDetections):
        return cls._dll.YoloDetect(
            instance, modelHandle, x1, y1, x2, y2, classes.encode("utf-8"), confidence, iou, maxDetections
        )

    _dll.YoloDetectSimple.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int]
    _dll.YoloDetectSimple.restype = c_int64

    @classmethod
    def YoloDetectSimple(cls, instance, modelHandle, x1, y1, x2, y2):
        return cls._dll.YoloDetectSimple(instance, modelHandle, x1, y1, x2, y2)

    _dll.YoloDetectFromPtr.argtypes = [c_int64, c_int64, c_int64, c_char_p, c_double, c_double, c_int]
    _dll.YoloDetectFromPtr.restype = c_int64

    @classmethod
    def YoloDetectFromPtr(cls, instance, modelHandle, imagePtr, classes, confidence, iou, maxDetections):
        return cls._dll.YoloDetectFromPtr(
            instance, modelHandle, imagePtr, classes.encode("utf-8"), confidence, iou, maxDetections
        )

    _dll.YoloDetectFromFile.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_double, c_double, c_int]
    _dll.YoloDetectFromFile.restype = c_int64

    @classmethod
    def YoloDetectFromFile(cls, instance, modelHandle, imagePath, classes, confidence, iou, maxDetections):
        return cls._dll.YoloDetectFromFile(
            instance, modelHandle, imagePath.encode("utf-8"), classes.encode("utf-8"), confidence, iou, maxDetections
        )

    _dll.YoloDetectFromBase64.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_double, c_double, c_int]
    _dll.YoloDetectFromBase64.restype = c_int64

    @classmethod
    def YoloDetectFromBase64(cls, instance, modelHandle, base64Data, classes, confidence, iou, maxDetections):
        return cls._dll.YoloDetectFromBase64(
            instance, modelHandle, base64Data.encode("utf-8"), classes.encode("utf-8"), confidence, iou, maxDetections
        )

    _dll.YoloDetectBatch.argtypes = [c_int64, c_int64, c_char_p, c_char_p, c_double, c_double, c_int]
    _dll.YoloDetectBatch.restype = c_int64

    @classmethod
    def YoloDetectBatch(cls, instance, modelHandle, imagesJson, classes, confidence, iou, maxDetections):
        return cls._dll.YoloDetectBatch(
            instance, modelHandle, imagesJson.encode("utf-8"), classes.encode("utf-8"), confidence, iou, maxDetections
        )

    _dll.YoloClassify.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int, c_int]
    _dll.YoloClassify.restype = c_int64

    @classmethod
    def YoloClassify(cls, instance, modelHandle, x1, y1, x2, y2, topK):
        return cls._dll.YoloClassify(instance, modelHandle, x1, y1, x2, y2, topK)

    _dll.YoloClassifyFromPtr.argtypes = [c_int64, c_int64, c_int64, c_int]
    _dll.YoloClassifyFromPtr.restype = c_int64

    @classmethod
    def YoloClassifyFromPtr(cls, instance, modelHandle, imagePtr, topK):
        return cls._dll.YoloClassifyFromPtr(instance, modelHandle, imagePtr, topK)

    _dll.YoloClassifyFromFile.argtypes = [c_int64, c_int64, c_char_p, c_int]
    _dll.YoloClassifyFromFile.restype = c_int64

    @classmethod
    def YoloClassifyFromFile(cls, instance, modelHandle, imagePath, topK):
        return cls._dll.YoloClassifyFromFile(instance, modelHandle, imagePath.encode("utf-8"), topK)

    _dll.YoloSegment.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int, c_double, c_double]
    _dll.YoloSegment.restype = c_int64

    @classmethod
    def YoloSegment(cls, instance, modelHandle, x1, y1, x2, y2, confidence, iou):
        return cls._dll.YoloSegment(instance, modelHandle, x1, y1, x2, y2, confidence, iou)

    _dll.YoloSegmentFromPtr.argtypes = [c_int64, c_int64, c_int64, c_double, c_double]
    _dll.YoloSegmentFromPtr.restype = c_int64

    @classmethod
    def YoloSegmentFromPtr(cls, instance, modelHandle, imagePtr, confidence, iou):
        return cls._dll.YoloSegmentFromPtr(instance, modelHandle, imagePtr, confidence, iou)

    _dll.YoloPose.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int, c_double, c_double]
    _dll.YoloPose.restype = c_int64

    @classmethod
    def YoloPose(cls, instance, modelHandle, x1, y1, x2, y2, confidence, iou):
        return cls._dll.YoloPose(instance, modelHandle, x1, y1, x2, y2, confidence, iou)

    _dll.YoloPoseFromPtr.argtypes = [c_int64, c_int64, c_int64, c_double, c_double]
    _dll.YoloPoseFromPtr.restype = c_int64

    @classmethod
    def YoloPoseFromPtr(cls, instance, modelHandle, imagePtr, confidence, iou):
        return cls._dll.YoloPoseFromPtr(instance, modelHandle, imagePtr, confidence, iou)

    _dll.YoloObb.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int, c_double, c_double]
    _dll.YoloObb.restype = c_int64

    @classmethod
    def YoloObb(cls, instance, modelHandle, x1, y1, x2, y2, confidence, iou):
        return cls._dll.YoloObb(instance, modelHandle, x1, y1, x2, y2, confidence, iou)

    _dll.YoloObbFromPtr.argtypes = [c_int64, c_int64, c_int64, c_double, c_double]
    _dll.YoloObbFromPtr.restype = c_int64

    @classmethod
    def YoloObbFromPtr(cls, instance, modelHandle, imagePtr, confidence, iou):
        return cls._dll.YoloObbFromPtr(instance, modelHandle, imagePtr, confidence, iou)

    _dll.YoloKeyPoint.argtypes = [c_int64, c_int64, c_int, c_int, c_int, c_int, c_double, c_double]
    _dll.YoloKeyPoint.restype = c_int64

    @classmethod
    def YoloKeyPoint(cls, instance, modelHandle, x1, y1, x2, y2, confidence, iou):
        return cls._dll.YoloKeyPoint(instance, modelHandle, x1, y1, x2, y2, confidence, iou)

    _dll.YoloKeyPointFromPtr.argtypes = [c_int64, c_int64, c_int64, c_double, c_double]
    _dll.YoloKeyPointFromPtr.restype = c_int64

    @classmethod
    def YoloKeyPointFromPtr(cls, instance, modelHandle, imagePtr, confidence, iou):
        return cls._dll.YoloKeyPointFromPtr(instance, modelHandle, imagePtr, confidence, iou)

    _dll.YoloGetInferenceStats.argtypes = [c_int64, c_int64]
    _dll.YoloGetInferenceStats.restype = c_int64

    @classmethod
    def YoloGetInferenceStats(cls, instance, modelHandle):
        return cls._dll.YoloGetInferenceStats(instance, modelHandle)

    _dll.YoloResetStats.argtypes = [c_int64, c_int64]
    _dll.YoloResetStats.restype = c_int

    @classmethod
    def YoloResetStats(cls, instance, modelHandle):
        return cls._dll.YoloResetStats(instance, modelHandle)

    _dll.YoloGetLastError.argtypes = [c_int64]
    _dll.YoloGetLastError.restype = c_int64

    @classmethod
    def YoloGetLastError(cls, instance):
        return cls._dll.YoloGetLastError(instance)

    _dll.YoloClearError.argtypes = [c_int64]
    _dll.YoloClearError.restype = c_int

    @classmethod
    def YoloClearError(cls, instance):
        return cls._dll.YoloClearError(instance)
