import random
from typing import List, Tuple
import matplotlib.pyplot as plt
import time
from algo.models import Teacher, Subject, Processor


class GeneticAlgorithmProcessor(Processor):
    def __init__(self, population_size: int = 1000, generations: int = 1000, initial_mutation_rate: float = 0.05,
                 initial_crossover_rate: float = 0.7, elite_size: int = 5):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = initial_mutation_rate
        self.crossover_rate = initial_crossover_rate
        self.elite_size = elite_size
        self.mutation_rate_decay = 0.99  # Снижение вероятности мутации
        self.crossover_rate_increase = 1.01  # Повышение вероятности кроссовера при стагнации
        self.last_best_fitness = None
        self.stagnation_counter = 0  # Счетчик стагнации

    def process_data(self, subjects: List[Subject], teachers: List[Teacher]) -> List[Tuple[Subject, Teacher]]:
        population = self._initialize_population(subjects, teachers)
        best_individual = None

        for generation in range(self.generations):
            population = self._evolve_population(population, subjects, teachers)

            # Адаптивная настройка операторов
            best_fitness = self._get_best_fitness(population, subjects, teachers)
            if self.last_best_fitness is None or best_fitness > self.last_best_fitness:
                self.last_best_fitness = best_fitness
                self.stagnation_counter = 0
            else:
                self.stagnation_counter += 1

            if self.stagnation_counter >= 5:  # Если фитнес не улучшается 5 поколений, изменяем операторы
                self.mutation_rate *= self.mutation_rate_decay
                self.crossover_rate *= self.crossover_rate_increase

            # Сохраняем лучшее решение
            if best_individual is None or self._fitness(self._get_best_solution(population, subjects, teachers),
                                                        subjects, teachers) > self._fitness(best_individual, subjects,
                                                                                            teachers):
                best_individual = self._get_best_solution(population, subjects, teachers)

        return best_individual

    def _initialize_population(self, subjects: List[Subject], teachers: List[Teacher]) -> List[
        List[Tuple[Subject, Teacher]]]:
        population = []
        for _ in range(self.population_size):
            individual = []
            for subject in subjects:
                # Фильтруем преподавателей по требованиям предмета
                eligible_teachers = [
                    teacher for teacher in teachers
                    if (set(subject.required_competencies).issubset(set(teacher.competencies)))
                ]

                # Если есть подходящие преподаватели, выбираем случайного из них
                if eligible_teachers:
                    teacher = random.choice(eligible_teachers)
                    individual.append((subject, teacher))
                else:
                    # Если нет подходящих преподавателей, добавляем None или бросаем исключение
                    individual.append((subject, None))

            population.append(individual)

        return population

    def _evolve_population(self, population: List[List[Tuple[Subject, Teacher]]], subjects: List[Subject],
                           teachers: List[Teacher]) -> List[List[Tuple[Subject, Teacher]]]:
        new_population = []

        # Сохранение элиты (лучших решений)
        sorted_population = sorted(population, key=lambda ind: self._fitness(ind, subjects, teachers), reverse=True)
        new_population.extend(sorted_population[:self.elite_size])

        for _ in range(self.population_size - self.elite_size):
            parent1, parent2 = self._select_parents(population, subjects, teachers)
            if random.random() < self.crossover_rate:
                child = self._crossover(parent1, parent2)
            else:
                child = parent1
            if random.random() < self.mutation_rate:
                child = self._mutate(child, subjects, teachers)
            new_population.append(child)
        return new_population

    def _select_parents(self, population: List[List[Tuple[Subject, Teacher]]], subjects: List[Subject],
                        teachers: List[Teacher]) -> Tuple[List[Tuple[Subject, Teacher]], List[Tuple[Subject, Teacher]]]:
        # Турнирный отбор (отбираем лучшего из нескольких случайных индивидов)
        tournament_size = 3
        selected = random.sample(population, tournament_size)
        return max(selected, key=lambda ind: self._fitness(ind, subjects, teachers)), max(selected,
                                                                                          key=lambda ind: self._fitness(
                                                                                              ind, subjects, teachers))

    def _crossover(self, parent1: List[Tuple[Subject, Teacher]], parent2: List[Tuple[Subject, Teacher]]) -> List[
        Tuple[Subject, Teacher]]:
        crossover_point = random.randint(0, len(parent1) - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]
        return child

    def _mutate(self, individual: List[Tuple[Subject, Teacher]], subjects: List[Subject], teachers: List[Teacher]) -> \
    List[Tuple[Subject, Teacher]]:
        subject_idx = random.randint(0, len(individual) - 1)
        new_teacher = random.choice(teachers)
        individual[subject_idx] = (individual[subject_idx][0], new_teacher)
        return individual

    def _fitness(self, individual: List[Tuple[Subject, Teacher]], subjects: List[Subject],
                 teachers: List[Teacher]) -> float:
        teacher_hours = {teacher.teacher_id: 0 for teacher in teachers}
        fitness_score = 0

        for subject, teacher in individual:
            if teacher.available_hours >= teacher_hours[teacher.teacher_id] + subject.hours:
                teacher_hours[teacher.teacher_id] += subject.hours
            else:
                fitness_score -= 100  # Штраф за превышение часов

            # Проверка компетенций
            if not set(subject.required_competencies).issubset(teacher.competencies):
                fitness_score -= 120  # Штраф за несоответствие компетенций

            # # Проверка звания
            # if subject.required_rank != teacher.rank:
            #     fitness_score -= 50  # Штраф за несоответствие звания

        # Считаем равномерность нагрузки
        avg_hours = sum(teacher_hours.values()) / len(teachers)
        for teacher_id, hours in teacher_hours.items():
            fitness_score -= abs(hours - avg_hours) * 5  # Чем равномернее распределение, тем лучше

        return fitness_score

    def _get_best_fitness(self, population: List[List[Tuple[Subject, Teacher]]], subjects: List[Subject],
                          teachers: List[Teacher]) -> float:
        return max(self._fitness(ind, subjects, teachers) for ind in population)

    def _get_best_solution(self, population: List[List[Tuple[Subject, Teacher]]], subjects: List[Subject],
                           teachers: List[Teacher]) -> List[Tuple[Subject, Teacher]]:
        best_individual = max(population, key=lambda ind: self._fitness(ind, subjects, teachers))
        return best_individual

