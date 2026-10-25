37 bus entao 20% eh 7.4 entao 8 buses pra colocar pv (pelo menos 20%)
aleatorio 

pv1 742.1.2.3
pv2 725.1.2.3
pv3 722.1.2.3
pv4 741.1.2.3
pv5 735.1.2.3
pv6 729.1.2.3
pv7 736.1.2.3
pv8 718.1.2.3

 escolhenod elas carga 


 728.1.2.3 kv=4.8 irrad=.98 pmpp=310 kva=350 temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=Effic P-tcurve=PvsT Daily=Irrad Tdaily=Temp
733.1.2.3
737.1.2.3
740.1.2.3
718.1.2.3
720.1.2.3
722.1.2.3
742.1.2.3
pv total dimensionado pra demanda de pico

caso 1 sem pv sem storage loadmult 1

ja tem ovlerlado no tranformador subxf  de 122%  e teve uder voltage de 0.87 na barra 799 , pelado e ja deu ruim

caso 2 sem pv sem storage loadmult 0.2

eh matou o overload ne, se nao matasse tbm era pra jogar no lixo, sem under e overvoltage 


caso 3 com pv sem storage loadmult 1


caso 4 com pv sem storage loadmult 0.2
caso 5 com pv com storage loadmult 1 (talvez 0.2, eh la que sobra energia)
  5a storage central
  5b storage distribuido
caso 6 com pv com storage ilhamento

metricas: sobretensao, sobrecarga linhas e trafos, fluxo reverso, perdas

caso 3 sem violacao: aumenta o pv aos poucos e anota onde estoura
parte 2: geracao mais alta de proposito pra precisar do storage
parte 3: tempo de sobrevivencia da ilha + metodologia de corte de carga

entrega: notebook + zip + slides 20 min