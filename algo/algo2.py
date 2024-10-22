from typing import List, Tuple
from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpBinary, LpStatus, value
import random


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
        # Инициализация задачи
        prob = LpProblem("Subject-Teacher Assignment", LpMinimize)

        # Словарь для переменных: назначен ли предмет преподавателю
        assignment = LpVariable.dicts("Assign",
                                      [(s.subject_id, t.teacher_id) for s in subjects for t in teachers],
                                      0, 1, LpBinary)

        # Средняя нагрузка для равномерного распределения
        avg_hours = sum([s.hours for s in subjects]) / len(teachers)

        # Целевая функция - минимизация отклонения от средней нагрузки
        deviation = LpVariable.dicts("Deviation", [t.teacher_id for t in teachers], 0)
        prob += lpSum(deviation[t.teacher_id] for t in teachers), "Total Deviation"

        # Ограничение 1: Каждый предмет должен быть назначен ровно одному преподавателю
        for s in subjects:
            prob += lpSum(assignment[(s.subject_id, t.teacher_id)] for t in
                          teachers) == 1, f"One teacher per subject {s.subject_id}"

        # Ограничение 2: Преподаватель не может превышать доступные часы
        for t in teachers:
            prob += lpSum(assignment[(s.subject_id, t.teacher_id)] * s.hours for s in
                          subjects) <= t.available_hours, f"Max hours for teacher {t.teacher_id}"

        # Ограничение 3: Преподаватель должен соответствовать компетенциям и рангу предмета
        for s in subjects:
            for t in teachers:
                if s.required_rank != t.rank or not all(comp in t.competencies for comp in s.required_competencies):
                    prob += assignment[
                                (s.subject_id, t.teacher_id)] == 0, f"Competency check {s.subject_id}_{t.teacher_id}"

        # Ограничение 4: Балансировка нагрузки (равномерное распределение)
        for t in teachers:
            total_hours = lpSum(assignment[(s.subject_id, t.teacher_id)] * s.hours for s in subjects)
            prob += total_hours - avg_hours <= deviation[t.teacher_id], f"Positive deviation {t.teacher_id}"
            prob += avg_hours - total_hours <= deviation[t.teacher_id], f"Negative deviation {t.teacher_id}"

        # Решаем задачу
        prob.solve()

        # Проверка решения
        if LpStatus[prob.status] == "Optimal":
            result = []
            for s in subjects:
                for t in teachers:
                    if value(assignment[(s.subject_id, t.teacher_id)]) == 1:
                        result.append((s, t))
            return result
        else:
            raise ValueError("No optimal solution found")


# Тестирование алгоритма

def test_processor():
    # Простой случай
    print("Test Case 1: Simple Case")
    subjects = [
        Subject(1, 10, [1, 2], 'senior'),
        Subject(2, 15, [1], 'senior'),
        Subject(3, 20, [2, 3], 'senior'),
        Subject(4, 25, [3], 'senior'),
        Subject(5, 12, [1, 3], 'senior'),
        Subject(6, 18, [2], 'senior'),
        Subject(7, 22, [1, 2, 3], 'senior'),
        Subject(8, 8, [1], 'senior'),
        Subject(9, 30, [3, 4], 'senior'),
        Subject(10, 16, [2, 4], 'senior'),
    ]

    teachers = [
        Teacher(1, 50, 'senior', [1, 2]),
        Teacher(2, 30, 'senior', [1]),
        Teacher(3, 50, 'senior', [2, 3]),
        Teacher(4, 76, 'senior', [3]),
        Teacher(5, 66, 'senior', [1, 3]),
    ]
    processor = Processor()
    assignments = processor.process_data(subjects, teachers)

    for subject, teacher in assignments:
        print(f"Subject {subject.subject_id} is assigned to Teacher {teacher.teacher_id}")


# Запуск тестов
test_processor()