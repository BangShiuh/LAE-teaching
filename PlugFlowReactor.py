import cantera as ct
import numpy as np

class PlugFlowReactor:
    """
    A plug flow reactor with a flow on the side.

    :@param gas: ct.Solution object for the main flow gas
    :@param length: length of the plug flow reactor [m]
    :@param mdot_main: main mass flow rate [kg/s]
    :@param side_flow: side flow ct.Reservoir object
    :@param mdot_side: side mass flow rate [kg/s]
    """
    inlet: ct.Reservoir = None
    outlet_gas: ct.Solution = None

    def __init__(self, gas: ct.Solution, length: float,
                 mdot_main: float, side_flow: ct.Reservoir=None,
                 mdot_side: float=0.0) -> None:
        self._gas = gas
        self.inlet = ct.Reservoir(self._gas)
        self.length = length
        self.mdot_main = mdot_main
        self.side_flow = side_flow
        self.mdot_side = mdot_side
        self.solutions = ct.SolutionArray(self._gas, extra=['z'])

    def advance_to_exit(self, n_steps: int) -> None:
        dz = self.length / n_steps
        reactor = ct.IdealGasConstPressureReactor(self.inlet.thermo,
                                                  volume=dz)
        # side mass flow rate
        def mdot(t):
            return reactor.volume * self.mdot_side / self.length

        if self.side_flow != None:
            ct.MassFlowController(self.side_flow, reactor, mdot=mdot)

        sim = ct.ReactorNet([reactor])
        time = 0.0
        z = 0.0
        mdot_tot = self.mdot_main
        self.solutions.append(reactor.thermo.state, z=z)
        for _ in range(n_steps):
            u = mdot_tot / reactor.thermo.density
            z += dz
            time += dz / u
            sim.advance(time)
            self.solutions.append(reactor.thermo.state, z=z)
            mdot_tot += self.mdot_side * dz / self.length

        self.outlet_gas = reactor.thermo
