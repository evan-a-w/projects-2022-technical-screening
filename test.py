import re

COURSE_REGEX = re.compile(r'(\w{4})?(\d{4})(.*)?')

def a(s):
    res = COURSE_REGEX.match(s)
    if res:
        school = res.group(1)
        course = res.group(2)
        print(f"Shool: {school}, cs: {course}")
        if school is None:
            school = 'COMP'
        rest = "" if res.group(3) is None else res.group(3)
        return (f"{school}{course}", rest)
    return None

LEVEL_PREREQ = re.compile(r'(\d+)\s+units\s+of\s+credit\s+in\s+(.*)')

def level(s):
    res = LEVEL_PREREQ.match(s)
    if res:
        units = res.group(1)
        course = res.group(2)
