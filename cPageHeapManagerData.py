import hashlib, re;
from .cHeapManagerData import cHeapManagerData;
from .dxConfig import dxConfig;
from .fsGetNumberDescription import fsGetNumberDescription;
from mWindowsAPI import cVirtualAllocation;
from mWindowsAPI.mTypes import *;
from mWindowsAPI.mDefines import *;

gbDebugOutput = False;

# SINGLE_LIST_ENTRY
SINGLE_LIST_ENTRY_32 = fcStructure("SINGLE_LIST_ENTRY",
  (PVOID_32,        "Next"),                          # PSINGLE_LIST_ENTRY
  uAlignmentBytes = 4,
);
SINGLE_LIST_ENTRY_64 = fcStructure("SINGLE_LIST_ENTRY",
  (PVOID_64,        "Next"),                          # PSINGLE_LIST_ENTRY
  uAlignmentBytes = 8,
);
# LIST_ENTRY
LIST_ENTRY_32 = fcStructure("LIST_ENTRY",
  (PVOID_32,        "pBLink"),                        # PLIST_ENTRY_32
  (PVOID_32,        "pFLink"),                        # PLIST_ENTRY_32
  uAlignmentBytes = 4,
);
LIST_ENTRY_64 = fcStructure("LIST_ENTRY",
  (PVOID_64,        "pBLink"),                        # PLIST_ENTRY_64
  (PVOID_64,        "pFLink"),                        # PLIST_ENTRY_64
  uAlignmentBytes = 8,
);
# RTL_BALANCED_LINKS
RTL_BALANCED_LINKS_32 = fcStructure("RTL_BALANCED_LINKS",
  (PVOID_32,        "Parent"),                        # PRTL_BALANCED_LINKS
  (PVOID_32,        "LeftChild"),                     # PRTL_BALANCED_LINKS
  (PVOID_32,        "RightChild"),                    # PRTL_BALANCED_LINKS
  (CHAR,            "Balance"),
  (UCHAR * 3,       "Reserved"),
  uAlignmentBytes = 4,
);
RTL_BALANCED_LINKS_64 = fcStructure("RTL_BALANCED_LINKS",
  (PVOID_64,        "Parent"),                        # PRTL_BALANCED_LINKS
  (PVOID_64,        "LeftChild"),                     # PRTL_BALANCED_LINKS
  (PVOID_64,        "RightChild"),                    # PRTL_BALANCED_LINKS
  (CHAR,            "Balance"),
  (UCHAR * 3,       "Reserved"),
  uAlignmentBytes = 8,
);
# DPH_DELAY_FREE_FLAGS
DPH_DELAY_FREE_FLAGS_32 = fcStructure("DPH_DELAY_FREE_FLAGS",
  (UINT32,          "All"),
  uAlignmentBytes = 4,
);
DPH_DELAY_FREE_FLAGS_64 = fcStructure("DPH_DELAY_FREE_FLAGS",
  (UINT32,          "All"),
  uAlignmentBytes = 8,
);
DPH_DELAY_FREE_FLAGS_PageHeapBlock    = 1 << 0;
DPH_DELAY_FREE_FLAGS_NormalHeapBlock  = 1 << 1;
DPH_DELAY_FREE_FLAGS_Lookaside        = 1 << 2;
# DPH_DELAY_FREE_QUEUE_ENTRY
DPH_DELAY_FREE_QUEUE_ENTRY_32 = fcStructure("DPH_DELAY_FREE_QUEUE_ENTRY",
  (DPH_DELAY_FREE_FLAGS_32, "Flags"),
  (PVOID_32,        "NextEntry"),                     # DPH_DELAY_FREE_QUEUE_ENTRY
  uAlignmentBytes = 4,
);
DPH_DELAY_FREE_QUEUE_ENTRY_64 = fcStructure("DPH_DELAY_FREE_QUEUE_ENTRY",
  (DPH_DELAY_FREE_FLAGS_64, "Flags"),
  (PVOID_64,        "NextEntry"),                     # DPH_DELAY_FREE_QUEUE_ENTRY
  uAlignmentBytes = 8,
);
# DPH_HEAP_BLOCK_FLAGS
DPH_HEAP_BLOCK_FLAGS_32 = fcStructure("DPH_HEAP_BLOCK_FLAGS",
  (UINT32,          "All"),
  uAlignmentBytes = 4,
);
DPH_HEAP_BLOCK_FLAGS_64 = fcStructure("DPH_HEAP_BLOCK_FLAGS",
  (UINT32,          "All"),
  uAlignmentBytes = 8,
);
DPH_HEAP_BLOCK_FLAGS_UnusedNode       = 1 << 1;
DPH_HEAP_BLOCK_FLAGS_Delay            = 1 << 2;
DPH_HEAP_BLOCK_FLAGS_Lookaside        = 1 << 3;
DPH_HEAP_BLOCK_FLAGS_Free             = 1 << 4;
DPH_HEAP_BLOCK_FLAGS_Busy             = 1 << 5;
# DPH_HEAP_BLOCK
DPH_HEAP_BLOCK_32 = fcStructure("DPH_HEAP_BLOCK",
  UNION (
    (PVOID_32,    "pNextAlloc"),                      # PDPH_HEAP_BLOCK
    (LIST_ENTRY_32, "AvailableEntry"),
    (RTL_BALANCED_LINKS_32, "TableLinks"),
  ),
  (PVOID_32,        "pUserAllocation"),
  (PVOID_32,        "pVirtualBlock"),
  (SIZE_T_32,       "nVirtualBlockSize"),
  (UINT32,          "uState"),                        # I've only seen 4 (free) and 20 (allocated)
  (UINT32,          "nUserRequestedSize"),
  (LIST_ENTRY_32,   "AdjacencyEntry"),
  (UINT32,          "uUnknown1"),                     # 
  (PVOID_32,        "StackTrace"),                    # PRTL_TRACE_BLOCK
  uAlignmentBytes = 4,
);
DPH_HEAP_BLOCK_64 = fcStructure("DPH_HEAP_BLOCK",
  UNION (
    (PVOID_64,    "pNextAlloc"),                      # PDPH_HEAP_BLOCK
    (LIST_ENTRY_64, "AvailableEntry"),
    (RTL_BALANCED_LINKS_64, "TableLinks"),
  ),
  (PVOID_64,        "pUserAllocation"),
  (PVOID_64,        "pVirtualBlock"),
  (SIZE_T_64,       "nVirtualBlockSize"),
  (UINT32,          "uState"),                        # I've only seen 4 (free) and 20 (allocated)
  (UINT64,          "nUserRequestedSize"),
  (LIST_ENTRY_64,   "AdjacencyEntry"),
  (UINT64,          "uUnknown1"),                     # 
  (PVOID_64,        "StackTrace"),                    # PRTL_TRACE_BLOCK
  uAlignmentBytes = 8,
);
DPH_STATE_ALLOCATED = 0x20;
DPH_STATE_FREED = 0x4;

