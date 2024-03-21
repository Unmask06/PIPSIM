# strategy.py
"""
This module contains the class for building the strategy 
    for network simulation using Pipesim model.
"""
from abc import ABC, abstractmethod
from .simulation_modeller import PipsimModeller

class NetworkSimulationStrategy(ABC):
    """Abstract class for network simulation strategy."""
    @abstractmethod
    def build_model(self, modeller: PipsimModeller) -> None:
        """Build the model for network simulation."""
        pass