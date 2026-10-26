

import numpy as np    #np, mpl and pd serve as a nicknames
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import os
from dss import DSS
#### 3. Define the path where files are located

os.chdir('C:\\Users\\amy\\projects\\opendss\\trab' \'')   # force going to the working folder (ADJUST FOR YOUR OWN PATH!)
mydir=os.getcwd()                          # mydir stores the working path
print(mydir)  

#### 4. Initialize OpenDSS via dss-python module
dss_engine = scenarios.DSS
DSSText = dss_engine.Text                                                      
DSSCircuit = dss_engine.ActiveCircuit                                            
DSSSolution = dss_engine.ActiveCircuit.Solution                                      
ControlQueue = dss_engine.ActiveCircuit.CtrlQueue   

#### 5. Compile master_IEEE13.dss file

Note that in in the dss file (IEEE13_loads.dss) , loads are not modeled for daily simulation.
DSSText.Command = 'Compile ' + mydir + '/master_IEEE13.dss'
#### 6. List circuit elements
# Get all element names and store in variant array of strings
Elenames = DSSCircuit.AllElementNames
print('List of elements')
print ('Total:' +  str(len(Elenames)))
print(Elenames)

# Get all load names and store in variant array of strings
Loadnames = DSSCircuit.Loads.AllNames
print('List of Loads')
print ('Total:' +  str(len(Loadnames)))
print(Loadnames)

# Get all bus names and store in variant array of strings
Busnames = DSSCircuit.AllBusNames
print('List of Buses')
print ('Total:' +  str(len(Busnames)))
print(Busnames)

# Get all transformers names and store in variant array of strings
Trafonames = DSSCircuit.Transformers.AllNames
print('List of Transformers')
print ('Total:' +  str(len(Trafonames)))
print(Trafonames)

# Get all line names and store in variant array of strings
Linenames = DSSCircuit.Lines.AllNames
print('List of Lines')
print ('Total:' +  str(len(Linenames)))
print(Linenames)


#### 7. Base Case - Loads with peak value : snapshot power flow, with no PV
This scenario considers all loads with its peak value.
#Configure power flow options
DSSText.Command = 'reset'
DSSText.Command = 'set controlmode=static'
DSSText.Command = 'set mode=snapshot' 

DSSSolution.Solve()#Solve power flow


#### 7.1 Results - Base Case
#Power and Losses
kW_BC = DSSCircuit.TotalPower[0] #in kW
kvar_BC = DSSCircuit.TotalPower[1] #in kVAr
kW_Loss_BC = DSSCircuit.Losses[0]/1000 #property returns values in W, here stored in kW
kvar_Loss_BC = DSSCircuit.Losses[1]/1000 #property returns values in VAr, here stored in kVAr
print("Total kW delivered to the network: %.3f kW" %kW_BC)
print("Total kVAr delivered to the network: %.3f kvar" %kvar_BC)
print("Total active losses: %.3f kW" %kW_Loss_BC)
print("Percent losses: %.3f" %abs(((kW_Loss_BC/kW_BC)*100)) + "%")
print("Total reactive losses: %.3f kVAr" %kvar_Loss_BC)

##### Tranformer Amps loading and Line Amps loadins are <font color='red'> planning limits</font>

#Voltage
# DSSCircuit.AllNodeVmagPUByPhase: gets per unit line-ground voltage magnitudes for each Bus 
#(same order as returned by DSSCircuit.AllNodeNamesByPhase)
nodesA_filtered = []
busVpuA_BC_filtered = []
nodesB_filtered = []
busVpuB_BC_filtered = []
nodesC_filtered = []
busVpuC_BC_filtered = []

busVpuA_BC=(DSSCircuit.AllNodeVmagPUByPhase(1))#phase 1
nodesA=(DSSCircuit.AllNodeNamesByPhase(1))#phase 1
for node, voltage in zip(nodesA, busVpuA_BC):#remove voltage regulators
    if not node.startswith("reg"):
        nodesA_filtered.append(node)
        busVpuA_BC_filtered.append(voltage)
        
