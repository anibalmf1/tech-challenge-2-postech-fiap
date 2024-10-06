import os
import random
import uuid
import glob

from typing import List, Dict, Any

from matplotlib import pyplot as plt
from pydantic import BaseModel

from app.models import Resource
from app.requests import VMRequest, PredictRequest


class Allocation(BaseModel):
    vm: VMRequest
    resource: Any


class Solution(BaseModel):
    allocation: Dict[str, Allocation]
    fitness: float = 0.0

    def is_valid(self, resources: List[Resource]):
        [resource.clean() for resource in resources]
        for allocation in self.allocation.values():
            allocation.resource.allocate(allocation.vm)

        return all(resource.valid() for resource in resources)

    def to_response(self) -> dict:
        vms = []

        for allocation in self.allocation.values():
            vms.append({
                "vm": allocation.vm.id,
                "resource": allocation.resource.id
            })

        return {
            "allocation": vms,
            "energy_consumption": self.fitness,
        }


def fitness(solution: Solution, resources: List[Resource]) -> float:
    resource_energy = {}

    [resource.clean() for resource in resources]

    for allocation in solution.allocation.values():
        resource_energy[allocation.resource.id] = allocation.resource.energy_consumption

    total_energy = sum(resource_energy.values())

    return total_energy


def select_best(
        population: List[Solution],
        resources: List[Resource],
        k=5,
) -> List[Solution]:
    for solution in population:
        solution.fitness = fitness(solution, resources)

    return sorted(population, key=lambda x: x.fitness)[:k]


def crossover(
        resources: List[Resource],
        vms: List[VMRequest],
        parent1: Solution,
        parent2: Solution,
        attempt: int = 0,
) -> Solution:
    child_allocation = parent1.allocation.copy()

    vms_to_swap = random.sample(list(parent1.allocation.keys()), 1)

    for vm in vms_to_swap:
        child_allocation[vm] = parent2.allocation[vm]

    [resource.clean() for resource in resources]
    for allocation in child_allocation.values():
        allocation.resource.allocate(allocation.vm)
        
    valid_allocation = all(resource.valid() for resource in resources)
    
    if valid_allocation:
        return Solution(allocation=child_allocation)
    
    if attempt < 5:
        return crossover(resources, vms, parent1, parent2, attempt + 1)

    best_parent = parent1 if parent1.fitness < parent2.fitness else parent2

    return Solution(allocation=best_parent.allocation.copy())


def remove_resource_chart():
    files = glob.glob('./plot/resource_utilization_gen*')
    for f in files:
        os.remove(f)


def generate_initial_population(
        vm_requests: List[VMRequest],
        resources: List[Resource],
        population_size=10,
) -> List[Solution]:
    population = []

    invalid_solutions = 0

    for _ in range(population_size):
        [resource.clean() for resource in resources]

        allocation = {}
        for vm in vm_requests:
            vm.id = vm.id or str(uuid.uuid4())

            valid_resources = [r for r in resources if
                               r.get_available_cpu_cores() >= vm.cpu_cores and
                               r.get_available_memory() >= vm.memory and
                               r.get_available_storage() >= vm.storage and
                               r.network_bandwidth >= vm.network_bandwidth and
                               r.status == "ACTIVE"]

            if valid_resources:
                resource = random.choice(valid_resources)
                allocation[vm.id] = Allocation(
                    vm=vm,
                    resource=resource,
                )
                resource.allocate(vm)

        if len(allocation) == len(vm_requests):
            population.append(Solution(allocation=allocation))
            invalid_solutions = 0
        else:
            invalid_solutions += 1
            if invalid_solutions > len(population):
                raise ValueError("infrastructure can't handle request")

    return population


def apply_mutation(
        chance_mutation: int,
        resources: List[Resource],
        child: Solution,
        attempt: int = 0,
):
    if random.randint(0, 100) > chance_mutation and attempt == 0:
        return child

    qtd_vms_to_swap = random.randint(1, len(child.allocation))
    vms_to_swap = random.sample(list(child.allocation.keys()), qtd_vms_to_swap)

    mutated_allocation = child.allocation.copy()
    for vm in vms_to_swap:
        mutated_allocation[vm] = Allocation(
            vm=child.allocation[vm].vm,
            resource=random.choice(list(resources)),
        )

    mutated = Solution(allocation=mutated_allocation)

    if mutated.is_valid(resources):
        return mutated

    if attempt > 10:
        return child

    return apply_mutation(chance_mutation, resources, child, attempt + 1)


