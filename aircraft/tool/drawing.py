#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 23:22:21 2019

@author: DRUOT Thierry
         PETEILH Nicolas
         MONROLIN Nicolas
"""

import numpy as np

from scipy import interpolate

import pandas
import six
import matplotlib as mpl
import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from aircraft.tool import unit


class Drawing(object):

    def __init__(self, aircraft):
        self.aircraft = aircraft

    def payload_range(self,window_title):
        """
        Print the payload - range diagram
        """
        plot_title = self.aircraft.name

        payload = [self.aircraft.performance.mission.max_payload.payload,
                   self.aircraft.performance.mission.max_payload.payload,
                   self.aircraft.performance.mission.max_fuel.payload,
                   0.]

        range = [0.,
                 unit.NM_m(self.aircraft.performance.mission.max_payload.range),
                 unit.NM_m(self.aircraft.performance.mission.max_fuel.range),
                 unit.NM_m(self.aircraft.performance.mission.zero_payload.range)]

        nominal = [self.aircraft.performance.mission.nominal.payload,
                   unit.NM_m(self.aircraft.performance.mission.nominal.range)]

        fig,axes = plt.subplots(1,1)
        fig.canvas.set_window_title(window_title)
        fig.suptitle(plot_title, fontsize=14)

        plt.plot(range,payload,linewidth=2,color="blue")
        plt.scatter(range[1:],payload[1:],marker="+",c="orange",s=100)
        plt.scatter(nominal[1],nominal[0],marker="o",c="green",s=50)

        plt.grid(True)

        plt.ylabel('Payload (kg)')
        plt.xlabel('Range (NM)')

        plt.show()

    def view_3d(self, window_title):
        """
        Build a 3 viewx drawing of the airplane
        """
        plot_title = self.aircraft.name

        fus_width = self.aircraft.airframe.body.width
        fus_height = self.aircraft.airframe.body.height
        fus_length = self.aircraft.airframe.body.length

        htp_span = self.aircraft.airframe.horizontal_stab.span
        htp_dihedral = self.aircraft.airframe.horizontal_stab.dihedral
        htp_t_o_c = self.aircraft.airframe.horizontal_stab.toc
        htp_x_axe = self.aircraft.airframe.horizontal_stab.axe_loc[0]
        htp_z_axe = self.aircraft.airframe.horizontal_stab.axe_loc[2]
        htp_c_axe = self.aircraft.airframe.horizontal_stab.axe_c
        htp_x_tip = self.aircraft.airframe.horizontal_stab.tip_loc[0]
        htp_z_tip = self.aircraft.airframe.horizontal_stab.tip_loc[2]
        htp_c_tip = self.aircraft.airframe.horizontal_stab.tip_c

        vtp_t_o_c = self.aircraft.airframe.vertical_stab.toc
        vtp_x_root = self.aircraft.airframe.vertical_stab.root_loc[0]
        vtp_y_root = self.aircraft.airframe.vertical_stab.root_loc[1]
        vtp_z_root = self.aircraft.airframe.vertical_stab.root_loc[2]
        vtp_c_root = self.aircraft.airframe.vertical_stab.root_c
        vtp_x_tip = self.aircraft.airframe.vertical_stab.tip_loc[0]
        vtp_y_tip = self.aircraft.airframe.vertical_stab.tip_loc[1]
        vtp_z_tip = self.aircraft.airframe.vertical_stab.tip_loc[2]
        vtp_c_tip = self.aircraft.airframe.vertical_stab.tip_c

        wing_x_root = self.aircraft.airframe.wing.root_loc[0]
        wing_y_root = self.aircraft.airframe.wing.root_loc[1]
        wing_z_root = self.aircraft.airframe.wing.root_loc[2]
        wing_c_root = self.aircraft.airframe.wing.root_c
        wing_toc_r = self.aircraft.airframe.wing.root_toc
        wing_x_kink = self.aircraft.airframe.wing.kink_loc[0]
        wing_y_kink = self.aircraft.airframe.wing.kink_loc[1]
        wing_z_kink = self.aircraft.airframe.wing.kink_loc[2]
        wing_c_kink = self.aircraft.airframe.wing.kink_c
        wing_toc_k = self.aircraft.airframe.wing.kink_toc
        wing_x_tip = self.aircraft.airframe.wing.tip_loc[0]
        wing_y_tip = self.aircraft.airframe.wing.tip_loc[1]
        wing_z_tip = self.aircraft.airframe.wing.tip_loc[2]
        wing_c_tip = self.aircraft.airframe.wing.tip_c
        wing_toc_t = self.aircraft.airframe.wing.tip_toc

        if (self.aircraft.arrangement.tank_architecture in ["piggy_back", "pods"]):
            body_width = self.aircraft.airframe.tank.pod_width
            body_length = self.aircraft.airframe.tank.pod_length
            body_x_axe = self.aircraft.airframe.tank.frame_origin[0]
            body_y_axe = self.aircraft.airframe.tank.frame_origin[1]
            body_z_axe = self.aircraft.airframe.tank.frame_origin[2]
            wing_x_body = self.aircraft.airframe.tank.wing_axe_x
            wing_c_body = self.aircraft.airframe.tank.wing_axe_c

        nacelle = self.aircraft.airframe.nacelle

        nac_length = self.aircraft.airframe.nacelle.nacelle_length
        nac_height = self.aircraft.airframe.nacelle.nacelle_width
        nac_width = self.aircraft.airframe.nacelle.nacelle_width
        nac_x_ext = self.aircraft.airframe.nacelle.nacelle_loc[0]
        nac_y_ext = self.aircraft.airframe.nacelle.nacelle_loc[1]
        nac_z_ext = self.aircraft.airframe.nacelle.nacelle_loc[2]
        if (self.aircraft.arrangement.number_of_engine=="quadri"):
            nac_x_int = self.aircraft.airframe.internal_nacelle.nacelle_loc[0]
            nac_y_int = self.aircraft.airframe.internal_nacelle.nacelle_loc[1]
            nac_z_int = self.aircraft.airframe.internal_nacelle.nacelle_loc[2]

        # r_nac_length = aircraft.rear_electric_nacelle.length
        # r_nac_width = aircraft.rear_electric_nacelle.width
        # r_nac_x_axe = aircraft.rear_electric_nacelle.x_axe
        # r_nac_y_axe = aircraft.rear_electric_nacelle.y_axe
        # r_nac_z_axe = aircraft.rear_electric_nacelle.z_axe

        r_nose = 0.15       # Fuselage length ratio of nose evolutive part
        r_cone = 0.35       # Fuselage length ratio of tail cone evolutive part

        nose,nose2,nose3,cone,cone2,cyl = get_shape()

        # Fuselage shape
        #-----------------------------------------------------------------------------------------------------------
        cyl_yz = np.stack([cyl[0:,0]*fus_width , cyl[0:,1]*fus_height+0.5*fus_height , cyl[0:,2]*fus_height+0.5*fus_height], axis=1)

        fus_front = np.vstack([np.stack([cyl_yz[0:,0] , cyl_yz[0:,1]],axis=1) , np.stack([cyl_yz[::-1,0] , cyl_yz[::-1,2]],axis=1)])

        nose_xz = np.stack([nose[0:,0]*fus_length*r_nose , nose[0:,1]*fus_height , nose[0:,2]*fus_height], axis=1)
        cone_xz = np.stack([(1-r_cone)*fus_length + cone[0:,0]*fus_length*r_cone , cone[0:,1]*fus_height , cone[0:,2]*fus_height], axis=1)
        fus_xz = np.vstack([nose_xz , cone_xz])

        fus_side = np.vstack([np.stack([fus_xz[0:-2,0] , fus_xz[0:-2,1]],axis=1) , np.stack([fus_xz[:0:-1,0] , fus_xz[:0:-1,2]],axis=1)])

        nose_xy = np.stack([nose[0:,0]*fus_length*r_nose , nose[0:,3]*fus_width , nose[0:,4]*fus_width], axis=1)
        cone_xy = np.stack([(1-r_cone)*fus_length + cone[0:,0]*fus_length*r_cone , cone[0:,3]*fus_width , cone[0:,4]*fus_width], axis=1)
        fus_xy = np.vstack([nose_xy , cone_xy])

        fus_top = np.vstack([np.stack([fus_xy[1:-2,0]  , fus_xy[1:-2,1]],axis=1) , np.stack([fus_xy[:0:-1,0] , fus_xy[:0:-1,2]],axis=1)])

        # Pod body shape
        #-----------------------------------------------------------------------------------------------------------
        if (self.aircraft.arrangement.tank_architecture in ["piggy_back", "pods"]):
            body_cyl_yz = np.stack([body_y_axe + cyl[0:,0]*body_width , body_z_axe + cyl[0:,1]*body_width , body_z_axe + cyl[0:,2]*body_width], axis=1)

            body_front = np.vstack([np.stack([body_cyl_yz[0:,0] , body_cyl_yz[0:,1]],axis=1) , np.stack([body_cyl_yz[::-1,0] , body_cyl_yz[::-1,2]],axis=1)])

            body_nose_xz = np.stack([body_x_axe + nose2[0:,0]*body_length*r_nose , body_z_axe - 0.5*body_width + nose2[0:,1]*body_width , body_z_axe - 0.5*body_width + nose2[0:,2]*body_width], axis=1)
            body_cone_xz = np.stack([body_x_axe + (1-r_cone)*body_length + cone2[0:,0]*body_length*r_cone , body_z_axe - 0.5*body_width + cone2[0:,1]*body_width , body_z_axe - 0.5*body_width + cone2[0:,2]*body_width], axis=1)
            body_xz = np.vstack([body_nose_xz , body_cone_xz])

            body_side = np.vstack([np.stack([body_xz[0:-2,0] , body_xz[0:-2,1]],axis=1) , np.stack([body_xz[:0:-1,0] , body_xz[:0:-1,2]],axis=1)])

            body_nose_xy = np.stack([body_x_axe + nose2[0:,0]*body_length*r_nose , body_y_axe + nose2[0:,3]*body_width , body_y_axe + nose2[0:,4]*body_width], axis=1)
            body_cone_xy = np.stack([body_x_axe + (1-r_cone)*body_length + cone2[0:,0]*body_length*r_cone , body_y_axe + cone2[0:,3]*body_width , body_y_axe + cone2[0:,4]*body_width], axis=1)
            body_xy = np.vstack([body_nose_xy , body_cone_xy])

            body_top = np.vstack([np.stack([body_xy[1:-2,0]  , body_xy[1:-2,1]],axis=1) , np.stack([body_xy[:0:-1,0] , body_xy[:0:-1,2]],axis=1)])

        # HTP shape
        #-----------------------------------------------------------------------------------------------------------
        htp_xy = np.array([[htp_x_axe           ,  0            ],
                           [htp_x_tip           ,  0.5*htp_span ],
                           [htp_x_tip+htp_c_tip ,  0.5*htp_span ],
                           [htp_x_axe+htp_c_axe ,  0            ],
                           [htp_x_tip+htp_c_tip , -0.5*htp_span ],
                           [htp_x_tip           , -0.5*htp_span ],
                           [htp_x_axe           ,  0            ]])

        htp_xz = np.array([[htp_x_tip              , htp_z_tip                          ],
                           [htp_x_tip+0.1*htp_c_tip , htp_z_tip+0.5*htp_t_o_c*htp_c_tip ],
                           [htp_x_tip+0.7*htp_c_tip , htp_z_tip+0.5*htp_t_o_c*htp_c_tip ],
                           [htp_x_tip+htp_c_tip     , htp_z_tip                         ],
                           [htp_x_tip+0.7*htp_c_tip , htp_z_tip-0.5*htp_t_o_c*htp_c_tip ],
                           [htp_x_tip+0.1*htp_c_tip , htp_z_tip-0.5*htp_t_o_c*htp_c_tip ],
                           [htp_x_tip               , htp_z_tip                         ],
                           [htp_x_axe               , htp_z_axe                         ],
                           [htp_x_axe+0.1*htp_c_axe , htp_z_axe-0.5*htp_t_o_c*htp_c_axe ],
                           [htp_x_axe+0.7*htp_c_axe , htp_z_axe-0.5*htp_t_o_c*htp_c_axe ],
                           [htp_x_axe+htp_c_axe     , htp_z_axe                         ],
                           [htp_x_tip+htp_c_tip     , htp_z_tip                         ],
                           [htp_x_tip+0.7*htp_c_tip , htp_z_tip-0.5*htp_t_o_c*htp_c_tip ],
                           [htp_x_tip+0.1*htp_c_tip , htp_z_tip-0.5*htp_t_o_c*htp_c_tip ],
                           [htp_x_tip               , htp_z_tip                         ]])

        htp_yz = np.array([[ 0           , htp_z_axe                                                        ],
                           [ 0.5*htp_span , htp_z_axe+0.5*htp_span*np.tan(htp_dihedral)                     ],
                           [ 0.5*htp_span , htp_z_axe+0.5*htp_span*np.tan(htp_dihedral)-htp_t_o_c*htp_c_tip ],
                           [ 0            , htp_z_axe-htp_t_o_c*htp_c_axe                                   ],
                           [-0.5*htp_span , htp_z_axe+0.5*htp_span*np.tan(htp_dihedral)-htp_t_o_c*htp_c_tip ],
                           [-0.5*htp_span , htp_z_axe+0.5*htp_span*np.tan(htp_dihedral)                     ],
                           [ 0            , htp_z_axe                                                       ]])

        # VTP shape
        #-----------------------------------------------------------------------------------------------------------
        vtp_xz = np.array([[vtp_x_root            , vtp_z_root ],
                           [vtp_x_tip             , vtp_z_tip  ],
                           [vtp_x_tip+vtp_c_tip   , vtp_z_tip  ],
                           [vtp_x_root+vtp_c_root , vtp_z_root ],
                           [vtp_x_root            , vtp_z_root ]])

        vtp_xy = np.array([[vtp_x_root                , vtp_y_root                            ],
                           [vtp_x_root+0.1*vtp_c_root , vtp_y_root + 0.5*vtp_t_o_c*vtp_c_root ],
                           [vtp_x_root+0.7*vtp_c_root , vtp_y_root + 0.5*vtp_t_o_c*vtp_c_root ],
                           [vtp_x_root+vtp_c_root     , vtp_y_root                            ],
                           [vtp_x_root+0.7*vtp_c_root , vtp_y_root - 0.5*vtp_t_o_c*vtp_c_root ],
                           [vtp_x_root+0.1*vtp_c_root , vtp_y_root - 0.5*vtp_t_o_c*vtp_c_root ],
                           [vtp_x_root                , vtp_y_root                            ],
                           [vtp_x_tip                 , vtp_y_tip                             ],
                           [vtp_x_tip+0.1*vtp_c_tip   , vtp_y_tip + 0.5*vtp_t_o_c*vtp_c_tip   ],
                           [vtp_x_tip+0.7*vtp_c_tip   , vtp_y_tip + 0.5*vtp_t_o_c*vtp_c_tip   ],
                           [vtp_x_tip+vtp_c_tip       , vtp_y_tip                             ],
                           [vtp_x_tip+0.7*vtp_c_tip   , vtp_y_tip - 0.5*vtp_t_o_c*vtp_c_tip   ],
                           [vtp_x_tip+0.1*vtp_c_tip   , vtp_y_tip - 0.5*vtp_t_o_c*vtp_c_tip   ],
                           [vtp_x_tip                 , vtp_y_tip                             ]])

        vtp_yz = np.array([[vtp_y_root + 0.5*vtp_t_o_c*vtp_c_root , vtp_z_root ],
                           [vtp_y_tip + 0.5*vtp_t_o_c*vtp_c_tip   , vtp_z_tip  ],
                           [vtp_y_tip - 0.5*vtp_t_o_c*vtp_c_tip   , vtp_z_tip  ],
                           [vtp_y_root - 0.5*vtp_t_o_c*vtp_c_root , vtp_z_root ],
                           [vtp_y_root + 0.5*vtp_t_o_c*vtp_c_root , vtp_z_root ]])

        # wing_ shape
        #-----------------------------------------------------------------------------------------------------------
        wing_xy = np.array([[wing_x_root             ,  wing_y_root ],
                            [wing_x_tip              ,  wing_y_tip  ],
                            [wing_x_tip+wing_c_tip   ,  wing_y_tip  ],
                            [wing_x_kink+wing_c_kink ,  wing_y_kink ],
                            [wing_x_root+wing_c_root ,  wing_y_root ],
                            [wing_x_root+wing_c_root , -wing_y_root ],
                            [wing_x_kink+wing_c_kink , -wing_y_kink ],
                            [wing_x_tip+wing_c_tip   , -wing_y_tip  ],
                            [wing_x_tip              , -wing_y_tip  ],
                            [wing_x_root             , -wing_y_root ],
                            [wing_x_root             ,  wing_y_root ]])

        wing_yz = np.array([[ wing_y_root  , wing_z_root                        ],
                            [ wing_y_kink  , wing_z_kink                        ],
                            [ wing_y_tip   , wing_z_tip                         ],
                            [ wing_y_tip   , wing_z_tip+wing_toc_t*wing_c_tip   ],
                            [ wing_y_kink  , wing_z_kink+wing_toc_k*wing_c_kink ],
                            [ wing_y_root  , wing_z_root+wing_toc_r*wing_c_root ],
                            [-wing_y_root  , wing_z_root+wing_toc_r*wing_c_root ],
                            [-wing_y_kink  , wing_z_kink+wing_toc_k*wing_c_kink ],
                            [-wing_y_tip   , wing_z_tip+wing_toc_t*wing_c_tip   ],
                            [-wing_y_tip   , wing_z_tip                         ],
                            [-wing_y_kink  , wing_z_kink                        ],
                            [-wing_y_root  , wing_z_root                        ],
                            [ wing_y_root  , wing_z_root                        ]])

        wing_xz = np.array([[wing_x_tip                  , wing_z_tip+wing_toc_t*wing_c_tip                           ],
                            [wing_x_tip+0.1*wing_c_tip   , wing_z_tip+wing_toc_t*wing_c_tip-0.5*wing_toc_t*wing_c_tip ],
                            [wing_x_tip+0.7*wing_c_tip   , wing_z_tip+wing_toc_t*wing_c_tip-0.5*wing_toc_t*wing_c_tip ],
                            [wing_x_tip+wing_c_tip       , wing_z_tip+wing_toc_t*wing_c_tip                           ],
                            [wing_x_tip+0.7*wing_c_tip   , wing_z_tip+wing_toc_t*wing_c_tip+0.5*wing_toc_t*wing_c_tip ],
                            [wing_x_tip+0.1*wing_c_tip   , wing_z_tip+wing_toc_t*wing_c_tip+0.5*wing_toc_t*wing_c_tip ],
                            [wing_x_tip                  , wing_z_tip+wing_toc_t*wing_c_tip                           ],
                            [wing_x_kink                 , wing_z_kink+0.5*wing_toc_k*wing_c_kink                     ],
                            [wing_x_root                 , wing_z_root+0.5*wing_toc_r*wing_c_root                     ],
                            [wing_x_root+0.1*wing_c_root , wing_z_root                                                ],
                            [wing_x_root+0.7*wing_c_root , wing_z_root                                                ],
                            [wing_x_root+wing_c_root     , wing_z_root+0.5*wing_toc_r*wing_c_root                     ],
                            [wing_x_kink+wing_c_kink     , wing_z_kink+0.5*wing_toc_k*wing_c_kink                     ],
                            [wing_x_tip+wing_c_tip       , wing_z_tip+wing_toc_t*wing_c_tip                           ]])

        if (self.aircraft.arrangement.tank_architecture=="pods"):
            tip_wing_xz = np.array([[wing_x_tip                  , wing_z_tip+wing_toc_t*wing_c_tip                           ],
                                    [wing_x_tip+0.1*wing_c_tip   , wing_z_tip+wing_toc_t*wing_c_tip-0.5*wing_toc_t*wing_c_tip ],
                                    [wing_x_tip+0.7*wing_c_tip   , wing_z_tip+wing_toc_t*wing_c_tip-0.5*wing_toc_t*wing_c_tip ],
                                    [wing_x_tip+wing_c_tip       , wing_z_tip+wing_toc_t*wing_c_tip                           ],
                                    [wing_x_tip+0.7*wing_c_tip   , wing_z_tip+wing_toc_t*wing_c_tip+0.5*wing_toc_t*wing_c_tip ],
                                    [wing_x_tip+0.1*wing_c_tip   , wing_z_tip+wing_toc_t*wing_c_tip+0.5*wing_toc_t*wing_c_tip ],
                                    [wing_x_tip                  , wing_z_tip+wing_toc_t*wing_c_tip                           ],
                                    [wing_x_body                  , body_z_axe+0.5*wing_toc_k*wing_c_body                      ],
                                    [wing_x_body+wing_c_body      , body_z_axe+0.5*wing_toc_k*wing_c_body                      ],
                                    [wing_x_tip+wing_c_tip       , wing_z_tip+wing_toc_t*wing_c_tip                           ]])

        # External engine shape
        #-----------------------------------------------------------------------------------------------------------
        nac_xz_ext,nac_xy_ext,nac_yz_ext,fan_yz_ext = self.nacelle_shape(nac_x_ext,nac_y_ext,nac_z_ext,nac_width,nac_height,nac_length,cyl)

        if (self.aircraft.arrangement.number_of_engine=="quadri"):
            nac_xz_int,nac_xy_int,nac_yz_int,fan_yz_int = self.nacelle_shape(nac_x_int,nac_y_int,nac_z_int,nac_width,nac_height,nac_length,cyl)

        # Rear nacelle
        #-----------------------------------------------------------------------------------------------------------
        # if (nacelle.rear_nacelle==1):
        #     r_nac_xz = np.array([[r_nac_x_axe                 , r_nac_z_axe+0.5*fus_height+0.4*r_nac_width ],
        #                         [r_nac_x_axe+0.1*r_nac_length , r_nac_z_axe+0.5*fus_height+0.5*r_nac_width ],
        #                         [r_nac_x_axe+0.7*r_nac_length , r_nac_z_axe+0.5*fus_height+0.5*r_nac_width ],
        #                         [r_nac_x_axe+r_nac_length     , r_nac_z_axe+0.5*fus_height+0.4*r_nac_width ],
        #                         [r_nac_x_axe+r_nac_length     , r_nac_z_axe+0.5*fus_height-0.4*r_nac_width ],
        #                         [r_nac_x_axe+0.7*r_nac_length , r_nac_z_axe+0.5*fus_height-0.5*r_nac_width ],
        #                         [r_nac_x_axe+0.1*r_nac_length , r_nac_z_axe+0.5*fus_height-0.5*r_nac_width ],
        #                         [r_nac_x_axe                  , r_nac_z_axe+0.5*fus_height-0.4*r_nac_width ],
        #                         [r_nac_x_axe                  , r_nac_z_axe+0.5*fus_height+0.4*r_nac_width ]])
        #
        #     r_nac_xy = np.array([[r_nac_x_axe                 ,  0.4*r_nac_width ],
        #                         [r_nac_x_axe+0.1*r_nac_length ,  0.5*r_nac_width ],
        #                         [r_nac_x_axe+0.7*r_nac_length ,  0.5*r_nac_width ],
        #                         [r_nac_x_axe+r_nac_length     ,  0.4*r_nac_width ],
        #                         [r_nac_x_axe+r_nac_length     , -0.4*r_nac_width ],
        #                         [r_nac_x_axe+0.7*r_nac_length , -0.5*r_nac_width ],
        #                         [r_nac_x_axe+0.1*r_nac_length , -0.5*r_nac_width ],
        #                         [r_nac_x_axe                  , -0.4*r_nac_width ],
        #                         [r_nac_x_axe                  ,  0.4*r_nac_width ]])
        #
        #     r_d_nac_yz = np.stack([cyl[0:,0]*r_nac_width , cyl[0:,1]*r_nac_width , cyl[0:,2]*r_nac_width], axis=1)
        #
        #     r_d_fan_yz = np.stack([cyl[0:,0]*0.80*r_nac_width , cyl[0:,1]*0.80*r_nac_width , cyl[0:,2]*0.80*r_nac_width], axis=1)
        #
        #     r_nac_yz = np.vstack([np.stack([r_nac_y_axe+r_d_nac_yz[0:,0] , r_nac_z_axe+r_d_nac_yz[0:,1]],axis=1) ,
        #                              np.stack([r_nac_y_axe+r_d_nac_yz[::-1,0] , r_nac_z_axe+r_d_nac_yz[::-1,2]],axis=1)])
        #
        #     r_fan_yz = np.vstack([np.stack([r_nac_y_axe+r_d_fan_yz[0:,0] , r_nac_z_axe+r_d_fan_yz[0:,1]],axis=1) ,
        #                              np.stack([r_nac_y_axe+r_d_fan_yz[::-1,0] , r_nac_z_axe+r_d_fan_yz[::-1,2]],axis=1)])

        # Drawing_ box
        #-----------------------------------------------------------------------------------------------------------
        fig,axes = plt.subplots(1,1)
        fig.canvas.set_window_title(window_title)
        fig.suptitle(plot_title, fontsize=14)
        axes.set_aspect('equal', 'box')
        plt.plot(np.array([0,100,100,0,0]), np.array([0,0,100,100,0]))      # Draw a square box of 100m side

        xTopView = 50 - (self.aircraft.airframe.wing.mac_loc[0] + 0.25*self.aircraft.airframe.wing.mac)      # Top view positionning
        yTopView = 50

        xSideView = 50 - (self.aircraft.airframe.wing.mac_loc[0] + 0.25*self.aircraft.airframe.wing.mac)       # Top view positionning
        ySideView = 82

        xFrontView = 50
        yFrontView = 10

        # Draw top view
        #-----------------------------------------------------------------------------------------------------------
        if (self.aircraft.arrangement.power_architecture!="tp" or
            self.aircraft.arrangement.power_architecture!="ep1"):
            plt.plot(xTopView+nac_xy_ext[0:,0], yTopView+nac_xy_ext[0:,1], color="grey", zorder=3)        # Left nacelle top view
            plt.plot(xTopView+nac_xy_ext[0:,0], yTopView-nac_xy_ext[0:,1], color="grey", zorder=3)        # Right nacelle top view
            if (self.aircraft.arrangement.number_of_engine=="quadri"):
                plt.plot(xTopView+nac_xy_int[0:,0], yTopView+nac_xy_int[0:,1], color="grey", zorder=3)        # Left nacelle top view
                plt.plot(xTopView+nac_xy_int[0:,0], yTopView-nac_xy_int[0:,1], color="grey", zorder=3)        # Right nacelle top view
            plt.fill(xTopView+wing_xy[0:,0], yTopView+wing_xy[0:,1], color="white", zorder=4)     # wing_ top view
            plt.plot(xTopView+wing_xy[0:,0], yTopView+wing_xy[0:,1], color="grey", zorder=4)      # wing_ top view
        else:
            plt.fill(xTopView+wing_xy[0:,0], yTopView+wing_xy[0:,1], color="white", zorder=3)     # wing_ top view
            plt.plot(xTopView+wing_xy[0:,0], yTopView+wing_xy[0:,1], color="grey", zorder=3)      # wing_ top view
            plt.fill(xTopView+nac_xy_ext[0:,0], yTopView+nac_xy_ext[0:,1], color="white", zorder=4)        # Left nacelle top view
            plt.plot(xTopView+nac_xy_ext[0:,0], yTopView+nac_xy_ext[0:,1], color="grey", zorder=4)        # Left nacelle top view
            plt.fill(xTopView+nac_xy_ext[0:,0], yTopView-nac_xy_ext[0:,1], color="white", zorder=4)        # Right nacelle top view
            plt.plot(xTopView+nac_xy_ext[0:,0], yTopView-nac_xy_ext[0:,1], color="grey", zorder=4)        # Right nacelle top view

        if (self.aircraft.arrangement.tank_architecture=="pods"):
            plt.fill(xTopView+body_top[0:,0], yTopView-body_top[0:,1], color="white", zorder=5)   # Left pod top view
            plt.plot(xTopView+body_top[0:,0], yTopView-body_top[0:,1], "grey", zorder=5)          # Left pod top view
            plt.fill(xTopView+body_top[0:,0], yTopView+body_top[0:,1], color="white", zorder=5)   # Right pod top view
            plt.plot(xTopView+body_top[0:,0], yTopView+body_top[0:,1], "grey", zorder=5)          # Right pod top view

        if (self.aircraft.arrangement.stab_architecture=="classic"):
            plt.plot(xTopView+htp_xy[0:,0], yTopView+htp_xy[0:,1], "grey", zorder=1)      # htp_ top view (Classic or Vtail)

        if (self.aircraft.arrangement.wing_attachment=="low"):
            plt.fill(xTopView+fus_top[0:,0], yTopView+fus_top[0:,1], color="white", zorder=6)   # fuselage top view
            plt.plot(xTopView+fus_top[0:,0], yTopView+fus_top[0:,1], "grey", zorder=6)          # fuselage top view
        elif (self.aircraft.arrangement.wing_attachment=="high"):
            plt.fill(xTopView+fus_top[0:,0], yTopView+fus_top[0:,1], color="white", zorder=2)   # fuselage top view
            plt.plot(xTopView+fus_top[0:,0], yTopView+fus_top[0:,1], "grey", zorder=2)          # fuselage top view

        if (self.aircraft.arrangement.tank_architecture=="piggy_back"):
            plt.fill(xTopView+body_top[0:,0], yTopView-body_top[0:,1], color="white", zorder=7)   # pod top view
            plt.plot(xTopView+body_top[0:,0], yTopView-body_top[0:,1], "grey", zorder=7)          # pod top view

        if (self.aircraft.arrangement.stab_architecture=="classic"):
            plt.plot(xTopView+vtp_xy[0:,0], yTopView+vtp_xy[0:,1], "grey", zorder=8)            # vtp top view
        elif (self.aircraft.arrangement.stab_architecture=="h_tail"):
            plt.plot(xTopView+vtp_xy[0:,0], yTopView+vtp_xy[0:,1], "grey", zorder=8)            # vtp top view
            plt.plot(xTopView+vtp_xy[0:,0], yTopView-vtp_xy[0:,1], "grey", zorder=8)            # vtp top view
        else:
            raise Exception("draw_3d_view, vertical_tail.attachment value is out of range")

        if (self.aircraft.arrangement.stab_architecture=="t_tail"):
            plt.plot(xTopView+htp_xy[0:,0], yTopView+htp_xy[0:,1], "grey", zorder=9)      # htp_ top view (T-tail)

        # if (nacelle.rear_nacelle==1):
        #     plt.plot(xTopView+r_nac_xy[0:,0], yTopView+r_nac_xy[0:,1], color="grey", zorder=7)        # rear nacelle top view

        # Draw side view
        #-----------------------------------------------------------------------------------------------------------
        plt.fill(xSideView+vtp_xz[0:,0], ySideView+vtp_xz[0:,1], color="white", zorder=2)      # vtp_ side view
        plt.plot(xSideView+vtp_xz[0:,0], ySideView+vtp_xz[0:,1], color="grey", zorder=2)      # vtp_ side view

        plt.fill(xSideView+fus_side[0:,0], ySideView+fus_side[0:,1], color="white", zorder=2) # fuselage side view
        plt.plot(xSideView+fus_side[0:,0], ySideView+fus_side[0:,1], color="grey", zorder=3)  # fuselage side view

        if (self.aircraft.arrangement.tank_architecture=="piggy_back"):
            plt.fill(xSideView+body_side[0:,0], ySideView+body_side[0:,1], color="white", zorder=1)     # Pod side view
            plt.plot(xSideView+body_side[0:,0], ySideView+body_side[0:,1], color="grey", zorder=1)      # Pod side view

        # if (nacelle.rear_nacelle==1):
        #     plt.fill(xSideView+r_nac_xz[0:,0], ySideView+r_nac_xz[0:,1], color="white", zorder=4)   # rear nacelle side view
        #     plt.plot(xSideView+r_nac_xz[0:,0], ySideView+r_nac_xz[0:,1], color="grey", zorder=5)    # rear nacelle side view

        if (self.aircraft.arrangement.power_architecture=="tp" or
            self.aircraft.arrangement.power_architecture!="ep1"):
            if (self.aircraft.arrangement.number_of_engine=="quadri"):
                plt.fill(xSideView+nac_xz_int[0:,0], ySideView+nac_xz_int[0:,1], color="white", zorder=4)     # nacelle side view
                plt.plot(xSideView+nac_xz_int[0:,0], ySideView+nac_xz_int[0:,1], color="grey", zorder=4)      # nacelle side view
            plt.fill(xSideView+nac_xz_ext[0:,0], ySideView+nac_xz_ext[0:,1], color="white", zorder=5)     # nacelle side view
            plt.plot(xSideView+nac_xz_ext[0:,0], ySideView+nac_xz_ext[0:,1], color="grey", zorder=5)      # nacelle side view
            plt.fill(xSideView+wing_xz[0:,0], ySideView+wing_xz[0:,1], color="white", zorder=6)   # wing_ side view
            plt.plot(xSideView+wing_xz[0:,0], ySideView+wing_xz[0:,1], color="grey", zorder=7)    # wing_ side view
        else:
            plt.fill(xSideView+wing_xz[0:,0], ySideView+wing_xz[0:,1], color="white", zorder=4)   # wing_ side view
            plt.plot(xSideView+wing_xz[0:,0], ySideView+wing_xz[0:,1], color="grey", zorder=5)    # wing_ side view
            if (self.aircraft.arrangement.number_of_engine=="quadri"):
                plt.fill(xSideView+nac_xz_int[0:,0], ySideView+nac_xz_int[0:,1], color="white", zorder=6)     # nacelle side view
                plt.plot(xSideView+nac_xz_int[0:,0], ySideView+nac_xz_int[0:,1], color="grey", zorder=6)      # nacelle side view
            plt.fill(xSideView+nac_xz_ext[0:,0], ySideView+nac_xz_ext[0:,1], color="white", zorder=7)     # nacelle side view
            plt.plot(xSideView+nac_xz_ext[0:,0], ySideView+nac_xz_ext[0:,1], color="grey", zorder=7)      # nacelle side view

        if (self.aircraft.arrangement.tank_architecture=="pods"):
            plt.fill(xSideView+body_side[0:,0], ySideView+body_side[0:,1], color="white", zorder=8)     # Pod side view
            plt.plot(xSideView+body_side[0:,0], ySideView+body_side[0:,1], color="grey", zorder=8)      # Pod side view
            plt.fill(xSideView+tip_wing_xz[0:,0], ySideView+tip_wing_xz[0:,1], color="white", zorder=9)   # wing_ side view
            plt.plot(xSideView+tip_wing_xz[0:,0], ySideView+tip_wing_xz[0:,1], color="grey", zorder=9)    # wing_ side view

        plt.fill(xSideView+htp_xz[0:,0], ySideView+htp_xz[0:,1], color="white", zorder=4)     # htp_ side view
        plt.plot(xSideView+htp_xz[0:,0], ySideView+htp_xz[0:,1], color="grey", zorder=5)      # htp_ side view

        # Draw front view
        #-----------------------------------------------------------------------------------------------------------
        if (self.aircraft.arrangement.stab_architecture=="classic"):
            plt.plot(xFrontView-vtp_yz[0:,0], yFrontView+vtp_yz[0:,1], color="grey", zorder=1)     # vtp_ front view
        elif (self.aircraft.arrangement.stab_architecture=="h_tail"):
            plt.plot(xFrontView-vtp_yz[0:,0], yFrontView+vtp_yz[0:,1], color="grey", zorder=1)     # vtp_ front view
            plt.plot(xFrontView+vtp_yz[0:,0], yFrontView+vtp_yz[0:,1], color="grey", zorder=1)     # vtp_ front view
        else:
            raise Exception("draw_3d_view, vertical_tail.attachment value is out of range")

        plt.plot(xFrontView-htp_yz[0:,0], yFrontView+htp_yz[0:,1], color="grey", zorder=1)     # htp_ front view

        plt.plot(xFrontView-wing_yz[0:,0], yFrontView+wing_yz[0:,1], color="grey", zorder=2)   # wing_ front view

        # if (nacelle.rear_nacelle==1):
        #     plt.plot(xFrontView-r_nac_yz[0:,0], yFrontView+r_nac_yz[0:,1], color="grey", zorder=3)    # rear nacelle front view
        #     plt.plot(xFrontView-r_fan_yz[0:,0], yFrontView+r_fan_yz[0:,1], color="grey", zorder=3)    # rear inlet front view

        plt.fill(xFrontView-fus_front[0:,0], yFrontView+fus_front[0:,1], color="white", zorder=4)   # fuselage front view
        plt.plot(xFrontView-fus_front[0:,0], yFrontView+fus_front[0:,1], color="grey", zorder=5)    # fuselage front view

        plt.fill(xFrontView-nac_yz_ext[0:,0], yFrontView+nac_yz_ext[0:,1], color="white", zorder=6)   # Left nacelle front view
        plt.plot(xFrontView-nac_yz_ext[0:,0], yFrontView+nac_yz_ext[0:,1], color="grey", zorder=7)    # Left nacelle front view
        plt.plot(xFrontView-fan_yz_ext[0:,0], yFrontView+fan_yz_ext[0:,1], color="grey", zorder=8)    # Left Inlet front view
        if (self.aircraft.arrangement.number_of_engine=="quadri"):
            plt.fill(xFrontView-nac_yz_int[0:,0], yFrontView+nac_yz_int[0:,1], color="white", zorder=6)   # Left nacelle front view
            plt.plot(xFrontView-nac_yz_int[0:,0], yFrontView+nac_yz_int[0:,1], color="grey", zorder=7)    # Left nacelle front view
            plt.plot(xFrontView-fan_yz_int[0:,0], yFrontView+fan_yz_int[0:,1], color="grey", zorder=8)    # Left Inlet front view

        plt.fill(xFrontView+nac_yz_ext[0:,0], yFrontView+nac_yz_ext[0:,1], color="white", zorder=6)   # Right nacelle front view
        plt.plot(xFrontView+nac_yz_ext[0:,0], yFrontView+nac_yz_ext[0:,1], color="grey", zorder=7)    # Right nacelle front view
        plt.plot(xFrontView+fan_yz_ext[0:,0], yFrontView+fan_yz_ext[0:,1], color="grey", zorder=8)    # Right Inlet front view
        if (self.aircraft.arrangement.number_of_engine=="quadri"):
            plt.fill(xFrontView+nac_yz_int[0:,0], yFrontView+nac_yz_int[0:,1], color="white", zorder=6)   # Right nacelle front view
            plt.plot(xFrontView+nac_yz_int[0:,0], yFrontView+nac_yz_int[0:,1], color="grey", zorder=7)    # Right nacelle front view
            plt.plot(xFrontView+fan_yz_int[0:,0], yFrontView+fan_yz_int[0:,1], color="grey", zorder=8)    # Right Inlet front view

        if (self.aircraft.arrangement.tank_architecture=="pods"):
            plt.fill(xFrontView-body_front[0:,0], yFrontView+body_front[0:,1], color="white", zorder=9)   # Left pod front view
            plt.plot(xFrontView-body_front[0:,0], yFrontView+body_front[0:,1], color="grey", zorder=10)    # Left pod front view
            plt.fill(xFrontView+body_front[0:,0], yFrontView+body_front[0:,1], color="white", zorder=9)   # Right pod front view
            plt.plot(xFrontView+body_front[0:,0], yFrontView+body_front[0:,1], color="grey", zorder=10)    # Right pod front view
        elif (self.aircraft.arrangement.tank_architecture in ["pods", "piggy_back"]):
            plt.fill(xFrontView-body_front[0:,0], yFrontView+body_front[0:,1], color="white", zorder=9)   # pod front view
            plt.plot(xFrontView-body_front[0:,0], yFrontView+body_front[0:,1], color="grey", zorder=10)    # pod front view

        plt.show()
        return

    def nacelle_shape(self,nac_x,nac_y,nac_z,nac_width,nac_height,nac_length,cyl):

        nac_xz = np.array([[nac_x                , nac_z+0.4*nac_height ] ,
                           [nac_x+0.1*nac_length , nac_z+0.5*nac_height ] ,
                           [nac_x+0.5*nac_length , nac_z+0.5*nac_height ] ,
                           [nac_x+nac_length     , nac_z+0.3*nac_height ] ,
                           [nac_x+nac_length     , nac_z-0.3*nac_height ] ,
                           [nac_x+0.5*nac_length , nac_z-0.5*nac_height ] ,
                           [nac_x+0.1*nac_length , nac_z-0.5*nac_height ] ,
                           [nac_x                , nac_z-0.4*nac_height ] ,
                           [nac_x                , nac_z+0.4*nac_height ]])

        nac_xy = np.array([[nac_x                , nac_y+0.4*nac_width ] ,
                           [nac_x+0.1*nac_length , nac_y+0.5*nac_width ] ,
                           [nac_x+0.5*nac_length , nac_y+0.5*nac_width ] ,
                           [nac_x+nac_length     , nac_y+0.3*nac_width ] ,
                           [nac_x+nac_length     , nac_y-0.3*nac_width ] ,
                           [nac_x+0.5*nac_length , nac_y-0.5*nac_width ] ,
                           [nac_x+0.1*nac_length , nac_y-0.5*nac_width ] ,
                           [nac_x                , nac_y-0.4*nac_width ] ,
                           [nac_x                , nac_y+0.4*nac_width ]])

        d_nac_yz = np.stack([cyl[0:,0]*nac_width , cyl[0:,1]*nac_height , cyl[0:,2]*nac_height], axis=1)

        d_fan_yz = np.stack([cyl[0:,0]*0.80*nac_width , cyl[0:,1]*0.80*nac_height , cyl[0:,2]*0.80*nac_height], axis=1)

        nac_yz = np.vstack([np.stack([nac_y+d_nac_yz[0:,0] , nac_z+d_nac_yz[0:,1]],axis=1) ,
                               np.stack([nac_y+d_nac_yz[::-1,0] , nac_z+d_nac_yz[::-1,2]],axis=1)])

        fan_yz = np.vstack([np.stack([nac_y+d_fan_yz[0:,0] , nac_z+d_fan_yz[0:,1]],axis=1) ,
                               np.stack([nac_y+d_fan_yz[::-1,0] , nac_z+d_fan_yz[::-1,2]],axis=1)])

        return nac_xz,nac_xy,nac_yz,fan_yz


def get_shape():
    """
    Total aircraft drag with the assumption that the wing takes all the lift
    """

    nose1 = np.array([[ 0.0000 , 0.4453 , 0.4453 , 0.0000 ,  0.0000 ] ,
                      [ 0.0050 , 0.4733 , 0.4112 , 0.0335 , -0.0335 ] ,
                      [ 0.0191 , 0.5098 , 0.3833 , 0.0646 , -0.0646 ] ,
                      [ 0.0624 , 0.5718 , 0.3188 , 0.1196 , -0.1196 ] ,
                      [ 0.1355 , 0.6278 , 0.2531 , 0.1878 , -0.1878 ] ,
                      [ 0.1922 , 0.7263 , 0.2142 , 0.2297 , -0.2297 ] ,
                      [ 0.2773 , 0.8127 , 0.1631 , 0.2859 , -0.2859 ] ,
                      [ 0.4191 , 0.8906 , 0.0962 , 0.3624 , -0.3624 ] ,
                      [ 0.5610 , 0.9392 , 0.0536 , 0.4211 , -0.4211 ] ,
                      [ 0.7738 , 0.9818 , 0.0122 , 0.4761 , -0.4761 ] ,
                      [ 0.9156 , 0.9976 , 0.0025 , 0.4976 , -0.4976 ] ,
                      [ 1.0000 , 1.0000 , 0.0000 , 0.5000 , -0.5000 ]])

    nose2 = np.array([[ 0.0000 , 0.5000 ,  0.5000 , 0.0000 ,  0.0000 ] ,
                      [ 0.0050 , 0.5335 ,  0.4665 , 0.0335 , -0.0335 ] ,
                      [ 0.0191 , 0.5646 ,  0.4354 , 0.0646 , -0.0646 ] ,
                      [ 0.0624 , 0.6196 ,  0.3804 , 0.1196 , -0.1196 ] ,
                      [ 0.1355 , 0.6878 ,  0.3122 , 0.1878 , -0.1878 ] ,
                      [ 0.1922 , 0.7297 ,  0.2703 , 0.2297 , -0.2297 ] ,
                      [ 0.2773 , 0.7859 ,  0.2141 , 0.2859 , -0.2859 ] ,
                      [ 0.4191 , 0.8624 ,  0.1376 , 0.3624 , -0.3624 ] ,
                      [ 0.5610 , 0.9211 ,  0.0789 , 0.4211 , -0.4211 ] ,
                      [ 0.7738 , 0.9761 ,  0.0239 , 0.4761 , -0.4761 ] ,
                      [ 0.9156 , 0.9976 ,  0.0024 , 0.4976 , -0.4976 ] ,
                      [ 1.0000 , 1.0000 ,  0.0000 , 0.5000 , -0.5000 ]])

    nose3 = np.array([[ 0.0000 , 0.3339 , 0.3339 , 0.0000 ,  0.0000 ] ,
                      [ 0.0050 , 0.3848 , 0.3084 , 0.0335 , -0.0335 ] ,
                      [ 0.0150 , 0.4253 , 0.2881 , 0.0652 , -0.0652 ] ,
                      [ 0.0500 , 0.5033 , 0.2490 , 0.1101 , -0.1101 ] ,
                      [ 0.1000 , 0.5811 , 0.2100 , 0.1585 , -0.1585 ] ,
                      [ 0.1800 , 0.6808 , 0.1600 , 0.2215 , -0.2215 ] ,
                      [ 0.2773 , 0.7704 , 0.1151 , 0.2859 , -0.2859 ] ,
                      [ 0.4191 , 0.8562 , 0.0721 , 0.3624 , -0.3624 ] ,
                      [ 0.5610 , 0.9198 , 0.0402 , 0.4211 , -0.4211 ] ,
                      [ 0.7738 , 0.9816 , 0.0092 , 0.4761 , -0.4761 ] ,
                      [ 0.9156 , 0.9962 , 0.0019 , 0.4976 , -0.4976 ] ,
                      [ 1.0000 , 1.0000 , 0.0000 , 0.5000 , -0.5000 ]])

    cone1 = np.array([[ 0.0000 , 1.0000 , 0.0000 , 0.5000 , -0.5000 ] ,
                      [ 0.0213 , 1.0000 , 0.0082 , 0.5000 , -0.5000 ] ,
                      [ 0.0638 , 1.0000 , 0.0230 , 0.4956 , -0.4956 ] ,
                      [ 0.1064 , 1.0000 , 0.0393 , 0.4875 , -0.4875 ] ,
                      [ 0.1489 , 1.0000 , 0.0556 , 0.4794 , -0.4794 ] ,
                      [ 0.1915 , 1.0000 , 0.0786 , 0.4720 , -0.4720 ] ,
                      [ 0.2766 , 1.0000 , 0.1334 , 0.4566 , -0.4566 ] ,
                      [ 0.3617 , 1.0000 , 0.1964 , 0.4330 , -0.4330 ] ,
                      [ 0.4894 , 1.0000 , 0.3024 , 0.3822 , -0.3822 ] ,
                      [ 0.6170 , 1.0000 , 0.4159 , 0.3240 , -0.3240 ] ,
                      [ 0.7447 , 1.0000 , 0.5374 , 0.2577 , -0.2577 ] ,
                      [ 0.8723 , 1.0000 , 0.6627 , 0.1834 , -0.1834 ] ,
                      [ 0.8936 , 0.9963 , 0.6901 , 0.1679 , -0.1679 ] ,
                      [ 0.9149 , 0.9881 , 0.7139 , 0.1524 , -0.1524 ] ,
                      [ 0.9362 , 0.9800 , 0.7413 , 0.1333 , -0.1333 ] ,
                      [ 0.9574 , 0.9652 , 0.7687 , 0.1097 , -0.1097 ] ,
                      [ 0.9787 , 0.9533 , 0.8043 , 0.0788 , -0.0788 ] ,
                      [ 0.9894 , 0.9377 , 0.8280 , 0.0589 , -0.0589 ] ,
                      [ 1.0000 , 0.9103 , 0.8784 , 0.0162 , -0.0162 ]])

    cone2 = np.array([[ 0.0000 , 1.0000 , 0.0000 , 0.5000 , -0.5000 ] ,
                      [ 0.0213 , 1.0000 , 0.0000 , 0.5000 , -0.5000 ] ,
                      [ 0.0638 , 0.9956 , 0.0044 , 0.4956 , -0.4956 ] ,
                      [ 0.1064 , 0.9875 , 0.0125 , 0.4875 , -0.4875 ] ,
                      [ 0.1489 , 0.9794 , 0.0206 , 0.4794 , -0.4794 ] ,
                      [ 0.1915 , 0.9720 , 0.0280 , 0.4720 , -0.4720 ] ,
                      [ 0.2766 , 0.9566 , 0.0434 , 0.4566 , -0.4566 ] ,
                      [ 0.3617 , 0.9330 , 0.0670 , 0.4330 , -0.4330 ] ,
                      [ 0.4894 , 0.8822 , 0.1178 , 0.3822 , -0.3822 ] ,
                      [ 0.6170 , 0.8240 , 0.1760 , 0.3240 , -0.3240 ] ,
                      [ 0.7447 , 0.7577 , 0.2423 , 0.2577 , -0.2577 ] ,
                      [ 0.8723 , 0.6834 , 0.3166 , 0.1834 , -0.1834 ] ,
                      [ 0.8936 , 0.6679 , 0.3321 , 0.1679 , -0.1679 ] ,
                      [ 0.9149 , 0.6524 , 0.3476 , 0.1524 , -0.1524 ] ,
                      [ 0.9362 , 0.6333 , 0.3667 , 0.1333 , -0.1333 ] ,
                      [ 0.9574 , 0.6097 , 0.3903 , 0.1097 , -0.1097 ] ,
                      [ 0.9787 , 0.5788 , 0.4212 , 0.0788 , -0.0788 ] ,
                      [ 0.9894 , 0.5589 , 0.4411 , 0.0589 , -0.0589 ] ,
                      [ 1.0000 , 0.5162 , 0.4838 , 0.0162 , -0.0162 ]])

    cyl = np.array([[  0.5000000 , 0.0000000 ,  0.0000000 ] ,
                    [  0.4903926 , 0.0975452 , -0.0975452 ] ,
                    [  0.4619398 , 0.1913417 , -0.1913417 ] ,
                    [  0.4157348 , 0.2777851 , -0.2777851 ] ,
                    [  0.3535534 , 0.3535534 , -0.3535534 ] ,
                    [  0.2777851 , 0.4157348 , -0.4157348 ] ,
                    [  0.1913417 , 0.4619398 , -0.4619398 ] ,
                    [  0.0975452 , 0.4903926 , -0.4903926 ] ,
                    [  0.0000000 , 0.5000000 , -0.5000000 ] ,
                    [- 0.0975452 , 0.4903926 , -0.4903926 ] ,
                    [- 0.1913417 , 0.4619398 , -0.4619398 ] ,
                    [- 0.2777851 , 0.4157348 , -0.4157348 ] ,
                    [- 0.3535534 , 0.3535534 , -0.3535534 ] ,
                    [- 0.4157348 , 0.2777851 , -0.2777851 ] ,
                    [- 0.4619398 , 0.1913417 , -0.1913417 ] ,
                    [- 0.4903926 , 0.0975452 , -0.0975452 ] ,
                    [- 0.5000000 , 0.0000000 ,  0.0000000 ]])

    return nose1,nose2,nose3,cone1,cone2,cyl


def draw_design_space(file, mark, field, const, color, limit, bound):
    # Read information
    #------------------------------------------------------------------------------------------------------
    #dat = numpy.genfromtxt(file,delimiter = ";")
    data_frame = pandas.read_csv(file, delimiter = ";",skipinitialspace=True, header=None)

    # Create figure
    #------------------------------------------------------------------------------------------------------
    name = [el.strip() for el in data_frame[0]]     # Remove blanks
    uni_ = [el.strip() for el in data_frame[1]]     # Remove blanks
    data = data_frame.iloc[:,2:].values             # Extract matrix of data

    abs = list(set(data[0,:]))
    abs.sort()
    nx = len(abs)

    ord = list(set(data[1,:]))
    ord.sort()
    ny = len(ord)

    dat = {}
    for j in range(2,len(data)):
       dat[name[j]] = data[j,:]

    uni = {}
    for j in range(2,len(data)):
       uni[name[j]] = uni_[j]

    res = []
    res.append(unit.convert_to(uni_[0],mark[0]))
    res.append(unit.convert_to(uni_[1],mark[1]))

    mpl.rcParams['hatch.linewidth'] = 0.3

    fig, axs = plt.subplots(figsize=(7,7))
    gs = mpl.gridspec.GridSpec(2,1, height_ratios=[3,1])

    F = {}
    typ = 'cubic'

    axe = plt.subplot(gs[0])
    X, Y = np.meshgrid(abs, ord)
    Z = dat[field].reshape(ny,nx)
    F[field] = interpolate.interp2d(X, Y, Z, kind=typ)
    ctf = axe.contourf(X, Y, Z, cmap=mpl.cm.Greens, levels=100)
    axins = inset_axes(axe,
                       width="5%",  # width = 5% of parent_bbox width
                       height="60%",  # height : 50%
                       loc='upper left',
                       bbox_to_anchor=(1.03, 0., 1, 1),
                       bbox_transform=axe.transAxes,
                       borderpad=0,
                       )
    plt.colorbar(ctf,cax=axins)
    axe.set_title("Criterion : "+field+" ("+uni[field]+")")
    axe.set_xlabel(name[0]+" ("+uni_[0]+")")
    axe.set_ylabel(name[1]+" ("+uni_[1]+")")

    axe.plot(res[0],res[1],'ok',ms='10',mfc='none')             # Draw solution point
    marker, = axe.plot(res[0],res[1],'+k',ms='10',mfc='none')     # Draw plot marker

    bnd = [{"ub":1.e10,"lb":-1.e10}.get(s) for s in bound]

    ctr = []
    hdl = []
    for j in range(0,len(const),1):
        Z = dat[const[j]].reshape(ny,nx)
        F[const[j]] = interpolate.interp2d(X, Y, Z, kind=typ)
        ctr.append(axe.contour(X, Y, Z, levels=[limit[j]], colors=color[j]))
        levels = [limit[j],bnd[j]]
        levels.sort()
        axe.contourf(X, Y, Z, levels=levels,alpha=0.,hatches=['/'])
        h,_ = ctr[j].legend_elements()
        hdl.append(h[0])

    handle = [hl for hl in hdl]

    axe.legend(handle,const, loc = "lower left", bbox_to_anchor=(1.02, 0.))

    # Set introspection
    #------------------------------------------------------------------------------------------------------
    axe =  plt.subplot(gs[1])
    axe.axis('off')
    val1 = [["%6.0f"%12000., uni_[0]], ["%5.2f"%135.4, uni_[1]], ["%6.0f"%70000., uni[field]]]
    rowlabel=(name[0], name[1], field)

    the_table = axe.table(cellText=val1,rowLabels=rowlabel, rowLoc='right', cellLoc='left', bbox=[0.18,0.25,0.4,0.6])
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(10)

    for k,cell in six.iteritems(the_table._cells):
        cell.set_edgecolor("silver")

    cst_uni = [uni[c] for c in const]

    val2 = np.random.random(len(const))*100.
    val2 = ["%8.1f" %v for v in val2]
    val2 = list(map(list, zip(*[val2,cst_uni])))

    the_table2 = axe.table(cellText=val2,rowLabels=const, rowLoc='right', cellLoc='left', bbox=[0.85,0.,0.4,1.])
    the_table2.auto_set_font_size(False)
    the_table2.set_fontsize(10)

    for k,cell in six.iteritems(the_table2._cells):
        cell.set_edgecolor("silver")

    the_table[0,0].get_text().set_text("%6.0f" %res[0])
    the_table[1,0].get_text().set_text("%5.2f" %res[1])
    the_table[2,0].get_text().set_text("%6.0f" %F[field](res[0],res[1]))
    for j in range(len(const)):
        the_table2[j,0].get_text().set_text("%8.1f" %F[const[j]](res[0],res[1]))


    def onclick(event):
    #    global ix, iy
        try:
            ix, iy = event.xdata, event.ydata
            the_table[0,0].get_text().set_text("%6.0f" %ix)
            the_table[1,0].get_text().set_text("%5.2f" %iy)
            the_table[2,0].get_text().set_text("%6.0f" %F[field](ix,iy))
            for j in range(len(const)):
                the_table2[j,0].get_text().set_text("%8.1f" %F[const[j]](ix,iy))
            marker.set_xdata(ix)
            marker.set_ydata(iy)
            plt.draw()
        except TypeError:
            no_op = 0

    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    # Pack and draw
    #------------------------------------------------------------------------------------------------------
    plt.tight_layout()
    plt.show()

