from src.models import WorkloadContainer, EmployeePosition


class Processor:
    def process_data(self, subjects: list[WorkloadContainer], teachers: list[EmployeePosition]) -> (
            tuple)[list[WorkloadContainer], list[EmployeePosition]]:
        pass

    @staticmethod
    def load_percentage(teacher: EmployeePosition) -> float:
        """Возвращает процент загруженности преподавателя относительно доступных часов."""
        if teacher.available_workload + teacher.extra_workload == 0:
            return float('100')  # Если нет доступных часов, возвращаем бесконечность
        return (teacher.sum_workload / (
                    teacher.available_workload + teacher.extra_workload + teacher.sum_workload)) * 100
