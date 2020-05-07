# ============================================================================================
#
# Coded to Python by João Maria de Oliveira -
# ============================================================================================
import SupportFunctions as Support
import numpy as np

def WriteMultipliers(tTuplesIa, tTuplesIb, tTuplesII, vNameSector, sDirectoryOutput, nYear, nSectors):
    vDataSheet = []
    vSheetName = []
    vRowsLabel = []
    vColsLabel = []
    vUseHeader = []
    vNameCols = ['VA_I', 'VA_II', 'Occup_I', 'Occup_II', 'Remun_I', 'Remun_II', 'EOB_I', 'EOB_II', 'Salary_I',
                    'Salary_II']
    vNameMult = ['Multiplier', 'Gerador', 'Coef']

    xI = np.concatenate(tTuplesIa, axis=1)
    vDataSheet.append(xI)
    vSheetName.append(vNameMult[0])
    vRowsLabel.append(vNameSector)
    vColsLabel.append(vNameCols)
    vUseHeader.append(True)

    xI = np.concatenate(tTuplesIb, axis=1)
    vDataSheet.append(xI)
    vSheetName.append(vNameMult[1])
    vRowsLabel.append(vNameSector)
    vColsLabel.append(vNameCols)
    vUseHeader.append(True)

    vNameCols = ['VA', 'Occup', 'Remun', 'EOB', 'Salary']
    xI = np.concatenate(tTuplesII, axis=1)
    vDataSheet.append(xI)
    vSheetName.append(vNameMult[2])
    vRowsLabel.append(vNameSector)
    vColsLabel.append(vNameCols)
    vUseHeader.append(True)

    sFileSheet = 'Multip_' + str(nYear) + '_' + str(nSectors) + '.xlsx'
    Support.write_data_excel(sDirectoryOutput, sFileSheet, vSheetName, vDataSheet, vRowsLabel, vColsLabel,
                             vUseHeader)
    return

def WriteChockValues(mChock, vNameSector, mChockName, sDirectoryOutput, nYear, nSectors):
    vDataSheet = []
    vSheetName = []
    vRowsLabel = []
    vColsLabel = []
    vUseHeader = []

    vNameRowsReg = vNameSector
    vNameColsReg = mChockName

    vDataSheet.append(mChock)
    vSheetName.append('ChockBase')
    vRowsLabel.append(vNameRowsReg)
    vColsLabel.append(vNameColsReg)
    vUseHeader.append(True)
    sFileSheet = 'Chock_Base_' + str(nYear) + '_' + str(nSectors) + '.xlsx'
    Support.write_data_excel(sDirectoryOutput, sFileSheet, vSheetName, vDataSheet, vRowsLabel, vColsLabel,
                             vUseHeader)
    return




