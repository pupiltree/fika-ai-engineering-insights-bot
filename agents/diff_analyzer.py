from typing import Dict, List
from datetime import datetime, timedelta
import random

class DiffAnalyzerAgent:
    def __init__(self):
        self.name = "DiffAnalyzer"
        print(f"🔧 {self.name} initialized")

    def run(self, github_data: Dict) -> Dict:
        print(f"📊 {self.name}: Analyzing commit data...")
        try:
            commits = github_data.get('commits', [])
            prs = github_data.get('prs', [])
            if not commits:
                return self.get_empty_analysis()
            churn_analysis = self.analyze_churn(commits)
            risk_assessment = self.assess_risk(commits, churn_analysis['avg_churn'])
            author_metrics = self.aggregate_author_stats(commits)
            pr_stats = self.analyze_prs(prs)
            ci_failures = self.analyze_ci_failures(prs)
            review_latency = self.analyze_review_latency(prs)
            temporal_patterns = self.analyze_temporal_patterns(commits)
            dora_metrics = self.calculate_dora_metrics(commits, pr_stats, ci_failures)
            after_hours_count = sum(1 for c in commits if c.get('after_hours'))
            risky_commit_count = sum(1 for c in commits if c.get('is_risky'))
            risky_commits = [c['sha'] for c in commits if c.get('is_risky')]
            return {
                'churn_analysis': churn_analysis,
                'risk_assessment': risk_assessment,
                'author_metrics': author_metrics,
                'pr_stats': pr_stats,
                'ci_failures': ci_failures,
                'review_latency': review_latency,
                'temporal_patterns': temporal_patterns,
                'dora_metrics': dora_metrics,
                'after_hours_commits': after_hours_count,
                'risky_commit_count': risky_commit_count,
                'risky_commits': risky_commits
            }
        except Exception as e:
            print(f"❌ DiffAnalyzer error: {e}")
            return self.get_empty_analysis()

    def analyze_churn(self, commits: List[Dict]) -> Dict:
        import statistics
        total_additions = sum(c.get('additions', 0) for c in commits)
        total_deletions = sum(c.get('deletions', 0) for c in commits)
        total_churn = total_additions + total_deletions
        avg_churn = total_churn / len(commits) if commits else 0
        net_change = total_additions - total_deletions
        churn_values = [(c.get('additions', 0) + c.get('deletions', 0)) for c in commits]
        stdev_churn = statistics.stdev(churn_values) if len(churn_values) > 1 else 0
        churn_outliers = [c for c in commits if (c.get('additions', 0) + c.get('deletions', 0)) > avg_churn + 2*stdev_churn]
        churn_spikes = [c for c in commits if (c.get('additions', 0) + c.get('deletions', 0)) > avg_churn * 1.5]

        return {
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'net_change': net_change,
            'total_churn': total_churn,
            'avg_churn': round(avg_churn, 2),
            'spike_count': len(churn_spikes),
            'stdev_churn': round(stdev_churn, 2),
            'outlier_count': len(churn_outliers)
        }

    def assess_risk(self, commits: List[Dict], avg_churn: float) -> Dict:
        high_risk = []
        medium_risk = []

        for c in commits:
            churn = c.get('additions', 0) + c.get('deletions', 0)
            if churn > avg_churn * 2:
                high_risk.append(c['sha'])
            elif churn > avg_churn * 1.2:
                medium_risk.append(c['sha'])

        return {
            'high_risk_commits': high_risk,
            'medium_risk_commits': medium_risk,
            'total_risky_commits': len(high_risk) + len(medium_risk),
            'risk_percentage': round((len(high_risk) + len(medium_risk)) / len(commits) * 100, 2)
        }

    def aggregate_author_stats(self, commits: List[Dict]) -> Dict:
        author_data = {}
        for c in commits:
            author = c.get('author', 'unknown')
            if author not in author_data:
                author_data[author] = {
                    'commits': 0,
                    'total_churn': 0,
                    'files_changed': 0,
                    'after_hours_commits': 0
                }
            author_data[author]['commits'] += 1
            author_data[author]['total_churn'] += c.get('additions', 0) + c.get('deletions', 0)
            author_data[author]['files_changed'] += c.get('files_changed', 0)
            try:
                dt = datetime.fromisoformat(c['date'].replace('Z', '+00:00'))
                if dt.hour < 9 or dt.hour > 19:
                    author_data[author]['after_hours_commits'] += 1
            except:
                pass
        return author_data

    def analyze_prs(self, prs: list) -> dict:
        if not prs:
            return {'total_prs': 0, 'avg_review_latency_hrs': 0, 'failed_prs': 0}
        total_prs = len(prs)
        avg_review_latency = sum(pr.get('review_latency_hrs', 0) for pr in prs) / total_prs
        failed_prs = sum(1 for pr in prs if pr.get('ci_status') == 'failure')
        return {
            'total_prs': total_prs,
            'avg_review_latency_hrs': round(avg_review_latency, 2),
            'failed_prs': failed_prs
        }

    def analyze_ci_failures(self, prs: list) -> dict:
        total = len(prs)
        failed = sum(1 for pr in prs if pr.get('ci_status') == 'failure')
        return {
            'total_ci_failures': failed,
            'ci_failure_rate': round((failed / total) * 100, 1) if total else 0
        }

    def analyze_review_latency(self, prs: list) -> dict:
        if not prs:
            return {'avg_review_latency_hrs': 0, 'max_review_latency_hrs': 0}
        latencies = [pr.get('review_latency_hrs', 0) for pr in prs]
        return {
            'avg_review_latency_hrs': round(sum(latencies) / len(latencies), 2),
            'max_review_latency_hrs': round(max(latencies), 2)
        }

    def mock_pr_data(self, commit_count: int) -> Dict:
        total_prs = int(commit_count / 3)
        return {
            'total_prs': total_prs,
            'avg_changes_per_pr': round((commit_count * 150) / total_prs, 2) if total_prs else 0
        }

    def mock_ci_failures(self, commit_count: int) -> Dict:
        failed = random.randint(0, int(commit_count * 0.1))
        return {
            'total_ci_failures': failed,
            'ci_failure_rate': round((failed / commit_count) * 100, 1) if commit_count else 0
        }

    def mock_review_latency(self) -> Dict:
        return {
            'avg_review_latency_hrs': round(random.uniform(5, 36), 2),
            'max_review_latency_hrs': round(random.uniform(24, 72), 2)
        }

    def analyze_temporal_patterns(self, commits: List[Dict]) -> Dict:
        after_hours = 0
        weekday_counts = [0]*7
        for c in commits:
            try:
                dt = datetime.fromisoformat(c['date'].replace('Z', '+00:00'))
                if dt.hour < 9 or dt.hour > 19:
                    after_hours += 1
                weekday_counts[dt.weekday()] += 1
            except:
                continue
        return {
            'after_hours_commits': after_hours,
            'weekday_commit_distribution': weekday_counts
        }

    def calculate_dora_metrics(self, commits: List[Dict], pr_stats: Dict, ci_failures: Dict) -> Dict:
        deploy_freq = pr_stats.get('total_prs', 0)
        if commits:
            dates = sorted([datetime.fromisoformat(c['date'].replace('Z', '+00:00')) for c in commits])
            lead_time_hrs = (dates[-1] - dates[0]).total_seconds() / 3600 if len(dates) > 1 else 0
        else:
            lead_time_hrs = 0
        change_failure_rate = ci_failures.get('ci_failure_rate', 0)
        mttr_hrs = round(random.uniform(1, 12), 2)
        return {
            'deployment_frequency': deploy_freq,
            'lead_time_hrs': round(lead_time_hrs, 2),
            'change_failure_rate': change_failure_rate,
            'mttr_hrs': mttr_hrs
        }

    def get_empty_analysis(self) -> Dict:
        return {
            'churn_analysis': {},
            'risk_assessment': {},
            'author_metrics': {},
            'pr_stats': {},
            'ci_failures': {},
            'review_latency': {},
            'temporal_patterns': {},
            'dora_metrics': {}
        }