# Page heap stores a DPH_ALLOCATION_HEADER structure at the start of the virtual allocation for a heap block.
DPH_ALLOCATION_HEADER_32 = fcStructure("DPH_ALLOCATION_HEADER",
  (ULONG,           "uMarker"),                       # 0xEEEEEEED or 0xEEEEEEEE
  (PVOID_32,        "poAllocationInformation"),       # PDPH_HEAP_BLOCK
  uAlignmentBytes = 4,
);
auValidPageHeapAllocationHeaderMarkers = [0xEEEEEEED, 0xEEEEEEEE];

DPH_ALLOCATION_HEADER_64 = fcStructure("DPH_ALLOCATION_HEADER",
  (ULONG,           "uMarker"),                       # 0xEEEEEEED or 0xEEEEEEEE
  (ULONG,           "uPadding"),                      # 0xEEEEEEEE or (apparently) 0x00000000
  (PVOID_64,        "poAllocationInformation"),       # PDPH_HEAP_BLOCK
  uAlignmentBytes = 8,
);
auValidPageHeapAllocationHeaderPaddings = [0x0, 0xEEEEEEEE];

# Page heap stores a DPH_BLOCK_INFORMATION structure immediately before every heap block.
# Some information on DPH_BLOCK_INFORMATION can be found here:
# https://msdn.microsoft.com/en-us/library/ms220938(v=vs.90).aspx
# http://www.nirsoft.net/kernel_struct/vista/DPH_BLOCK_INFORMATION.html
DPH_BLOCK_INFORMATION_32 = fcStructure("DPH_BLOCK_INFORMATION",
  (ULONG,           "StartStamp"),
  (PVOID_32,        "Heap"),
  (SIZE_T_32,       "RequestedSize"),
  (SIZE_T_32,       "ActualSize"),
  UNION(
    (LIST_ENTRY_32, "FreeQueue"),
    (SINGLE_LIST_ENTRY_32, "FreePushList"),
    (WORD,          "TraceIndex"),
  ),
  (PVOID_32,        "StackTrace"),
  (ULONG,           "EndStamp"),
  uAlignmentBytes = 4,
);
DPH_BLOCK_INFORMATION_64 = fcStructure("DPH_BLOCK_INFORMATION",
  (ULONG,           "StartStamp"),
  (ULONG,           "PaddingStart"),
  (PVOID_64,        "Heap"),
  (SIZE_T_64,       "RequestedSize"),
  (SIZE_T_64,       "ActualSize"),
  UNION(
    (LIST_ENTRY_64, "FreeQueue"),
    (SINGLE_LIST_ENTRY_64, "FreePushList"),
    (WORD,          "TraceIndex"),
  ),
  (PVOID_64,        "StackTrace"),
  (ULONG,           "PaddingEnd"),
  (ULONG,           "EndStamp"),
  uAlignmentBytes = 8,
);
uPaddingStartAllocated = 0xABCDBBBB;
uPaddingStartFreed = 0xABCDBBBA;
uAllocatedEndStamp = 0xDCBABBBB;
uFreedEndStamp = 0xDCBABBBA;
uUninitializedHeapBlockFillByte = 0xC0;
uFreedHeapBlockFillByte = 0xF0;
uHeapBlockEndPaddingFillByte = 0xD0;

