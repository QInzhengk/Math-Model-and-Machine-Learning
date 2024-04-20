import math
import numpy as np


def NMI(A, B):
    # 样本点数
    total = len(A)
    A_ids = set(A)
    B_ids = set(B)
    MI = 0
    eps = 1.4e-45
    acc = 0
    purity = 0
    for idA in A_ids:
        max_purity = 0.0
        for idB in B_ids:
            idAOccur = np.where(A == idA)                     # 返回下标
            idBOccur = np.where(B == idB)
            idABOccur = np.intersect1d(idAOccur, idBOccur)
            px = 1.0*len(idAOccur[0])/total
            py = 1.0*len(idBOccur[0])/total
            pxy = 1.0*len(idABOccur)/total
            MI = MI + pxy*math.log(pxy/(px*py)+eps, 2)       # 互信息计算
            if idA == idB:
                acc = acc + pxy                              # 准确度计算

            if idABOccur > max_purity:                       # 纯度计算
                purity = purity + 1.0*len(idABOccur)/total
    # 标准化互信息
    Hx = 0
    for idA in A_ids:
        idAOccurCount = 1.0*len(np.where(A == idA)[0])
        Hx = Hx - (idAOccurCount/total)*math.log(idAOccurCount/total+eps, 2)
    Hy = 0
    for idB in B_ids:
        idBOccurCount = 1.0*len(np.where(B==idB)[0])
        Hy = Hy - (idBOccurCount/total)*math.log(idBOccurCount/total+eps, 2)
    NMI = 2.0*MI/(Hx+Hy)
    return NMI, acc, purity

