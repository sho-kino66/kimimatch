def calculate_match_percentage(student, company):
    """
    学生と企業のマッチ度を計算する関数
    戻り値: int (0-100)
    """
    # 重み定義 (1位:5点 ... 5位:1点)
    def get_weight(rank):
        return 6 - rank

    # 学生のタグ取得
    student_strengths = {t.tag.name: get_weight(t.rank) for t in student.tags.filter(tag_type='strength')}
    student_desires = {t.tag.name: get_weight(t.rank) for t in student.tags.filter(tag_type='desire')}

    # 企業のタグ取得
    company_needs = {t.tag.name: get_weight(t.rank) for t in company.tags.filter(tag_type='strength')}
    company_features = {t.tag.name: get_weight(t.rank) for t in company.tags.filter(tag_type='feature')}

    # 1. スキルマッチ（学生の強み vs 企業の求める強み）
    score_skills = 0
    for tag_name, s_weight in student_strengths.items():
        if tag_name in company_needs:
            c_weight = company_needs[tag_name]
            score_skills += (s_weight * c_weight)

    # 2. 条件マッチ（学生の要望 vs 企業の政策）
    score_conditions = 0
    for tag_name, s_weight in student_desires.items():
        if tag_name in company_features:
            c_weight = company_features[tag_name]
            score_conditions += (s_weight * c_weight)

    # 最大スコア (片側 55点 * 2 = 110点満点)
    # 計算: (5*5 + 4*4 + 3*3 + 2*2 + 1*1) = 55
    MAX_SCORE_PER_SECTION = 55
    TOTAL_MAX = MAX_SCORE_PER_SECTION * 2

    total_score = score_skills + score_conditions
    percentage = (total_score / TOTAL_MAX) * 100

    return int(percentage)