busVpuB_BC=(DSSCircuit.AllNodeVmagPUByPhase(2))#phase 2
nodesB=(DSSCircuit.AllNodeNamesByPhase(2))#phase 2
for node, voltage in zip(nodesB, busVpuB_BC):#remove voltage regulators
    if not node.startswith("reg"):
        nodesB_filtered.append(node)
        busVpuB_BC_filtered.append(voltage)
        
busVpuC_BC=(DSSCircuit.AllNodeVmagPUByPhase(3))#phase 3
nodesC=(DSSCircuit.AllNodeNamesByPhase(3))#phase 3
for node, voltage in zip(nodesC, busVpuC_BC):#remove voltage regulators
    if not node.startswith("reg"):
        nodesC_filtered.append(node)
        busVpuC_BC_filtered.append(voltage)

#Create figure
plt.figure(figsize=(15,4))
plt.suptitle('Voltage at each node')
         
plt.subplot(1,3,1)
plt.title('Phase 1')
plt.scatter(nodesA_filtered,busVpuA_BC_filtered)
plt.xticks(rotation=90)

plt.subplot(1,3,2)
plt.title('Phase 2')
plt.scatter(nodesB_filtered,busVpuB_BC_filtered,color='g')
plt.xticks(rotation=90)

plt.subplot(1,3,3)
plt.title('Phase 3')
plt.scatter(nodesC_filtered,busVpuC_BC_filtered, color='r')
plt.xticks(rotation=90)

plt.show()# Transformers AMPS loading 
#This function gets transformer current data:all phases current magnitude at HV(wdg1) side winding,
# all phases Amps loading at HV side 

#List of transformers (excluding the voltage regulators)
onlytrafo = [trafo for trafo in Trafonames if not trafo.startswith('reg')]

#Initialize variables
All_Wdg_Amp = np.zeros((len(onlytrafo),24))#to store all phases winding currents at HV and LV sides in complex form (24 entries for each three phase transformer)
Transf_Wdg1_Amps = np.zeros((len(onlytrafo),3))#to store all phases current magnitude at HV side winding )   
Transf_Amps_loading = np.zeros((len(onlytrafo),3))#to store all phases Amps loading at HV side 
Transf_Max_Amps_loading = np.zeros((len(onlytrafo)))#to store maximun amps loading at HV side (the maximun of the three phases)       
#------------------------------
for itrafo, trafo in enumerate(onlytrafo):
          DSSCircuit.SetActiveElement('Transformer.%s' %(trafo))
          DSSCircuit.Transformers.Name = trafo
          DSSCircuit.Transformers.Wdg = 1
          amp_rate = DSSCircuit.ActiveElement.NormalAmps#get Normal ampere rating (OpenDSS defines it for Winding 1)
          All_Wdg_Amp[itrafo,:] = DSSCircuit.Transformers.WdgCurrents#get all winding currents at HV and LV sides in complex form  
          Transf_Wdg1_Amps[itrafo,0]=(np.sqrt(All_Wdg_Amp[itrafo,0]**2+All_Wdg_Amp[itrafo,1]**2))#HV side Wdg current , phase 1
          Transf_Wdg1_Amps[itrafo,1]=(np.sqrt(All_Wdg_Amp[itrafo,8]**2+All_Wdg_Amp[itrafo,9]**2)) #HV side Wdg current , phase 2
          Transf_Wdg1_Amps[itrafo,2]=(np.sqrt(All_Wdg_Amp[itrafo,16]**2+All_Wdg_Amp[itrafo,17]**2))#HV side Wdg current , phase 3
    
          Transf_Amps_loading[itrafo,0]=Transf_Wdg1_Amps[itrafo,0]/amp_rate #HV side Wdg current loading, phase 1 
          Transf_Amps_loading[itrafo,1]=Transf_Wdg1_Amps[itrafo,1]/amp_rate #HV side Wdg current loading, phase 2
          Transf_Amps_loading[itrafo,2]=Transf_Wdg1_Amps[itrafo,2]/amp_rate #HV side Wdg current loading, phase 3

