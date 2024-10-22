from typing import List, Tuple, Dict
import time

class Subject:
    def __init__(self, subject_id: int, hours: int, required_competencies: List[int]):
        self.subject_id = subject_id
        self.hours = hours
        self.required_competencies = required_competencies


class Teacher:
    def __init__(self, teacher_id: int, available_hours: int, competencies: List[int]):
        self.teacher_id = teacher_id
        self.available_hours = available_hours
        self.competencies = competencies
        self.loaded_hours = 0  # Инициализация загруженности


class Processor:
    def process_data(self, subjects: List[Subject], teachers: List[Teacher]) -> List[Tuple[Subject, Teacher]]:
        allocations = []

        for subject in subjects:
            # Находим подходящих учителей
            eligible_teachers = [
                teacher for teacher in teachers
                if subject.hours <= teacher.available_hours and
                   all(comp in teacher.competencies for comp in subject.required_competencies)
            ]

            # Если есть подходящие учителя, выбираем того с наименьшим процентом загруженности
            if eligible_teachers:
                selected_teacher = min(eligible_teachers, key=lambda
                    t: Processor.load_percentage(t))  # Выбираем учителя с наименьшим процентом загруженности
                allocations.append((subject, selected_teacher))

                # Обновляем доступные часы и загруженность
                selected_teacher.available_hours -= subject.hours
                selected_teacher.loaded_hours += subject.hours
            else:
                print(f"Предмет {subject.subject_id} не может быть распределен (недостаточно часов или компетенций).")

        return allocations

    def calculate_load(self, teachers: List[Teacher]) -> Dict[int, Tuple[int, float]]:
        load_summary = {teacher.teacher_id: (teacher.loaded_hours, Processor.load_percentage(teacher)) for teacher in teachers}
        return load_summary

    @staticmethod
    def load_percentage(teacher: Teacher) -> float:
        """Возвращает процент загруженности преподавателя относительно доступных часов."""
        if teacher.available_hours == 0:
            return float('100')  # Если нет доступных часов, возвращаем бесконечность
        return (teacher.loaded_hours / (teacher.available_hours + teacher.loaded_hours)) * 100

if __name__ == "__main__":
    # subjects = [
    #     Subject(1, 10, [1]),  # Предмет 1 требует 10 часов и компетенцию 1
    #     Subject(2, 5, [2]),  # Предмет 2 требует 5 часов и компетенцию 2
    #     Subject(3, 15, [1]),  # Предмет 3 требует 15 часов и компетенцию 1
    #     Subject(4, 5, [1]),  # Предмет 4 требует 5 часов и компетенцию 1
    #     Subject(5, 8, [2]),  # Предмет 5 требует 8 часов и компетенцию 2
    #     Subject(6, 12, [3]),  # Предмет 6 требует 12 часов и компетенцию 3
    #     Subject(7, 4, [1]),  # Предмет 7 требует 4 часа и компетенцию 1
    #     Subject(8, 7, [2]),  # Предмет 8 требует 7 часов и компетенцию 2
    #     Subject(9, 10, [3]),  # Предмет 9 требует 10 часов и компетенцию 3
    # ]
    #
    # teachers = [
    #     Teacher(1, 20, [1]),  # Преподаватель 1 имеет доступные часы и компетенцию 1
    #     Teacher(2, 15, [2]),  # Преподаватель 2 имеет доступные часы и компетенцию 2
    #     Teacher(3, 25, [1, 2]),  # Преподаватель 3 имеет доступные часы и компетенции 1 и 2
    #     Teacher(4, 10, [3]),  # Преподаватель 4 имеет доступные часы и компетенцию 3
    #     Teacher(5, 5, [1]),  # Преподаватель 5 имеет доступные часы и компетенцию 1
    #     Teacher(6, 30, [2]),  # Преподаватель 6 имеет много доступных часов и компетенцию 2
    # ]

    subjects = [
        Subject(1, 10, [1]),
        Subject(2, 10, [1]),
        Subject(3, 10, [1]),
        Subject(4, 10, [1]),
        Subject(5, 10, [1]),
        Subject(6, 10, [1]),

        Subject(7, 10, [2]),
        Subject(8, 10, [2]),
        Subject(9, 10, [2]),
        Subject(10, 10, [2]),
        Subject(11, 10, [2]),
        Subject(12, 10, [2]),

        Subject(13, 10, [1]),
        Subject(14, 10, [2]),

        Subject(15, 10, [3]),

    ]

    teachers = [
        Teacher(1, 100, [1]),
        Teacher(2, 100, [2]),
        Teacher(3, 100, [1,2])
    ]

    processor = Processor()
    start_time = time.perf_counter()
    allocations = processor.process_data(subjects, teachers)
    end_time = time.perf_counter()

    for subject, teacher in allocations:
        print(f"Предмет {subject.subject_id} назначен преподавателю {teacher.teacher_id}")

    # Подсчет загруженности преподавателей с процентами
    load_summary = processor.calculate_load(teachers)

    print("\nЗагруженность преподавателей:")
    for teacher_id in load_summary:
        loaded_hours, percentage = load_summary[teacher_id]
        print(f"Преподаватель {teacher_id}: {loaded_hours} часов ({percentage:.2f}%)")

    print("\n")
    print(f"Время выполнения: {end_time - start_time} секунд")