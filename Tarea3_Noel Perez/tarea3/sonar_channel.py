"""Canal acústico para el problema 1. Requiere NumPy.

Uso: from sonar_channel import sonar_channel
     received = sonar_channel(chirp, fs)
"""

import base64 as _b
import zlib as _z

_payload = (
    'c-nnZy>1&Z4Bqc42zap_!*Pse36QZbkc@$Gpd}_&prcfYI>3+9v18Fk@Qanw#df{)wj=fZk#s{0Nr1}`kAN9CcAc'
    'en$bm8S=77xP=jPy2T)}%@JawR-foFJl+-%kxxO_7h$p_;sTCn6RgR=qNhWos0AnURq8=9~abat*f1oRO0pClEt>'
    'ly?_hzp7ftSH4iRtOH!J1LV4nE;7$B%?qCkC5r~Te&15=fQ~@YFr##rap^pOb^>HdCH?h<4%7VD9h<5TTG2Om1=+'
    'Q)m)g|%;1FtlU7YgRWq=4#6s12qFSsFOQ4!?gt3s9Nn8o>sKQ%~y}VB19?Z4f=NgQ%K65Pd6bjq<1YFk9FU~GrNd'
    'cb-g(1?9qH#k-P#V!!`5epXSFS#^30fZ<6HK#e6ro5g(tF|$IjG#N{2gdxTKPhMs+TtTX5uo5f2O0^V+ytyxA)Zg'
    'i9eK<<63uM!?4zi!s4aZ`uy8=F})!}Zlt;nEw4GG0ew|kU01cbwR%zi-bCvzP+jQZwllHehWM>JpXP18r~l+_kR9'
    'AT-<;mEM!}3J;qm<NOG--Oi(>Z|INc9$'
)
exec(compile(_z.decompress(_b.b85decode(_payload)), __file__, "exec"), globals())
del _b, _z, _payload