def foGetAllocationInformationForProcessAndAddress(oProcess, uAllocationInformationStartAddress):
  # DPH_HEAP_BLOCK structures are stored sequentially in a virtual allocation.
  oAllocationInformationVirtualAllocation = cVirtualAllocation(oProcess.uId, uAllocationInformationStartAddress);
  assert oAllocationInformationVirtualAllocation, \
      "Cannot find virtual allocation for page heap allocation information at 0x%X" % uAllocationInformationStartAddress;
  if gbDebugOutput:
    print (",- oAllocationInformationVirtualAllocation ").ljust(80, "-");
    for sLine in oAllocationInformationVirtualAllocation.fasDump():
      print "| %s" % sLine;
    print "`".ljust(80, "-");
  if not oAllocationInformationVirtualAllocation.bAllocated:
    return None;
  # Read the page heap allocation information
  DPH_HEAP_BLOCK = {4: DPH_HEAP_BLOCK_32, 8: DPH_HEAP_BLOCK_64}[oProcess.uPointerSize]; 
  oAllocationInformation = oAllocationInformationVirtualAllocation.foReadStructureForOffset(
    cStructure = DPH_HEAP_BLOCK,
    uOffset = uAllocationInformationStartAddress - oAllocationInformationVirtualAllocation.uStartAddress,
  );
  if gbDebugOutput:
    print (",- oAllocationInformation ").ljust(80, "-");
    for sLine in oAllocationInformation.fasDump():
      print "| %s" % sLine;
    print "`".ljust(80, "-");
  return oAllocationInformation;

def foGetVirtualAllocationForProcessAndAddress(oProcess, uAddressInVirtualAllocation):
  oVirtualAllocation = cVirtualAllocation(oProcess.uId, uAddressInVirtualAllocation);
  assert oVirtualAllocation, \
      "Cannot find virtual allocation for page heap block allocation at 0x%X" % uAddressInVirtualAllocation;
  if gbDebugOutput:
    print (",- oVirtualAllocation ").ljust(80, "-");
    for sLine in oVirtualAllocation.fasDump():
      print "| %s" % sLine;
    print "`".ljust(80, "-");
  return oVirtualAllocation;

def foGetAllocationHeaderForVirtualAllocationAndPointerSize(oVirtualAllocation, uPointerSize):
    if not oVirtualAllocation.bAllocated:
      return None;
    # A page heap allocation for a heap block starts with a DPH_ALLOCATION_HEADER structure:
    DPH_ALLOCATION_HEADER = {4: DPH_ALLOCATION_HEADER_32, 8: DPH_ALLOCATION_HEADER_64}[uPointerSize];
    oAllocationHeader = oVirtualAllocation.foReadStructureForOffset(
      cStructure = DPH_ALLOCATION_HEADER,
      uOffset = 0,
    );
    assert oAllocationHeader.uMarker in auValidPageHeapAllocationHeaderMarkers, \
        "Page heap allocation header marker has unhandled value 0x%X (expected %s):\r\n%s" % \
        (oAllocationHeader.uMarker, " or ".join(["0x%X" % uValidMarker for uValidMarker in auValidPageHeapAllocationHeaderMarkers]),
        "\r\n".join(oAllocationHeader.fasDump()));
