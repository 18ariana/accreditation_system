from .db import GeneralizedWorkFunction, RequiredSkills, LaborActions, NecessaryKnowledges, Blanks, BlankStandards, session
from hashlib import md5


def get_token(data):
    result = data['blank_name'] + data['start_date'] + data['end_date']
    result = result.encode('utf-8')
    result = md5(result).hexdigest()

    return result


def add_new_blank(data):
    result = {
        'blank_name': data['blank_name'],
        'start_date': data['start_date'],
        'end_date': data['end_date']
    }

    token = get_token(result)
    state = 'moderating'

    s = session()

    check = []
    rows = s.query(Blanks).filter(Blanks.token == token)

    for row in rows:
        check.append(row.token)

    if token not in check:
        blank = Blanks(
            name=data['blank_name'],
            startDate=data['start_date'],
            endDate=data['end_date'],
            token=token,
            state=state
        )
        s.add(blank)
    s.commit()

    gwf = data['standards']
    add_new_gwf(gwf, token)


def add_new_gwf(data, token):
    print(data)

    otf = [
        {
            'codeOTF': data[i]['codeOTF'],
            'nameOTF': data[i]['nameOTF'],
            'registrationNumber': data[i]['registrationNumber'],
            'levelOfQualification': data[i]['levelOfQualification']
        }
        for i in range(len(data))
    ]

    add_new_otf(otf)

    pwf = [elem['particularWorkFunctions'] for elem in data][0]
    rn = data[0]['registrationNumber']
    add_new_pwf(pwf, rn)
    add_new_blank_standard(token, rn)


def add_new_blank_standard(token, standard_registration_number):
    s = session()

    blank_id = s.query(Blanks).filter(Blanks.token == token)

    for row in blank_id:
        blank_id = row.id

    bs = BlankStandards(
        blankId=blank_id,
        standardRegistrationNumber=standard_registration_number
    )

    s.add(bs)
    s.commit()

    get_all_questions_by_token(token)


def add_new_pwf(data, rn):

    tf = [elem['codeTF'] for elem in data]
    rs = [elem['requiredSkills'] for elem in data]
    nk = [elem['necessaryKnowledges'] for elem in data]
    la = [elem['laborActions'] for elem in data]

    add_new_rs(rs, tf, rn)
    add_new_nk(nk, tf, rn)
    add_new_la(la, tf, rn)


def add_new_rs(data, tf, rn):

    result = [

        {
            'codeTF': tf[i],
            'registrationNumber': rn,
            'requiredSkill': data[i][j]
        }

        for i in range(len(data))
        for j in range(len(data[i]))

    ]

    s = session()

    rows = s.query(RequiredSkills).all()
    check = []
    for row in rows:
        check.append(row.registrationNumber)
        check.append(row.codeTF)
        check.append(row.requiredSkill)

    for curr_row in result:
        if str(curr_row["registrationNumber"]) not in check \
                and str(curr_row["codeTF"]) not in check \
                and str(curr_row["requiredSkill"] not in check):
            rs = RequiredSkills(
                codeTF=curr_row['codeTF'],
                registrationNumber=curr_row['registrationNumber'],
                requiredSkill=curr_row['requiredSkill']
            )
            s.add(rs)
    s.commit()


def add_new_la(data, tf, rn):

    result = [

        {
            'codeTF': tf[i],
            'registrationNumber': rn,
            'laborAction': data[i][j]
        }

        for i in range(len(data))
        for j in range(len(data[i]))

    ]

    s = session()

    rows = s.query(LaborActions).all()
    check = []
    for row in rows:
        check.append(row.registrationNumber)
        check.append(row.codeTF)
        check.append(row.laborAction)

    for curr_row in result:
        if str(curr_row["registrationNumber"]) not in check \
                and str(curr_row["codeTF"]) not in check \
                and str(curr_row["laborAction"] not in check):
            la = LaborActions(
                codeTF=curr_row['codeTF'],
                registrationNumber=curr_row['registrationNumber'],
                laborAction=curr_row['laborAction']
            )
            s.add(la)
    s.commit()


