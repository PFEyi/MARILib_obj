#!/usr/bin/env python3
"""
Created on Thu Jan 20 20:20:20 2020

@author: DRUOT Thierry, Nicolas Monrolin
"""


import numpy as np

from aircraft.tool import unit
import earth

from engine.ExergeticEngine import ExergeticEngine, Turbofan

from aircraft.airframe.component import Component, Inboard_wing_mounted_nacelle, Outboard_wing_mounted_nacelle


class Exergetic_tf_nacelle(Component):

    def __init__(self, aircraft):
        super(Exergetic_tf_nacelle, self).__init__(aircraft)

        ne = self.aircraft.arrangement.number_of_engine
        n_pax_ref = self.aircraft.requirement.n_pax_ref
        design_range = self.aircraft.requirement.design_range

        self.n_engine = {"twin":2, "quadri":4}.get(ne, "number of engine is unknown")
        self.cruise_thrust = self.__cruise_thrust__()
        self.reference_thrust = (1.e5 + 177.*n_pax_ref*design_range*1.e-6)/self.n_engine
        self.reference_offtake = 0.
        self.reference_wBleed = 0.
        self.rating_factor = {"MTO":1.00, "MCN":0.95, "MCL":0.92, "MCR":0.90, "FID":0.25}
        self.engine_bpr = self.__turbofan_bpr__()
        self.engine_fpr = 1.2
        self.engine_lpc_pr = 3.0
        self.engine_hpc_pr = 14.2
        self.engine_T4max = 1700.
        self.cooling_flow = 0.1

        self.TF_model = Turbofan()

        self.width = None
        self.length = None

        self.frame_origin = np.full(3,None)

    def __turbofan_bpr__(self):
        n_pax_ref = self.aircraft.requirement.n_pax_ref
        if (80<n_pax_ref):
            bpr = 9.
        else:
            bpr = 5.
        return bpr

    def __cruise_thrust__(self):
        g = earth.gravity()
        mass = 20500. + 67.e-6*self.aircraft.requirement.n_pax_ref*self.aircraft.requirement.design_range
        lod = 18.
        fn =(mass*g/lod)/self.n_engine
        return fn

    def eval_geometry(self):

        disa = self.aircraft.requirement.cruise_disa
        altp = self.aircraft.requirement.cruise_altp
        mach = self.aircraft.requirement.cruise_mach

        pamb,tamb,tstd,dtodz = earth.atmosphere(altp,disa)

        # Set the flight conditions as static temperature, static pressure and Mach number
        self.TF_model.set_flight(tamb,pamb,mach)

        # Set the losses for all components
        self.TF_model.ex_loss = {"inlet": 0., "LPC": 0.132764781, "HPC": 0.100735895, "Burner": 0.010989737,
                                 "HPT": 0.078125215, "LPT": 0.104386722, "Fan": 0.074168491, "SE": 0.0, "PE": 0.}
        self.TF_model.ex_loss["inlet"] = self.TF_model.from_PR_loss_to_Ex_loss(0.9985)
        tau_f, self.TF_model.ex_loss["Fan"] = self.TF_model.from_PR_to_tau_pol(1.166, 0.93689)
        tau_l, self.TF_model.ex_loss["LPC"] = self.TF_model.from_PR_to_tau_pol(3.12, 0.89)
        tau_h, self.TF_model.ex_loss["HPC"] = self.TF_model.from_PR_to_tau_pol(14.22820513, 0.89)
        self.TF_model.ex_loss["SE"] = self.TF_model.from_PR_loss_to_Ex_loss(0.992419452)

        self.TF_model.cooling_flow = self.cooling_flow

        # Design for a given thrust (Newton), BPR, FPR, LPC PR, HPC PR, T41 (Kelvin)
        s, c, p = self.TF_model.design(self.cruise_thrust,
                                       self.engine_bpr,
                                       self.engine_fpr,
                                       self.engine_lpc_pr,
                                       self.engine_hpc_pr,
                                       Ttmax = self.engine_T4max * self.rating_factor["MCR"],
                                       HPX = self.reference_offtake,
                                       wBleed = self.reference_wBleed)

        # info : reference_thrust is defined by thrust(mach=0.25, altp=0, disa=15) / 0.80
        disa = 15.
        altp = 0.
        mach = 0.25

        pamb,tamb,tstd,dtodz = earth.atmosphere(altp,disa)

        # Off design at take off
        self.TF_model.set_flight(tamb, pamb, mach)
        Ttmax = self.engine_T4max * self.rating_factor["MTO"]
        x0 = self.TF_model.magic_guess()
        s, c, p = self.TF_model.off_design(Ttmax=Ttmax, guess=x0)

        self.reference_thrust = p['Fnet']

        self.width = 0.5*self.engine_bpr**0.7 + 5.E-6*self.reference_thrust
        self.length = 0.86*self.width + self.engine_bpr**0.37      # statistical regression

        knac = np.pi * self.width * self.length
        self.gross_wet_area = knac*(1.48 - 0.0076*knac)*2.       # statistical regression, two engines
        self.net_wet_area = self.gross_wet_area
        self.aero_length = self.length
        self.form_factor = 1.15

        self.frame_origin = self.__locate_nacelle__()

    def eval_mass(self):
        self.mass = (1250. + 0.021*self.reference_thrust)*2.       # statistical regression, two engines
        self.cg = self.frame_origin + 0.7 * np.array([self.length, 0., 0.])      # statistical regression

    def unitary_thrust(self,pamb,tamb,mach,rating,throttle=1.,pw_offtake=0.):
        """Unitary thrust of a pure turbofan engine (semi-empirical model)
        Thrust is defined by flying conditions and rating, throttle may be used to modulate max thrust but should be avoided if possible
        Note that throttle is used here to drive T4 which is not the usual way of working as throttle, normally, drives N1
        """
        self.TF_model.set_flight(tamb, pamb, mach)
        kthrttl = throttle + self.rating_factor["FID"]*(1.-throttle)
        T4 = self.engine_T4max * self.rating_factor[rating] * kthrttl
        x0 = self.TF_model.magic_guess()

        s, c, p = self.TF_model.off_design(Ttmax=T4, guess=x0, HPX=pw_offtake)

        total_thrust = p['Fnet']
        fuel_flow = p['wfe']
        return total_thrust, fuel_flow

    def unitary_sc(self,pamb,tamb,mach,rating,thrust,pw_offtake=0.):
        """Unitary thrust of a pure turbofan engine (semi-empirical model)
        Consumption is driven by flying conditions and thrust, rating is their to provide a reference of T4 to compute throttle
        Note that throttle is used here to drive T4 which is not the usual way of working as throttle, normally, drives N1
        """
        self.TF_model.set_flight(tamb, pamb, mach)
        x0 = self.TF_model.magic_guess()

        s, c, p = self.TF_model.off_design(Fnet=thrust, guess=x0, HPX=pw_offtake)

        T4 = s["4"]["Tt"]
        T4max = self.engine_T4max * self.rating_factor[rating]

        throttle = T4/T4max
        sfc = p['wfe']/p['Fnet']

        return sfc, throttle


class Outboard_wing_mounted_extf_nacelle(Exergetic_tf_nacelle,Outboard_wing_mounted_nacelle):

    def __init__(self, aircraft):
        super(Outboard_wing_mounted_extf_nacelle, self).__init__(aircraft)


class Inboard_wing_mounted_extf_nacelle(Exergetic_tf_nacelle,Inboard_wing_mounted_nacelle):

    def __init__(self, aircraft):
        super(Inboard_wing_mounted_extf_nacelle, self).__init__(aircraft)



