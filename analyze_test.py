import analyze


def test_analyze_article():
    article = {
        'title': '여성 따라가며 몹쓸 짓을 한 30대 검거',
        'description': '몰카를 촬영한 혐의로...',
        'keywords': '',
    }
    assert ['molka', 'trivialize'] == analyze.analyze_article(article)


def test_trivialize():
    positives = [
        ('몹쓸 짓', '여성을 따라가며 "몹쓸 짓"을..'),
        ('검은 손', '여고생 유혹하는 검은 손길'),
    ]
    for description, text in positives:
        assert analyze.analyze_trivialize(text), description

    negatives = [
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('젠더 문제와 무관', '주식 시장 노리는 검은 손'),
    ]
    for description, text in negatives:
        assert not analyze.analyze_trivialize(text), description


def test_demonize():
    positives = [
        ('인면수심', '친딸을 성폭행한 인면수심의'),
        ('괴물', '친딸을 성폭행한 그는 괴물이었다'),
    ]
    for description, text in positives:
        assert analyze.analyze_demonize(text), description

    negatives = [
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('젠더 문제와 무관', '봉준호 감독의 괴물은'),
        ('작품명', '최영미 시인의 작품 "괴물"은 성폭력의'),
    ]
    for description, text in negatives:
        assert not analyze.analyze_demonize(text), description


def test_molka():
    positives = [
        ('몰카', '지하철에서 몰카 찍은 30대 덜미'),
        ('몰래카메라', '지하철에서 몰래카메라 찍은 30대 덜미'),
    ]
    for description, text in positives:
        assert analyze.analyze_molka(text), description

    negatives = [
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('파파라치 학원', '파파라치 학원을 운영하며 실제로는 몰카를 팔아'),
    ]
    for description, text in negatives:
        assert not analyze.analyze_molka(text), description


def test_metoo():
    positives = [
        ('한글표기', '김뫄뫄씨 미투(나도 당했다) 기자회견'),
        ('영문표기', '김뫄뫄씨 Me Too(나도 당했다) 기자회견'),
        ('미투를 고백', '김뫄뫄씨도 미투 피해 사실을 고백했다'),
    ]
    for description, text in positives:
        assert analyze.analyze_metoo(text), description

    negatives = [
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('미투와 당했다가 이어지지 않음', '미투(나도 고발한다)에 고발 당했다'),
        ('심경을 고백', '김뫄뫄씨도 당시의 심경을 고백했다'),
    ]
    for description, text in negatives:
        assert not analyze.analyze_metoo(text), description


def test_porn():
    positives = [
        ('리벤지 포르노', '김모씨가 리벤지 포르노를 촬영한 혐의로...'),
        ('리벤지포르노', '김모씨가 리벤지포르노를 촬영한 혐의로...'),
    ]
    for description, text in positives:
        assert analyze.analyze_porn(text), description

    negatives = [
        ('관련 키워드 없음', '무해하고 좋은 제목'),
    ]
    for description, text in negatives:
        assert not analyze.analyze_porn(text), description


def test_abuse():
    positives = [
        ('아동 포르노', '김모씨가 아동 포르노를 촬영한 혐의로...'),
        ('아동 음란물', '김모씨가 아동 음란물을 촬영한 혐의로...'),
        ('청소년 음란물', '김모씨가 청소년 음란물을 촬영한 혐의로...'),
        ('미성년자 음란물', '김모씨가 미성년자 음란물을 촬영한 혐의로...'),
    ]
    for description, text in positives:
        assert analyze.analyze_abuse(text), description

    negatives = [
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('잘못을 지적하는 기사', '아동 음란물이 아니라 성착취물...'),
    ]
    for description, text in negatives:
        assert not analyze.analyze_abuse(text), description


def test_bearing():
    positives = [
        ('저출산', '국내 저출산 문제가 심각...'),
    ]
    for description, text in positives:
        assert analyze.analyze_bearing(text), description

    negatives = [
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('출산율은 통계량이므로 허용', '2019년 출산율이 사상 최저'),
        ('저출산과 저출생을 함께 언급', '저출산을 저출생으로 고쳐쓰자'),
    ]
    for description, text in negatives:
        assert not analyze.analyze_bearing(text), description


def test_gender():
    positives = [
        ('이름(여)', '지난 주말 김뫄뫄(여)씨는'),
        ('이름(女)', '지난 주말 김뫄뫄(女)씨는'),
        ('이름(여성)', '지난 주말 김뫄뫄(여성)씨는'),
        ('이름(나이,여)', '지난 주말 김뫄뫄(20,여)씨는'),
        ('이름(여,나이)', '지난 주말 김뫄뫄(여,20)씨는'),
        ('여대생', '지난 주말 여고생 김뫄뫄씨는'),
    ]
    for description, text in positives:
        assert analyze.analyze_gender(text), description

    negatives = [
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('여남 모두 성별표기', '지난 주말 김뫄뫄(여)씨와 이솨솨(남)씨는'),
        ('여의도', '지난 주말 김뫄뫄(여의도)씨와'),
        ('물건(30여개)', '물건(30여개)를 입수하여'),
    ]
    for description, text in negatives:
        assert not analyze.analyze_gender(text), description


def test_profession():
    positives = [
        ('여의사', '김뫄뫄씨는 여의사에게 진료를'),
        ('여교사', '김뫄뫄씨는 여교사에게 교육을'),
    ]
    for description, text in positives:
        assert analyze.analyze_profession(text), description

    negatives = [
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('참여 의사', '김뫄뫄씨는 참여 의사를 밝혔다'),
        ('여남 모두 성별표기', '오늘 여의사 A씨와 남학생 B씨는'),
    ]
    for description, text in negatives:
        assert not analyze.analyze_profession(text), description


def test_neutral():
    positives = [
        ('남녀갈등', '남녀갈등이 심해지고 있다'),
        ('역차별', '김뫄뫄씨는 페미니즘이 역차별이라며'),
    ]
    for description, text in positives:
        assert analyze.analyze_neutral(text), description

    negatives = [
        ('관련 키워드 없음', '무해하고 좋은 제목'),
        ('젠더 문제와 무관', '정규직에 대한 역차별이라며'),
        ('유해성 논란', '한 여성이 전자담배의 유해성 논란으로'),
    ]
    for description, text in negatives:
        assert not analyze.analyze_neutral(text), description
