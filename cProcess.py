import os, re;
from .cModule import cModule;
from .cProcess_fdsSymbol_by_uAddressForPartialSymbol import cProcess_fdsSymbol_by_uAddressForPartialSymbol;
from .cProcess_fEnsurePageHeapIsEnabled import cProcess_fEnsurePageHeapIsEnabled;
from .cProcess_foGetHeapManagerDataForAddress import cProcess_foGetHeapManagerDataForAddress;
from .cProcess_ftxSplitSymbolOrAddress import cProcess_ftxSplitSymbolOrAddress;
from .cProcess_fuGetAddressForSymbol import cProcess_fuGetAddressForSymbol;
from mWindowsAPI import cProcess as cWindowsAPIProcess, oSystemInfo;

class cProcess(object):
  def __init__(oProcess, oCdbWrapper, uId):
    oProcess.oCdbWrapper = oCdbWrapper;
    oProcess.uId = uId;
    oProcess.bNew = True; # Will be set to False by `fCdbStdInOutThread` once running.
    oProcess.bTerminated = False; # Will be set to True by `foSetCurrentProcessAfterApplicationRan` once terminated
    
    # Modules will be cached here. They are discarded whenever the application is resumed.
    oProcess.__doModules_by_sCdbId = {};
    
    # We'll try to determine if page heap is enabled for every process. However, this may not always work. So until
    # we've successfully found out, the following value will be None. Once we know, it is set to True or False.
    oProcess.bPageHeapEnabled = None;
    
    # Process Information is only determined when needed and cached.
    oProcess.__oWindowsAPIProcess = None; 
    
    # oProcess.__uIntegrityLevel is only determined when needed and cached
    oProcess.__uIntegrityLevel = None;
    
    # oProcess.oMainModule is only determined when needed and cached
    oProcess.__oMainModule = None; # .oMainModule is JIT
    
    # oProcess.aoModules is only determined when needed; it creates an entry in __doModules_by_sCdbId for every loaded
    # module and returns all the values in the first dict. Since this dict is cached, this only needs to be done once
    # until the cache is invalidated.
    oProcess.__bAllModulesEnumerated = False;
  
  @property
  def oWindowsAPIProcess(oProcess):
    if oProcess.__oWindowsAPIProcess is None:
      oProcess.__oWindowsAPIProcess = cWindowsAPIProcess(oProcess.uId);
    return oProcess.__oWindowsAPIProcess;
  
  def foGetThreadForId(oProcess, uThreadId):
    return oProcess.oWindowsAPIProcess.foGetThreadForId(uThreadId);
  
  @property
  def sSimplifiedBinaryName(oProcess):
    # Windows filesystems are case-insensitive and the casing of the binary name may change between versions.
    # Lowercasing the name prevents this from resulting in location ids that differ in casing while still returning
    # a name that can be used to access the file.
    return oProcess.sBinaryName.lower();
  
  @property
  def oMainModule(oProcess):
    if oProcess.__oMainModule is None:
      uMainModuleStartAddress = oProcess.oWindowsAPIProcess.uBinaryStartAddress;
      oProcess.__oMainModule = oProcess.foGetOrCreateModuleForStartAddress(uMainModuleStartAddress);
    return oProcess.__oMainModule;
  
  def foGetOrCreateModuleForStartAddress(oProcess, uStartAddress):
    for oModule in oProcess.__doModules_by_sCdbId.values():
      if oModule.uStartAddress == uStartAddress:
        return oModule;
    return cModule.foCreateForStartAddress(oProcess, uStartAddress);
  
  def foGetOrCreateModuleForCdbId(oProcess, sCdbId):
    if sCdbId not in oProcess.__doModules_by_sCdbId:
      return cModule.foCreateForCdbId(oProcess, sCdbId);
    return oProcess.__doModules_by_sCdbId[sCdbId];
  
  def foGetOrCreateModule(oProcess, uStartAddress, uEndAddress, sCdbId, sSymbolStatus):
    if sCdbId not in oProcess.__doModules_by_sCdbId:
      oProcess.__doModules_by_sCdbId[sCdbId] = cModule(oProcess, uStartAddress, uEndAddress, sCdbId, sSymbolStatus);
    return oProcess.__doModules_by_sCdbId[sCdbId];
  
  @property
  def aoModules(oProcess):
    if not oProcess.__bAllModulesEnumerated:
      oProcess.__bAllModulesEnumerated = True;
      return cModule.faoGetOrCreateAll(oProcess);
    return oProcess.__doModules_by_sCdbId.values();
  
  def fClearCache(oProcess):
    # Assume that all modules can be unloaded, except the main module.
    oProcess.__doModules_by_sCdbId = {};
    oProcess.__oMainModule = None;
    oProcess.__bAllModulesEnumerated = False;
  
  def fSelectInCdb(oProcess):
    oProcess.oCdbWrapper.fSelectProcess(oProcess.uId);
  
  def __str__(oProcess):
    return 'Process(%s %s #%d)' % (oProcess.sBinaryName, oProcess.sISA, oProcess.uProcessId);
  
  def ftxSplitSymbolOrAddress(oProcess, sSymbolOrAddress):
    return cProcess_ftxSplitSymbolOrAddress(oProcess, sSymbolOrAddress);
  
  def fEnsurePageHeapIsEnabled(oProcess):
    return cProcess_fEnsurePageHeapIsEnabled(oProcess);
    
  def fasGetStack(oProcess, sCdbCommand):
    return cProcess_fasGetStack(oProcess, sCdbCommand);
  
  def fuAddBreakpointForAddress(oProcess, uAddress, fCallback, uThreadId = None, sCommand = None):
    return oProcess.oCdbWrapper.fuAddBreakpointForAddress(
      uAddress = uAddress,
      fCallback = fCallback,
      uProcessId = oProcess.uId,
      uThreadId = uThreadId,
      sCommand = sCommand,
    );
  
  def fasExecuteCdbCommand(oProcess, sCommand, sComment, **dxArguments):
    # Make sure all commands send to cdb are send in the context of this process.
    oProcess.fSelectInCdb();
    return oProcess.oCdbWrapper.fasExecuteCdbCommand(sCommand, sComment, **dxArguments);
  
  def fuGetAddressForSymbol(oProcess, sSymbol):
    return cProcess_fuGetAddressForSymbol(oProcess, sSymbol);
  def fuGetValueForRegister(oProcess, sRegister, sComment):
    oProcess.fSelectInCdb();
    return oProcess.oCdbWrapper.fuGetValueForRegister(sRegister, sComment);
  def fdsSymbol_by_uAddressForPartialSymbol(oProcess, sSymbol, sComment):
    return cProcess_fdsSymbol_by_uAddressForPartialSymbol(oProcess, sSymbol, sComment);
  def foGetHeapManagerDataForAddress(oProcess, uAddress, sType = None):
    return cProcess_foGetHeapManagerDataForAddress(oProcess, uAddress, sType);

  # Proxy properties and methods to oWindowsAPIProcess
  @property
  def sISA(oProcess):
    return oProcess.oWindowsAPIProcess.sISA;
  @property
  def uPointerSize(oProcess):
    return oProcess.oWindowsAPIProcess.uPointerSize;
  @property
  def sBinaryPath(oProcess):
    return oProcess.oWindowsAPIProcess.sBinaryPath;
  @property
  def sBinaryName(oProcess):
    return oProcess.oWindowsAPIProcess.sBinaryName;
  @property
  def sCommandLine(oProcess):
    return oProcess.oWindowsAPIProcess.sCommandLine;
  @property
  def uIntegrityLevel(oProcess):
    return oProcess.oWindowsAPIProcess.uIntegrityLevel;
  def foGetVirtualAllocationForAddress(oSelf, uAddress):
    return oSelf.oWindowsAPIProcess.foGetVirtualAllocationForAddress(uAddress);  
  def fsReadStringForAddressAndSize(oSelf, uAddress, uSize, bUnicode = False):
    return oSelf.oWindowsAPIProcess.fsReadStringForAddressAndSize(uAddress, uSize, bUnicode);  
  def fsReadNullTerminatedStringForAddress(oSelf, uAddress, bUnicode = False):
    return oSelf.oWindowsAPIProcess.fsReadNullTerminatedStringForAddress(uAddress, bUnicode);  
  def fauReadBytesForAddressAndSize(oSelf, uAddress, uSize):
    return oSelf.oWindowsAPIProcess.fauReadBytesForAddressAndSize(uAddress, uSize);  
  def fuReadValueForAddressAndSize(oSelf, uAddress, uSize):
    return oSelf.oWindowsAPIProcess.fuReadValueForAddressAndSize(uAddress, uSize);  
  def fauReadValuesForAddressSizeAndCount(oSelf, uAddress, uSize, uCount):
    return oSelf.oWindowsAPIProcess.fauReadValuesForAddressSizeAndCount(uAddress, uSize, uCount);  
  def fuReadPointerForAddress(oSelf, uAddress):
    return oSelf.oWindowsAPIProcess.fuReadPointerForAddress(uAddress);  
  def fauReadPointersForAddressAndCount(oSelf, uAddress, uCount):
    return oSelf.oWindowsAPIProcess.fauReadPointersForAddressAndCount(uAddress, uCount);  
  def foReadStructureForAddress(oSelf, cStructure, uAddress):
    return oSelf.oWindowsAPIProcess.foReadStructureForAddress(cStructure, uAddress);  
  def fWriteBytesForAddress(oSelf, sData, uAddress):
    return oSelf.oWindowsAPIProcess.fWriteBytesForAddress(oSelf, sData, uAddress, bUnicode);
  def fWriteStringForAddress(oSelf, sData, uAddress, bUnicode = False):
    return oSelf.oWindowsAPIProcess.fWriteStringForAddress(oSelf, sData, uAddress, bUnicode);
