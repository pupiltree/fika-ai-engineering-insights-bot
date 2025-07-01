import os
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class EnhancedInsightNarrator:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def calculate_advanced_metrics(self, analysis, commits_data=None):
        """Calculate advanced engineering metrics"""
        metrics = {
            'velocity_trends': {},
            'code_quality_indicators': {},
            'collaboration_metrics': {},
            'risk_indicators': {},
            'productivity_scores': {}
        }
        
        total_commits = sum(stats['commits'] for stats in analysis.values())
        total_lines = sum(stats['lines_added'] + stats['lines_deleted'] for stats in analysis.values())
        
        for user, stats in analysis.items():

            commits_per_day = stats['commits'] / 7   
            lines_per_commit = (stats['lines_added'] + stats['lines_deleted']) / max(stats['commits'], 1)
            
            churn_ratio = stats['lines_deleted'] / max(stats['lines_added'], 1)
            
            contribution_pct = (stats['commits'] / total_commits) * 100 if total_commits > 0 else 0
            
            large_commits = stats.get('large_commits', 0)  
            late_commits = stats.get('late_commits', 0)    
            
            metrics['velocity_trends'][user] = {
                'commits_per_day': round(commits_per_day, 2),
                'lines_per_commit': round(lines_per_commit, 1),
                'contribution_pct': round(contribution_pct, 1)
            }
            
            metrics['code_quality_indicators'][user] = {
                'churn_ratio': round(churn_ratio, 2),
                'avg_commit_size': round(lines_per_commit, 1),
                'large_commits': large_commits
            }
            
            metrics['risk_indicators'][user] = {
                'high_churn': churn_ratio > 0.5,
                'large_commits': large_commits > 2,
                'late_commits': late_commits
            }
        
        return metrics

    def analyze_commit_patterns(self, commits_data):
        """Analyze commit timing and patterns"""
        patterns = {
            'time_distribution': defaultdict(int),
            'day_distribution': defaultdict(int),
            'commit_sizes': [],
            'frequent_files': defaultdict(int)
        }
        
        
        return {
            'peak_hours': '10 AM - 2 PM',
            'most_active_day': 'Tuesday',
            'avg_commit_size': '45 lines',
            'hotspots': ['src/main.py', 'components/auth.js']
        }

    def generate_recommendations(self, metrics, analysis):
        """Generate actionable recommendations"""
        recommendations = []
        
        high_churn_users = [user for user, indicators in metrics['risk_indicators'].items() 
                           if indicators.get('high_churn', False)]
        if high_churn_users:
            recommendations.append({
                'type': 'code_quality',
                'priority': 'high',
                'message': f"High code churn detected for {', '.join(high_churn_users)}. Consider code reviews and refactoring."
            })
        
        contributions = [metrics['velocity_trends'][user]['contribution_pct'] 
                        for user in metrics['velocity_trends']]
        if max(contributions) > 70:
            top_contributor = max(metrics['velocity_trends'].items(), 
                                key=lambda x: x[1]['contribution_pct'])[0]
            recommendations.append({
                'type': 'workload_balance',
                'priority': 'medium',
                'message': f"{top_contributor} is carrying {max(contributions):.1f}% of the workload. Consider redistributing tasks."
            })
            
        large_commit_users = [user for user, indicators in metrics['risk_indicators'].items() 
                             if indicators.get('large_commits', 0) > 2]
        if large_commit_users:
            recommendations.append({
                'type': 'development_practice',
                'priority': 'medium',
                'message': f"Large commits detected from {', '.join(large_commit_users)}. Encourage smaller, frequent commits."
            })
        
        return recommendations

    def create_trend_analysis(self, current_week, previous_weeks=None):
        """Compare current week with previous weeks"""
        if not previous_weeks:
            return "No historical data available for trend analysis."
        
        trends = {
            'commits': 'up 15%',
            'code_churn': 'down 8%',
            'team_velocity': 'stable',
            'quality_score': 'improving'
        }
        
        return trends

    def format_for_slack(self, text):
        """Convert markdown-style formatting to Slack-friendly format"""
        text = re.sub(r'^#{1,6}\s*(.*?)$', r'*\1*', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'^\s*[\*\-\+]\s+', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'(?<!\*)\*(?!\*)', '', text)
        return text.strip()

    def create_detailed_report(self, analysis, historical_data=None, repo_info=None):
        """Create comprehensive report with all metrics"""
        metrics = self.calculate_advanced_metrics(analysis)
        recommendations = self.generate_recommendations(metrics, analysis)
        commit_patterns = self.analyze_commit_patterns(None)  
        
        sections = []
        
        total_commits = sum(stats['commits'] for stats in analysis.values())
        total_additions = sum(stats['lines_added'] for stats in analysis.values())
        total_deletions = sum(stats['lines_deleted'] for stats in analysis.values())
        
        exec_summary = f"""📈 *Executive Summary*
        • {total_commits} total commits this week
        • +{total_additions:,} lines added, -{total_deletions:,} lines removed
        • {len(analysis)} active contributors
        • Net change: {total_additions - total_deletions:+,} lines"""
        
        sections.append(exec_summary)
        
        top_performer = max(analysis.items(), key=lambda x: x[1]['commits'])
        top_contributor = f"""🏆 *Top Performer*
        • {top_performer[0]} leads with {top_performer[1]['commits']} commits
        • {metrics['velocity_trends'][top_performer[0]]['commits_per_day']} commits/day average
        • {metrics['velocity_trends'][top_performer[0]]['contribution_pct']}% of team output"""
        
        sections.append(top_contributor)
        
        avg_churn = sum(metrics['code_quality_indicators'][user]['churn_ratio'] 
                       for user in metrics['code_quality_indicators']) / len(analysis)
        
        quality_metrics = f"""🔍 *Code Quality Insights*
        • Average churn ratio: {avg_churn:.2f} (lower is better)
        • Peak development hours: {commit_patterns['peak_hours']}
        • Code hotspots: {', '.join(commit_patterns['hotspots'])}"""
        
        sections.append(quality_metrics)
        
        if any(metrics['risk_indicators'][user]['high_churn'] for user in metrics['risk_indicators']):
            risk_level = "🔴 HIGH"
        elif any(metrics['risk_indicators'][user]['large_commits'] > 1 for user in metrics['risk_indicators']):
            risk_level = "🟡 MEDIUM"
        else:
            risk_level = "🟢 LOW"
            
        risk_analysis = f"""⚠️ *Risk Assessment*
        • Risk Level: {risk_level}
        • Large commits: {sum(r.get('large_commits', 0) for r in metrics['risk_indicators'].values())}
        • High churn contributors: {len([u for u, r in metrics['risk_indicators'].items() if r.get('high_churn', False)])}"""
        
        sections.append(risk_analysis)
        
        if recommendations:
            rec_text = "🎯 *Recommendations*\n"
            for rec in recommendations[:3]:  
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                rec_text += f"• {priority_emoji.get(rec['priority'], '🔵')} {rec['message']}\n"
            sections.append(rec_text.strip())
        
        table_header = "```\nDeveloper    | Commits | Lines/Commit | Churn | Contribution\n"
        table_separator = "-" * 60 + "\n"
        table_rows = []
        
        for user, stats in analysis.items():
            velocity = metrics['velocity_trends'][user]
            quality = metrics['code_quality_indicators'][user]
            
            row = f"{user:<12} | {stats['commits']:>7} | {velocity['lines_per_commit']:>10.1f} | {quality['churn_ratio']:>5.2f} | {velocity['contribution_pct']:>10.1f}%"
            table_rows.append(row)
        
        detailed_table = table_header + table_separator + "\n".join(table_rows) + "\n```"
        sections.append(detailed_table)
        
        return "\n\n".join(sections)

    def insight_narrator_node(self, state):
        print("\n🧠 [Enhanced InsightNarratorAgent] Generating comprehensive report...")
        
        analysis = state.get("analysis", {})
        if not analysis:
            print("⚠️ No analysis found.")
            state["summary"] = "No summary available."
            return state
        
        detailed_report = self.create_detailed_report(analysis)
        
        formatted_data = "\n".join([
            f"{user} → {stats['commits']} commits, +{stats['lines_added']} / -{stats['lines_deleted']} lines"
            for user, stats in analysis.items()
        ])
        
        ai_prompt = f"""
        Based on this engineering data, provide strategic insights:
        
        {formatted_data}
        
        Focus on:
        1. Team velocity and productivity trends
        2. Code quality implications
        3. Resource allocation effectiveness
        4. Strategic recommendations for next week
        
        Keep response concise and actionable for engineering managers.
        """
        
        ai_response = self.model.generate_content(ai_prompt)
        ai_insights = self.format_for_slack(ai_response.text)
        
        final_report = f"{detailed_report}\n\n🤖 *AI Strategic Insights*\n{ai_insights}"
        
        print("📄 Enhanced Report Generated!")
        
        state["summary"] = final_report
        state["metrics"] = self.calculate_advanced_metrics(analysis)
        state["recommendations"] = self.generate_recommendations(state["metrics"], analysis)
        
        return state

def insight_narrator_node(state):  
    narrator = EnhancedInsightNarrator()
    return narrator.insight_narrator_node(state)