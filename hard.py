"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their 
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine 
if their course can be taken or not. 

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the 
code by eye.

NOTE: This challenge is EXTREMELY hard and we are not expecting anyone to pass all
our tests. In fact, we are not expecting many people to even attempt this.
For complete transparency, this is worth more than the easy challenge. 
A good solution is favourable but does not guarantee a spot in Projects because
we will also consider many other criteria.
"""
import json
import re

"""
Rule =
    course: str
    | empty: None
    | uoc: ('UOC', amt, Rule)
    | and: ('AND', Rule, Rule)
    | or: ('OR', Rule, Rule)
    | level: ('level', level, course)
"""

COURSE_REGEX = re.compile(r'\s*(\w{4})?(\d{4})(.*)')
AND_REGEX = re.compile(r'\s*(and|AND)(.*)')
OR_REGEX = re.compile(r'\s*(or|OR|,)(.*)')
UOC = re.compile(r'\s*(\d+)\s+units\s+\w{2}\s+credit(.*)')
IN = re.compile(r'\s*in(.*)')
COMPLETION_OF = re.compile(r'\s*completion\s+of(.*)')
PREREQ = re.compile(r'pre-?(req)?(quisite)?(uisite)?:(.*)')
LEVEL = re.compile(r'\s*(level\s+(\d+)\s+)?(\w{4})\s+courses(.*)')


def preprocess(s):
    res = PREREQ.match(s.lower())
    if res:
        return res.group(4).strip()
    res = COMPLETION_OF.match(s.lower())
    if res:
        return res.group(1)
    s = s.strip()
    return s.strip('.')

def get_uoc(s):
    res = UOC.match(s.lower())
    if res:
        return (int(res.group(1)), res.group(2))
    return None

def get_level(s):
    res = LEVEL.match(s.lower())
    if res:
        level = res.group(2)
        if level is None:
            level = '*'
        school = res.group(3).upper()
        rest = res.group(4)
        return (('level', level, school), rest)
    return None

def get_in(s):
    res = IN.match(s)
    if res:
        return res.group(1)
    return None

def get_and(s):
    res = AND_REGEX.match(s)
    if res:
        return res.group(2)
    return None

def get_or(s):
    res = OR_REGEX.match(s)
    if res:
        return res.group(2)
    return None

def get_course_code(s):
    res = COURSE_REGEX.match(s)
    if res:
        school = res.group(1)
        course = res.group(2)
        if school is None:
            school = 'CURR' # signal that it is the school of the current course
        rest = res.group(3)
        return (f"{school.upper()}{course}", rest)
    return None

def inside_brackets_course(s):
    s = preprocess(s)
    if s[0] != '(':
        raise ValueError('Invalid course doobs')
    s = s[1:]
    curr = None
    while s[0] != ')':
        res = get_and(s)
        if res:
            s = res
            (rhs, s) = parse_rule_expr(s)
            curr = ('AND', curr, rhs)
            continue
        res = get_or(s)
        if res:
            s = res
            (rhs, s) = parse_rule_expr(s)
            curr = ('OR', curr, rhs)
            continue
        if curr:
            return (curr, s)
        (curr, s) = parse_rule(s)
    return (curr, s[1:])


def parse_rule(s):
    s = preprocess(s)
    if len(s) == 0:
        return (None, "")
    if s[0] == '(':
        return inside_brackets_course(s)
    elif s[0] == ')':
        raise ValueError('Invalid course doobs')

    res = get_uoc(s)
    if res:
        (amt, ts) = res
        maybe_in = get_in(ts)
        if maybe_in:
            (rule, rest) = parse_rule(maybe_in)
            return (('UOC', amt, rule), rest)
        return (('UOC', amt, None), ts)
    
    res = get_course_code(s)
    if res:
        return res

    res = get_level(s)
    if res:
        return res

    if res is None:
        raise ValueError('Invalid course doobs')
    return res

def parse_rule_expr_single(s):
    s = preprocess(s)
    curr = None
    while True:
        res = get_and(s)
        if res:
            s = res
            (rhs, s) = parse_rule_expr(s)
            curr = ('AND', curr, rhs)
            continue
        res = get_or(s)
        if res:
            s = res
            (rhs, s) = parse_rule_expr(s)
            curr = ('OR', curr, rhs)
            continue
        if curr != None:
            return (curr, s)
        res = parse_rule(s)
        (curr, s) = res

def parse_rule_expr(s):
    s = preprocess(s)
    curr = None
    while True:
        res = get_and(s)
        if res:
            s = res
            (rhs, s) = parse_rule_expr(s)
            curr = ('AND', curr, rhs)
            continue
        res = get_or(s)
        if res:
            s = res
            (rhs, s) = parse_rule_expr(s)
            curr = ('OR', curr, rhs)
            continue
        if curr != None:
            return (curr, s)
        res = parse_rule(s)
        (curr, s) = res

def parse(s):
    if len(s) == 0:
        return None
    return parse_rule_expr(s)[0]


# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()

"""
Rule =
    course: str
    | empty: None
    | uoc: ('UOC', amt, Rule)
    | and: ('AND', Rule, Rule)
    | or: ('OR', Rule, Rule)
    | level: ('level', level, course)
"""

def num_satisfying(rule, courses_list, target_course):
    if rule is None:
        return len(courses_list)
    if isinstance(rule, str):
        course = re.sub("CURR", target_course[:4], rule)
        return len([*filter(lambda x: course == x, courses_list)])
    if rule[0] == 'level':
        if rule[1] == '*':
            return len([*filter(lambda x: x[:4] == rule[2], courses_list)])
        return len([*filter(lambda x: x[4] == rule[1] and x[:4] == rule[2],
                            courses_list)])
    if rule[0] == 'OR':
        return num_satisfying(rule[1], courses_list, target_course) \
               + num_satisfying(rule[2], courses_list, target_course)
    print("Shouldn't reach here but ehh")
    return 0

def unlocked(courses_list, target_course, expr):
    if expr is None:
        return True
    if isinstance(expr, str):
        course = re.sub("CURR", target_course[:4], expr)
        return course in courses_list
    if expr[0] == 'AND':
        return unlocked(courses_list, target_course, expr[1]) \
               and unlocked(courses_list, target_course, expr[2])
    if expr[0] == 'OR':
        return unlocked(courses_list, target_course, expr[1]) \
               or unlocked(courses_list, target_course, expr[2])
    if expr[0] == 'UOC':
        return num_satisfying(expr[2], courses_list, target_course) * 6 \
               >= expr[1]
    print("Shouldn't reach here but ehh")
    return False



def is_unlocked(courses_list, target_course):
    parsed = parse(CONDITIONS[target_course])
    print(parsed)
    return unlocked(courses_list, target_course, parsed)
