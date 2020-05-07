
import numpy as np
import pandas as pd
import string
import xlrd
import numpy.core.multiarray
from pandas import ExcelWriter
from pandas import ExcelFile
# ============================================================================================
def Calc_MultiplierI(vVar, nSectors, vTotalProduction, mLeontief):
    vVar=vVar.reshape(1, nSectors)
    vCoef = np.zeros([1, nSectors], dtype=float)
    for j in range(nSectors):
        vCoef[0, j] = vVar[0, j] / vTotalProduction[0, j]

    vGerador = np.zeros([1,nSectors], dtype=float)
    for j in range(nSectors):
        vGerador[0,j] = np.sum(mLeontief[:,j] * vCoef[0,:])

    vMultiplier = np.zeros([1, nSectors], dtype=float)
    vMultiplier[0, :] = vGerador[0, :] / vCoef[0, :]
    vMultiplier = np.nan_to_num(vMultiplier, nan=0, posinf=0, neginf=0)
    return vMultiplier.reshape(nSectors,1), vGerador.reshape(nSectors,1), vCoef.reshape(nSectors,1)

# ============================================================================================
def Calc_MultiplierII(vCoef, nSectors, mLeontief):
    vCoef=vCoef.reshape(1, nSectors)
    vGerador = np.zeros([1,nSectors], dtype=float)
    for j in range(nSectors):
        vGerador[0,j] = np.sum(mLeontief[0:nSectors,j] * vCoef[0,:])

    vMultiplier = np.zeros([1, nSectors], dtype=float)
    vMultiplier[0,:] = vGerador[0, :] / vCoef[0, :]
    vMultiplier = np.nan_to_num(vMultiplier, nan=0, posinf=0, neginf=0)
    return vMultiplier.reshape(nSectors,1), vGerador.reshape(nSectors,1)

# ============================================================================================

def read_file_excel(sDirectory, sFileName, sSheetName):
    sFileName = sDirectory + sFileName
    mSheet = pd.read_excel(sFileName, sheet_name=sSheetName, header=None, index_col=None)
    return mSheet

# =============================================================
# Função que lê dados de um arquivo txt e retorna uma matriz
# lê de uma pasta input
# ============================================================================================

def read_file_txt(sFileName, sDirectory):
    sFileName = sDirectory + sFileName
    temp = np.loadtxt(sFileName, dtype=np.float64, skiprows= 1)
    return temp

# ============================================================================================
def load_data_comextstat(sDirectoryInput, sFile, nStates, nProducts):
    mSheet = read_file_txt(sFile, sDirectoryInput)
#    mSheet = read_file_excel(sDirectoryInput, sFile, sSheet)
    mValue = np.zeros([nStates, nProducts], dtype=float)
    for s in range(nStates):
        for p in range(nProducts):
            mValue[s, p] =mSheet[nProducts*s+p, 5]
    return mValue

# ============================================================================================
def load_table_states(sDirectoryInput, sFileStates, nStates):
    mSheet = read_file_excel(sDirectoryInput, sFileStates, 'TabStates')
    vCodStates = []
    vNameRegions = []
    vNameStates = []
    vShortNameStates = []
    for s in range(nStates):
        vCodStates.append(mSheet.values[s+1, 0])
        vNameRegions.append(mSheet.values[s+1, 1])
        vNameStates.append(mSheet.values[s+1, 2])
        vShortNameStates.append(mSheet.values[s+1, 3])

    return vCodStates, vNameRegions, vNameStates, vShortNameStates
# ============================================================================================
# ============================================================================================
def load_convert_states(sDirectoryInput, sFileStates, nStates):
    mSheet = read_file_excel(sDirectoryInput, sFileStates, 'Convert')
    nLinIni=29
    nColIni=1

    vConvertStates = np.zeros([nStates], dtype=int)
    for l in range(nStates):
        sAux=mSheet.values[nLinIni+l, nColIni+l]
        vConvertStates[l]=mSheet.values[nLinIni-1, nColIni+l]

    return vConvertStates
# ============================================================================================
def load_DemandShock(sDirectoryInput, sFileDemandShock, sSheetName, nSectors, nAdjustUni):
    mSheet = pd.read_excel(sDirectoryInput + sFileDemandShock, sheet_name=sSheetName, header=None)
    nColIni = 2
    nLinIni = 1
    mDemandShock=np.zeros([nSectors,6],dtype=float)
    for i in range(nSectors):
        mDemandShock[i,:] = nAdjustUni + mSheet.values[nLinIni + i, nColIni:nColIni+6]

    return mDemandShock
# ============================================================================================
def load_OfferShock(sDirectoryInput, sFileDemandShock, sSheetName, nSectors, nAdjustUni):
    mSheet = pd.read_excel(sDirectoryInput + sFileDemandShock, sheet_name=sSheetName, header=None)
    nColIni = 2
    nLinIni = 1
    vLaborRestriction=np.zeros([nSectors,1],dtype=float)
    for i in range(nSectors):
        vLaborRestriction[i,0]= nAdjustUni + mSheet.values[nLinIni + i, nColIni]

    return vLaborRestriction
