#!/usr/bin/env python3
"""
Created on Thu Jan 20 20:20:20 2020

@author: DRUOT Thierry, Nicolas Monrolin
"""

import unit
from aircraft.requirement import Requirement
from aircraft.arrangement import Arrangement
from aircraft.root import Aircraft

from aircraft.airframe import component

agmt = Arrangement(body_type = "fuselage",          # "fuselage" or "blended"
                   wing_type = "classic",           # "classic" or "blended"
                   wing_attachment = "low",         # "low" or "high"
                   stab_architecture = "classic",   # "classic", "t_tail" or "h_tail"
                   tank_architecture = "wing_box",  # "wing_box", "piggy_back" or "pods"
                   number_of_engine = "twin",       # "twin" or "quadri"
                   nacelle_attachment = "wing",     # "wing" or "rear"
                   power_architecture = "tf",       # "tf", "pf", "pte1", "ef1", "ep1",
                   energy_source = "kerosene")      # "kerosene", "methane", "liquid_h2", "700bar_h2" or "battery"

reqs = Requirement(n_pax_ref = 150.,
                   design_range = unit.m_NM(3000.),
                   cruise_mach = 0.78,
                   cruise_altp = unit.m_ft(35000.),
                   arrangement = agmt)


def factory(name = "my_plane",
            reqs = None,
            agmt = None):
    """
    Build an aircraft
    :param name: the name of your aircraft
    :param reqs: requirement object
    :param agmt: arrangement object
    :return: an aircraft
    """

    ac = Aircraft(reqs,agmt)

    # plug a cabin component
    ac.airframe.cabin = component.Cabin(ac)

    if (ac.arrangement.body_type=="fuselage"):
        ac.airframe.fuselage = component.Fuselage(ac)
    else:
        raise Exception("Type of body is unknown")

    if (ac.arrangement.wing_type=="classic"):
        ac.airframe.wing = component.Wing(ac)
    else:
        raise Exception("Type of wing is unknown")

    if (ac.arrangement.stab_architecture=="classic"):
        ac.airframe.vertical_stab = component.VTP_classic(ac)
        ac.airframe.horizontal_stab = component.HTP_classic(ac)
    elif (ac.arrangement.stab_architecture=="t_tail"):
        ac.airframe.vertical_stab = component.VTP_T(ac)
        ac.airframe.horizontal_stab = component.HTP_T(ac)
    elif (ac.arrangement.stab_architecture=="h_tail"):
        ac.airframe.vertical_stab = component.VTP_H(ac)
        ac.airframe.horizontal_stab = component.HTP_H(ac)
    else:
        raise Exception("stab_architecture is unknown")

    if (ac.arrangement.tank_architecture=="wing_box"):
        ac.airframe.tank = component.Tank_wing_box(ac)
    elif (ac.arrangement.tank_architecture=="piggy_back"):
        ac.airframe.tank = component.Tank_piggy_back(ac)
    elif (ac.arrangement.tank_architecture=="pods"):
        ac.airframe.tank = component.Tank_wing_pod(ac)
    else:
        raise Exception("Type of tank is unknown")

    ac.airframe.landing_gear = component.Landing_gear(ac)


    return ac



ac = factory(name = "my_plane", reqs = reqs, agmt = agmt)


ac.airframe.cabin.eval_geometry()

ac.airframe.fuselage.eval_geometry()

ac.airframe.wing.eval_geometry()

if (ac.arrangement.stab_architecture=="classic"):
    ac.airframe.vertical_stab.eval_geometry()
    ac.airframe.horizontal_stab.eval_geometry()
elif (ac.arrangement.stab_architecture=="t_tail"):
    ac.airframe.vertical_stab.eval_geometry()
    ac.airframe.horizontal_stab.eval_geometry()
elif (ac.arrangement.stab_architecture=="h_tail"):
    ac.airframe.horizontal_stab.eval_geometry()
    ac.airframe.vertical_stab.eval_geometry()
else:
    raise Exception("stab_architecture is unknown")

ac.airframe.tank.eval_geometry()

ac.airframe.landing_gear.eval_geometry()



ac.airframe.cabin.eval_mass()

ac.airframe.fuselage.eval_mass()

ac.airframe.wing.eval_mass()

ac.airframe.vertical_stab.eval_mass()

ac.airframe.horizontal_stab.eval_mass()

ac.airframe.tank.eval_mass()

ac.airframe.landing_gear.eval_mass()