# Maybe this should be enabled in a "strict" setting, as I would like to know what other values are common. But I've
# missed bugs because this assertion terminated cBugId while reporting one, which is not good.
#    if hasattr(oAllocationHeader, "uPadding"):
#      assert oAllocationHeader.uPadding in auValidPageHeapAllocationHeaderPaddings, \
#          "Page heap allocation header padding has unhandled value 0x%X (expected %s):\r\n%s" % \
#          (oAllocationHeader.uPadding, " or ".join(["0x%X" % uValidMarker for uValidMarker in auValidPageHeapAllocationHeaderPaddings]),
#          "\r\n".join(oAllocationHeader.fasDump()));
    if gbDebugOutput:
      print (",- oAllocationHeader ").ljust(80, "-");
      for sLine in oAllocationHeader.fasDump():
        print "| %s" % sLine;
      print "`".ljust(80, "-");
    return oAllocationHeader;

def foGetPageHeapManagerDataHelper(uPointerSize, uAllocationInformationStartAddress, oAllocationInformation, oVirtualAllocation, oAllocationHeader):
  # The page heap header structure at the start of the virtual allocation should point to a page heap allocation
  # information structure that points back to the same virtual allocation:
  DPH_BLOCK_INFORMATION = {4: DPH_BLOCK_INFORMATION_32, 8: DPH_BLOCK_INFORMATION_64}[uPointerSize];
  uUserAllocationAddress = POINTER_VALUE(oAllocationInformation.pUserAllocation);
  uHeapBlockHeaderStartAddress = uUserAllocationAddress - SIZEOF(DPH_BLOCK_INFORMATION);
  uHeapBlockEndAddress = uUserAllocationAddress + oAllocationInformation.nUserRequestedSize;
  if oVirtualAllocation.bAllocated:
    # A DPH_BLOCK_INFORMATION structure is stored immediately before the heap block in the same allocation.
    oHeapBlockHeader = oVirtualAllocation.foReadStructureForOffset(
      cStructure = DPH_BLOCK_INFORMATION,
      uOffset = uHeapBlockHeaderStartAddress - oVirtualAllocation.uStartAddress,
    );
    uHeapBlockEndPaddingSize = oVirtualAllocation.uEndAddress - uHeapBlockEndAddress;
  else:
    oHeapBlockHeader = None;
    uHeapBlockEndPaddingSize = None;
  return cPageHeapManagerData(
    uPointerSize,
    uAllocationInformationStartAddress,
    oAllocationInformation,
    oVirtualAllocation,
    oAllocationHeader,
    uHeapBlockHeaderStartAddress,
    oHeapBlockHeader,
    uHeapBlockEndPaddingSize,
  );

