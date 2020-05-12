# ============================================================================================
# Main Module of Building Input output Regional
# Coded to Python by João Maria de Oliveira -
# ============================================================================================
import yaml
import numpy as np
import WriteMatrix
import SupportFunctions as Support
import sys
import time

# ============================================================================================
# read Parameters into Confg file
# ============================================================================================
conf = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)

sDirectoryInput  = conf['sDirectoryInput']
sDirectoryOutput = conf['sDirectoryOutput']

nColsDemand = conf['nColsDemand']
nColsDemandEach = conf['nColsDemandEach']
nColsOffer = conf['nColsOffer']
nRowsAV = conf['nRowsAV']
nColExport = conf['nColExport']
nColISFLSFConsum = conf['nColISFLSFConsum']
nColGovernConsum = conf['nColGovernConsum']
nColFamilyConsum = conf['nColFamilyConsum']
nColFBCF = conf['nColFBCF']
nColStockVar = conf['nColStockVar']
nColMarginTrade = conf['nColMarginTrade']
nColMarginTransport = conf['nColMarginTransport']
nColIPI = conf['nColIPI']
nColICMS = conf['nColICMS']
nColOtherTaxes = conf['nColOtherTaxes']
nColImport = conf['nColImport']
nColImportTax = conf['nColImportTax']


nDimension = 3





# vRowsTrade  - Números das linhas (inicial e final), dos produtos relacionados ao comercio
# vRowTransp - Números das linhas (inicial e final), dos produtos reacionados ao  tranporte
# vColsTrade  - Números das colunas (inicial e final), das atividades reacionadas ao comercio
# vColsTransp - Números das  colunas (inicial e final), das atividades reacionadas ao  tranporte
#  - a posição em cada vetor é dada por nDimensao ( Tamanho da MIP)
vProducts = [12, 20, 107, 128]
vSectors  = [12, 20,  51,  68]
vRowsTrade  = [[5, 5], [6, 6], [88, 88], [92, 93]]
vRowsTransp = [[6, 6], [7, 7], [89, 90], [94, 97]]
vColsTrade  = [[5, 5], [6, 6], [36, 36], [40, 41]]
vColsTransp = [[6, 6], [7, 7], [37, 37], [42, 44]]

# nProducts - Número de produtos de acordo com a dimensão da MIP
# nSectors - Número de atividades de acordo com a dimensão da MIP
# lAdjustMargins - True se ajusta as margens de comércio e transporte para apenas um produto e uma atividade
nProducts = vProducts [nDimension]
nSectors = vSectors [nDimension]
vRowsTradeElim  = vRowsTrade[nDimension]
vRowsTranspElim = vRowsTransp[nDimension]
vColsTradeElim  = vColsTrade[nDimension]
vColsTranspElim = vColsTransp[nDimension]
nGrupSectors = 18

#lAdjustMargins = True
lAdjustMargins = False
if lAdjustMargins:
   sAdjustMargins = '_Agreg'
else:
    sAdjustMargins = ''

# nRowTotalProduction - Número da linha do total da produção
# nRowAddedValueGross - Número da Linha do valor adicionado Bruto
# nColTotalDemand - Numero da coluna da demanda total na  tabela demanda
# nColFinalDemand - Numero da coluna da demanda total na  tabela demanda
nRowTotalProduction = nRowsAV - 2
nRowAddedValueGross = 0
nColTotalDemand = nColsDemand - 1
nColFinalDemand = nColsDemand - 2

# sFileUses             - Arquivo de usos - Demanda
# sFileResources        - Arquivo de recursos
# sFileSheet - nome do arquivo de saida contendo as = tabelas
#sFileInputNational ='MIPNAT_2013_guilhoto.xlsx'
#nYear = 2013
#sSheetNational='BR'
#nColIni = 2
#nLinIni = 3
#nColsDemandNat = 6
#nLinExtra = 25
#nColExtra = 3
#nLinsTaxes =7
#nLinsVA = 15
#nLinWages= 0
#nLinTotalProduction = 13
#nColFamilyConsum = 3
#nLinEOBTotal = 6
#nLinRMB = 7
#nLinEOBPure = 8
#nLinVA = 12
#nLinOccup = 14

