import random
import time
from typing import List, Tuple

from algo.models import Subject, Teacher, Processor


class AlgoProcessor(Processor):
    def process_data(self, subjects: List[Subject], teachers: List[Teacher]) -> List[Tuple[Subject, Teacher]]:
        # Результат распределения
        assignments = []

        # Сортируем преподавателей по доступным часам (начинаем с наименее занятых)
        teachers.sort(key=lambda t: t.available_hours)

        # Проходим по каждому предмету
        for subject in subjects:
            # Находим подходящих преподавателей для предмета
            suitable_teachers = [
                teacher for teacher in teachers
                if teacher.rank == subject.required_rank and
                   set(subject.required_competencies).issubset(teacher.competencies) and
                   teacher.available_hours - teacher.assigned_hours >= subject.hours
            ]

            # Если подходящих преподавателей нет, то предмет невозможно распределить
            if not suitable_teachers:
                print(f"Нет подходящих преподавателей для предмета {subject.subject_id}")

            # Назначаем предмет первому подходящему преподавателю (с наименьшей текущей нагрузкой)
            suitable_teachers.sort(key=lambda t: t.assigned_hours)
            chosen_teacher = suitable_teachers[0]
            chosen_teacher.assigned_hours += subject.hours
            assignments.append((subject, chosen_teacher))

        return assignments

def test_adaptive_genetic_algorithm_processor(subjects, teachers):
    processor = AlgoProcessor()

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
        if subject.required_rank != teacher.rank:
            print(f"Teacher {teacher.teacher_id} does not meet rank for Subject {subject.subject_id}")
            valid = False
        if teacher_hours[teacher.teacher_id] + subject.hours > teacher.available_hours:
            print(f"Teacher {teacher.teacher_id} exceeds available hours for Subject {subject.subject_id}")
            valid = False
        teacher_hours[teacher.teacher_id] += subject.hours

    if valid:
        print("All assignments are valid")
    else:
        print("Some assignments are invalid")


subjects = [
    Subject(i, random.randint(10, 50), [random.randint(1, 5) for _ in range(random.randint(1, 3))],
            random.choice(["Professor", "Associate Professor"])) for i in range(100)
]

teachers = [
    Teacher(i, random.randint(100, 150), random.choice(["Professor", "Associate Professor"]),
            [random.randint(1, 5) for _ in range(random.randint(2, 5))]) for i in range(20)
]
test_adaptive_genetic_algorithm_processor(subjects, teachers)