def test_adaptive_genetic_algorithm_processor(subjects, teachers):
    processor = GeneticAlgorithmProcessor(population_size=200, generations=500)

    # Замер времени
    start_time = time.time()
    assignment = processor.process_data(subjects, teachers)
    end_time = time.time()

    print(f"Algorithm execution time: {end_time - start_time} seconds")

    # Валидация результата
    teacher_hours = {teacher.teacher_id: 0 for teacher in teachers}
    valid = True
    for subject, teacher in assignment:
        if not set(subject.required_competencies).issubset(teacher.competencies):
            print(f"Teacher {teacher.teacher_id} does not meet competencies for Subject {subject.subject_id}")
            valid = False
        if teacher_hours[teacher.teacher_id] + subject.hours > teacher.available_hours:
            print(f"Teacher {teacher.teacher_id} exceeds available hours for Subject {subject.subject_id}")
            valid = False
        teacher_hours[teacher.teacher_id] += subject.hours

    if valid:
        print("All assignments are valid")
    else:
        print("Some assignments are invalid")


def generate_test_data(num_subjects: int, num_teachers: int) -> (List[Subject], List[Teacher]):
    subjects = []
    teachers = []

    # Генерация преподавателей с достаточным количеством часов и компетенциями
    for teacher_id in range(num_teachers):
        available_hours = random.randint(5, 15)  # Доступные часы от 5 до 15
        # rank = random.choice(['A', 'B', 'C'])  # Ранги A, B или C
        competencies = random.sample(range(1, 4), k=random.randint(1, 3))  # Компетенции от 1 до 3
        teachers.append(Teacher(teacher_id=teacher_id, available_hours=available_hours, competencies =competencies))

    total_hours_available = sum(teacher.available_hours for teacher in teachers)

    # Генерация предметов с учетом доступных часов преподавателей
    for subject_id in range(num_subjects):
        hours = random.randint(1, total_hours_available // num_subjects)  # Часы не превышают среднее доступное время
        # required_rank = random.choice(['A', 'B', 'C'])

        # Выбор необходимых компетенций из доступных у преподавателей
        required_competencies = random.sample(range(1, 4), k=random.randint(1, 3))

        subjects.append(Subject(subject_id, hours, required_competencies))

    return subjects, teachers


# Пример использования генератора тестовых данных
num_subjects = 200
num_teachers = 100
subjects, teachers = generate_test_data(num_subjects, num_teachers)

test_adaptive_genetic_algorithm_processor(subjects, teachers)