# ============================================================================================
def load_NationalMIP(sDirectoryInput, sFileInput, sSheetName, nSector
                     , nLinIni, nColIni, nColsDemandNat, nLinExtra, nColExtra, nLinsTaxes, nLinsVA):
    mSheet=pd.read_excel(sDirectoryInput+sFileInput, sheet_name=sSheetName,  header =None)
    nLinTotProd=1
    nLinIniTaxes= nSector + 2
    nLinFimTaxes= nSector + nLinsTaxes+2
    vCodSector = []
    vNameSector= []
    vNameTaxes = []
    vNameVA    = []
    vNameDemand = []

    mMipAux = np.empty([nSector + nLinExtra, nSector + nColsDemandNat + nColExtra], dtype=float)
    for l in range(nSector + nLinExtra):
        for c in range(nSector + nColsDemandNat + nColExtra):
            mMipAux[l, c] = mSheet.values[nLinIni + l, nColIni + c]

    # National - Intermediate consum  + National Production Line +Imports + taxes + Intermediate Consum Total Line + Added Value
    mIntermConsumNat=np.copy(mMipAux[0:nSector,0:nSector])
    vIntermConsumNatTotCons=np.copy(mMipAux[0:nSector,nSector])
    vNatProductNat=np.copy(mMipAux[nSector,0:nSector]).reshape(1,nSector)
    vImportsNat =np.copy(mMipAux[nSector+nLinTotProd,0:nSector]).reshape(1,nSector)
    mTaxesNat=np.copy(mMipAux[nLinIniTaxes:nLinFimTaxes,0:nSector])
    vIntermConsumNatTotProd=(np.copy(mMipAux[nLinFimTaxes,0:nSector])).reshape(1,nSector)
    mVANat =np.copy(mMipAux[nLinFimTaxes+1:nSector+nLinExtra,0:nSector])
    # Intermediate Consum Total Column + Intermediate Consum Total Taxes  Column+ Intermediate Consum Total Tazes Column
    vIntermConsumNatTotConsum=np.copy(mMipAux[0:nSector,nSector]).reshape(nSector,1)
    vProdIntermConsumNatTotConsum = np.copy(mMipAux[nSector, nSector]).reshape(1, 1)
    vImportsConsumNatTotConsum = np.copy(mMipAux[nSector+1, nSector]).reshape(1, 1)
    vTaxesIntermNatTotConsum = np.copy(mMipAux[nLinIniTaxes:nLinFimTaxes, nSector]).reshape(nLinsTaxes,1)
    vTotProdIntermConsumNatTotConsum=np.copy(mMipAux[nLinFimTaxes, nSector]).reshape(1,1)
    vTotVAIntermNatTotConsum=np.copy(mMipAux[nLinFimTaxes+1:nSector + nLinExtra,nSector]).reshape(nLinsVA,1)
    # National - Demad + total national Demand Line + Imports Demand + Taxes Demand + Total taxes Demand line + Added Value Demand
    mDemandNat=np.copy(mMipAux[0:nSector, nSector+1:nSector+1+nColsDemandNat])
    vNatDemandNat=np.copy(mMipAux[nSector, nSector+1:nSector+1+nColsDemandNat]).reshape(1,nColsDemandNat)
    vImportsDemandNat=np.copy(mMipAux[nSector+1, nSector+1:nSector+1+nColsDemandNat]).reshape(1,nColsDemandNat)
    mTaxesDemandNat=np.copy(mMipAux[nLinIniTaxes:nLinFimTaxes, nSector+1:nSector+1+nColsDemandNat])
    vTotTaxesDemandNat=np.copy(mMipAux[nLinFimTaxes, nSector+1:nSector+1+nColsDemandNat]).reshape(1,nColsDemandNat)
    mVADemandNat =np.copy(mMipAux[nLinFimTaxes+1:nSector + nLinExtra, nSector+1:nSector+1+nColsDemandNat])
    # National - Final Demand + total national Fial Demand Point + Taxes Final Demand + Total Final Demand point +   Added Value Final Demand
    vTotFinalDemandNat=np.copy(mMipAux[0:nSector, nSector+1+nColsDemandNat]).reshape(nSector,1)
    vTotProdNacFinalDemandNat=np.copy(mMipAux[nSector, nSector+1+nColsDemandNat]).reshape(1,1)
    vTotImportsFinalDemandNat=np.copy(mMipAux[nSector+1, nSector+1+nColsDemandNat]).reshape(1,1)
    vTotTaxesFinalDemandNat=np.copy(mMipAux[nLinIniTaxes:nLinFimTaxes, nSector+1+nColsDemandNat]).reshape(nLinsTaxes,1)
    vTotIntermConsumFinalDemandNat = np.copy(mMipAux[nLinFimTaxes:nLinFimTaxes+1, nSector+1+nColsDemandNat]).reshape(1, 1)
    vTotVAFinalDemandNat=np.copy(mMipAux[nLinFimTaxes+1:nSector + nLinExtra, nSector+1+nColsDemandNat]).reshape(nLinsVA,1)
    # National - Total Demand + total national Demand Point + Taxes total Demand + Total Demand point +   Added Value Total Demand
    vTotalDemandNat=np.copy(mMipAux[0:nSector, nSector+1+nColsDemandNat+1]).reshape(nSector,1)
    vTotProdNacDemandNat = np.copy(mMipAux[nSector:nSector+1, nSector+1+nColsDemandNat+1]).reshape(1, 1)
    vTotImportsDemandNat=np.copy(mMipAux[nSector+1:nSector+2, nSector+1+nColsDemandNat+1]).reshape(1,1)
    vTotalTaxesNat=np.copy(mMipAux[nLinIniTaxes:nLinFimTaxes, nSector+1+nColsDemandNat+1]).reshape(nLinsTaxes, 1)
    vTotIntermConsumDemandNat = np.copy(mMipAux[nLinFimTaxes:nLinFimTaxes+1, nSector+1+nColsDemandNat+1]).reshape(1, 1)
    vTotalVANat=np.copy(mMipAux[nLinFimTaxes+1:nSector + nLinExtra, nSector+1+nColsDemandNat+1]).reshape(nLinsVA,1)

    for l in range(nSector):
        vCodSector.append(mSheet.values[nLinIni + l, 0])
        vNameSector.append(mSheet.values[nLinIni + l,nColIni-1])

    for c in range(nColsDemandNat):
        nCAdd = nColIni + nSector + 1 + c
        vNameDemand.append(mSheet.values[nLinIni-1,nCAdd])

    for l in range(nLinsTaxes):
        nLAdd=nLinIni + nSector + 2 + l
        vNameTaxes.append(mSheet.values[nLAdd, nColIni-1])
    for l in range(nLinsVA):
        nLAdd = nLinIni + nLinFimTaxes+1 + l
        vNameVA.append(mSheet.values[nLAdd, nColIni-1])

    return vCodSector, vNameSector, vNameTaxes, vNameVA, vNameDemand, \
           mIntermConsumNat, vIntermConsumNatTotCons, vNatProductNat, vImportsNat, mTaxesNat, vIntermConsumNatTotProd, mVANat,  \
           vIntermConsumNatTotConsum, vProdIntermConsumNatTotConsum, vImportsConsumNatTotConsum, vTaxesIntermNatTotConsum, vTotProdIntermConsumNatTotConsum, vTotVAIntermNatTotConsum, \
           mDemandNat, vNatDemandNat, vImportsDemandNat, mTaxesDemandNat,vTotTaxesDemandNat, mVADemandNat, \
           vTotFinalDemandNat, vTotProdNacFinalDemandNat,vTotImportsFinalDemandNat, vTotTaxesFinalDemandNat, vTotIntermConsumFinalDemandNat, vTotVAFinalDemandNat,  \
           vTotalDemandNat, vTotProdNacDemandNat,vTotImportsDemandNat, vTotalTaxesNat, vTotIntermConsumDemandNat, vTotalVANat