class cPageHeapManagerData(cHeapManagerData):
  sType = "page heap";
  @staticmethod 
  def foGetForProcessAndAllocationInformationStartAddress(oProcess, uAllocationInformationStartAddress):
    oAllocationInformation = foGetAllocationInformationForProcessAndAddress(
      oProcess,
      uAllocationInformationStartAddress,
    );
    if not oAllocationInformation:
      return None;
    # The DPH_HEAP_BLOCK structure contains a pointer to the virtual allocation that contains the
    # heap block.
    oVirtualAllocation = foGetVirtualAllocationForProcessAndAddress(
      oProcess,
      POINTER_VALUE(oAllocationInformation.pVirtualBlock),
    );
    if oVirtualAllocation.bAllocated:
      # This virtual allocation starts with a DPH_ALLOCATION_HEADER structure
      oAllocationHeader = foGetAllocationHeaderForVirtualAllocationAndPointerSize(
        oVirtualAllocation,
        oProcess.uPointerSize,
      );
    else:
      oAllocationHeader = None;
    return foGetPageHeapManagerDataHelper(oProcess.uPointerSize, uAllocationInformationStartAddress, oAllocationInformation, oVirtualAllocation, oAllocationHeader)
    
  @staticmethod
  def foGetForProcessAndAddress(oProcess, uAddressInVirtualAllocation):
    oVirtualAllocation = foGetVirtualAllocationForProcessAndAddress(
      oProcess,
      uAddressInVirtualAllocation,
    );
    if not oVirtualAllocation.bAllocated:
      # There really is nothing here for us to report details on:
      return None;
    # The virtual allocation starts with a DPH_ALLOCATION_HEADER structure
    oAllocationHeader = foGetAllocationHeaderForVirtualAllocationAndPointerSize(
      oVirtualAllocation,
      oProcess.uPointerSize,
    );
    # The DPH_ALLOCATION_HEADER structure contains a pointer to a DPH_HEAP_BLOCK structure
    uAllocationInformationStartAddress = POINTER_VALUE(oAllocationHeader.poAllocationInformation);
    oAllocationInformation = foGetAllocationInformationForProcessAndAddress(
      oProcess,
      uAllocationInformationStartAddress,
    );
    return foGetPageHeapManagerDataHelper(oProcess.uPointerSize, uAllocationInformationStartAddress, oAllocationInformation, oVirtualAllocation, oAllocationHeader);
  
  def __init__(oSelf,
    uPointerSize,
    uAllocationInformationStartAddress,
    oAllocationInformation,
    oVirtualAllocation,
    oAllocationHeader,
    uHeapBlockHeaderStartAddress,
    oHeapBlockHeader,
    uHeapBlockEndPaddingSize,
  ):
    oSelf.uHeapRootAddress = None;
    oSelf.uPointerSize = uPointerSize;
    
    oSelf.uAllocationInformationStartAddress = uAllocationInformationStartAddress;
    oSelf.oAllocationInformation = oAllocationInformation;
    oSelf.uAllocationInformationEndAddress = uAllocationInformationStartAddress + SIZEOF(oAllocationInformation);
    oSelf.uAllocationInformationSize = oSelf.uAllocationInformationEndAddress - oSelf.uAllocationInformationStartAddress;

    oSelf.oVirtualAllocation = oVirtualAllocation;
    oSelf.oVirtualAllocation.uEndAddress;
    
    oSelf.uHeapBlockStartAddress = POINTER_VALUE(oAllocationInformation.pUserAllocation);
    oSelf.uHeapBlockEndAddress = oSelf.uHeapBlockStartAddress + oAllocationInformation.nUserRequestedSize;
    oSelf.uHeapBlockSize = oAllocationInformation.nUserRequestedSize;

    if oAllocationHeader:
      oSelf.uAllocationHeaderStartAddress = oVirtualAllocation.uStartAddress;
      oSelf.oAllocationHeader = oAllocationHeader;
      oSelf.uAllocationHeaderEndAddress = oVirtualAllocation.uStartAddress + SIZEOF(oAllocationHeader);
      oSelf.uAllocationHeaderSize = oSelf.uAllocationHeaderEndAddress - oSelf.uAllocationHeaderStartAddress;
    else:
#      oSelf.uAllocationHeaderStartAddress = None;
      oSelf.oAllocationHeader = None;
#      oSelf.uAllocationHeaderEndAddress = None;
#      oSelf.uAllocationHeaderSize = None;
    
    if oHeapBlockHeader:
      oSelf.uHeapBlockHeaderStartAddress = uHeapBlockHeaderStartAddress;
      oSelf.oHeapBlockHeader = oHeapBlockHeader;
      oSelf.uHeapBlockHeaderEndAddress = uHeapBlockHeaderStartAddress + SIZEOF(oHeapBlockHeader);
      oSelf.uHeapBlockHeaderSize = oSelf.uHeapBlockHeaderEndAddress - oSelf.uHeapBlockHeaderStartAddress;
      assert oSelf.uHeapBlockHeaderEndAddress == oSelf.uHeapBlockStartAddress, \
          "Page heap block header end address 0x%X should be the same as the heap block start address 0x%X" % \
          (oSelf.uHeapBlockHeaderEndAddress, oSelf.uHeapBlockStartAddress);
    else:
#      oSelf.uHeapBlockHeaderStartAddress = None;
      oSelf.oHeapBlockHeader = None;
