import statistics

from itertools import groupby


def aggregate_by_date_cp_tag(articles):
    """원본 데이터를 받아서 일별/언론별/태그별로 집계"""
    counters = {}
    for i, a in enumerate(articles):
        if i >= 50000 and i % 50000 == 0:
            print(f'{i}')
        for tag in a['tags'] or ['clean']:
            key = (a['date'], a['cp_name'], tag)
            counters[key] = counters.get(key, 0) + 1

    keys = sorted(counters.keys())
    return [
        {'date': k[0], 'cp_name': k[1], 'tag': k[2], 'count': counters[k]}
        for k in keys
    ]


def frequent_tags(table):
    """일별/언론별/태그별 집계 테이블을 받아서 태그별로 재집계한 후 가장
    빈번한 태그 순으로 정렬"""
    counters = {}
    total = 0
    for row in (r for r in table if r['tag'] != 'clean'):
        counters[row['tag']] = counters.get(row['tag'], 0) + row['count']
        total += row['count']

    results = (
        {'tag': tag, 'count': count, 'total': total, 'ratio': count / total}
        for tag, count in counters.items()
    )
    return sorted(results, key=lambda row: (-row['ratio'], row['tag']))


def daily_articles(table):
    """일별/언론별/태그별 집계 테이블을 받아서 일별로 재집계"""
    results = []

    # 일별 단순 집계
    for date, group in groupby(table, key=lambda row: row['date']):
        day = {'date': date, 'bad': 0, 'clean': 0, 'total': 0, 'ratio': 0}
        for row in group:
            if row['tag'] == 'clean':
                day['clean'] += row['count']
            else:
                day['bad'] += row['count']
            day['total'] += row['count']
        day['ratio'] = day['bad'] / day['total']
        results.append(day)

    # 평균과 표준편차 구하기
    ratio_mean = statistics.mean(d['ratio'] for d in results)
    ratio_sd = statistics.stdev(d['ratio'] for d in results)

    # 일별 표준점수 추가
    return [{**d, 'z': (d['ratio'] - ratio_mean) / ratio_sd} for d in results]


def best_cps(table, min_count):
    """일별/언론별/태그별 집계 테이블을 받아서 언론사별로 재집계한 후 가장
    부적절한 표현의 비율이 낮은 순으로 정렬"""
    results = _cps(table, min_count)
    return sorted(results, key=lambda row: (row['ratio'], -row['total']))


def worst_cps(table, min_count):
    """일별/언론별/태그별 집계 테이블을 받아서 언론사별로 재집계한 후 가장
    부적절한 표현의 비율이 높은 순으로 정렬"""
    results = _cps(table, min_count)
    return sorted(results, key=lambda row: (-row['ratio'], -row['total']))


def _cps(table, min_count):
    """일별/언론별/태그별 집계 테이블을 받아서 언론사별로 재집계"""
    counters = {}
    for row in table:
        counter = counters.get(row['cp_name'], {'clean': 0, 'bad': 0})
        if row['tag'] == 'clean':
            counter['clean'] += row['count']
        else:
            counter['bad'] += row['count']
        counters[row['cp_name']] = counter

    return (
        {
            'cp_name': cp_name,
            'clean': counter['clean'],
            'bad': counter['bad'],
            'total': counter['clean'] + counter['bad'],
            'ratio': counter['bad'] / (counter['clean'] + counter['bad']),
        }
        for cp_name, counter in counters.items()
        if counter['clean'] + counter['bad'] >= min_count
    )


def mask(name):
    masked = []
    for i, c in enumerate(name):
        if '가' <= c <= '힣':
            # 한글이면 자음 추출
            ch1 = (ord(c) - ord('가')) // 588
            ## 중성은 총 28가지 종류
            ch2 = ((ord(c) - ord('가')) - (588 * ch1)) // 28
            ch3 = (ord(c) - ord('가')) - (588 * ch1) - 28 * ch2
            masked.append(chr(ch1 + 0x1100))
        elif '0' <= c <= '9':
            # 숫자는 그대로
            masked.append(c)
        else:
            # 나머지는 첫글자 뺴고 마스킹
            masked.append(c if i == 0 else '○')

    return ''.join(masked)