# ============================================================================================
# ============================================================================================
# Função que grava dados em um arquivo excel
# Grava em uma pasta output e pode gravar várias planilhas em um mesmo arquivo
# ============================================================================================

def write_data_excel(sDirectoryOutput, sFileName, lSheetName, lDataSheet, lRowsLabel, lColsLabel, vUseHeader):
    Writer = pd.ExcelWriter(sDirectoryOutput+sFileName, engine='xlsxwriter')
    df=[]
    for each in range(len(lSheetName)):
        if vUseHeader[each] == True:
            df.append(pd.DataFrame(lDataSheet[each],  index=lRowsLabel[each], columns=lColsLabel[each], dtype=float))
            df[each].to_excel(Writer, lSheetName[each], header=True, index=True)
        else:
            df.append(pd.DataFrame(lDataSheet[each],  dtype=float))
            df[each].to_excel(Writer, lSheetName[each], header=False, index=False)

    Writer.save()

# ============================================================================================
# Função que grava dados em um arquivo excel
# Grava em uma pasta output e pode gravar uma só planilha em um mesmo arquivo
# ============================================================================================

def write_file_excel(sDirectoryOutput, sFileName, sSheet, mData, vRows, vCols, lUseHeader):
    Writer = pd.ExcelWriter(sDirectoryOutput+sFileName, engine='xlsxwriter')
    if lUseHeader == True:
        df=pd.DataFrame(mData, index=vRows, columns=vCols, dtype=float)
        df.to_excel(Writer, sheet_name=sSheet, header=True, index=True)
    else:
        df=pd.DataFrame(mData, dtype=float)
        df.to_excel(Writer, sheet_name=sSheet, header=False, index=False)
    Writer.save()

# ============================================================================================