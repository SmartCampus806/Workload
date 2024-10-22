import random
import time
from typing import List, Tuple
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus, LpBinary

from algo.models import Processor, Subject, Teacher


class LpProcessor(Processor):
    def process_data(self, subjects: List[Subject], teachers: List[Teacher]) -> List[Tuple[Subject, Teacher]]:
        # Создаем задачу линейного программирования
        problem = LpProblem("Teacher_Assignment_Problem", LpMinimize)

        # Создаем переменные для распределения часов между учителями и предметами
        assignment_vars = {
            (teacher.teacher_id, subject.subject_id): LpVariable(
                f"assign_{teacher.teacher_id}_{subject.subject_id}",
                lowBound=0,
                upBound=subject.hours,
                cat=LpBinary  # Используем бинарные переменные для назначения
            )
            for teacher in teachers for subject in subjects
        }

        # Ограничение по доступным часам для каждого учителя
        for teacher in teachers:
            problem += lpSum(assignment_vars[(teacher.teacher_id, subject.subject_id)]
                             for subject in subjects) <= teacher.available_hours

        # Ограничение по компетенциям
        for subject in subjects:
            for teacher in teachers:
                if not (set(subject.required_competencies).issubset(set(teacher.competencies))):
                    problem += assignment_vars[(teacher.teacher_id, subject.subject_id)] == 0

        # Целевая функция: минимизация разницы в загруженности между учителями (равномерная загрузка)
        problem += lpSum(assignment_vars[(teacher.teacher_id, subject.subject_id)]
                         for teacher in teachers for subject in subjects)

        # Решаем задачу
        problem.solve()

        # Получаем результаты
        assignments = []
        for teacher in teachers:
            for subject in subjects:
                if assignment_vars[(teacher.teacher_id, subject.subject_id)].varValue > 0:
                    assignments.append((subject, teacher))

        return assignments

def test_adaptive_genetic_algorithm_processor(subjects, teachers):
    processor = LpProcessor()

    # Замер времени
    start_time = time.time()
    assignment = processor.process_data(subjects, teachers)
    end_time = time.time()

    print(f"Algorithm execution time: {end_time - start_time} seconds")

    # Валидация результата
    teacher_hours = {teacher.teacher_id: 0 for teacher in teachers}
    print(f"{len(assignment)} == {len(subjects)}")
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
num_subjects = 500
num_teachers = 100
subjects, teachers = generate_test_data(num_subjects, num_teachers)

test_adaptive_genetic_algorithm_processor(subjects, teachers)