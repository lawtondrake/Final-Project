import numpy as np
import CreateGeo,sys

# Common variables to be changed for the desig
Userfile = 'EigMat.txt'
RSMmaxsize=1
delta_theta=10.
delta_phi=10.
dir_settings='Settings.cc'
Nodesfile='/nodes.inp'
Elemfile='/elem.inp'

nps=5000
StructMesh=1
MainDir='./Test'
# MUST BE LOWERCASE FOR MCNP TO CREATE UNSTRUCTURED MESH
fout=MainDir + '/mcnp.inp'
Nodesfile='/nodes.inp'

# Other geometry paramters
start_phi=0
end_phi=170
det_height=2.54
det_rad=1.27
MaskMinThick=0.81
sleeve_inner_rad=2.3496
sleeve_outer_rad=2.69875
sleeve_height=2.69875
sleeve_bottom=55
s_dist=86.36

# MCNP input variables
start_cells=700
start_surfaces=1000  # Do not use 500 to 600
RSM_mat_num=30
det_mat_num=20
sleeve_mat_num=21
air_mat_num=10
det_density=-0.959
RSM_density=-1.19
sleeve_density=-2.78
air_density=-0.001205

CreateGeo.CreateGeo(RSMmaxsize,delta_theta,delta_phi,start_phi,end_phi,det_height,det_rad,sleeve_inner_rad,sleeve_outer_rad,sleeve_height,sleeve_bottom,\
start_cells,s_dist,Userfile,MainDir,Nodesfile,Elemfile,dir_settings,MaskMinThick,StructMesh,start_surfaces,det_mat_num,RSM_mat_num,sleeve_mat_num,air_mat_num,det_density,RSM_density,\
sleeve_density,air_density,fout,nps)
