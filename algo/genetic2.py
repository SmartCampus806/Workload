import random
from typing import List, Tuple


class Subject:
    def __init__(self, subject_id: int, hours: int, required_competencies: List[int], required_rank: str):
        self.subject_id = subject_id
        self.hours = hours
        self.required_competencies = required_competencies
        self.required_rank = required_rank


class Teacher:
    def __init__(self, teacher_id: int, available_hours: int, rank: str, competencies: List[int]):
        self.teacher_id = teacher_id
        self.available_hours = available_hours
        self.rank = rank
        self.competencies = competencies


class Processor:
    def process_data(self, subjects: List[Subject], teachers: List[Teacher]) -> List[Tuple[Subject, Teacher]]:
        population_size = 100
        generations = 1000

        # Инициализация популяции
        population = self.initialize_population(subjects, teachers, population_size)

        for generation in range(generations):
            fitness_scores = [self.fitness(individual, subjects, teachers) for individual in population]
            next_population = self.selection(population, fitness_scores)
            next_population = self.crossover(next_population)
            next_population = self.mutation(next_population)
            population = next_population

        best_individual = max(population, key=lambda ind: self.fitness(ind, subjects, teachers))
        return best_individual

    def initialize_population(self, subjects: List[Subject], teachers: List[Teacher], size: int) -> List[
        List[Tuple[Subject, Teacher]]]:
        population = []
        for _ in range(size):
            individual = [(subject, random.choice(teachers)) for subject in subjects]
            population.append(individual)
        return population

    def fitness(self, individual: List[Tuple[Subject, Teacher]], subjects: List[Subject],
                teachers: List[Teacher]) -> int:
        score = 0
        teacher_hours = {teacher.teacher_id: 0 for teacher in teachers}

        for subject, teacher in individual:
            if (teacher.available_hours >= teacher_hours[teacher.teacher_id] + subject.hours and
                    set(subject.required_competencies).issubset(set(teacher.competencies)) and
                    (subject.required_rank == teacher.rank)):
                score += 1  # Увеличиваем балл за корректное соответствие
                teacher_hours[teacher.teacher_id] += subject.hours

        # Проверка равномерности нагрузки
        avg_hours_per_teacher = sum(teacher_hours.values()) / len(teachers)
        score -= sum(abs(hours - avg_hours_per_teacher) for hours in teacher_hours.values())

        return score

    def selection(self, population: List[List[Tuple[Subject, Teacher]]], fitness_scores: List[int]) -> List[
        List[Tuple[Subject, Teacher]]]:
        selected_indices = random.choices(range(len(population)), weights=fitness_scores, k=len(population) // 2)
        return [population[i] for i in selected_indices]

    def crossover(self, population: List[List[Tuple[Subject, Teacher]]]) -> List[List[Tuple[Subject, Teacher]]]:
        offspring = []
        for _ in range(len(population) // 2):
            parent1, parent2 = random.sample(population, 2)
            cut_point = random.randint(1, len(parent1) - 1)
            child1 = parent1[:cut_point] + parent2[cut_point:]
            child2 = parent2[:cut_point] + parent1[cut_point:]
            offspring.extend([child1, child2])
        return offspring

    def mutation(self, population: List[List[Tuple[Subject, Teacher]]]) -> List[List[Tuple[Subject, Teacher]]]:
        for individual in population:
            if random.random() < 0.1:  # Вероятность мутации 10%
                subject_index = random.randint(0, len(individual) - 1)
                new_teacher = random.choice([t for t in teachers if t != individual[subject_index][1]])
                individual[subject_index] = (individual[subject_index][0], new_teacher)
        return population

def test_processor():
    subjects = [
        Subject(1, 5, [1], 'A'),
        Subject(2, 3, [2], 'B'),
    ]

    teachers = [
        Teacher(1, 10, 'A', [1]),
        Teacher(2, 10, 'B', [2]),
    ]

    processor = Processor()

    # Проверка на корректное распределение
    result = processor.process_data(subjects, teachers)

    assert len(result) == len(
        subjects), "Количество распределенных предметов должно совпадать с количеством предметов."

    # Проверка на соответствие компетенций и ранга
    for subject, teacher in result:
        assert set(subject.required_competencies).issubset(
            set(teacher.competencies)), "Преподаватель не имеет необходимых компетенций."
        assert subject.required_rank == teacher.rank, "Ранг преподавателя не соответствует требуемому."

    print("Все тесты пройдены успешно!")

# Запуск теста
test_processor()