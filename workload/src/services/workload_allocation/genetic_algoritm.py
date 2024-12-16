import random
from typing import List, Dict, Tuple

from src.models import EmployeePosition, WorkloadContainer


class GeneticAllocation:
    def __init__(self, max_generations=100, population_size=50, mutation_rate=0.1):
        self.max_generations = max_generations
        self.population_size = population_size
        self.mutation_rate = mutation_rate

    def initialize_population(self, employees: list[EmployeePosition], workload_containers: list[WorkloadContainer]) -> List[Dict[int, int]]:
        """Инициализация популяции случайных распределений."""
        population = []
        for _ in range(self.population_size):
            individual = {}
            for container in workload_containers:
                suitable_employees = [
                    e.id for e in employees if container.workloads[0].lesson in e.employee.lessons
                ]
                if suitable_employees:
                    individual[container.id] = random.choice(suitable_employees)
            population.append(individual)
        return population

    def fitness(self, individual: Dict[int, int], employees, workload_containers) -> float:
        """Функция приспособленности: минимизация перегрузки и учет квалификации."""
        fitness_score = 0
        workload_by_employee = {e.id: 0 for e in employees}

        for container_id, employee_id in individual.items():
            container = next(c for c in workload_containers if c.id == container_id)
            employee = next(e for e in employees if e.id == employee_id)

            if container.workloads[0].lesson not in employee.employee.lessons:
                fitness_score += 1000  # Штраф за неквалифицированного педагога
            workload_by_employee[employee_id] += container.sum_workload

        for employee in employees:
            overload = max(0, workload_by_employee[employee.id] - employee.available_workload)
            fitness_score += overload * 10  # Штраф за перегрузку

        return -fitness_score  # Чем ниже штрафы, тем лучше

    def select(self, population: List[Dict[int, int]], employees, workload_containers) -> List[Dict[int, int]]:
        """Селекция лучших особей на основе их приспособленности."""
        sorted_population = sorted(population, key=lambda ind: self.fitness(ind, employees, workload_containers), reverse=True)
        return sorted_population[:self.population_size // 2]

    def crossover(self, parent1: Dict[int, int], parent2: Dict[int, int]) -> Dict[int, int]:
        """Скрещивание двух родителей для создания нового ребенка."""
        child = {}
        for container_id in parent1.keys():
            child[container_id] = parent1[container_id] if random.random() < 0.5 else parent2[container_id]
        return child

    def mutate(self, individual: Dict[int, int], employees, workload_containers) -> Dict[int, int]:
        """Мутация особи: случайное изменение распределения нагрузки."""
        if random.random() < self.mutation_rate:
            container_id = random.choice(list(individual.keys()))
            container = next(c for c in workload_containers if c.id == container_id)
            suitable_employees = [
                e.id for e in employees if container.workloads[0].lesson in e.employee.lessons
            ]
            if suitable_employees:
                individual[container_id] = random.choice(suitable_employees)
        return individual

    async def run(self, employees: list[EmployeePosition], workload_containers: list[WorkloadContainer]) -> List[Tuple[EmployeePosition, WorkloadContainer]]:
        """Запуск генетического алгоритма."""
        population = self.initialize_population(employees, workload_containers)

        for generation in range(self.max_generations):
            population = self.select(population, employees, workload_containers)
            new_population = []

            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(population, 2)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child, employees, workload_containers)
                new_population.append(child)

            population = new_population
            best_fitness = max(self.fitness(ind, employees, workload_containers) for ind in population)
            print(f"Generation {generation}: Best Fitness {best_fitness}")

        best_individual = max(population, key=lambda ind: self.fitness(ind, employees, workload_containers))

        # Формируем пары объектов employee и workload_container
        result = []
        for container_id, employee_id in best_individual.items():
            container = next(c for c in workload_containers if c.id == container_id)
            employee = next(e for e in employees if e.id == employee_id)
            result.append((employee, container))

        return result
