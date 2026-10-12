"""Efectos de audio para el problema Pirata de Efectos. Requiere NumPy.

Interfaz:
    from efectos_fir import eco, reverberacion
    y_eco = eco(audio, fs)
    y_reverberacion = reverberacion(audio, fs)
    y_cascada = reverberacion(eco(audio, fs), fs)

Entrada: arreglo mono (muestras,) o multicanal (muestras, canales).
fs: frecuencia de muestreo en Hz. Salida: arreglo con la cola completa.
Cada llamada parte de reposo. Utilice los arreglos directamente para comparar
salidas; la escritura en PCM introduce cuantización.

También admite: python efectos_fir.py entrada.wav --salida directorio
"""

import base64 as _b
import zlib as _z

_payload = (
    'c-oy-%Wm676y579Zn+{|nvoPg0wpRC1TGpNb&WJg7luKM$e}a|Ib>(Z*mB^n>Mq;-SkF8tQkI)VjUd#_-1j~A5d^'
    '_SR#Wx;TiJ@H<g_Klzi_qUie=*aKawh*3np7mSuMZRW#?{xefvI{Oy2XqJHZvF%dWcGCUhZN#c~EAnw27FdO?4^{'
    'zzAEey5z%?2J~T)iG7ItO-gx=**a8Wiq+=#H*&P7u0OqO)ZHRJZo#67D6S>mXhQd{<TbTHh-qY+VI@6FLZqD6j3q'
    '>f?zTcRa2{$m|8bXX+9}bT~Wi@O(|C7AFpui2_b{;xMWvB71Jb}$z+oA0-?}N$92n6p4DNYqs4^q2UTx6)~cFttx'
    '0nzV>y1!Pp4GDL4=AJ{1I)Ja}D1!#WTSXMV%NsjgXv|Y^!MrZHW@H4e^B-x#r<%L`O7D=BM~TX~J~7ZFmTx$g*x6'
    '*F9IY4xOCq<Jk@UOfye#?QU;CI8Dyz=!nMBEsf%BrzC9-Tpi`VmU~XW=S9iya0{PW<O}i;tu5Rw8ReqrG^0X%Vm8'
    '_F8R?g#g@kD2sDk$nQ9}ee#ac*%k+bB?UYXw}7OL)K9_|Qi7$W1JrD~o3-X9s!GrT*e<l0A+$-J%-c*cOT6!+oD+'
    '&SJdQGy6piL6z{%211YzLX~D;N*8rc#LmZufy4NIyKiVH1x&{LatkSh44;a*f87cg2DB%3wWM;^9R0TL$<h~BWr3'
    'Yq;6Qo!&ywz*oqh#dSo(q0{xDXmCowWJPv3uC!hH#aA0`Ook6v7NQ(zR!aNGCWv9@X%ub@1%<<&8Jx=}c?93de=a'
    'C116F<t15$k=kI(G`5!WY9^#*``OkafAJW7>?$Y1~`jCJ+NuK^|{e4106laGBc*A}%R2O~!W)E8-oaHI6b90|KY<'
    'DL(jJp&ft;SG|P^UDhaDa`_kc42SjiZ_>&Fmbvd^QWz@KF4_Y_D>Mb7OjqM2HLA|IW|c7t!o<4c_#al*^zOskr1#'
    '8zt-~I)nkmJ$eGGC_*~_A=nXhfz8<&nFfy)&wmmc<_u&+Zlda?F<y@=tJ<TuU<F4wI=27WkQrhLp{6Vb63SQKr#B'
    'b?EzR}}gqD53<-+CPWRHr=2ptFCgMfICt6uXjZ*2YEo-ozTl^-)eMIOU)ngZT5MheGkBd%C!yb)K#Wo6qa*m$k9&'
    'rf9StnxQm-HCY@-b4#nc5ij>+^n->q+l5>?}LWE|3c&y$EM8`~xqy{2Gz`?!76sT1YndyPoAw`gmbF$_wpwirm+y'
    's+;TGE_Qnf}Qj-FA5U5?uaqc@YdEtl><+x{s{v_=Qrn3WGn5v3~k?@`*8<1kp}JVP?{XNeL$rQLna8tU{Y_p*QaD'
    'WKR}G2QV`!z&u@bMZr~Q7|_{sD@BJrzduG%kL}=<m<M|!$6*_x-Z1!lJR5A=jXGBl=z7oR=Vvcs)81W9xXzSVi6J'
    'jBdHC%HRm0h5XKlsq>{MN8Ujk8IN0#OnfPM(`L5PdsN?<kmYG@b9^WtFv2lDPdW2QyywVRjdB%@BzhrY?G(R_DdJ'
    'hCpG?>rra=LgujeF|G9<a(Sk7g!tC>)B28m~cSg{NQcC0^+#$c&kLqeOBR6($=eOYcuRqQZXUJKK5qoQl=&O4J>)'
    'B)}5LCSM~)%!z8dVgLIjud7Y(cG~!HHo~O*Sgn{qFK};4(W^?-ib-xUb$$>(*0@za+AT>?`*i0#SLH1)r^|&`b6D'
    'KaIKIg)uLP3jOeo!5n4b~vtruAogjD{v}aA>=(Zyi>ScO%+OWQk~E{<%RM05qxHg)#16`@zx~#e2P={|ke?O>K|!'
    'V22wIaW}a%&rP158p}IMWUIx_;g_^gOw7g=d^K)7m_0n$aqQLSh&>*(+EN`EV`>A!M#QMJuVz&3SlouUNan=@p_K'
    ')X;sNeLKhSUYF{-ua+10^=+Z6bdjEybv{a!JsjTXsC@emlKqiLk6aX3xQL=Mu_;66=#qjp8mH!0-paaZbl-(kED^'
    'WAUc;~f4Ud50*N{0ns_S{('
)
_namespace = {"__name__": "_efectos_impl", "__file__": __file__}
exec(compile(_z.decompress(_b.b85decode(_payload)), __file__, "exec"), _namespace)
eco = _namespace["eco"]
reverberacion = _namespace["reverberacion"]
__all__ = ["eco", "reverberacion"]
del _b, _z, _payload

if __name__ == "__main__":
    _namespace["main"]()
