import json
from datetime import datetime

with open('exams.txt') as f:
    exams = f.readlines()

exams_json = []

for exam in exams:
    parts = exam.split()
    course_code = parts.pop(0)
    duration = parts.pop(len(parts) - 1)
    start_time = parts.pop(len(parts) - 1)
    start_date = parts.pop(len(parts) - 1)
    day = parts.pop(len(parts) - 1)
    course_name = ' '.join(parts)

    combined = start_date + ' ' + start_time
    dt = datetime.strptime(combined, '%d/%m/%Y %H:%M')

    exams_json.append({
        'course_code': course_code,
        'course_name': course_name,
        'day': day,
        'datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': duration,
    })

exams_json.sort(key=lambda e: datetime.strptime(
    e.get('datetime'), '%Y-%m-%d %H:%M:%S'))

with open('exams.json', 'w') as f:
    json.dump(exams_json, f, indent=4, sort_keys=True)