#Create figure
plt.figure(figsize=(4,2))
plt.suptitle('Transformer Amps Loading',fontsize=9)

X = range(0,len(onlytrafo))#0 1 2 3 ... len(onlytrafo)-1
X = np.array(X) 
bar_width = 0.2

plt.bar(X - bar_width,Transf_Amps_loading[:,0],width=bar_width, label='Phase 1')
plt.bar(X,Transf_Amps_loading[:,1],width=bar_width, label='Phase 2')
plt.bar(X +  bar_width,Transf_Amps_loading[:,2],width=bar_width, label='Phase 3')
plt.xticks(X, onlytrafo)
plt.ylabel("pu",fontsize="small")
plt.legend(fontsize=4)
plt.xticks(fontsize=8)
plt.yticks(fontsize=8)
plt.legend()
plt.show()



#**************--------------Lines Amps Loading
Line_Max_Amp = np.zeros((len(Linenames)))
for iline, line in enumerate(Linenames):
        DSSCircuit.SetActiveElement('line.%s' %(line))
        amp_rate = DSSCircuit.ActiveElement.NormalAmps
        Line_Max_Amp[iline] = max(DSSCircuit.ActiveElement.CurrentsMagAng[0:12:2])/amp_rate

#Creat e figure
plt.figure(figsize=(4,2))
plt.title('Lines Amps Loading (Maximun of the three phases)',fontsize=9)
plt.scatter(Linenames,Line_Max_Amp, s=10)
plt.ylabel("pu",fontsize="small")
plt.xticks(rotation=90)
plt.xticks(fontsize=8)
plt.yticks(fontsize=8)
plt.ylim(min(Line_Max_Amp)-0.5, max(Line_Max_Amp) + 0.5)
plt.show()

#Instalar pv no snapshot

#### 8. Scenario 1 - Loads with 20% of peak value : snapshot power flow, with no PV
In this scenario, the load must be adjusted to 20% of the peak load. To adjust the load for this condition, you can use the command 'set loadmult'.
#Configure power flow options
DSSText.Command = 'set loadmult = 0.2'
DSSText.Command = 'reset'
DSSText.Command = 'set controlmode=static'
DSSText.Command = 'set mode=snapshot' 

DSSSolution.Solve() #Solve power flow


DSSSolution.Solve() #Solve power flow
#### 9. Scenario 2 - Loads with 20% of peak value and PV generation

##### <font color='red'> Homework: 

<font color='red'>In this scenario, the load must be adjusted to 20% of the peak load and PV generation must be installed in Buses 633, 675 e 680. Generation will be increased gradually and the limiting metrics will be analysed. 
Limiting metrics and acceptable limits:<br>
. Overvoltage: 1,05 pu<br>
. Line Amps loading: 100% (1 pu)<br>
. Transformer Amps loading: 100% (1 pu)<br>
Run a power flow for each level of generation, starting with 50kW. Each new power flow calculation should consider the generation increased by 100 kW. The KVA parameter must be adjusted accordingly.<br><br>
Check which metric limits the penetration of the photovoltaic generation.. </font>
#Load the circuit model
DSSText.Command = 'Compile ' + mydir + '/master_IEEE13.dss'

#Get list of elements
Elenames = DSSCircuit.AllElementNames
Loadnames = DSSCircuit.Loads.AllNames
Busnames = DSSCircuit.AllBusNames
Trafonames = DSSCircuit.Transformers.AllNames
Linenames = DSSCircuit.Lines.AllNames

#Define curves fo the PV System: Temperature x Output Power(pu) and Output Power(pu) x Inversor efficiency
#(there is no irradiance curce because it won´t be a daily simulation)
DSSText.Command = 'New XYCurve.TempxP npts=4 xarray=[0 25 75 100] yarray=[1.2 1.0 0.8 0.6]'
DSSText.Command = 'New XYCurve.PxEff npts=4 xarray=[.1 .2 .4 1.0] yarray=[.86 .9 .93 1]'

