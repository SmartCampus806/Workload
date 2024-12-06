from models import WorkloadContainer, EmployeePosition
from src.services.workload_allocation.utils import Processor


class Processor1(Processor):
    def process_data(self, subjects: list[WorkloadContainer], teachers: list[EmployeePosition]) -> (
            tuple)[list[WorkloadContainer], list[EmployeePosition]]:
        for subject in subjects:
            # Находим подходящих учителей
            eligible_teachers = [
                teacher for teacher in teachers
                if subject.sum_workload <= teacher.available_workload + teacher.extra_workload and
                   all(comp in teacher.employee.competences for comp in subject.workloads[0].lesson.competences)
            ]

            # Если есть подходящие учителя, выбираем того с наименьшим процентом загруженности
            if eligible_teachers:
                selected_teacher = min(eligible_teachers, key=lambda
                    t: Processor.load_percentage(t))  # Выбираем учителя с наименьшим процентом загруженности

                subject.employee_id = selected_teacher.employee_id
                subject.employee = selected_teacher
                selected_teacher.workload_containers = subject
            else:
                print(f"WorkloadContainer {subject.id} не может быть распределен (недостаточно часов или компетенций).")

        return subjects, teachers

    # def calculate_load(self, teachers: List[Teacher]) -> Dict[int, Tuple[int, float]]:
    #     load_summary = {teacher.teacher_id: (teacher.loaded_hours, Processor.load_percentage(teacher)) for teacher in
    #                     teachers}
    #     return load_summary
