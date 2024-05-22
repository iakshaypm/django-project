from celery import shared_task

from assignment.models import AssignmentMark, Assignment
from user.models import Student


@shared_task
def assignNewAssignment():
    students = Student.objects.all()
    for student in students:
        assignment_type = Assignment.objects.values('type').get(id=student.assignment_id)
        assignment = AssignmentMark.objects.get(assignment_id=student.assignment_id)
        if assignment_type['type'] == 1:
            if int(assignment.mark) < 5:
                Student.objects.filter(id=student.id).update(assignment_id=4)
        elif assignment_type['type'] == 2:
            if int(assignment.mark) < 4:
                Student.objects.filter(id=student.id).update(assignment_id=3)
            else:
                Student.objects.filter(id=student.id).update(assignment_id=5)
        elif assignment_type['type'] == 3:
            if int(assignment.mark) < 3:
                Student.objects.filter(id=student.id).update(assignment_id=2)
            else:
                Student.objects.filter(id=student.id).update(assignment_id=4)
        elif assignment_type['type'] == 4:
            if int(assignment.mark) < 2:
                Student.objects.filter(id=student.id).update(assignment_id=1)
            else:
                Student.objects.filter(id=student.id).update(assignment_id=3)
        elif assignment_type['type'] == 5:
            if int(assignment.mark) > 1:
                Student.objects.filter(id=student.id).update(assignment_id=2)

