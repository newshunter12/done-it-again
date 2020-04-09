import csv
import os
import statistics
import sys
from datetime import datetime, timedelta

import fire

import analyze
import stats


SRC_DIR = 'news/docs/data'
DATA_DIR = 'docs/_data'

FIELDS = [
    'date', 'article_id', 'original_url', 'daum_url', 'image_url',
    'cp_url', 'cp_name', 'title', 'description', 'author', 'keywords',
    'tags',
]


class CLI:
    """News analyzer"""
    def tag(self):
        """기사 전체를 분석하여 분류 태그를 추가한 후 별도 파일로 저장"""
        overrides = self._load_override_rules()
        articles = self._analyze_articles(self._get_articles(), overrides)
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(os.path.join(DATA_DIR, 'articles.csv'), 'w') as f:
            csvw = csv.DictWriter(f, FIELDS)
            csvw.writeheader()
            for article in articles:
                if len(article['tags']) == 0:
                    continue
                article['tags'] = ';'.join(article['tags'])
                csvw.writerow(article)

    def stats(self):
        """통계분석"""
        overrides = self._load_override_rules()
        articles = self._analyze_articles(self._get_articles(), overrides)
        os.makedirs(DATA_DIR, exist_ok=True)

        # 일별/언론별/분류별 빈도 집계
        table = stats.aggregate_by_date_cp_tag(articles)
        with open(os.path.join(DATA_DIR, 'stats.csv'), 'w') as f:
            fields = ['date', 'cp_name', 'tag', 'count']
            csvw = csv.DictWriter(f, fields)
            csvw.writeheader()
            csvw.writerows(table)

        # 최근 6개월 이내 데이터만 남기기
        latest = datetime.strptime(max(t['date'] for t in table), '%Y%m%d')
        window = (latest - timedelta(days=180)).strftime('%Y%m%d')
        recent_table = [t for t in table if t['date'] >= window]

        # 일별 집계
        daily = stats.daily_articles(recent_table)
        with open(os.path.join(DATA_DIR, 'stats_daily.csv'), 'w') as f:
            fields = ['date', 'clean', 'bad', 'total', 'ratio', 'z']
            csvw = csv.DictWriter(f, fields)
            csvw.writeheader()
            csvw.writerows(daily)

        # 최근 6개월 이내에 가장 빈도가 높은 태그 집계
        freq_tags = stats.frequent_tags(recent_table)
        with open(os.path.join(DATA_DIR, 'stats_freq_tags.csv'), 'w') as f:
            fields = ['tag', 'count', 'total', 'ratio']
            csvw = csv.DictWriter(f, fields)
            csvw.writeheader()
            csvw.writerows(freq_tags)

        # 최근 6개월 이내에 가장 부적절한 표현이 담긴 기사의 비율이 낮은
        # 언론사 집계 (단, 최근 6개월 이내에 기사가 50개 이상인 경우만)
        best_cps = stats.best_cps(recent_table, min_count=50)
        with open(os.path.join(DATA_DIR, 'stats_best_cps.csv'), 'w') as f:
            fields = ['cp_name', 'cp_name_masked', 'clean', 'bad', 'total',
                      'ratio']
            csvw = csv.DictWriter(f, fields)
            csvw.writeheader()
            csvw.writerows({**c, 'cp_name_masked': stats.mask(c['cp_name'])}
                           for c in best_cps)

        # 최근 6개월 이내에 가장 부적절한 표현이 담긴 기사의 비율이 높은
        # 언론사 집계 (단, 최근 6개월 이내에 기사가 50개 이상인 경우만)
        worst_cps = stats.worst_cps(recent_table, min_count=50)
        with open(os.path.join(DATA_DIR, 'stats_worst_cps.csv'), 'w') as f:
            fields = ['cp_name', 'cp_name_masked', 'clean', 'bad', 'total',
                      'ratio']
            csvw = csv.DictWriter(f, fields)
            csvw.writeheader()
            csvw.writerows({**c, 'cp_name_masked': stats.mask(c['cp_name'])}
                           for c in worst_cps)

    def test(self, tag):
        """기사 전체 중 특정 분류에 속하는 기사만 출력. 개발 중 테스트용"""
        articles = (
            a for a in self._analyze_articles(self._get_articles())
            if tag in a['tags']
        )
        csvw = csv.DictWriter(sys.stdout, FIELDS)
        csvw.writeheader()
        csvw.writerows(articles)

    def _get_articles(self):
        """Yields all articles in SRC_DIR"""
        for filename in sorted(os.listdir(SRC_DIR)):
            date = filename[:-4]
            with open(os.path.join(SRC_DIR, filename), 'r') as f:
                csvr = csv.DictReader(f)
                for article in csvr:
                    article['date'] = date
                    yield article

    def _analyze_articles(self, articles, overrides):
        """Analyze articles"""
        for article in articles:
            yield analyze.analyze_article(article, overrides)

    def _load_override_rules(self):
        with open(os.path.join(DATA_DIR, 'overrides.csv'), 'r') as f:
            csvr = csv.DictReader(f)
            return {r['article_id']: r['rules'].split(' ') for r in csvr}


if __name__ == '__main__':
    fire.Fire(CLI())