#Install the PV System (no transformer will be used to connect the system to the bus)
DSSText.Command = 'New PVSystem.PV_633 phases=3 conn=wye bus=633 kV=4.16 kVA=50 Pmpp=50 temperature=25 effcurve=PxEff P-TCurve=TempxP vmaxpu=2 vminpu=0.5 pf=1'

#Configure power flow options
DSSText.Command = 'set loadmult = 0.2'
DSSText.Command = 'reset'
DSSText.Command = 'set controlmode=static'
DSSText.Command = 'set mode=snapshot' 

DSSSolution.Solve()
#### 10. Scenario 2: daily simulation, with no PV
DSSText.Command = 'Compile ' + mydir + '/master_IEEE13.dss'

Elenames = DSSCircuit.AllElementNames
Loadnames = DSSCircuit.Loads.AllNames
Busnames = DSSCircuit.AllBusNames
Trafonames = DSSCircuit.Transformers.AllNames
Linenames = DSSCircuit.Lines.AllNames

#### 10.1 Prepare the loads to perform daily simulation
ind_loads=['Load.671', 'Load.646']#list of undustrial load, all others are residential

#load the residential profile file
# Initialize an empty list to store the values
resd_profile = []
#read the file
with open(mydir + '/resd_profile.csv', 'r') as file:
    for line in file:
        # Convert each line to a float and append it to the list
        resd_profile.append(float(line.strip()))

#load the industrial profile file
# Initialize an empty list to store the values
ind_profile = []
#read the file
with open(mydir + '/ind_profile.csv', 'r') as file:
    for line in file:
        # Convert each line to a float and append it to the list
        ind_profile.append(float(line.strip()))

#Create the loadshapes objetcs
#residential
DSSCircuit.LoadShapes.New('resd_loadshape')
DSSCircuit.LoadShapes.Npts = 24
DSSCircuit.LoadShapes.HrInterval = 1
DSSCircuit.LoadShapes.Pmult = resd_profile

#industrial
DSSCircuit.LoadShapes.New('ind_loadshape')
DSSCircuit.LoadShapes.Npts = 24
DSSCircuit.LoadShapes.HrInterval = 1
DSSCircuit.LoadShapes.Pmult = ind_profile

#Assign loadshape to load
for iload, load in enumerate (Loadnames):
    DSSCircuit.SetActiveElement('load.%s' %(load))
    if load in ind_loads:#industrial
        DSSCircuit.ActiveElement.Properties('daily').Val = str('ind_loadshape')
    else:#residential
        DSSCircuit.ActiveElement.Properties('daily').Val = str('resd_loadshape')


        #### 10.2 Run power flow hour by hour while retrieving data

        #### 10.2 Run power flow hour by hour while retrieving data
        #------Results for Voltage
#get node names
nodesA=(DSSCircuit.AllNodeNamesByPhase(1))#nodes in phase 1
nodesB=(DSSCircuit.AllNodeNamesByPhase(2))#nodes in phase 2
nodesC=(DSSCircuit.AllNodeNamesByPhase(3))#nodes in phase 3

#Each dataframes will have 24 rows and a column for voltages of each node
dfbusVpuA_SC1 = pd.DataFrame(np.row_stack(busVpuA_SC1),columns=nodesA)
dfbusVpuB_SC1 = pd.DataFrame(np.row_stack(busVpuB_SC1),columns=nodesB)
dfbusVpuC_SC1 = pd.DataFrame(np.row_stack(busVpuC_SC1),columns=nodesC)

# Drop dataframe columns related to the voltage regulators
columns_to_drop = [col for col in dfbusVpuA_SC1.columns if col.startswith('reg')]
dfbusVpuA_SC1 = dfbusVpuA_SC1.drop(columns=columns_to_drop, axis=1)

columns_to_drop = [col for col in dfbusVpuB_SC1.columns if col.startswith('reg')]
dfbusVpuB_SC1 = dfbusVpuB_SC1.drop(columns=columns_to_drop, axis=1)

