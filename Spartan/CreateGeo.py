# Make all numpy available via shorter 'num' prefix
import numpy as np
# Make all matlib functions accessible at the top level via M.func()
import numpy.matlib as M
# Make some matlib functions accessible directly at the top level via, e.g. rand(3,3)
from numpy.matlib import rand,zeros,ones,empty,eye

import math as m
#import subprocess
import intersectLinePlane
import intersectLineCylinder


def CreateGeo(RSMmaxsize,th_angle,ph_angle,start_phi,end_phi,det_height,det_rad,sleeve_inner_rad,sleeve_outer_rad,sleeve_height,sleeve_bottom,\
    start_cells,s_dist,Userfile,MainDir,Nodesfile,Elemfile,dir_settings,MaskMinThick,StructMesh,start_surfaces,det_mat_num,RSM_mat_num,sleeve_mat_num,air_mat_num,det_density,RSM_density,\
    sleeve_density,air_density,fout,nps):

        #%  Code to optimize the RSM geometry - Creation
        #   Created by: Dr. Darren Holland 2/13/17

    # TO DO
    #Can't have source coincident with planes (every 90 degrees) nor z axis
    #Linear/continuous surface

    s_x = s_dist * m.sin(m.radians(0 + 0.01)) * m.cos(m.radians(0 + 0.01))
    s_y = s_dist * m.sin(m.radians(0 + 0.01)) * m.sin(m.radians(0 + 0.01))
    s_z = s_dist * m.cos(m.radians(0 + 0.01))

    #%  Initialize variables and coordinates
    theta_angle = th_angle
    phi_angle = ph_angle

    edge_angle = m.degrees(m.atan(sleeve_height/sleeve_outer_rad))
    edge_dist = m.sqrt(sleeve_outer_rad ** 2 + sleeve_height ** 2)
    gap = max(np.asarray([0, edge_dist * m.cos(m.radians(edge_angle - phi_angle / 2)) - sleeve_outer_rad, edge_dist * m.sin(m.radians(edge_angle + phi_angle / 2)) - sleeve_height]))





    # For New Spartan design add 0.2 to gap to avoid overlapping elements
    gap = gap + 0.2






    RSM_outer_rad = sleeve_outer_rad + sleeve_outer_rad * (1 - m.cos(m.radians(theta_angle / 2))) + gap
    theta = np.arange(theta_angle / 2.0, 360+1, theta_angle)
    phi = np.arange(start_phi+phi_angle/2.0, end_phi, phi_angle)
    n_theta = theta.shape[0]
    n_phi = phi.shape[0]

    #Create nodal mapping
    n_mapping = np.empty((n_theta,n_phi))
    n_mapping[range(n_theta),0] = np.transpose(np.arange(1,n_theta+1) + start_cells)
    for kk in np.arange(0,n_phi-1):
        n_mapping[:, kk+1] = (n_mapping[:, kk] + n_theta)   
    m_theta = np.kron(np.ones((1,n_phi)), np.transpose(theta[np.newaxis]))
    m_phi = np.kron(np.ones((n_theta,1)), (phi[np.newaxis]))

    #%
    #Find points on the detector cylinder at each phi and theta value.
    x_c = np.zeros(n_mapping.shape)
    y_c = np.zeros(n_mapping.shape)
    z_c = np.zeros(n_mapping.shape)
    # TO DO
    #Can't have source coincident with planes (every 90 degrees) nor z axis
    #Linear/continuous surface

    x_c1 = np.zeros(n_mapping.shape)
    y_c1 = np.zeros(n_mapping.shape)
    z_c1 = np.zeros(n_mapping.shape)
    x_c2 = np.zeros(n_mapping.shape)
    y_c2 = np.zeros(n_mapping.shape)
    z_c2 = np.zeros(n_mapping.shape)
    x_c3 = np.zeros(n_mapping.shape)
    y_c3 = np.zeros(n_mapping.shape)
    z_c3 = np.zeros(n_mapping.shape)
    x_c4 = np.zeros(n_mapping.shape)
    y_c4 = np.zeros(n_mapping.shape)
    z_c4 = np.zeros(n_mapping.shape)

    p_cyl = np.asarray([0., 0., - 500., 0., 0., sleeve_height, RSM_outer_rad])
    p_plane = np.asarray([0., 0., sleeve_height + gap, 1., 0., 0., 0., 1., 0.])
    
    overlapfactor=0.0001 # Value used to avoid Geant overlapping geometry
    overlapfactorzero=0.01 # Value used to avoid Geant overlapping geometry
    
    for kk in np.arange(1,6):
        if kk == 1:
            temp_theta = m_theta - theta_angle / 2 + overlapfactor
            temp_phi = m_phi + phi_angle / 2 - overlapfactor
        if kk == 2:
            temp_theta = m_theta - theta_angle / 2 + overlapfactor
            temp_phi = m_phi - phi_angle / 2.0
            temp_phi[temp_phi > 0] = temp_phi[temp_phi > 0] + overlapfactor
            temp_phi[temp_phi == 0] = overlapfactorzero
        if kk == 3:
            temp_theta = m_theta + theta_angle / 2 - overlapfactor
            temp_phi = m_phi + phi_angle / 2 - overlapfactor
        if kk == 4:
            temp_theta = m_theta + theta_angle / 2 - overlapfactor
            temp_phi = m_phi - phi_angle / 2.0
            temp_phi[temp_phi > 0] = temp_phi[temp_phi > 0] + overlapfactor
            temp_phi[temp_phi == 0] = overlapfactorzero
        if kk == 5:
            temp_theta = m_theta
            temp_phi = m_phi

        for jj in np.arange(n_phi):
            for ii in np.arange(n_theta):
                p_line = np.asarray([0., 0., 0., m.sin(m.radians(temp_phi[ii, jj])) * m.cos(m.radians(temp_theta[ii, jj])), m.sin(m.radians(temp_phi[ii, jj])) * m.sin(m.radians(temp_theta[ii, jj])), m.cos(m.radians(temp_phi[ii, jj]))])

                if RSM_outer_rad >=  sleeve_height * m.tan(m.radians(temp_phi[ii, jj])) and temp_phi[ii, jj] < 90:
                    points = intersectLinePlane.intersectLinePlane(p_line, p_plane)
                    points = points[np.newaxis]
                else:
                    points = intersectLineCylinder.intersectLineCylinder(p_line, p_cyl)
                    if temp_phi[ii, jj] < 90:
                        pick_z = points[:, 2] >= 0
                        points = points[pick_z, :]
                    elif temp_phi[ii,jj] == 90: # Created to better handle the boundary condition at phi = 90 deg.
                        if temp_theta[ii,jj] < 90 or temp_theta[ii,jj] > 270:
                            points = points[1,:]
                            points = points[np.newaxis]
                            points[0,0] = np.absolute(points[0,0])
                        else:
                            points = points[0,:]
                            points = points[np.newaxis]
                            points[0,0] = -np.absolute(points[0,0])
                        if 0 < temp_theta[ii,jj] < 180:
                            points[0,1] = np.absolute(points[0,1])
                        else:
                            points[0,1] = -np.absolute(points[0,1])
                    else:
                        pick_z = points[:, 2] <= 0
                        #if np.sum((pick_z)) == 2:              # Not needed now with the new elif segment
                        #pick_z = np.asarray([False, True])
                        points = points[pick_z, :]           

                if kk == 1:
                    x_c1[ii, jj] = points[0,0]
                    y_c1[ii, jj] = points[0,1]
                    z_c1[ii, jj] = points[0,2]
                elif kk == 2:
                    x_c2[ii, jj] = points[0,0]
                    y_c2[ii, jj] = points[0,1]
                    z_c2[ii, jj] = points[0,2]
                elif kk == 3:
                    x_c3[ii, jj] = points[0,0]
                    y_c3[ii, jj] = points[0,1]
                    z_c3[ii, jj] = points[0,2]
                elif kk == 4:
                    x_c4[ii, jj] = points[0,0]
                    y_c4[ii, jj] = points[0,1]
                    z_c4[ii, jj] = points[0,2]
                elif kk == 5:
                    x_c[ii, jj] = points[0,0]
                    y_c[ii, jj] = points[0,1]
                    z_c[ii, jj] = points[0,2]
             
    e_vec = np.genfromtxt(Userfile, dtype='float')

    EVcoords = e_vec[:, np.arange(0,n_phi)]
    #Normalize so adding material
    
    # 0.4053 centimeters added to new Spartan mask (Calculated to match wall thickness at 1.919810 centimeters from detector center aka base of wall)
    #EVcoords = EVcoords + 0.4053
    
    EVcoords = EVcoords + MaskMinThick


    # ***************************************** MAY NEED FOR MACE DESIGN *****************************************
    # Skip first mode since it will probably look similar to constant shift
    #EVcoords=e_vec[:,0:n_phi]
    #EVcoords=EVcoords+np.absolute(EVcoords.min(0).min(0))+0.1
    #Normalize so same amount added over theta (if moves over phi, also need to
    #add normalization over phi)
    #for ii in np.arange(0,EVcoords.shape[1]):
    #    EVcoords[:, ii] = EVcoords[:, ii] / EVcoords[:, ii].max(0)
    #Scale RSM size
    #EVcoords = EVcoords / (EVcoords.max(0).max(0)) * 20.

    
    #%
    #  Convert coordinates to rectangular
    x_RSM = EVcoords * np.sin(np.radians(m_phi)) * np.cos(np.radians(m_theta))
    y_RSM = EVcoords * np.sin(np.radians(m_phi)) * np.sin(np.radians(m_theta))
    z_RSM = EVcoords * np.cos(np.radians(m_phi))

    # EVcoords=ones(size(EVcoords))+1
    xp1_RSM = EVcoords * np.sin(np.radians(m_phi + phi_angle / 2 - overlapfactor)) * np.cos(np.radians(m_theta - theta_angle / 2 + overlapfactor))
    yp1_RSM = EVcoords * np.sin(np.radians(m_phi + phi_angle / 2 - overlapfactor)) * np.sin(np.radians(m_theta - theta_angle / 2 + overlapfactor))
    zp1_RSM = EVcoords * np.cos(np.radians(m_phi + phi_angle / 2 - overlapfactor))
    xp2_RSM = EVcoords * np.sin(np.radians(m_phi - phi_angle / 2 + overlapfactor)) * np.cos(np.radians(m_theta - theta_angle / 2 + overlapfactor))
    yp2_RSM = EVcoords * np.sin(np.radians(m_phi - phi_angle / 2 + overlapfactor)) * np.sin(np.radians(m_theta - theta_angle / 2 + overlapfactor))
    zp2_RSM = EVcoords * np.cos(np.radians(m_phi - phi_angle / 2 + overlapfactor))
    xp3_RSM = EVcoords * np.sin(np.radians(m_phi + phi_angle / 2 - overlapfactor)) * np.cos(np.radians(m_theta + theta_angle / 2 - overlapfactor))
    yp3_RSM = EVcoords * np.sin(np.radians(m_phi + phi_angle / 2 - overlapfactor)) * np.sin(np.radians(m_theta + theta_angle / 2 - overlapfactor))
    zp3_RSM = EVcoords * np.cos(np.radians(m_phi + phi_angle / 2 - overlapfactor))
    xp4_RSM = EVcoords * np.sin(np.radians(m_phi - phi_angle / 2 + overlapfactor)) * np.cos(np.radians(m_theta + theta_angle / 2 - overlapfactor))
    yp4_RSM = EVcoords * np.sin(np.radians(m_phi - phi_angle / 2 + overlapfactor)) * np.sin(np.radians(m_theta + theta_angle / 2 - overlapfactor))
    zp4_RSM = EVcoords * np.cos(np.radians(m_phi - phi_angle / 2 + overlapfactor))

    RSMcoords_x = x_c + x_RSM
    RSMcoords_y = y_c + y_RSM
    RSMcoords_z = z_c + z_RSM
    RSMcoords_x1 = x_c1 + xp1_RSM
    RSMcoords_y1 = y_c1 + yp1_RSM
    RSMcoords_z1 = z_c1 + zp1_RSM
    RSMcoords_x2 = x_c2 + xp2_RSM
    RSMcoords_y2 = y_c2 + yp2_RSM
    RSMcoords_z2 = z_c2 + zp2_RSM
    RSMcoords_x3 = x_c3 + xp3_RSM
    RSMcoords_y3 = y_c3 + yp3_RSM
    RSMcoords_z3 = z_c3 + zp3_RSM
    RSMcoords_x4 = x_c4 + xp4_RSM
    RSMcoords_y4 = y_c4 + yp4_RSM
    RSMcoords_z4 = z_c4 + zp4_RSM

    maxpt = np.empty((1,4))
    maxpt[0,0] = (np.sqrt(RSMcoords_x1 ** 2 + RSMcoords_y1 ** 2 + RSMcoords_z1 ** 2)).max(0).max(0)
    maxpt[0,1] = (np.sqrt(RSMcoords_x2 ** 2 + RSMcoords_y2 ** 2 + RSMcoords_z2 ** 2)).max(0).max(0)
    maxpt[0,2] = (np.sqrt(RSMcoords_x3 ** 2 + RSMcoords_y3 ** 2 + RSMcoords_z3 ** 2)).max(0).max(0)
    maxpt[0,3] = (np.sqrt(RSMcoords_x4 ** 2 + RSMcoords_y4 ** 2 + RSMcoords_z4 ** 2)).max(0).max(0)

    
    
    
    
    
    
    
    
    if StructMesh==1:
        w_file = open(fout, 'w')
        w_file.write('Write optimization MCNP scripts for RSM\n')
        w_file.write('c RSM Cells\n')
        w_file.write('c Environment Cells\n')
        w_file.write('501 0   550 552           imp:p,n=0 $ignore p out of sphere\n')
        w_file.write('502 %u %4.6f -551       imp:p,n=1 $EJ-309 detector \n'%(det_mat_num,det_density))
        w_file.write('503 %u %4.6f -552 553 -558   imp:p,n=1 $sleeve \n'%(sleeve_mat_num,sleeve_density))
        w_file.write('504 %u %1.6f -553 551 imp:p,n=1 $air around detector an\n'%(air_mat_num,air_density))
        w_file.write('505 %u %4.6f -552 553 558   imp:p,n=1 $sleeve \n'%(sleeve_mat_num,sleeve_density))         
        
        find_theta=np.reshape(m_theta.T,(1,n_theta*n_phi))
        find_phi=np.reshape(m_phi.T,(1,n_theta*n_phi))
        ww=1
        ind_exc_all=np.logical_or(np.remainder(find_theta,90.)==0,np.remainder(find_phi,90.)==0)
        for gg in range(1,5):
            if gg==1:
                plane1=554
                plane3=556
                ind_exc=np.logical_and(ind_exc_all,np.logical_and(find_phi<=90.,np.logical_or(find_theta<=180.,find_theta>=360)))
                ind_inc=np.logical_and(find_phi<90.,find_theta<180.)
            if gg==2:
                plane1=554
                plane3=-556
                ind_exc=np.logical_and(ind_exc_all,np.logical_and(find_phi<=90.,np.logical_and(find_theta>=180.,find_theta<=360.)))
                ind_inc=np.logical_and(find_phi<90.,find_theta>180.)
            if gg==3:
                plane1=-554
                plane3=556
                ind_exc=np.logical_and(ind_exc_all,np.logical_and(find_phi>=90.,np.logical_or(find_theta<=180.,find_theta>=360)))
                ind_inc=np.logical_and(find_phi>90.,find_theta<180.)
            if gg==4:
                plane1=-554
                plane3=-556
                ind_exc=[]
                ind_inc=np.logical_and(find_phi>=90.,np.logical_and(find_theta>=180.,find_theta<=360.))
            w_file.write('%i %u %1.6f ('%(start_cells+ww,RSM_mat_num,RSM_density))
            mm=np.array([np.arange(start_surfaces,start_surfaces+n_phi*n_theta)])
            tt=np.copy(mm[ind_exc])
            mm=np.copy(mm[ind_inc])
            for jj in range(0,int(np.ceil(mm.shape[0]/8))):
                w_file.write('\n     ')
                if mm.shape[0]>8:
                    for pp in range(0,8):
                        w_file.write('-%i:'%(np.round(mm[pp])))
                    mm=np.delete(mm,range(0,8))
                else:
                    if mm.shape[0]>1:
                        for pp in range(0,mm.shape[0]-1):
                            w_file.write('-%i:'%(np.round(mm[pp])))
            w_file.write('%i)'%(-np.round(mm[-1])))
            w_file.write('     imp:p,n=1 $in RSM\n')
            aa=np.copy(ww)
            ww=ww+1
            if tt.size>0:
                rem_exc=1
                w_file.write('%i %u %1.6f ('%(start_cells+ww,RSM_mat_num,RSM_density))
                for kk in range(0,int(np.ceil(tt.shape[0]/8))):
                    w_file.write('\n     ')
                    if tt.shape[0]>8:
                        for pp in range(0,8):
                            w_file.write('-%i:'%(np.round(tt[pp])))
                        tt=np.delete(tt,range(0,8))
                    else:
                        if tt.shape[0]>1:
                            for pp in range(0,mm.shape[0]-1):
                                w_file.write('-%i:'%(np.round(tt[pp])))
                w_file.write('%i)'%(-np.round(tt[-1])))
                w_file.write('     imp:p,n=1 $Edge cells\n')
                ww=ww+1
            else:
                rem_exc=0
        
            w_file.write('%i %u %1.6f -550 552 %i %i \n     '%(start_cells+ww,air_mat_num,air_density,plane1,plane3))
            w_file.write('#%i '%(start_cells+aa))
            w_file.write(' imp:p,n=1 $in sphere, out RSM\n')
            ww=ww+1
    
        w_file.write('\nc Surfaces\n')
        w_file.write('550 so %4.6f                        $sphere around everything\n'%(s_dist+1))
        w_file.write('551 rcc 0 0 %4.6f 0 0 %4.6f %4.6f   $detector\n'%(-det_height/2,det_height,det_rad))
        w_file.write('552 rcc 0 0 %6.4f 0 0 %4.6f %4.6f   $1/8 inch sleeve outside \n'%(sleeve_height-sleeve_bottom,sleeve_bottom,sleeve_outer_rad))
        w_file.write('553 rcc 0 0 %6.4f 0 0 %4.6f %4.6f  $1/8 inch sleeve inside\n'%(sleeve_height-sleeve_bottom,sleeve_bottom,sleeve_inner_rad))
        w_file.write('554 pz 0  $ZPlane to subdivide domain due to MCNP limits\n')
        w_file.write('555 px 0  $XPlane to subdivide domain due to MCNP limits\n')
        w_file.write('556 py 0  $YPlane to subdivide domain due to MCNP limits\n')
        w_file.write('557 rcc 0 0 %4.6f 0 0 %4.6f %4.6f   $detector\n'%(-det_height/2-0.0001,det_height-0.0001,det_rad-0.0001))
        w_file.write('558 P 1 -1 0 0\n')                  # Plane to intersect the detector
    
        w_file.write('c RSM Surfaces\n')
    
        tt=1
        for jj in range(0,n_phi):
            for ii in range(0,n_theta):
                if m_phi[ii,jj]>phi_angle:   # Normal rectangular elements
                    w_file.write('%u ARB %4.7f %4.7f %4.7f %4.7f %4.7f\n     %4.7f %4.7f %4.7f %4.7f %4.7f %4.7f\n'\
                    %(start_surfaces+tt-1,RSMcoords_x1[ii,jj],RSMcoords_y1[ii,jj],RSMcoords_z1[ii,jj],\
                    RSMcoords_x2[ii,jj],RSMcoords_y2[ii,jj],RSMcoords_z2[ii,jj],\
                    RSMcoords_x3[ii,jj],RSMcoords_y3[ii,jj],RSMcoords_z3[ii,jj],\
                    RSMcoords_x4[ii,jj],RSMcoords_y4[ii,jj]))
                    w_file.write('     %4.7f %4.7f %4.7f %4.7f %4.7f %4.7f\n     %4.7f %4.7f %4.7f %4.7f %4.7f %4.7f\n     %4.7f 1243 1265 3487 1375 2486 5687\n'\
                    %(RSMcoords_z4[ii,jj],x_c1[ii,jj],y_c1[ii,jj],z_c1[ii,jj],\
                    x_c2[ii,jj],y_c2[ii,jj],z_c2[ii,jj],x_c3[ii,jj],y_c3[ii,jj],\
                    z_c3[ii,jj],x_c4[ii,jj],y_c4[ii,jj],z_c4[ii,jj]))
                else:   # Triangulars prism at phi=0
                    w_file.write('%u ARB %4.7f %4.7f %4.7f %4.7f %4.7f\n      %4.7f %4.7f %4.7f %4.7f 0 0 0 %4.7f\n'\
                    %(start_surfaces+tt-1,RSMcoords_x1[ii,jj],RSMcoords_y1[ii,jj],RSMcoords_z1[ii,jj],\
                    RSMcoords_x2[ii,jj],RSMcoords_y2[ii,jj],RSMcoords_z2[ii,jj],\
                    RSMcoords_x3[ii,jj],RSMcoords_y3[ii,jj],RSMcoords_z3[ii,jj],\
                    x_c1[ii,jj]))
                    w_file.write('     %4.7f %4.7f %4.7f %4.7f %4.7f %4.7f\n     %4.7f %4.7f 0 0 0 1230 1265 1375 2376 5670 0\n'\
                    %(y_c1[ii,jj],z_c1[ii,jj],x_c2[ii,jj],y_c2[ii,jj],z_c2[ii,jj],x_c3[ii,jj],y_c3[ii,jj],z_c3[ii,jj]))
                tt=tt+1
    
        w_file.write('\nc  DATA CARDS\n')
        w_file.write('mode n                                  $ p only\n')
        w_file.write('prdmp j 100000 2j -1                       $ dump data to runtpe earlier to avoid memory issue (seg fault) if parallel\n')
        w_file.write('nps %u                              $ number of histories\n'%(nps))
        w_file.write('c material\n')
        w_file.write('m%u 6000 -0.000124                      $ air via pnnl \n'%(air_mat_num))
        w_file.write('      7014 -0.755268                  $ 7014 for neutrons\n')
        w_file.write('      8016 -0.231781                  $ 8016 for neutrons\n')
        w_file.write('     18000 -0.012827 \n')
        w_file.write('m%u 1001 -0.543                     $EJ-309 (from https://eljentechnology.com/ there are approx 5.43xH and 4.35xC\n'%(det_mat_num)) 
        w_file.write('     6012 -0.435\n')
        w_file.write('m%u 12000 -0.015                        $ aluminum sleeve (assume 2024)\n'%(sleeve_mat_num))
        w_file.write('     13027 -0.927                   $ 13027 for neutrons\n')
        w_file.write('     14000 -0.00283\n')
        w_file.write('     22000 -0.00085\n')
        w_file.write('     24000 -0.00057\n')
        w_file.write('     25055 -0.006                   $ 25055 for neutrons \n')
        w_file.write('     26000 -0.00283\n')
        w_file.write('     29000 -0.0435\n')
        w_file.write('     30000 -0.00142\n')
        w_file.write('m%u 1001 -0.080538                  $ lucite/acrylic vi pnnl - h 1001 for ne\n'%(RSM_mat_num))
        w_file.write('     6000 -0.599848\n')
        w_file.write('     8016 -0.319614                 $ 8016 for neutrons\n')
        # w_file.write('ELPT:n j j 13.9999 9j\n')           # Kill neutrons with E < 14 MeV inside the sleeve
        w_file.write('WWE:n 1e-6 13.9999 14.1 \n')               # Weight Window Generator for neutrons above 1e-6 but below 14 MeV
        w_file.write('WWN1:n 0 0 1 0 -1 0 0 0 0 0 0 0 0 \n')    # Weight window for front scattered cell based bounds
        w_file.write('WWN2:n 0 0 1 0 -1 0 0 0 0 0 0 0 0 \n')    # Weight window for front scattered cell based bounds
        # w_file.write('WWN1:n 0 0 0 0 0 0 0 0 0 0 0 0 0 \n')   # Weight window for back scattered cell based bounds
        # w_file.write('WWN2:n 0 0 -1 0 0 0 0 0 0 0 0 0 0 \n')  # Weight window for back scattered cell based bounds


        w_file.write('c source\n')
        red_cone = np.degrees(np.arctan(((maxpt).max() + 2) / s_dist)) # Source variance reduction cone (degrees)
        w_file.write('sdef erg 14 pos %4.6f %4.6f %4.6f \n     vec %4.6f %4.6f %4.6f dir d1\n'%(s_x,s_y,s_z,-s_x,-s_y,-s_z))
        # w_file.write('sp2 -3 1.028 2.084 1\n)               $ Used U-235 as source for 14MeV neutron
        w_file.write('si1 -1 %4.6f 1\n'%(np.cos(np.radians(red_cone))))
        w_file.write('sp1 0 %4.6f %4.6f\n'%(1-(1-np.cos(np.radians(red_cone)))/2,(1-np.cos(np.radians(red_cone)))/2))
        w_file.write('sb1 0 0 1\n')
        #w_file.write('f8:p 502                                $ detector response\n')
        #w_file.write('e8 0 1e-6 0.001 0.1 599i 0.7\n')
        
        # Tally for Neutrons direct to detector (Using Energy Cut)
        # w_file.write('f2:n (551.1 551.2 551.3) \n')      # Surface tally for detector and Total flux over all surfaces
        # w_file.write('fm2:n -1 %u \n'%(det_mat_num))
        # w_file.write('e2:n 1e-6 5000ILog 14\n')
        
                                                            
        # Tally for Neutrons frontcattered to detector (Using Weight Windows)
        w_file.write('f2:n (551.1 551.2 551.3) \n')        # Surface tally for Front Scatter Neutrons
        # w_file.write('fm2:n -1 %u \n'%(det_mat_num))
        w_file.write('e2:n 1e-6 5000ILog 14\n')
        
    else:
        #   if noise == 0:
        #       with open(fout, 'w') as w_file:
                #w_file = fopen(fout, 'wt')
        #   else:
        #       with open(np.concatenate([fout[np.arange(1,end - 4)], 'noise.inp'],axis=1), 'w') as w_file:
        #w_file = fopen(np.concatenate([fout(np.arange(1,end - 4)), 'noise.inp'],axis=1), 'wt')
        #MainDir = np.asarray(MainDir)
        #print type(MainDir)
        #print MainDir.shape
    
        
        #w_file.write("*Heading\n")
        #w_file.write("** Job name: Job-1 Model name: Model-1\n")
        #w_file.write('** Generated by: Dr. Darren Holland\n')
        #w_file.write('*Preprint, echo=NO, model=NO, history=NO, contact=NO\n')
        #w_file.write('**\n** PARTS\n**\n')
        #w_file.write('*Part, name="Unstructured"\n')
        #w_file.write('*Node\n') 
        w_file = open((MainDir + Nodesfile), 'w')

        tt = 1
        n_nodes = n_theta * n_phi * 8
        NodeNums = np.zeros((n_nodes, 4))
        for ii in np.arange(0,n_theta):
            for jj in np.arange(0,n_phi):
                 NodeNums[np.arange(tt-1,tt + 7), :] = np.asarray([[tt, RSMcoords_x1[ii, jj], RSMcoords_y1[ii, jj], RSMcoords_z1[ii, jj]], \
                 [tt + 1, RSMcoords_x2[ii, jj], RSMcoords_y2[ii, jj], RSMcoords_z2[ii, jj]],\
                 [tt + 2, RSMcoords_x3[ii, jj], RSMcoords_y3[ii, jj], RSMcoords_z3[ii, jj]],\
                 [tt + 3, RSMcoords_x4[ii, jj], RSMcoords_y4[ii, jj], RSMcoords_z4[ii, jj]],\
                 [tt + 4, x_c1[ii, jj], y_c1[ii, jj], z_c1[ii, jj]],\
                 [tt + 5, x_c2[ii, jj], y_c2[ii, jj], z_c2[ii, jj]],\
                 [tt + 6, x_c3[ii, jj], y_c3[ii, jj], z_c3[ii, jj]],\
                 [tt + 7, x_c4[ii, jj], y_c4[ii, jj], z_c4[ii, jj]]])
                 w_file.write('     %u, %4.15f, %4.15f, %4.15f\n' % (tt, RSMcoords_x1[ii,jj], RSMcoords_y1[ii,jj], RSMcoords_z1[ii,jj]))
                 w_file.write('     %u, %4.15f, %4.15f, %4.15f\n' % (tt+1,RSMcoords_x2[ii,jj],RSMcoords_y2[ii,jj],RSMcoords_z2[ii,jj]))
                 w_file.write('     %u, %4.15f, %4.15f, %4.15f\n' % (tt+2,RSMcoords_x3[ii,jj],RSMcoords_y3[ii,jj],RSMcoords_z3[ii,jj]))
                 w_file.write('     %u, %4.15f, %4.15f, %4.15f\n' % (tt+3,RSMcoords_x4[ii,jj],RSMcoords_y4[ii,jj],RSMcoords_z4[ii,jj]))
                 w_file.write('     %u, %4.15f, %4.15f, %4.15f\n' % (tt+4,x_c1[ii,jj],y_c1[ii,jj],z_c1[ii,jj]))
                 w_file.write('     %u, %4.15f, %4.15f, %4.15f\n' % (tt+5,x_c2[ii,jj],y_c2[ii,jj],z_c2[ii,jj]))
                 w_file.write('     %u, %4.15f, %4.15f, %4.15f\n' % (tt+6,x_c3[ii,jj],y_c3[ii,jj],z_c3[ii,jj]))
                 w_file.write('     %u, %4.15f, %4.15f, %4.15f\n' % (tt+7,x_c4[ii,jj],y_c4[ii,jj],z_c4[ii,jj]))
                 tt = tt + 8
        w_file.close
        n_elements = n_theta * n_phi

        #test=open("test.txt",'w')
        #test.write("NodeNums\n" )
        #print NodeNums.shape
        ##test.write("%u" % (sfs))
        ##test.write("\n")
        #for jj in range(0, n_nodes):
        #    for ii in range(0,4):
        #        test.write("%.3f " % (NodeNums[jj,ii]))
        #    test.write("\n " )
        #test.close

        w_file = open((MainDir + Elemfile), 'w')
        #w_file.write( '*Element, type=C3D8\n')
        Elem = np.zeros((n_elements, 9))
        for bb in np.arange(1,n_elements+1):
        #    print [bb, 8*(bb-1)+1, 8*(bb-1)+2, 8*(bb-1)+3,8*(bb-1)+4, 8*(bb-1)+5,8*(bb-1)+6, 8*(bb-1)+7, 8*(bb-1)+8]
        #    print np.r_[[np.asarray(bb), np.arange(8*(bb-1)+1, 8*bb+1)]]
        #print np.asarray([bb+1, np.transpose(NodeNums[np.arange(8 * (bb-1) + 1,8 * bb),1])])
        #Elem[bb,:] = np.asarray([bb+1, np.transpose(NodeNums[np.arange(8 * (bb-1) + 1,8 * bb),1])])
            w_file.write('%u, %u, %u, %u, %u, %u, %u, %u, %u \n'%  (bb, NodeNums[8 * (bb - 1) ,0], NodeNums[8 * (bb - 1) + 1,0], NodeNums[8 * (bb - 1) + 3,0], NodeNums[8 * (bb - 1) + 2,0], NodeNums[8 * (bb - 1) + 4,0], NodeNums[8 * (bb - 1) + 5,0], NodeNums[8 * (bb - 1) + 7,0], NodeNums[8 * (bb - 1) + 6,0]))
        w_file.close

        red_cone = np.degrees(np.arctan(((maxpt).max() + 2) / s_dist)) # Source variance reduction cone (degrees)
        #sed_cone = 's?coneangle(17.5)?coneangle(' + str(red_cone) + ')?g'
        #subprocess.call(['sed', '-i', '-e', sed_cone, dir_settings])
        #w_file = open((MainDir + "coneangle.inp"), 'w')
        #w_file.write('%4.15f'% (red_cone))
        #w_file.close
        

