from .fbIgnoreAccessViolationException import fbIgnoreAccessViolationException;
from ..fsGetNumberDescription import fsGetNumberDescription;
from ..ftuLimitedAndAlignedMemoryDumpStartAddressAndSize import ftuLimitedAndAlignedMemoryDumpStartAddressAndSize;

def fbUpdateReportForHeapManagerPointer(
  oCdbWrapper, oBugReport, oProcess, oThread, sViolationTypeId, uAccessViolationAddress, sViolationTypeDescription, oVirtualAllocation
):
  # This is not a special marker or NULL, so it must be some corrupt pointer
  # Get information about the memory region:
  oHeapManagerData = oProcess.foGetHeapManagerDataForAddress(uAccessViolationAddress);
  if not oHeapManagerData:
    return False;
  oBugReport.atxMemoryRemarks.extend(oHeapManagerData.fatxMemoryRemarks());
  if oProcess.oCdbWrapper.bGenerateReportHTML and oHeapManagerData.uMemoryDumpStartAddress:
    uMemoryDumpStartAddress = oHeapManagerData.uMemoryDumpStartAddress;
    uMemoryDumpSize = oHeapManagerData.uMemoryDumpSize;
    if uAccessViolationAddress < oHeapManagerData.uHeapBlockStartAddress:
      uPrefix = oHeapManagerData.uHeapBlockStartAddress - uAccessViolationAddress;
      uMemoryDumpStartAddress -= uPrefix;
      uMemoryDumpSize += uPrefix;
      # If the memory dump because too large, truncate it.
      if uMemoryDumpSize > 0x1000:
        uMemoryDumpSize = 0x1000;
    elif uAccessViolationAddress >= oHeapManagerData.uHeapBlockEndAddress:
      uPostFix = uAccessViolationAddress - oHeapManagerData.uHeapBlockEndAddress + 1;
      # Show some of the guard page so we can insert labels where the AV took place, but only
      # if this does not cause the memory dump to become too large.
      if uMemoryDumpSize + uPostFix < 0x1000:
        uMemoryDumpSize += uPostFix;
    # Check if we're not trying to dump a rediculous amount of memory:
    # Clamp start and end address
    uMemoryDumpStartAddress, uMemoryDumpSize = ftuLimitedAndAlignedMemoryDumpStartAddressAndSize(
      uAccessViolationAddress, oHeapManagerData.uPointerSize, uMemoryDumpStartAddress, uMemoryDumpSize
    );
    oBugReport.fAddMemoryDump(
      uMemoryDumpStartAddress,
      uMemoryDumpStartAddress + uMemoryDumpSize,
      "Memory near access violation at 0x%X" % uAccessViolationAddress,
    );
  bOutOfBounds = (uAccessViolationAddress < oHeapManagerData.uHeapBlockStartAddress) \
              or (uAccessViolationAddress >= oHeapManagerData.uHeapBlockEndAddress);
  (sBlockSizeId, sBlockOffsetId, sBlockOffsetDescription, sBlockSizeDescription) = \
      oHeapManagerData.ftsGetIdAndDescriptionForAddress(uAccessViolationAddress);
  sBlockSizeAndOffsetId = sBlockSizeId + sBlockOffsetId;
  sBlockOffsetAndSizeDescription = sBlockOffsetDescription + " " + sBlockSizeDescription;
  oBugReport.sBugDescription = "Access violation while %s %smemory at 0x%X; %s." % (sViolationTypeDescription, \
      oHeapManagerData.bFreed and "freed " or "", uAccessViolationAddress, sBlockOffsetAndSizeDescription);
  sPotentialRisk = {
    "R": "might allow information disclosure and (less likely) arbitrary code execution",
    "W": "indicates arbitrary code execution may be possible",
    "E": "indicates arbitrary code execution is very likely possible",
  }[sViolationTypeId];
  oBugReport.sSecurityImpact = "Potentially exploitable security issue that %s." % sPotentialRisk;
  if oHeapManagerData.bFreed:
    # --- (OOB)UAF -----------------------------------------------------------
    # We do not expect to see corruption of the page heap struct, as this should have been detected when the memory was
    # freed. The code may have tried to access data outside the bounds of the freed memory (double face-palm!).
    sBugAccessTypeId = (bOutOfBounds and "OOB" or "") + sViolationTypeId + "AF";
    oBugReport.sBugDescription += " This indicates a Use-After-Free (UAF) bug was triggered.";
    if bOutOfBounds:
      oBugReport.sBugDescription += " In addition, the code attempted to access data Out-Of-Bounds (OOB).";
    sCorruptionId = "";
  else:
    sBugAccessTypeId = (bOutOfBounds and "OOB" or "AV") + sViolationTypeId;
    if bOutOfBounds:
      oBugReport.sBugDescription += " This indicates an Out-Of-Bounds (OOB) access bug was triggered.";
    else:
      oBugReport.sBugDescription += " suggests an earlier memory corruption has corrupted a pointer, index or offset.";
    # We may be able to check the heap manager structures for signs of corruption to detect earlier out-of-bounds writes
    # that overwrite them but did not cause an access violation.
    if oHeapManagerData.bCorruptionDetected:
      # We detected a modified byte; there was an OOB write before the one that caused this access
      # violation.
      if oHeapManagerData.uHeapBlockStartAddress > oHeapManagerData.uCorruptionStartAddress:
        # Corruption before the heap block
        uOffsetBeforeStartOfBlock = oHeapManagerData.uHeapBlockStartAddress - oHeapManagerData.uCorruptionStartAddress;
        oBugReport.sBugDescription += (
          " An earlier out-of-bounds write was detected at 0x%X, %d/0x%X bytes " \
          "before that block because it modified the page heap prefix pattern."
        ) % (oHeapManagerData.uCorruptionStartAddress, uOffsetBeforeStartOfBlock, uOffsetBeforeStartOfBlock);
      elif oHeapManagerData.uHeapBlockEndAddress <= oHeapManagerData.uCorruptionStartAddress:
        # Corruption after the heap block
        uOffsetBeyondEndOfBlock = oHeapManagerData.uCorruptionStartAddress - oHeapManagerData.uHeapBlockEndAddress;
        oBugReport.sBugDescription += (
          " An earlier out-of-bounds write was detected at 0x%X, %d/0x%X bytes " \
          "beyond that block because it modified the page heap suffix pattern."
        ) % (oHeapManagerData.uCorruptionStartAddress, uOffsetBeyondEndOfBlock, uOffsetBeyondEndOfBlock);
        # If the corruption starts where the heap block ends and ends where a write access violation happened, this is
        # probably a classic linear buffer overflow.
        if (
          sViolationTypeId == "W"
          and oHeapManagerData.uHeapBlockEndAddress == oHeapManagerData.uCorruptionStartAddress
          and oHeapManagerData.uCorruptionEndAddress == uAccessViolationAddress
        ):
          sBugAccessTypeId = "BOF";
          oBugReport.sBugDescription += " This appears to be a classic linear buffer-overrun vulnerability.";
          sSecurityImpact = "Potentially highly exploitable security issue that might allow arbitrary code execution.";
      sCorruptionId = "{%s}" % oHeapManagerData.sCorruptionId;
    else:
      sCorruptionId = "";
      # --- OOB ---------------------------------------------------------------------
      # An out-of-bounds read on a heap block that is allocated and has padding that happens in or immedaitely after this 
      # padding could be the result of a sequential read where earlier out-of-bound reads of (parts of) this padding did
      # not trigger an access violation:
      if sViolationTypeId == "R" \
        and oHeapManagerData.bAllocated \
        and oHeapManagerData.uHeapBlockEndPaddingSize \
        and uAccessViolationAddress >= oHeapManagerData.uHeapBlockEndAddress \
        and uAccessViolationAddress <= oHeapManagerData.oVirtualAllocation.uEndAddress:
        oBugReport.sBugDescription += " An earlier out-of-bounds read before this address may have happened without " \
              "having triggered an access violation.";
  oBugReport.sBugTypeId = "".join([
    sBugAccessTypeId,
    sBlockSizeAndOffsetId,
    sCorruptionId,
  ]);
  # If this was a read AV, the heap manager may have made the memory inaccessible to detect use-after-frees. In this
  # case we may be able to read a pointer sized value from this memory for use with collateral later:
  if (
    sViolationTypeId == "R" and \
    oHeapManagerData.oVirtualAllocation and \
    oHeapManagerData.oVirtualAllocation.bAllocated and \
    uAccessViolationAddress >= oHeapManagerData.uHeapBlockStartAddress and \
    uAccessViolationAddress + oProcess.uPointerSize < oHeapManagerData.uHeapBlockEndAddress
  ):
    uPointerSizedValue = oHeapManagerData.oVirtualAllocation.fuReadValueForOffsetAndSize(
      uAccessViolationAddress - oHeapManagerData.uHeapBlockStartAddress,
      oProcess.uPointerSize,
    );
  else:
    uPointerSizedValue = None;
  oCdbWrapper.oCollateralBugHandler.fSetIgnoreExceptionFunction(lambda oCollateralBugHandler:
    fbIgnoreAccessViolationException(oCollateralBugHandler, oCdbWrapper, oProcess, oThread, sViolationTypeId, uPointerSizedValue = uPointerSizedValue)
  );
  return True;