#      oSelf.uHeapBlockHeaderEndAddress = None;
#      oSelf.uHeapBlockHeaderSize = None;
    
    oSelf.bAllocated = oAllocationInformation.uState == DPH_STATE_ALLOCATED;
    oSelf.bFreed = oAllocationInformation.uState == DPH_STATE_FREED;
    
    if uHeapBlockEndPaddingSize:
      oSelf.uHeapBlockEndPaddingStartAddress = oSelf.uHeapBlockEndAddress;
      oSelf.uHeapBlockEndPaddingSize = uHeapBlockEndPaddingSize;
      oSelf.uHeapBlockEndPaddingEndAddress = oSelf.uHeapBlockEndAddress + uHeapBlockEndPaddingSize;
      assert oSelf.uHeapBlockEndPaddingEndAddress == oSelf.oVirtualAllocation.uEndAddress, \
          "Page heap block end padding end address 0x%X should be the same as the allocation end address 0x%X" % \
          (oSelf.uHeapBlockEndPaddingEndAddress, oSelf.oVirtualAllocation.uEndAddress);
    else:
      oSelf.uHeapBlockEndPaddingStartAddress = None;
      oSelf.uHeapBlockEndPaddingSize = None;
      oSelf.uHeapBlockEndPaddingEndAddress = None;
    
    oSelf.__dsCorruptedByte_by_uAddress = None;
    oSelf.__uCorruptionStartAddress = None;
    oSelf.__uCorruptionEndAddress = None;
    
  @property
  def bCorruptionDetected(oSelf):
    if oSelf.__dsCorruptedByte_by_uAddress is None:
      oSelf.__fDetectCorruption();
    return len(oSelf.__dsCorruptedByte_by_uAddress) > 0;
  
  @property
  def uCorruptionStartAddress(oSelf):
    if oSelf.__dsCorruptedByte_by_uAddress is None:
      oSelf.__fDetectCorruption();
    return oSelf.__uCorruptionStartAddress;
  
  @property
  def uCorruptionEndAddress(oSelf):
    if oSelf.__dsCorruptedByte_by_uAddress is None:
      oSelf.__fDetectCorruption();
    return oSelf.__uCorruptionEndAddress;
  
  @property
  def uMemoryDumpStartAddress(oSelf):
    if oSelf.__dsCorruptedByte_by_uAddress is None:
      oSelf.__fDetectCorruption();
    return oSelf.__uMemoryDumpStartAddress;
  
  @property
  def uMemoryDumpEndAddress(oSelf):
    if oSelf.__dsCorruptedByte_by_uAddress is None:
      oSelf.__fDetectCorruption();
    return oSelf.__uMemoryDumpEndAddress;

  @property
  def uMemoryDumpSize(oSelf):
    if oSelf.__dsCorruptedByte_by_uAddress is None:
      oSelf.__fDetectCorruption();
    return oSelf.__uMemoryDumpEndAddress - oSelf.__uMemoryDumpStartAddress;
  
  @property
  def sCorruptionId(oSelf):
    if oSelf.__dsCorruptedByte_by_uAddress is None:
      oSelf.__fDetectCorruption();
    assert oSelf.bCorruptionDetected, \
        "Cannot get a corruption id if no corruption was detected!";
    (sIgnoredSizeId, sCorruptionOffsetId, sCorruptionOffsetDescription, sIgnoredSizeDescription) = \
        oSelf.ftsGetIdAndDescriptionForAddress(oSelf.__uCorruptionStartAddress);
    # ^^^ sCorruptionOffsetDescription is not used.
    uCorruptionLength = oSelf.__uCorruptionEndAddress - oSelf.__uCorruptionStartAddress;
    sId = "%s~%s" % (sCorruptionOffsetId, fsGetNumberDescription(uCorruptionLength));
    # Only hash the chars when the bugid is not architecture independent, as different architectures may result in
    # different sixed corruptions, which we can compensate for in the length, but not in the hash.
    if dxConfig["uArchitectureIndependentBugIdBits"] == 0 and dxConfig["uHeapCorruptedBytesHashChars"]:
      oHasher = hashlib.md5();
      uAddress = oSelf.__uCorruptionStartAddress;
      while uAddress < oSelf.__uCorruptionEndAddress:
        if uAddress in oSelf.__dsCorruptedByte_by_uAddress:
          oHasher.update(oSelf.__dsCorruptedByte_by_uAddress[uAddress]);
        uAddress += 1;
      sId += "#%s" % oHasher.hexdigest()[:dxConfig["uHeapCorruptedBytesHashChars"]];
    return sId;
  
  def fuHeapBlockHeaderFieldAddress(oSelf, sFieldName, sSubFieldName = None):
    uAddress = oSelf.uHeapBlockHeaderStartAddress + oSelf.oHeapBlockHeader.fuOffsetOf(sFieldName);
    if sSubFieldName:
      oField = getattr(oSelf.oHeapBlockHeader, sFieldName);
      uAddress += oField.fuOffsetOf(sSubFieldName);
    return uAddress;

  def fuHeapBlockHeaderFieldSize(oSelf, sFieldName, sSubFieldName = None):
    if sSubFieldName:
      oField = getattr(oSelf.oHeapBlockHeader, sFieldName);
      return oField.fuSizeOf(sSubFieldName);
    return oSelf.oHeapBlockHeader.fuSizeOf(sFieldName);

  def fatxMemoryRemarks(oSelf):
    if oSelf.__dsCorruptedByte_by_uAddress is None:
      oSelf.__fDetectCorruption();
    atxMemoryRemarks = [
      ("Allocation start",                  oSelf.oVirtualAllocation.uStartAddress, None),
      ("Heap block start",                  oSelf.uHeapBlockStartAddress, None),
      ("Heap block end",                    oSelf.uHeapBlockEndAddress, None),
      ("Allocation end",                    oSelf.oVirtualAllocation.uEndAddress, None),
    ];
    if oSelf.oAllocationHeader:
      atxMemoryRemarks += [
        ("Allocation header start",         oSelf.uAllocationHeaderStartAddress, None),
        ("Allocation header end",           oSelf.uAllocationHeaderEndAddress, None),
      ];
    if oSelf.oHeapBlockHeader:
      atxMemoryRemarks += [
        ("Page heap StartStamp",            oSelf.fuHeapBlockHeaderFieldAddress("StartStamp"), None),
        ("Page heap Heap",                  oSelf.fuHeapBlockHeaderFieldAddress("Heap"), None),
        ("Page heap RequestedSize",         oSelf.fuHeapBlockHeaderFieldAddress("RequestedSize"), None),
        ("Page heap ActualSize",            oSelf.fuHeapBlockHeaderFieldAddress("ActualSize"), None),
        ("Page heap StackTrace",            oSelf.fuHeapBlockHeaderFieldAddress("StackTrace"), None),
        ("Page heap EndStamp",              oSelf.fuHeapBlockHeaderFieldAddress("EndStamp"), None),
      ];
    if oSelf.uHeapBlockEndPaddingSize:
      atxMemoryRemarks += [
        ("Page heap allocation end padding", oSelf.uHeapBlockEndPaddingStartAddress, None),
      ];
    for (uAddress, sCorruptedByte) in oSelf.__dsCorruptedByte_by_uAddress.items():
      atxMemoryRemarks += [
       ("Corrupted (should be %02X)" % ord(sCorruptedByte), uAddress, None)
      ];
    return atxMemoryRemarks;
  
  def __fDetectCorruptionHelper(oSelf, uStartAddress, sExpectedBytes, sActualBytes):
    assert len(sExpectedBytes) == len(sActualBytes), \
        "Cannot compare %d expected bytes to %d actual bytes" % (len(sExpectedBytes), len(sActualBytes));
    asStatus = [];
    uFirstDetectedCorruption = None;
    uLastDetectedCorruption = None;
    for uIndex in xrange(len(sExpectedBytes)):
      if sActualBytes[uIndex] != sExpectedBytes[uIndex]:
        asStatus.append("^^");
        uAddress = uStartAddress + uIndex;
        if uFirstDetectedCorruption is None:
          uFirstDetectedCorruption = uAddress;
        uLastDetectedCorruption = uAddress;
        if oSelf.__uCorruptionStartAddress is None or oSelf.__uCorruptionStartAddress > uAddress:
          oSelf.__uCorruptionStartAddress = uAddress;
        if oSelf.__uCorruptionEndAddress is None or oSelf.__uCorruptionEndAddress < uAddress + 1:
          oSelf.__uCorruptionEndAddress = uAddress + 1;
        oSelf.__dsCorruptedByte_by_uAddress[uAddress] = sExpectedBytes[uIndex];
        if uAddress < oSelf.__uMemoryDumpStartAddress:
          oSelf.__uMemoryDumpStartAddress = uAddress;
        if uAddress > oSelf.__uMemoryDumpEndAddress:
          oSelf.__uMemoryDumpEndAddress = uAddress;
      else:
        asStatus.append("  ");
    if gbDebugOutput:
      print "Comparing memory @ 0x%X" % uStartAddress;
      print "Expected: %s" % " ".join(["%02X" % ord(sChar) for sChar in sExpectedBytes]);
      print "Actual:   %s" % " ".join(["%02X" % ord(sChar) for sChar in sActualBytes]);
      if uFirstDetectedCorruption:
        print "Detected: %s" % " ".join([sStatus for sStatus in asStatus]);
        print "New:      0x%X-0x%X" % (uFirstDetectedCorruption, uLastDetectedCorruption + 1);
        print "Total:    0x%X-0x%X" % (oSelf.__uCorruptionStartAddress, oSelf.__uCorruptionEndAddress);
      else:
        print "OK";
  
  def __fDetectCorruption(oSelf):
    oSelf.__dsCorruptedByte_by_uAddress = {};
    if not oSelf.oVirtualAllocation.bAllocated:
      oSelf.__uMemoryDumpStartAddress = None;
      oSelf.__uMemoryDumpEndAddress = None;
      return;
    oSelf.__uMemoryDumpStartAddress = oSelf.uHeapBlockHeaderSize and oSelf.uHeapBlockHeaderStartAddress or oSelf.uHeapBlockStartAddress;
    oSelf.__uMemoryDumpEndAddress = oSelf.uHeapBlockEndPaddingSize and oSelf.uHeapBlockEndPaddingEndAddress or oSelf.uHeapBlockEndAddress;
    # Check the empty space between the allocation header and the heap block header; it should contain nothing but "\0"s
    uEmptySpaceBetweenAllocationHeaderAndHeapBlockHeaderOffset = oSelf.uAllocationHeaderEndAddress - oSelf.oVirtualAllocation.uStartAddress;
    uEmptySpaceBetweenAllocationHeaderAndHeapBlockHeaderSize = oSelf.uHeapBlockHeaderStartAddress - oSelf.uAllocationHeaderEndAddress;
    sExpectedBytes = "\0" * uEmptySpaceBetweenAllocationHeaderAndHeapBlockHeaderSize;
    sActualBytes = oSelf.oVirtualAllocation.fsReadBytesForOffsetAndSize(
      uEmptySpaceBetweenAllocationHeaderAndHeapBlockHeaderOffset,
      uEmptySpaceBetweenAllocationHeaderAndHeapBlockHeaderSize,
    );
    oSelf.__fDetectCorruptionHelper(oSelf.uAllocationHeaderEndAddress, sExpectedBytes, sActualBytes)
    # Check the page heap block header
    DPH_BLOCK_INFORMATION = {4: DPH_BLOCK_INFORMATION_32, 8: DPH_BLOCK_INFORMATION_64}[oSelf.uPointerSize];
    LIST_ENTRY = {4: LIST_ENTRY_32, 8: LIST_ENTRY_64}[oSelf.uPointerSize];
    oExpectedHeapBlockHeader = DPH_BLOCK_INFORMATION(**dict([tx for tx in [
      ("StartStamp", oSelf.bAllocated and uPaddingStartAllocated or uPaddingStartFreed),
      hasattr(oSelf.oHeapBlockHeader, "PaddingStart") and ("PaddingStart", 0),
      ("Heap", oSelf.uHeapRootAddress or oSelf.oHeapBlockHeader.Heap), # We do not always know the correct value
      ("RequestedSize", oSelf.oAllocationInformation.nUserRequestedSize),
      ("ActualSize", oSelf.oVirtualAllocation.uSize),
      ("FreeQueue", oSelf.oHeapBlockHeader.FreeQueue), # We do not know the correct value.
      ("StackTrace", oSelf.oAllocationInformation.StackTrace),
      hasattr(oSelf.oHeapBlockHeader, "PaddingEnd") and ("PaddingEnd", 0),
      ("EndStamp", oSelf.bAllocated and uAllocatedEndStamp or uFreedEndStamp),
    ] if tx]));
    sExpectedBytes = oExpectedHeapBlockHeader.fsToBytesString();
    sActualBytes = oSelf.oHeapBlockHeader.fsToBytesString();
    oSelf.__fDetectCorruptionHelper(oSelf.uHeapBlockHeaderStartAddress, sExpectedBytes, sActualBytes);
    # Check the heap block if it is freed
    if oSelf.bFreed:
      sExpectedBytes = chr(uFreedHeapBlockFillByte) * oSelf.uHeapBlockSize;
      sActualBytes = oSelf.oVirtualAllocation.fsReadBytesForOffsetAndSize(
        oSelf.uHeapBlockStartAddress - oSelf.oVirtualAllocation.uStartAddress,
        oSelf.uHeapBlockSize,
      );
      oSelf.__fDetectCorruptionHelper(oSelf.uHeapBlockStartAddress, sExpectedBytes, sActualBytes);
    # Check the allocation end padding
    if oSelf.uHeapBlockEndPaddingSize:
      sExpectedBytes = chr(uHeapBlockEndPaddingFillByte) * oSelf.uHeapBlockEndPaddingSize;
      sActualBytes = oSelf.oVirtualAllocation.fsReadBytesForOffsetAndSize(
        oSelf.uHeapBlockEndPaddingStartAddress - oSelf.oVirtualAllocation.uStartAddress,
        oSelf.uHeapBlockEndPaddingSize,
      );
      oSelf.__fDetectCorruptionHelper(oSelf.uHeapBlockEndPaddingStartAddress, sExpectedBytes, sActualBytes);
    if gbDebugOutput:
      if oSelf.__uCorruptionStartAddress:
        print "Result:   0x%X-0x%X" % (oSelf.__uCorruptionStartAddress, oSelf.__uCorruptionEndAddress);
      else:
        print "Result:   OK";