def add_new_nk(data, tf, rn):

    result = [

        {
            'codeTF': tf[i],
            'registrationNumber': rn,
            'necessaryKnowledge': data[i][j]
        }

        for i in range(len(data))
        for j in range(len(data[i]))

    ]

    s = session()

    rows = s.query(NecessaryKnowledges).all()
    check = []
    for row in rows:
        check.append(row.registrationNumber)
        check.append(row.codeTF)
        check.append(row.necessaryKnowledge)

    for curr_row in result:
        if str(curr_row["registrationNumber"]) not in check \
                and str(curr_row["codeTF"]) not in check \
                and str(curr_row["necessaryKnowledge"] not in check):
            nk = NecessaryKnowledges(
                codeTF=curr_row['codeTF'],
                registrationNumber=curr_row['registrationNumber'],
                necessaryKnowledge=curr_row['necessaryKnowledge']
            )
            s.add(nk)
    s.commit()


def add_new_otf(data):
    s = session()

    rows = s.query(GeneralizedWorkFunction).all()
    check = []
    for row in rows:
        check.append(row.registrationNumber)
    for curr_row in data:
        if str(curr_row["registrationNumber"]) not in check:
            gwf = GeneralizedWorkFunction(
                codeOTF=curr_row['codeOTF'],
                nameOTF=curr_row['nameOTF'],
                levelOfQualification=curr_row['levelOfQualification'],
                registrationNumber=curr_row['registrationNumber'],
            )
            s.add(gwf)
    s.commit()


def get_required_skills_by_registration_number(registration_number):
    s = session()

    rs = s.query(RequiredSkills).filter(RequiredSkills.registrationNumber == registration_number).all()

    result = [
        {
            'codeTF': rs[i].codeTF,
            'registrationNumber': rs[i].registrationNumber,
            'question': rs[i].requiredSkill,
            'questionType': 'requiredSkill'
        }
        for i in range(len(rs))
    ]

    return result


def get_necessary_knowledges_by_registration_number(registration_number):
    s = session()

    nk = s.query(NecessaryKnowledges).filter(NecessaryKnowledges.registrationNumber == registration_number).all()

    result = [
        {
            'codeTF': nk[i].codeTF,
            'registrationNumber': nk[i].registrationNumber,
            'question': nk[i].necessaryKnowledge,
            'questionType': 'necessaryKnowledge'
        }
        for i in range(len(nk))
    ]

    return result


def get_labor_actions_by_registration_number(registration_number):
    s = session()

    la = s.query(LaborActions).filter(LaborActions.registrationNumber == registration_number).all()

    result = [
        {
            'codeTF': la[i].codeTF,
            'registrationNumber': la[i].registrationNumber,
            'question': la[i].laborAction,
            'questionType': 'laborAction'
        }
        for i in range(len(la))
    ]

    return result


def get_all_questions_by_blank_id(blank_id):
    s = session()

    standards = s.query(BlankStandards).filter(BlankStandards.blankId == blank_id).all()

    rs = []
    la = []
    nk = []

    for standard in standards:
        rs_standard = get_required_skills_by_registration_number(standard.standardRegistrationNumber)
        rs.append(rs_standard)

        la_standard = get_labor_actions_by_registration_number(standard.standardRegistrationNumber)
        la.append(la_standard)

        nk_standard = get_necessary_knowledges_by_registration_number(standard.standardRegistrationNumber)
        nk.append(nk_standard)

    blank_questions = []

    for question in rs[0]:
        blank_questions.append(question)

    for question in la[0]:
        blank_questions.append(question)

    for question in nk[0]:
        blank_questions.append(question)

    questions = [
        {
            'question': question['question'],
            'questionType': question['questionType'],
            'codeTF': question['codeTF'],
            'standardRegistrationNumber': question['registrationNumber']
        }
        for question in blank_questions
    ]

    return questions


def get_all_questions_by_token(token):
    s = session()

    blank = s.query(Blanks).filter(Blanks.token == token)
    blank_id = blank[0].id

    questions = get_all_questions_by_blank_id(blank_id)
    print('questions', questions)
    return questions


def get_all_blanks(state="all"):
    s = session()

    blanks = s.query(Blanks).all()

    if state == "moderating":
        blanks = s.query(Blanks).filter(Blanks.state == "moderating").all()

    all_blanks = [
        {
            'name': blank.name,
            'startDate': blank.startDate,
            'endDate': blank.endDate,
            'token': blank.token,
            'state': blank.state
        }
        for blank in blanks
    ]

    return all_blanks
