from typing import List, Tuple


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
        # self.assigned_hours = 0  # Сколько часов уже назначено преподавателю

class Processor:
    def process_data(self, subjects: List[Subject], teachers: List[Teacher]) -> List[Tuple[Subject, Teacher]]:
        pass