nYear = 2017
sFileInputNational ='MIP_'+str(nYear)+'_68.xlsx'
sSheetNational='MIP'
nColIni = 1
nLinIni = 1
nColsDemandNat = 6
nLinExtra = 21
nColExtra = 3
nLinsTaxes = 4
nLinsVA = 14

nLinWages= 1
nLinTotalProduction = 12
nLinEOBTotal = 7
nLinRMB = 8
nLinEOBPure = 9
nLinVA = 0
nLinOccup = 13
nColFamilyConsum = 3


sFileShock='Choque.xlsx'
lRelativAbsolut=True
lChockOfferDemand = 2 # 0 = demand ; 1 = Offer ;  2= both


sFileSheetNat = 'Analise_Nacional_'+str(nYear)+'_'+str(nSectors)+sAdjustMargins+'.xlsx'
sFileNameOutput = str(nYear)+'_'+str(nSectors)+sAdjustMargins+'.xlsx'

def SectorAgregate(vCodGrupSector, vVariableIn, nSectors, sGrupSectors):
    vVariableOut = np.zeros([1, nGrupSectors  ], dtype=float)
    for sl in range(nSectors):
            nLin = vCodGrupSector[sl]
            vVariableOut[0, nLin] = vVariableOut[0, nLin] + vVariableIn[sl]

    return vVariableOut