columns_to_drop = [col for col in dfbusVpuC_SC1.columns if col.startswith('reg')]
dfbusVpuC_SC1 = dfbusVpuC_SC1.drop(columns=columns_to_drop, axis=1)

#plots

ax = dfbusVpuA_SC1.plot(figsize=(6,3))
plt.title('Voltage at all nodes - phase 1',fontsize=9)
plt.legend(fontsize=6,loc="upper left") 
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("p.u.",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

ax = dfbusVpuB_SC1.plot(figsize=(6,3))
plt.title('Voltage at all nodes - phase 2',fontsize=9)
plt.legend(fontsize=6,loc="upper left") 
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("p.u.",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

ax = dfbusVpuC_SC1.plot(figsize=(6,3))
plt.title('Voltage at all nodes - phase 3',fontsize=9)
plt.legend(fontsize=6,loc="upper left") 
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("p.u.",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

plt.show()



#-----Results for Amps Loading at each phase in pu for each transformer
Transf_Wdg1_Amps = np.zeros((len(onlytrafo),24,3))#to store all phases current magnitude at HV side winding )   
Transf_Amps_loading = np.zeros((len(onlytrafo),24,3))#to store all phases Amps loading at HV side 
#Transf_Max_Amps_loading = np.zeros((len(onlytrafo),24))#to store maximun amps loading at HV side (the maximun of the three phases)       
#amp_rate=[0 for i in range(len(onlytrafo))]

#calculate Amps loading at each phase in pu for each transformer
for itrafo, trafo in enumerate(onlytrafo):
          DSSCircuit.SetActiveElement('Transformer.%s' %(trafo))
          amp_rate = DSSCircuit.ActiveElement.NormalAmps#get Normal ampere rating (OpenDSS defines it for Winding 1)
          Transf_Wdg1_Amps[itrafo,:,0]=(np.sqrt(All_Wdg_Amp[itrafo,:,0]**2+All_Wdg_Amp[itrafo,:,1]**2))#HV side Wdg current , phase 1
          Transf_Wdg1_Amps[itrafo,:,1]=(np.sqrt(All_Wdg_Amp[itrafo,:,8]**2+All_Wdg_Amp[itrafo,:,9]**2)) #HV side Wdg current , phase 2
          Transf_Wdg1_Amps[itrafo,:,2]=(np.sqrt(All_Wdg_Amp[itrafo,:,16]**2+All_Wdg_Amp[itrafo,:,17]**2))#HV side Wdg current , phase 3

          Transf_Amps_loading[itrafo,:,0]=Transf_Wdg1_Amps[itrafo,:,0]/amp_rate #HV side Amps loading, phase 1 
          Transf_Amps_loading[itrafo,:,1]=Transf_Wdg1_Amps[itrafo,:,1]/amp_rate #HV side Amps loading, phase 2
          Transf_Amps_loading[itrafo,:,2]=Transf_Wdg1_Amps[itrafo,:,2]/amp_rate #HV side Amps loading, phase 3

#*********For each transformer, at each hour, get the maximun loading of the three phases
Max_Transf_Amps = np.max(Transf_Amps_loading, axis=2)

#Each dataframe has 24 rows and a column for Amps loading of each transformer
dfAmpsTrafo_phA_SC1 = pd.DataFrame(np.row_stack(Transf_Amps_loading[:,:,0].T),columns=onlytrafo)
dfAmpsTrafo_phB_SC1 = pd.DataFrame(np.row_stack(Transf_Amps_loading[:,:,1].T),columns=onlytrafo)
dfAmpsTrafo_phC_SC1 = pd.DataFrame(np.row_stack(Transf_Amps_loading[:,:,2].T),columns=onlytrafo)

dfAmpsTrafo_Max_SC1 = pd.DataFrame(np.row_stack(Max_Transf_Amps[:,:].T),columns=onlytrafo)

#plots
ax = dfAmpsTrafo_phA_SC1.plot(figsize=(6,3))
plt.title('Transformer Amps Loading - phase 1',fontsize=9)
plt.legend(fontsize=6,loc="upper left") 
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("p.u.",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

ax = dfAmpsTrafo_phB_SC1.plot(figsize=(6,3))
plt.title('Transformer Amps Loading - phase 2',fontsize=9)
plt.legend(fontsize=6,loc="upper left") 
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("p.u.",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

ax = dfAmpsTrafo_phC_SC1.plot(figsize=(6,3))
plt.title('Transformer Amps Loading - phase 3',fontsize=9)
plt.legend(fontsize=6,loc="upper left") 
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("p.u.",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

ax = dfAmpsTrafo_Max_SC1.plot(figsize=(6,3))
plt.title('Transformer Maximun Amps Loading',fontsize=9)
plt.legend(fontsize=6,loc="upper left") 
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("p.u.",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

plt.show()



#display(All_Wdg_Amp[1,:,:])
#display(All_Wdg_Amp[1,:,0])
#display(Transf_Amps_loading[:,:,0])
#display((Transf_Amps_loading[:,:,1]))
#display(dfAmpsTrafo_phA_SC1)


#*******------Results for load power
#each dataframe has a column associated with each load and 24 lines
dfLoad_kW = pd.DataFrame(np.row_stack(Load_kW[:,:].T),columns=Loadnames)
dfLoad_kvar = pd.DataFrame(np.row_stack(Load_kvar[:,:].T),columns=Loadnames)

#plots
ax = dfLoad_kW.plot(figsize=(6,3))
plt.title('Load active power',fontsize=9)
plt.legend(fontsize=6,loc="upper left") 
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("kW",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

ax = dfLoad_kvar.plot(figsize=(6,3))
plt.title('Load reactive power',fontsize=9)
plt.legend(fontsize=6,loc="upper left") 
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("kvar",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)
plt.show()



#*******---------Results for the substation

#Create figure
plt.figure(figsize=(15,4))
plt.suptitle('Power at the substation')

#Active power
plt.subplot(1,3,1)
plt.plot(Total_Act_Power)
plt.title('Circuit active power',fontsize=9)
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("kW",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

#Reactive power
plt.subplot(1,3,2)
plt.plot(Total_React_Power)
plt.title('Circuit reactive power',fontsize=9)
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("kvar",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

#Losses
# Calculate the percentage of total active losses to total active power
percentage_losses = [abs(loss / power) * 100 for loss, power in zip(Total_Act_Losses, Total_Act_Power)]

plt.subplot(1,3,3)
plt.plot(percentage_losses)
plt.title('Circuit total active losses',fontsize=9)
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("%",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

plt.show()

#DSSCircuit.SetActiveElement('line.632645')
#display(DSSCircuit.ActiveElement.Name)
#display(DSSCircuit.ActiveElement.CurrentsMagAng)
#display(DSSCircuit.ActiveElement.CurrentsMagAng[0:12:2])
#display(max(DSSCircuit.ActiveElement.CurrentsMagAng[0:12:2]))


#Max_Transf_Amps = np.max(Transf_Amps_loading, axis=2)
#display(Max_Transf_Amps)
#display(Transf_Amps_loading)


#*******---------Results for Line Amps Loading

Line_Max_Loading = np.zeros((len(Linenames),24))
for iline, line in enumerate(Linenames):
    DSSCircuit.SetActiveElement('Line.%s' %(line))
    amp_rate = DSSCircuit.ActiveElement.NormalAmps
    Line_Max_Loading[iline,:] = Line_Max_Amp[iline,:]/amp_rate

dfLine_Max_Amp = pd.DataFrame(np.row_stack(Line_Max_Loading[:,:].T),columns=Linenames)

#plots
ax = dfLine_Max_Amp.plot(figsize=(6,3))
plt.title('Line Amps Loading',fontsize=9)
plt.legend(fontsize=6,loc="upper left") 
plt.yticks(fontsize=8)
plt.xlabel("hour",fontsize=8)
plt.ylabel("pu",fontsize=8)
plt.xticks([0,3,6,9,12,15,18,21,24],fontsize=8)

plt.show()