import re


def analyze_article(article):
    """제목, 본문, 키워드를 분석해서 분류용 태그들을 추출"""
    text = ';'.join([
        article['title'],
        article['description'],
        article['keywords'],
    ])

    tags = set()
    if analyze_trivialize(text):
        tags.add('trivialize')
    if analyze_demonize(text):
        tags.add('demonize')
    if analyze_molka(text):
        tags.add('molka')
    if analyze_porn(text):
        tags.add('porn')
    if analyze_abuse(text):
        tags.add('abuse')
    if analyze_metoo(text):
        tags.add('metoo')
    if analyze_bearing(text):
        tags.add('bearing')
    if analyze_gender(text):
        tags.add('gender')
    if analyze_profession(text):
        tags.add('profession')
    if analyze_neutral(text):
        tags.add('neutral')

    return sorted(tags)


def analyze_trivialize(text):
    """'몹쓸 짓' 등 성범죄를 미화하거나 축소하는 표현이 나오는지 검사"""
    return (
        analyze(text, r'몹쓸\s?짓|검은\s?손|홧김에') and
        is_gender_related(text)
    )


def analyze_demonize(text):
    """'인면수심' 등 범죄자를 악마화하거나 비일상적 인물로 묘사하는지 검사"""
    return (
        analyze(
            text,
            r'인면수심|악마|괴물|인간의 탈을',
            r'최(영미)?\s시인|봉준호'
        ) and
        is_gender_related(text)
    )


def analyze_molka(text):
    """'몰카', '몰래카메라'라는 표현이 나오는지 검사"""
    return analyze(
        text,
        r'몰카|몰래\s?카메라',
        r'파파라치\s?학원',
    )


def analyze_porn(text):
    """'리벤지 포르노'라는 표현이 나오는지 검사"""
    return analyze(text, r'리벤지\s*포르노')


def analyze_abuse(text):
    """'아동 포르노'라는 표현이 나오는지 검사"""
    return analyze(
        text,
        r'(아동|청소년|미성년자)\s?(포르노|음란물?)',
        r'착취',
    )


def analyze_metoo(text):
    """'미투'를 '나도 당했다'로, 피해 고발을 피해 고백으로 잘못 표기하는지
    검사"""
    return analyze(
        text,
        r'(미투|me\s?too).{1,5}당했다|미투.+피해.{1,5}고백|피해.{1,5}고백.+미투'
    )


PROFESSIONS = ['가수','교사', '교수', '기자', '배우', '연예인', '의사']

OCCUPATIONS = ['중생', '고생', '대생', '학생', '종업원', '직원']


def analyze_gender(text):
    """여성만 성별 표기를 하는지 검사"""
    return analyze(
        text,
        r'(\w+\((\d{0,3}.?[여|女]성?|[여|女]성?.?\d{0,3})\)|' \
        r'\b[여女][자성]?\s?(' + '|'.join(OCCUPATIONS) +  '))',
        r'(\w+\((\d{0,3}.?[남|男]성?|[남|男]성?.?\d{0,3})\)|' \
        r'\b[남男][자성]?\s?(' + '|'.join(PROFESSIONS) + '|중생|고생|대생|학생))',
    )


def analyze_profession(text):
    """여의사 등 여성 전문직만 차별적으로 표현하는지 검사"""
    return analyze(
        text,
        r'\b[여女][자성]?\s?(' + '|'.join(PROFESSIONS) + ')',
        r'\b[남男][자성]?\s?(' + '|'.join(PROFESSIONS + OCCUPATIONS) + ')',
    )


def analyze_neutral(text):
    """남녀갈등, 역차별, 페미니즘 논란 등 기계적 중립 표현 검사"""
    return (
        analyze(
            text,
            r'남성\s?혐오|(젠더|남녀|성)\s?(갈등|대립|대결)|페미(니즘)\s?논란|역차별'
        ) and is_gender_related(text)
    )


def analyze_bearing(text):
    """'저출산'이라는 용어를 쓰는지 검사"""
    return analyze(text, r'저출산', r'저출생')


def analyze(text, p_pos, p_neg=None):
    """텍스트가 p_pos와 일치하고 p_neg와 불일치하는지 검사"""
    return bool(
        re.search(p_pos, text, re.I) and
        (p_neg is None or not re.search(p_neg, text, re.I))
    )


def is_gender_related(text):
    return analyze(
        text,
        r'강간|성\s?(매매|범죄|차별|추행|폭력|폭행|행위)|임신|' \
        r'[여女][자성]?\s?(' + '|'.join(PROFESSIONS + OCCUPATIONS) + ')|' \
        r'여아|소녀|모녀|부녀|딸|동생|동료|제자|후배|' \
        r'여성|성별|남.?녀|男.?女|젠더|페미(니즘)'
        )