if __name__ == '__main__':
    nBeginModel = time.perf_counter()
    sTimeBeginModel = time.localtime()
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Running Model for ", nSectors, "sectors")
    print("Begin at ", time.strftime("%d/%b/%Y - %H:%M:%S",sTimeBeginModel ))
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    if lRelativAbsolut:
        nAdjustUni=1
    else:
        nAdjustUni=0

    vCodGrupSector, vNameGrupSector =Support.load_GrupSector(sDirectoryInput, "SetoresGrupo.xlsx", nGrupSectors, nSectors)
    mDemandShock      = Support.load_DemandShock(sDirectoryInput, sFileShock, "Demanda", nSectors, nAdjustUni)
    vLaborRestriction = Support.load_OfferShock(sDirectoryInput, sFileShock, "Oferta", nSectors, nAdjustUni)
    #
    #    vCodStates, vNameRegions, vNameStates, vShortNameStates = Support.load_table_states(sDirectoryInput, sFileStates, nStates)
    # ============================================================================================
    # Import values from National MIP from guilhoto
    # ============================================================================================
    sTimeIntermediate = time.localtime()
    print(time.strftime("%d/%b/%Y - %H:%M:%S", sTimeIntermediate), " - Reading National Mip Matrix")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    vCodSector, vNameSector, vNameTaxes, vNameVA, vNameDemand, \
    mIntermConsumNat, vIntermConsumNatTotCons, vNatProductNat, vImportsNat, mTaxesNat, vIntermConsumNatTotProd, mVANat, \
    vIntermConsumNatTotConsum, vProdIntermConsumNatTotConsum, vImportsConsumNatTotConsum, vTaxesIntermNatTotConsum, vTotProdIntermConsumNatTotConsum, vTotVAIntermNatTotConsum, \
    mDemandNat, vNatDemandNat, vImportsDemandNat, mTaxesDemandNat, vTotTaxesDemandNat, mVADemandNat, \
    vTotFinalDemandNat, vTotProdNacFinalDemandNat, vTotImportsFinalDemandNat, vTotTaxesFinalDemandNat, vTotIntermConsumFinalDemandNat, vTotVAFinalDemandNat, \
    vTotalDemandNat, vTotProdNacDemandNat, vTotImportsDemandNat, vTotalTaxesNat, vTotIntermConsumDemandNat, vTotalVANat = \
        Support.load_NationalMIP (sDirectoryInput, sFileInputNational, sSheetNational, nSectors
                                  , nLinIni, nColIni, nColsDemandNat, nLinExtra, nColExtra, nLinsTaxes, nLinsVA)

    mInterConsumNatAux = np.concatenate((mIntermConsumNat, vNatProductNat, vImportsNat, mTaxesNat, vIntermConsumNatTotProd, mVANat), axis=0)
    mDemandNatAux= np.concatenate((mDemandNat, vNatDemandNat,vImportsDemandNat, mTaxesDemandNat, vTotTaxesDemandNat, mVADemandNat), axis=0)
    vInterConsumTotalAux= np.concatenate((vIntermConsumNatTotConsum, vProdIntermConsumNatTotConsum, vImportsConsumNatTotConsum, vTaxesIntermNatTotConsum, vTotProdIntermConsumNatTotConsum, vTotVAIntermNatTotConsum), axis=0)
    vFinalDemandAuxNat = np.concatenate((vTotFinalDemandNat, vTotProdNacFinalDemandNat, vTotImportsFinalDemandNat, vTotTaxesFinalDemandNat, vTotIntermConsumFinalDemandNat, vTotVAFinalDemandNat), axis=0)
    vTotalDemandAuxNat = np.concatenate((vTotalDemandNat, vTotProdNacDemandNat, vTotImportsDemandNat, vTotalTaxesNat, vTotIntermConsumDemandNat, vTotalVANat), axis=0)
    mMIPGeralNat= np.concatenate((mInterConsumNatAux, vInterConsumTotalAux, mDemandNatAux, vFinalDemandAuxNat, vTotalDemandAuxNat), axis=1)
    # ============================================================================================
    # Calculatin A, Leontief matrix
    # ============================================================================================
    sTimeIntermediate = time.localtime()
    print(time.strftime("%d/%b/%Y - %H:%M:%S", sTimeIntermediate), " - Calculating National Analisys")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    sTimeIntermediate = time.localtime()
    print(time.strftime("%d/%b/%Y - %H:%M:%S", sTimeIntermediate), " - Calculating Shock")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    mZ= np.copy(mIntermConsumNat)
    vTotalProduction = mVANat[nLinTotalProduction,:].reshape(1,nSectors)
    mI = np.eye(nSectors)
    mA = np.zeros([nSectors, nSectors], dtype=float)
    for j in range(nSectors):
        mA[:, j] = mZ[:, j] / vTotalProduction[0, j]

    mLeontief = np.linalg.inv(mI - mA)

    # Calculando os Coeficientes para avaliação do choque -  VA/Occ/EOB/RMB/Wages
    vVBPNat = vTotalProduction[0, :]
    mResults = np.zeros([3, 6], dtype=float)
    mResultSectors=np.zeros([3, nSectors], dtype=float)
    mResultAggSectors=np.zeros([3, nGrupSectors], dtype=float)

    vVANat   = mVANat[nLinVA,:]
    vOccNat  = mVANat[nLinOccup,:]
    vEOBNat  = mVANat[nLinEOBPure,:]
    vRMBNat  = mVANat[nLinRMB,:]
    vWagesNat= mVANat[nLinWages,:]

    mResults[0, 0] =np.sum(vVBPNat)
    mResults[0, 1] =np.sum(vVANat)
    mResults[0, 2] =np.sum(vEOBNat)
    mResults[0, 3] =np.sum(vRMBNat)
    mResults[0, 4] =np.sum(vWagesNat)
    mResults[0, 5] =np.sum(vOccNat)
    mResultSectors[0,:] =np.copy(vVANat)

    vV_VANat  = vVANat / vVBPNat
    vV_OccNat = vOccNat / vVBPNat
    vV_EOBNat = vEOBNat / vVBPNat
    vV_RMBNat = vRMBNat / vVBPNat
    vV_WagesNat = vWagesNat / vVBPNat

    # Calculando o VBP Normal
    vFinalDemandNorm=np.sum(mDemandNat, axis=1)
    vVBPNorm = np.dot(mLeontief, vFinalDemandNorm)

    if (lChockOfferDemand== 0) or (lChockOfferDemand== 2):
        # Aplicando o choque da demanda
        if lRelativAbsolut:
            mDemandNatShock = mDemandNat * mDemandShock
        else:
            mDemandNatShock = mDemandNat + mDemandShock
        # Calculando o VBP do choque
        vFinalDemandShock=np.sum(mDemandNatShock, axis=1)
        vVBPShock = np.dot(mLeontief, vFinalDemandShock)

        # Calculando o impacto do choque sobre o VBP
        vDeltaShock = vVBPShock - vVBPNorm
        vImpactVBP        = vDeltaShock / vVBPNorm

    if (lChockOfferDemand== 1) or (lChockOfferDemand== 2):
        if lRelativAbsolut:
            vLaborShock = vOccNat * vLaborRestriction
        else:
            vLaborShock = vOccNat + vLaborRestriction
       # Calculando o VBP do choque
        x = vLaborShock/vVBPNat
        mABarr = np.zeros([nSectors, nSectors], dtype=float)
        mZBarr = np.zeros([nSectors, nSectors], dtype=float)
        for j in range(nSectors):
            mZBarr[:, j] = mZ[:, j] * vLaborRestriction[j]
            mABarr[:, j] = mZBarr[:, j] / vTotalProduction[0, j]

        mLeontiefBarr = np.linalg.inv(mI - mABarr)
        vVBPShock = np.dot(mLeontiefBarr, vFinalDemandNorm)

        # Calculando o impacto do choque sobre o VBP
        vDeltaShock = vVBPShock - vVBPNorm
        vImpactVBP = vDeltaShock / vVBPNorm

    if (lChockOfferDemand == 2):
        vVBPShock = np.dot(mLeontiefBarr, vFinalDemandShock)
        vDeltaShock = vVBPShock - vVBPNorm
        vImpactVBP = vDeltaShock / vVBPNorm


    # CaLculando o impacto do choque
    mResults[1, 0]   = np.sum(vDeltaShock)
    mResults[1, 1]   = np.sum(vV_VANat  * vDeltaShock)
    mResults[1, 2]   = np.sum(vV_EOBNat * vDeltaShock)
    mResults[1, 3]   = np.sum(vV_RMBNat * vDeltaShock)
    mResults[1, 4]   = np.sum(vV_WagesNat * vDeltaShock)
    mResults[1, 5]   = np.sum(vV_OccNat * vDeltaShock)

    mResults[2,:]    = mResults[1,:]  / mResults[0,:] * 100

    mResults1= np.vstack((vVBPShock, vVBPNorm, vDeltaShock, vImpactVBP)).T

    mResultSectors[1, :] = vV_VANat  * vDeltaShock
    mResultSectors[2, :] = mResultSectors[1, :] / mResultSectors[0, :] * 100

    mResultAggSectors[0,:]=SectorAgregate(vCodGrupSector, mResultSectors[0, :], nSectors, nGrupSectors)
    mResultAggSectors[1,:]=SectorAgregate(vCodGrupSector, mResultSectors[1, :], nSectors, nGrupSectors)
    mResultAggSectors[2, :] = mResultAggSectors[1, :] / mResultAggSectors[0, :] * 100

    vDataSheet = []
    vSheetName = []
    vRowsLabel = []
    vColsLabel = []
    vUseHeader = []

    vNameCols1 = ['Exportações', 'Governo', 'ISFLSF' ,'Familia', 'FCBF', 'Estoque' ]
    vDataSheet.append(mDemandShock)
    vSheetName.append("ChoqueDemanda")
    vRowsLabel.append(vNameSector)
    vColsLabel.append(vNameCols1)
    vUseHeader.append(True)

    vNameCols2 = ['Restrição Trabalho']
    vDataSheet.append(vLaborRestriction)
    vSheetName.append("Oferta")
    vRowsLabel.append(vNameSector)
    vColsLabel.append(vNameCols2)
    vUseHeader.append(True)


    vNameCols3 = ['VBP_Choque', 'VBP_Normal', 'VBP_Diferen', 'VBP_Impact']
    vDataSheet.append(mResults1)
    vSheetName.append("Impact_VBP")
    vRowsLabel.append(vNameSector)
    vColsLabel.append(vNameCols3)
    vUseHeader.append(True)

    vNameCols3a = ['VA', 'VA_Choque', 'Variação %']
    vDataSheet.append(mResultSectors.T)
    vSheetName.append("Impact_VA_Sectors")
    vRowsLabel.append(vNameSector)
    vColsLabel.append(vNameCols3a)
    vUseHeader.append(True)

    vNameCols3c = ['VA', 'VA_Choque', 'Variação %']
    vDataSheet.append(mResultAggSectors.T)
    vSheetName.append("Impact_VA_Agg_Sectors")
    vRowsLabel.append(vNameGrupSector)
    vColsLabel.append(vNameCols3c)
    vUseHeader.append(True)

    vNameCols4 = ['VBP', 'PIB', 'EOB', 'RMB', 'Salários','Ocupações']
    vNameRows =  ['MIP', 'Impactos', 'Variação %']
    vDataSheet.append(mResults)
    vSheetName.append("Impactos")
    vRowsLabel.append(vNameRows)
    vColsLabel.append(vNameCols4)
    vUseHeader.append(True)
    sFileSheet = 'Chock_Nacional_' + str(nYear) + '_' + str(nSectors) + '.xlsx'
    Support.write_data_excel(sDirectoryOutput, sFileSheet, vSheetName, vDataSheet, vRowsLabel, vColsLabel,
                             vUseHeader)
    print("Terminou ")
    sys.exit(0)

