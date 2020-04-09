import re
import analyze


def test_analyze_article():
    article = {
        'article_id': '1',
        'title': '여성에게 몹쓸 짓을',
        'description': '몰카를 촬영한 혐의로',
        'keywords': '',
    }
    marked = analyze.analyze_article(article, {})
    assert marked['tags'] == ['molka', 'trivialize']
    assert marked['title'] == '여성에게 {trivialize}몹쓸 짓{/trivialize}을'
    assert marked['description'] == '{molka}몰카{/molka}를 촬영한 혐의로'


def test_manual_override():
    article = {
        'article_id': '1',
        'title': '"여성에게 몹쓸 짓"이라는 표현의 문제점',
        'description': '...',
        'keywords': '',
    }
    overrides = {
        '1': ['-trivialize', '+molka'],
    }
    marked = analyze.analyze_article(article, overrides)
    assert marked['tags'] == ['molka']
    assert marked['title'] == article['title']


def test_trivialize():
    cases = [
        # positives
        ('몹쓸 짓', '여성에게 "{trivialize}몹쓸 짓{/trivialize}"을..'),
        ('검은 손', '여고생 유혹하는 {trivialize}검은 손{/trivialize}길'),
        # negatives
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('젠더 문제와 무관', '주식 시장 노리는 검은 손'),
        ('젠더 문제와 무관', '여성이 홧김에 방화'),
    ]
    for description, text in cases:
        _, marked = analyze.analyze_trivialize(strip_markup(text))
        assert marked == text


def test_demonize():
    cases = [
        # positives
        ('인면수심', '친딸을 성폭행한 {demonize}인면수심{/demonize}의'),
        ('괴물', '친딸을 성폭행한 그는 {demonize}괴물{/demonize}이었다'),
        # negatives
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('젠더 문제와 무관', '봉준호 감독의 괴물은'),
        ('작품명', '최영미 시인의 작품 "괴물"은 성폭력의'),
        ('상품명', '여성들 사이에서 액체 괴물 유행'),
    ]
    for description, text in cases:
        _, marked = analyze.analyze_demonize(strip_markup(text))
        assert marked == text, description


def test_molka():
    cases = [
        # positives
        ('몰카', '지하철에서 {molka}몰카{/molka} 찍은 30대 덜미'),
        ('몰래카메라', '지하철에서 {molka}몰래카메라{/molka} 찍은 30대 덜미'),
        # negatives
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('파파라치 학원', '파파라치 학원을 운영하며 실제로는 몰카를 팔아'),
    ]
    for description, text in cases:
        _, marked = analyze.analyze_molka(strip_markup(text))
        assert marked == text, description


def test_metoo():
    cases = [
        # positives
        ('한글표기', '김뫄뫄씨 {metoo}미투(나도 당했다){/metoo} 기자회견'),
        ('영문표기', '김뫄뫄씨 {metoo}me too (나도 당했다){/metoo} 기자회견'),
        ('괄호 안 설명', '김뫄뫄씨 {metoo}미투(metoo, 나도 당했다){/metoo}'),
        ('미투를 고백', '김뫄뫄씨도 {metoo}미투 피해 사실을 고백{/metoo}했다'),
        # negatives
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('미투와 당했다가 이어지지 않음', '미투(나도 고발한다)에 고발 당했다'),
        ('심경을 고백', '김뫄뫄씨도 당시의 심경을 고백했다'),
    ]
    for description, text in cases:
        _, marked = analyze.analyze_metoo(strip_markup(text))
        assert marked == text, description


def test_porn():
    cases = [
        # positives
        ('리벤지 포르노', '김모씨가 {porn}리벤지 포르노{/porn}를 유포...'),
        ('리벤지포르노', '김모씨가 {porn}리벤지포르노{/porn}를 유포...'),
        # negatives
        ('관련 키워드 없음', '무해하고 좋은 제목'),
    ]
    for description, text in cases:
        _, marked = analyze.analyze_porn(strip_markup(text))
        assert marked == text, description


def test_abuse():
    cases = [
        # positives
        ('아동 포르노', '김모씨가 {abuse}아동 포르노{/abuse}를 촬영'),
        ('아동 음란물', '김모씨가 {abuse}아동 음란물{/abuse}을 촬영'),
        ('청소년 음란물', '김모씨가 {abuse}청소년 음란물{/abuse}을 촬영'),
        ('미성년자 음란물', '김모씨가 {abuse}미성년자 음란물{/abuse}을 촬영'),
        # negatives
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('잘못을 지적하는 기사', '아동 음란물이 아니라 성착취물...'),
    ]
    for description, text in cases:
        _, marked = analyze.analyze_abuse(strip_markup(text))
        assert marked == text, description


def test_bearing():
    cases = [
        # positives
        ('저출산', '국내 {bearing}저출산{/bearing} 문제가 심각...'),
        # negatives
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('출산율은 통계량이므로 허용', '2019년 출산율이 사상 최저'),
        ('저출산과 저출생을 함께 언급', '저출산을 저출생으로 고쳐쓰자'),
    ]
    for description, text in cases:
        _, marked = analyze.analyze_bearing(strip_markup(text))
        assert marked == text, description


def test_gender():
    cases = [
        # positives
        ('이름(여)', '지난 주말 {gender}김뫄뫄(여){/gender}씨는'),
        ('이름(女)', '지난 주말 {gender}김뫄뫄(女){/gender}씨는'),
        ('이름(여성)', '지난 주말 {gender}김뫄뫄(여성){/gender}씨는'),
        ('이름(나이,여)', '지난 주말 {gender}김뫄뫄(20,여){/gender}씨는'),
        ('이름(여,나이)', '지난 주말 {gender}김뫄뫄(여,20){/gender}씨는'),
        ('여대생', '지난 주말 {gender}여고생{/gender} 김뫄뫄씨는'),
        # negatives
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('여남 모두 성별표기', '지난 주말 김뫄뫄(여)씨와 이솨솨(남)씨는'),
        ('여의도', '지난 주말 김뫄뫄(여의도)씨와'),
        ('물건(30여개)', '물건(30여개)를 입수하여'),
    ]
    for description, text in cases:
        _, marked = analyze.analyze_gender(strip_markup(text))
        assert marked == text, description


def test_profession():
    cases = [
        # positives
        ('여의사', '김뫄뫄씨는 {profession}여의사{/profession}에게 진료를'),
        ('여교사', '김뫄뫄씨는 {profession}여교사{/profession}에게 교육을'),
        # negatives
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('참여 의사', '김뫄뫄씨는 참여 의사를 밝혔다'),
        ('여남 모두 성별표기', '오늘 여의사 A씨와 남학생 B씨는'),
    ]
    for description, text in cases:
        _, marked = analyze.analyze_profession(strip_markup(text))
        assert marked == text, description


def test_neutral():
    cases = [
        # positives
        ('남녀갈등', '{neutral}남녀갈등{/neutral}이 심해지고 있다'),
        ('역차별', '김뫄뫄씨는 페미니즘이 {neutral}역차별{/neutral}이라며'),
        # negatives
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('젠더 문제와 무관', '정규직에 대한 역차별이라며'),
        ('유해성 논란', '한 여성이 전자담배의 유해성 논란으로'),
    ]
    for description, text in cases:
        _, marked = analyze.analyze_neutral(strip_markup(text))
        assert marked == text, description


def strip_markup(text):
    return re.sub(r'\{.+?\}', '', text)
