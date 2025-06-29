import statistics
from typing import Dict, List
from datetime import datetime, timedelta

class DiffAnalystAgent:
    """Code churn and diff analysis agent"""
    
    def __init__(self):
        self.name = "DiffAnalyst"
        self.churn_threshold = 300
        print(f"🔧 {self.name} initialized")
    
    def run(self, github_data: Dict) -> Dict:
        print(f"📊 {self.name}: Analyzing code churn and patterns")
        
        commits = github_data.get('commits', [])
        
        if not commits:
            print("⚠️ No commits to analyze")
            return self.get_empty_analysis()
        
        analysis = {
            'churn_analysis': self.analyze_churn(commits),
            'author_metrics': self.calculate_author_metrics(commits),
            'risk_assessment': self.assess_defect_risk(commits),
            'temporal_patterns': self.analyze_temporal_patterns(commits),
            'outliers': self.detect_outliers(commits),
            'summary': self.generate_analysis_summary(commits)
        }
        
        print(f"✅ Analysis complete: {len(commits)} commits, {len(analysis['author_metrics'])} authors")
        return analysis
    
    def analyze_churn(self, commits: List[Dict]) -> Dict:
        """Analyze overall code churn patterns"""
        if not commits:
            return {}
        
        total_churn = [c['total'] for c in commits]
        additions = [c['additions'] for c in commits]
        deletions = [c['deletions'] for c in commits]
        
        return {
            'total_commits': len(commits),
            'avg_churn': round(statistics.mean(total_churn), 1),
            'median_churn': round(statistics.median(total_churn), 1),
            'max_churn': max(total_churn),
            'min_churn': min(total_churn),
            'total_additions': sum(additions),
            'total_deletions': sum(deletions),
            'net_change': sum(additions) - sum(deletions),
            'churn_std_dev': round(statistics.stdev(total_churn) if len(total_churn) > 1 else 0, 1)
        }
    
    def calculate_author_metrics(self, commits: List[Dict]) -> Dict:
        """Calculate per-author metrics"""
        author_stats = {}
        
        for commit in commits:
            author = commit['author']
            if author not in author_stats:
                author_stats[author] = {
                    'commits': 0,
                    'total_churn': 0,
                    'additions': 0,
                    'deletions': 0,
                    'files_touched': 0,
                    'avg_churn_per_commit': 0,
                    'largest_commit': 0,
                    'commit_messages': []
                }
            
            stats = author_stats[author]
            stats['commits'] += 1
            stats['total_churn'] += commit['total']
            stats['additions'] += commit['additions']
            stats['deletions'] += commit['deletions']
            stats['files_touched'] += commit['files_changed']
            stats['largest_commit'] = max(stats['largest_commit'], commit['total'])
            stats['commit_messages'].append(commit['message'][:50])
        
        # Calculate averages and productivity scores
        for author, stats in author_stats.items():
            stats['avg_churn_per_commit'] = round(stats['total_churn'] / stats['commits'], 1)
            stats['avg_files_per_commit'] = round(stats['files_touched'] / stats['commits'], 1)
            
            # Productivity score (balanced metric)
            productivity_score = (stats['commits'] * 0.3 + 
                                (stats['total_churn'] / 100) * 0.4 + 
                                (stats['files_touched'] / 10) * 0.3)
            stats['productivity_score'] = round(productivity_score, 1)
        
        return author_stats
    
    def assess_defect_risk(self, commits: List[Dict]) -> Dict:
        """Assess defect risk based on churn patterns"""
        risk_factors = []
        
        for commit in commits:
            risk_score = 0
            factors = []
            
            # High churn risk
            if commit['total'] > self.churn_threshold:
                risk_score += 3
                factors.append('high_churn')
            
            # Many files changed
            if commit['files_changed'] > 8:
                risk_score += 2
                factors.append('many_files')
            
            # High deletion ratio (might indicate major refactoring)
            deletion_ratio = commit['deletions'] / max(commit['additions'], 1)
            if deletion_ratio > 0.7:
                risk_score += 1
                factors.append('high_deletion_ratio')
            
            # Very large single commit
            if commit['total'] > 1000:
                risk_score += 2
                factors.append('massive_commit')
            
            if risk_score > 0:
                risk_factors.append({
                    'commit': commit['sha'],
                    'author': commit['author'],
                    'risk_score': risk_score,
                    'factors': factors,
                    'churn': commit['total'],
                    'message': commit['message'][:100]
                })
        
        # Categorize risks
        high_risk = [r for r in risk_factors if r['risk_score'] >= 5]
        medium_risk = [r for r in risk_factors if 2 <= r['risk_score'] < 5]
        low_risk = [r for r in risk_factors if r['risk_score'] < 2]
        
        return {
            'high_risk_commits': high_risk,
            'medium_risk_commits': medium_risk,
            'low_risk_commits': low_risk,
            'total_risky_commits': len(risk_factors),
            'risk_percentage': round((len(risk_factors) / len(commits)) * 100, 1) if commits else 0
        }
    
    def analyze_temporal_patterns(self, commits: List[Dict]) -> Dict:
        """Analyze temporal commit patterns"""
        day_patterns = {}
        hour_patterns = {}
        
        for commit in commits:
            try:
                dt = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                day = dt.strftime('%A')
                hour = dt.hour
                
                day_patterns[day] = day_patterns.get(day, 0) + 1
                hour_patterns[hour] = hour_patterns.get(hour, 0) + 1
            except:
                continue
        
        # Find peak times
        most_active_day = max(day_patterns.items(), key=lambda x: x[1]) if day_patterns else ('Unknown', 0)
        most_active_hour = max(hour_patterns.items(), key=lambda x: x[1]) if hour_patterns else (0, 0)
        
        return {
            'commits_by_day': day_patterns,
            'commits_by_hour': hour_patterns,
            'most_active_day': most_active_day[0],
            'most_active_hour': most_active_hour[0],
            'weekend_commits': day_patterns.get('Saturday', 0) + day_patterns.get('Sunday', 0),
            'after_hours_commits': sum(count for hour, count in hour_patterns.items() if hour < 8 or hour > 18)
        }
    
    def detect_outliers(self, commits: List[Dict]) -> List[Dict]:
        """Detect churn outliers using statistical methods"""
        if len(commits) < 4:
            return []
        
        churns = [c['total'] for c in commits]
        
        try:
            q1, q3 = statistics.quantiles(churns, n=4)[0], statistics.quantiles(churns, n=4)[2]
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = []
            for commit in commits:
                if commit['total'] < lower_bound or commit['total'] > upper_bound:
                    outliers.append({
                        'commit': commit['sha'],
                        'author': commit['author'],
                        'churn': commit['total'],
                        'type': 'high' if commit['total'] > upper_bound else 'low',
                        'deviation': abs(commit['total'] - statistics.mean(churns)),
                        'message': commit['message'][:80]
                    })
            
            return outliers
        except:
            return []
    
    def generate_analysis_summary(self, commits: List[Dict]) -> Dict:
        """Generate high-level analysis summary"""
        if not commits:
            return {}
        
        total_churn = sum(c['total'] for c in commits)
        avg_churn = total_churn / len(commits)
        
        # Determine team velocity
        if avg_churn > 400:
            velocity = "High"
        elif avg_churn > 200:
            velocity = "Medium"
        else:
            velocity = "Low"
        
        # Determine code stability
        deletions_ratio = sum(c['deletions'] for c in commits) / max(sum(c['additions'] for c in commits), 1)
        if deletions_ratio > 0.5:
            stability = "Refactoring Heavy"
        elif deletions_ratio > 0.3:
            stability = "Moderate Changes"
        else:
            stability = "Growth Focused"
        
        return {
            'velocity': velocity,
            'stability': stability,
            'total_churn': total_churn,
            'avg_churn': round(avg_churn, 1),
            'commit_frequency': len(commits),
            'unique_authors': len(set(c['author'] for c in commits))
        }
    
    def get_empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            'churn_analysis': {},
            'author_metrics': {},
            'risk_assessment': {'high_risk_commits': [], 'medium_risk_commits': [], 'total_risky_commits': 0},
            'temporal_patterns': {},
            'outliers': [],
            'summary': {}
        }
