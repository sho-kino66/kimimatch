def calculate_match_percentage(student, company):
    """
    学生と企業のマッチ度と、一致したタグを計算する関数
    戻り値: 辞書 {'percentage': int, 'matched_strengths': list, 'matched_conditions': list}
    """
    def get_weight(rank):
        return 6 - rank

    student_strengths = {t.tag.name: get_weight(t.rank) for t in student.tags.filter(tag_type='strength')}
    student_desires = {t.tag.name: get_weight(t.rank) for t in student.tags.filter(tag_type='desire')}

    company_needs = {t.tag.name: get_weight(t.rank) for t in company.tags.filter(tag_type='strength')}
    company_features = {t.tag.name: get_weight(t.rank) for t in company.tags.filter(tag_type='feature')}

    score_skills = 0
    matched_strengths = []
    
    for tag_name, s_weight in student_strengths.items():
        if tag_name in company_needs:
            c_weight = company_needs[tag_name]
            score_skills += (s_weight * c_weight)
            matched_strengths.append(tag_name)

    score_conditions = 0
    matched_conditions = []
    
    for tag_name, s_weight in student_desires.items():
        if tag_name in company_features:
            c_weight = company_features[tag_name]
            score_conditions += (s_weight * c_weight)
            matched_conditions.append(tag_name)

    MAX_SCORE_PER_SECTION = 55
    TOTAL_MAX = MAX_SCORE_PER_SECTION * 2

    total_score = score_skills + score_conditions
    percentage = (total_score / TOTAL_MAX) * 100

    return {
        'percentage': int(percentage),
        'matched_strengths': matched_strengths,
        'matched_conditions': matched_conditions
    }