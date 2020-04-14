import csv
import os
import statistics
import sys
from datetime import datetime, timedelta

import fire

import analyze
import stats

SRC_DIR = 'data'
DATA_DIR = 'docs/_data'

FIELDS = [
    'article_id', 'cp_name', 'title', 'description', 'authors', 'keywords',
    'date', 'url', 'tags'
]


class CLI:
    """News analyzer"""
    def tag_and_stats(self):
        articles = list(self._prepare())
        self._tag(articles)
        self._stats(articles)

    def tag(self):
        """기사 전체를 분석하여 분류 태그를 추가한 후 별도 파일로 저장"""
        articles = self._prepare()
        self._tag(articles)

    def stats(self):
        """통계분석"""
        articles = self._prepare()
        self._stats(articles)

    def _tag(self, articles):
        with open(os.path.join(DATA_DIR, 'articles.csv'), 'w') as f:
            csvw = csv.DictWriter(f, FIELDS)
            csvw.writeheader()
            for article in articles:
                if len(article['tags']) == 0:
                    continue

                csvw.writerow({
                    **article,
                    'tags': ';'.join(article['tags']),
                })

    def _stats(self, articles):
        # 일별/언론별/분류별 빈도 집계
        print('Creating stats.csv...')
        table = stats.aggregate_by_date_cp_tag(articles)
        with open(os.path.join(DATA_DIR, 'stats.csv'), 'w') as f:
            fields = ['date', 'cp_name', 'tag', 'count']
            csvw = csv.DictWriter(f, fields)
            csvw.writeheader()
            csvw.writerows(table)

        # 일별 집계
        print('Creating stats_daily.csv...')
        daily = stats.daily_articles(table)
        with open(os.path.join(DATA_DIR, 'stats_daily.csv'), 'w') as f:
            fields = ['date', 'clean', 'bad', 'total', 'ratio', 'z']
            csvw = csv.DictWriter(f, fields)
            csvw.writeheader()
            csvw.writerows(daily)

        # 가장 빈도가 높은 태그 집계
        print('Creating stats_freq_tags.csv...')
        freq_tags = stats.frequent_tags(table)
        with open(os.path.join(DATA_DIR, 'stats_freq_tags.csv'), 'w') as f:
            fields = ['tag', 'count', 'total', 'ratio']
            csvw = csv.DictWriter(f, fields)
            csvw.writeheader()
            csvw.writerows(freq_tags)

        # 가장 부적절한 표현이 담긴 기사의 비율이 낮은 언론사 집계
        # (단, 기사가 200개 이상인 경우만)
        print('Creating stats_best_tags.csv...')
        best_cps = stats.best_cps(table, min_count=200)
        with open(os.path.join(DATA_DIR, 'stats_best_cps.csv'), 'w') as f:
            fields = [
                'cp_name', 'cp_name_masked', 'clean', 'bad', 'total', 'ratio'
            ]
            csvw = csv.DictWriter(f, fields)
            csvw.writeheader()
            csvw.writerows({
                **c, 'cp_name_masked': stats.mask(c['cp_name'])
            } for c in best_cps)

        # 가장 부적절한 표현이 담긴 기사의 비율이 높은 언론사 집계
        # (단, 기사가 200개 이상인 경우만)
        print('Creating stats_worst_tags.csv...')
        worst_cps = stats.worst_cps(table, min_count=200)
        with open(os.path.join(DATA_DIR, 'stats_worst_cps.csv'), 'w') as f:
            fields = [
                'cp_name', 'cp_name_masked', 'clean', 'bad', 'total', 'ratio'
            ]
            csvw = csv.DictWriter(f, fields)
            csvw.writeheader()
            csvw.writerows({
                **c, 'cp_name_masked': stats.mask(c['cp_name'])
            } for c in worst_cps)

    def test(self, tag):
        """기사 전체 중 특정 분류에 속하는 기사만 출력. 개발 중 테스트용"""
        articles = (a for a in self._prepare() if tag in a['tags'])
        csvw = csv.DictWriter(sys.stdout, FIELDS)
        csvw.writeheader()
        csvw.writerows(articles)

    def _prepare(self):
        overrides = self._load_override_rules()
        articles = self._analyze_articles(self._get_articles(), overrides)
        os.makedirs(DATA_DIR, exist_ok=True)
        return articles

    def _get_articles(self):
        """Yields all articles in SRC_DIR"""
        filenames = (fn for fn in sorted(os.listdir(SRC_DIR))
                     if fn.endswith('.csv'))
        for filename in filenames:
            date = filename[:-4]
            with open(os.path.join(SRC_DIR, filename), 'r') as f:
                csvr = csv.DictReader(f)
                for a in csvr:
                    a['url'] = 'https://news.v.daum.net/v/' + a['article_id']
                    a['date'] = date
                    yield a

    def _analyze_articles(self, articles, overrides):
        """Analyze articles"""
        for i, article in enumerate(articles):
            if i >= 50000 and i % 50000 == 0:
                print(f'Analyzed {i} articles')
            yield analyze.analyze_article(article, overrides)

    def _load_override_rules(self):
        with open('overrides.csv', 'r') as f:
            csvr = csv.DictReader(f)
            return {r['article_id']: r['rules'].split(' ') for r in csvr}


if __name__ == '__main__':
    fire.Fire(CLI())
