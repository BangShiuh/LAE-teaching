import cantera as ct
import numpy as np

class PerfectlyStirredReactor:
    """
    A perfectly-stirred reactor

    :@param gas: cantera object for inlet gas
    :@param volume: volume [m-3]
    :@param mdot: mass flow rate [kg/s]
    """
    inlet: ct.Reservoir = None
    outlet_gas: ct.Solution = None
    reactor : ct.IdealGasReactor = None

    def __init__(self, gas: ct.Solution, volume: float, mdot: float) -> None:
        self._gas = gas
        self.inlet = ct.Reservoir(self._gas)
        self.volume = volume
        self.mdot = mdot

    def advance_to_steady_state(self) -> None:
        self._gas.TDY = self.inlet.thermo.TDY
        self._gas.equilibrate('HP')
        self.reactor = ct.IdealGasReactor(self._gas, volume=self.volume)
        inlet_mfc = ct.MassFlowController(self.inlet, self.reactor, mdot=self.mdot)
        exhaust = ct.Reservoir(self._gas)
        ct.PressureController(self.reactor, exhaust, master=inlet_mfc, K=0.01)
        sim = ct.ReactorNet([self.reactor])
        sim.advance_to_steady_state()
        self.outlet_gas = self.reactor.thermo
