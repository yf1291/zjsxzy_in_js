from mesa.model import Model
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

class Foraging(Model):

    number_of_bean = 0
    number_of_corn = 0
    number_of_soy = 0

    def __init__(self, width=50, height=50, torus=True, num_bug=50, seed=42, strategy=None):
        super().__init__(seed=seed)
        self.number_of_bug = num_bug
        if not(strategy om ["stick", "switch"]):
            raise TypeError("strategy must be one of {stick, switch}")
        self.strategy = strategy

        self.grid = SingleGrid(width, height, torus)
        self.schedule = RandomActivation(self)
        data = {'Bean': lambda m: m.number_of_bean,
                'Corn': lambda m: m.number_of_corn,
                'Soy': lambda m: m.number_of_soy,
                'Bug': lambda m: m.number_of_bug
                }
        self.datacollector = DataCollector(data)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

        if not(self.grid.exists_empty_cells()):
            self.running = False