def plot_fitness_statistics(best_fitness, mean_fitness, worst_fitness):
    if not os.path.exists('./plot'):
        os.makedirs('./plot')

    generations = range(len(best_fitness))
    plt.figure(figsize=(10, 6))
    plt.plot(generations, best_fitness, label='Best Energy Consumption', color='green')
    plt.plot(generations, mean_fitness, label='Mean Energy Consumption', color='blue')
    plt.plot(generations, worst_fitness, label='Worst Energy Consumption', color='red')
    plt.xlabel('Generations')
    plt.ylabel('Energy Consumption')
    plt.title('Genetic Algorithm Energy Consumption Over Generations')
    plt.legend()
    plt.grid(True)

    plt.savefig('./plot/fitness_plot.png')
    plt.close()


def plot_resource_utilization(generation, allocation, resources):
    if not os.path.exists('./plot'):
        os.makedirs('./plot')

    resource_labels = []
    usage_percentage = []

    energy_consumption = 0

    [resource.clean() for resource in resources]
    for alloc in allocation.values():
        alloc.resource.allocate(alloc.vm)

    for resource in resources:
        # Calculate CPU usage percentage
        total_cpu = resource.cpu_cores
        available_cpu = resource.get_available_cpu_cores()
        used_cpu = total_cpu - available_cpu
        cpu_usage_percentage = (used_cpu / total_cpu) * 100 if total_cpu != 0 else 0

        # Calculate memory usage percentage
        total_memory = resource.memory
        available_memory = resource.get_available_memory()
        used_memory = total_memory - available_memory
        memory_usage_percentage = (used_memory / total_memory) * 100 if total_memory != 0 else 0

        # Calculate storage usage percentage
        total_storage = resource.storage
        available_storage = resource.get_available_storage()
        used_storage = total_storage - available_storage
        storage_usage_percentage = (used_storage / total_storage) * 100 if total_storage != 0 else 0

        resource_labels.append(f'Resource {resource.energy_consumption}')

        usage = (cpu_usage_percentage + memory_usage_percentage + storage_usage_percentage) / 3

        if usage > 0:
            energy_consumption += resource.energy_consumption

        usage_percentage.append(usage)

    x = range(len(resource_labels))

    plt.figure(figsize=(12, 8))

    bar_width = 0.6
    opacity = 0.8

    plt.bar(x, usage_percentage, bar_width, alpha=opacity, color='b', label='Resource Usage')

    plt.xlabel('Resources')
    plt.ylabel('Usage Percentage (%)')
    plt.title(f'Resource Utilization in Generation {generation} - {energy_consumption} Watts')
    plt.xticks(x, resource_labels)
    plt.ylim(0, 100)
    plt.legend()

    plt.tight_layout()
    save_path = f'./plot/resource_utilization_gen_{generation}.png'
    plt.savefig(save_path)
    plt.close()

    # Debugging output
    print(f"Plot for generation {generation} saved at: {save_path}")

def genetic_algorithm(
        req: PredictRequest,
        resources: List[Resource],
) -> Solution:
    remove_resource_chart()

    population = generate_initial_population(req.vms, resources, req.population_size)
    qt_parents = req.population_size // 3
    qt_children = req.population_size - qt_parents

    best_fitness = []
    mean_fitness = []
    worst_fitness = []
    best_energy_consumption = []

    for generation in range(req.generations):
        selected_parents = select_best(population, resources, k=qt_parents)

        children = []
        for _ in range(qt_children):
            parent1, parent2 = random.sample(selected_parents, 2)
            child = crossover(resources, req.vms, parent1, parent2)
            child = apply_mutation(req.chance_mutation, resources, child)
            children.append(child)

        population = selected_parents + children
        best_solution = select_best(population, resources, k=1)[0]
        print(f"Generation {generation}: Best energy consumption = {best_solution.fitness} watts")

        fitness_values = [solution.fitness for solution in population]
        best_fitness.append(min(fitness_values))
        mean_fitness.append(sum(fitness_values) / len(fitness_values))
        worst_fitness.append(max(fitness_values))

        if generation == 0 or best_energy_consumption[-1] != best_solution.fitness:
            best_energy_consumption.append(best_solution.fitness)
            plot_resource_utilization(generation, best_solution.allocation, resources)

    plot_fitness_statistics(best_fitness, mean_fitness, worst_fitness)

    return select_best(population, resources, k=1)[0]