'''
    # Calculando Multiplicadores de produção
    vProductionMultiplierBarr = np.sum(mLeontiefBarr, axis=0).reshape(1,nSectors+1)
    vProductionMultiplier = np.sum(mLeontief, axis=0).reshape(1,nSectors)
    # Calculando Coeficentes, Geradores e multiplicadores v para VA, Ocupações, remunerações e salários
    tVAI = Support.Calc_MultiplierI(mVANat[nLinVA, :], nSectors, vTotalProduction, mLeontief)
    tVAII = Support.Calc_MultiplierII(tVAI[2], nSectors, mLeontiefBarr)
    vTotalProductionOccup = np.copy(vTotalProduction) * 1000000
    tOccupI = Support.Calc_MultiplierI(mVANat[nLinOccup, :], nSectors, vTotalProductionOccup, mLeontief)
    tOccupII = Support.Calc_MultiplierII(tOccupI[2], nSectors, mLeontiefBarr)
    vAux = mVANat[nLinWages, :] + mVANat[nLinEOBTotal, :]
    tRemunI = Support.Calc_MultiplierI(vAux, nSectors, vTotalProduction, mLeontief)
    tRemunII = Support.Calc_MultiplierII(tRemunI[2], nSectors, mLeontiefBarr)

    tEOBI = Support.Calc_MultiplierI(mVANat[nLinEOBPure, :], nSectors, vTotalProduction, mLeontief)
    tEOBII = Support.Calc_MultiplierII(tEOBI[2], nSectors, mLeontiefBarr)

    tSalaryI = Support.Calc_MultiplierI(mVANat[nLinWages, :], nSectors, vTotalProduction, mLeontief)
    tSalaryII = Support.Calc_MultiplierII(tSalaryI[2], nSectors, mLeontiefBarr)

    # ============================================================================================
    # writing  Multipliers
    # ============================================================================================
    if lWriteMultipliers:
        tTuplesIa = tVAI[0], tVAII[0], tOccupI[0], tOccupII[0], tRemunI[0], tRemunII[0], tEOBI[0], tEOBII[0], tSalaryI[0], tSalaryII[0]
        tTuplesIb = tVAI[1], tVAII[1], tOccupI[1], tOccupII[1], tRemunI[1], tRemunII[1], tEOBI[1], tEOBII[1], tSalaryI[1], tSalaryII[1]
        tTuplesII = tVAI[2], tOccupI[2], tRemunI[2], tEOBI[2], tSalaryI[2]
        WriteMatrix.WriteMultipliers(tTuplesIa, tTuplesIb, tTuplesII, vNameSector, sDirectoryOutput, nYear, nSectors)
    # Calculando Backwared e Forward Linkages
    nMeanL = np.mean(mLeontief)
    nMeanG = np.mean(mGhosh)
    # Calculando
    vBackLinkL= np.zeros([nSectors,1], dtype=float)
    vForwLinkL= np.zeros([nSectors,1], dtype=float)
    vBackLinkG= np.zeros([nSectors,1], dtype=float)
    vForwLinkG= np.zeros([nSectors,1], dtype=float)
    for i in range(nSectors):
        vBackLinkL [i,0] = sum(mLeontief[:,i])/ nSectors / nMeanL
        vForwLinkL [i,0] = sum(mLeontief[i,:])/ nSectors * nMeanL
        vBackLinkG [i,0] = sum(mLeontief[:,i])/ nSectors / nMeanG
        vForwLinkG [i,0] = sum(mLeontief[i,:])/ nSectors / nMeanG

'''