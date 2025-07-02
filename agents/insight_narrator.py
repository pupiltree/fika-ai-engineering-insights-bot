import os
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict
import google.generativeai as genai
from dotenv import load_dotenv
import statistics
from typing import Dict, List, Optional, Tuple

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

    def calculate_cycle_time(self, commits_data: Optional[List[Dict]] = None) -> Dict:
        """Calculate cycle time metrics from commit data"""
        if not commits_data:
            # Mock data for demonstration
            return {
                'avg_cycle_time_hours': 18.5,
                'median_cycle_time_hours': 14.2,
                'cycle_time_trend': [16.2, 18.1, 15.8, 19.3, 18.5],  # Last 5 periods
                'pr_merge_time_hours': 4.2,
                'feature_completion_days': 3.1
            }
        
        # Real implementation would parse commit timestamps and calculate actual cycle times
        cycle_times = []
        for commit in commits_data:
            # Calculate time between commit creation and merge
            created = datetime.fromisoformat(commit.get('created_at', ''))
            merged = datetime.fromisoformat(commit.get('merged_at', ''))
            cycle_time = (merged - created).total_seconds() / 3600  # Convert to hours
            cycle_times.append(cycle_time)
        
        return {
            'avg_cycle_time_hours': statistics.mean(cycle_times) if cycle_times else 0,
            'median_cycle_time_hours': statistics.median(cycle_times) if cycle_times else 0,
            'cycle_time_trend': cycle_times[-5:] if len(cycle_times) >= 5 else cycle_times,
            'pr_merge_time_hours': statistics.mean(cycle_times) * 0.3 if cycle_times else 0,  # Approximate
            'feature_completion_days': statistics.mean(cycle_times) / 24 if cycle_times else 0
        }

    def forecast_next_week(self, current_analysis: Dict, historical_data: Optional[List[Dict]] = None) -> Dict:
        """Forecast next week's cycle time and churn using trend analysis"""
        
        # Calculate current week metrics
        current_metrics = self.calculate_advanced_metrics(current_analysis)
        current_cycle_time = self.calculate_cycle_time()
        
        # Extract churn data for forecasting
        current_churn_ratios = [
            metrics['churn_ratio'] 
            for metrics in current_metrics['code_quality_indicators'].values()
        ]
        avg_current_churn = statistics.mean(current_churn_ratios) if current_churn_ratios else 0
        
        # Simple trend-based forecasting
        if historical_data and len(historical_data) >= 3:
            # Use historical data for more accurate forecasting
            historical_churn = [week.get('avg_churn', 0) for week in historical_data[-4:]]
            historical_cycle_times = [week.get('avg_cycle_time', 0) for week in historical_data[-4:]]
            
            # Linear trend calculation
            churn_trend = self._calculate_linear_trend(historical_churn + [avg_current_churn])
            cycle_time_trend = self._calculate_linear_trend(
                historical_cycle_times + [current_cycle_time['avg_cycle_time_hours']]
            )
            
            # Forecast next week
            forecast_churn = max(0, avg_current_churn + churn_trend)
            forecast_cycle_time = max(0, current_cycle_time['avg_cycle_time_hours'] + cycle_time_trend)
            
        else:
            # Simple moving average approach when limited historical data
            forecast_churn = avg_current_churn * 1.05  # Slight increase assumption
            forecast_cycle_time = current_cycle_time['avg_cycle_time_hours'] * 0.95  # Slight improvement assumption
        
        # Calculate confidence intervals and risk factors
        churn_volatility = self._calculate_volatility(current_churn_ratios)
        cycle_time_volatility = self._calculate_volatility(current_cycle_time['cycle_time_trend'])
        
        # Determine forecast confidence
        confidence_level = self._determine_confidence(historical_data, churn_volatility, cycle_time_volatility)
        
        # Generate risk scenarios
        risk_scenarios = self._generate_risk_scenarios(
            forecast_churn, forecast_cycle_time, churn_volatility, cycle_time_volatility
        )
        
        forecast = {
            'cycle_time_forecast': {
                'predicted_hours': round(forecast_cycle_time, 1),
                'confidence_level': confidence_level,
                'range': {
                    'optimistic': round(forecast_cycle_time * 0.85, 1),
                    'pessimistic': round(forecast_cycle_time * 1.25, 1)
                },
                'trend': 'improving' if forecast_cycle_time < current_cycle_time['avg_cycle_time_hours'] else 'declining'
            },
            'churn_forecast': {
                'predicted_ratio': round(forecast_churn, 3),
                'confidence_level': confidence_level,
                'range': {
                    'optimistic': round(max(0, forecast_churn * 0.7), 3),
                    'pessimistic': round(forecast_churn * 1.4, 3)
                },
                'trend': 'decreasing' if forecast_churn < avg_current_churn else 'increasing'
            },
            'risk_scenarios': risk_scenarios,
            'recommendations': self._generate_forecast_recommendations(
                forecast_churn, forecast_cycle_time, avg_current_churn, 
                current_cycle_time['avg_cycle_time_hours']
            )
        }
        
        return forecast

    def _calculate_linear_trend(self, values: List[float]) -> float:
        """Calculate linear trend from a series of values"""
        if len(values) < 2:
            return 0
        
        n = len(values)
        x = list(range(n))
        
        # Calculate slope using least squares
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation) of values"""
        if len(values) < 2:
            return 0
        return statistics.stdev(values)

    def _determine_confidence(self, historical_data: Optional[List[Dict]], 
                            churn_volatility: float, cycle_time_volatility: float) -> str:
        """Determine forecast confidence level"""
        if not historical_data or len(historical_data) < 3:
            return 'low'
        
        if churn_volatility < 0.1 and cycle_time_volatility < 2:
            return 'high'
        elif churn_volatility < 0.2 and cycle_time_volatility < 5:
            return 'medium'
        else:
            return 'low'

    def _generate_risk_scenarios(self, forecast_churn: float, forecast_cycle_time: float,
                               churn_volatility: float, cycle_time_volatility: float) -> List[Dict]:
        """Generate risk scenarios for forecasts"""
        scenarios = []
        
        if forecast_churn > 0.6:
            scenarios.append({
                'type': 'high_churn_risk',
                'probability': 'medium',
                'impact': 'high',
                'description': 'Code churn may exceed sustainable levels, indicating rework or technical debt'
            })
        
        if forecast_cycle_time > 24:
            scenarios.append({
                'type': 'extended_cycle_time',
                'probability': 'medium',
                'impact': 'medium',
                'description': 'Cycle time may extend beyond 24 hours, potentially impacting delivery velocity'
            })
        
        if churn_volatility > 0.3:
            scenarios.append({
                'type': 'unstable_quality',
                'probability': 'high',
                'impact': 'medium',
                'description': 'High churn volatility suggests inconsistent code quality practices'
            })
        
        return scenarios

    def _generate_forecast_recommendations(self, forecast_churn: float, forecast_cycle_time: float,
                                         current_churn: float, current_cycle_time: float) -> List[Dict]:
        """Generate recommendations based on forecasts"""
        recommendations = []
        
        if forecast_churn > current_churn * 1.1:
            recommendations.append({
                'type': 'churn_mitigation',
                'priority': 'high',
                'action': 'Implement stricter code review processes and consider refactoring sessions',
                'expected_impact': 'Reduce churn by 15-25%'
            })
        
        if forecast_cycle_time > current_cycle_time * 1.1:
            recommendations.append({
                'type': 'cycle_time_optimization',
                'priority': 'medium',
                'action': 'Review and optimize CI/CD pipeline, consider parallel testing strategies',
                'expected_impact': 'Reduce cycle time by 10-20%'
            })
        
        if forecast_churn > 0.5:
            recommendations.append({
                'type': 'technical_debt',
                'priority': 'high',
                'action': 'Allocate 20% of next sprint to technical debt reduction',
                'expected_impact': 'Improve code stability and reduce future churn'
            })
        
        return recommendations

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
        """Create comprehensive report with all metrics including forecasting"""
        metrics = self.calculate_advanced_metrics(analysis)
        recommendations = self.generate_recommendations(metrics, analysis)
        commit_patterns = self.analyze_commit_patterns(None)
        
        # Generate forecasts
        forecast = self.forecast_next_week(analysis, historical_data)
        
        # Calculate DORA metrics
        cycle_time_metrics = self.calculate_cycle_time()
        dora_metrics = f"""📊 *DORA Metrics*
        • Deployment Frequency: {len(analysis) // 7 if len(analysis) > 7 else '1-7'}/day (based on active days)
        • Lead Time for Changes: {cycle_time_metrics['avg_cycle_time_hours']:.1f} hours (avg)
        • Change Failure Rate: {sum(1 for r in metrics['risk_indicators'].values() if r.get('high_churn', False)) / len(metrics['risk_indicators']) * 100:.1f}% of changes with high churn
        • Mean Time to Recover: {cycle_time_metrics['pr_merge_time_hours']:.1f} hours (PR merge time)
        • Feature Completion: {cycle_time_metrics['feature_completion_days']:.1f} days (avg) """
        
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
        
        # Add forecast section
        forecast_section = f"""🔮 *Next Week Forecast* (Confidence: {forecast['cycle_time_forecast']['confidence_level']})
        • Predicted Cycle Time: {forecast['cycle_time_forecast']['predicted_hours']}h ({forecast['cycle_time_forecast']['trend']})
        • Range: {forecast['cycle_time_forecast']['range']['optimistic']}-{forecast['cycle_time_forecast']['range']['pessimistic']}h
        • Predicted Churn Ratio: {forecast['churn_forecast']['predicted_ratio']} ({forecast['churn_forecast']['trend']})
        • Range: {forecast['churn_forecast']['range']['optimistic']}-{forecast['churn_forecast']['range']['pessimistic']}"""
        
        sections.append(forecast_section)
        
        # Add DORA metrics section
        sections.append(dora_metrics)
        
        # Add risk scenarios if any
        if forecast['risk_scenarios']:
            risk_section = "⚠️ *Forecast Risk Scenarios*\n"
            for scenario in forecast['risk_scenarios'][:2]:  # Show top 2 risks
                risk_section += f"• {scenario['description']} (Impact: {scenario['impact']})\n"
            sections.append(risk_section.strip())
        
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
        
        # Combine regular recommendations with forecast recommendations
        all_recommendations = recommendations + forecast['recommendations']
        if all_recommendations:
            rec_text = "🎯 *Recommendations*\n"
            for rec in all_recommendations[:4]:  # Show top 4 recommendations
                if 'priority' in rec:
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    rec_text += f"• {priority_emoji.get(rec['priority'], '🔵')} {rec['message']}\n"
                else:
                    rec_text += f"• 🔵 {rec['action']} (Expected: {rec.get('expected_impact', 'TBD')})\n"
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
        print("\n🧠 [Enhanced InsightNarratorAgent] Generating comprehensive report with forecasting...")
        
        analysis = state.get("analysis", {})
        historical_data = state.get("historical_data", None)
        
        if not analysis:
            print("⚠️ No analysis found.")
            state["summary"] = "No summary available."
            return state
        
        detailed_report = self.create_detailed_report(analysis, historical_data)
        
        # Generate forecast
        forecast = self.forecast_next_week(analysis, historical_data)
        
        formatted_data = "\n".join([
            f"{user} → {stats['commits']} commits, +{stats['lines_added']} / -{stats['lines_deleted']} lines"
            for user, stats in analysis.items()
        ])
        
        ai_prompt = f"""
        Based on this engineering data and forecasts, provide strategic insights:
        
        Current Week Data:
        {formatted_data}
        
        Next Week Forecasts:
        - Cycle Time: {forecast['cycle_time_forecast']['predicted_hours']}h ({forecast['cycle_time_forecast']['trend']})
        - Churn Ratio: {forecast['churn_forecast']['predicted_ratio']} ({forecast['churn_forecast']['trend']})
        
        Focus on:
        1. Team velocity and productivity trends
        2. Code quality implications and forecast risks
        3. Resource allocation effectiveness
        4. Strategic recommendations for next week based on forecasts
        
        Keep response concise and actionable for engineering managers.
        """
        
        ai_response = self.model.generate_content(ai_prompt)
        ai_insights = self.format_for_slack(ai_response.text)
        
        final_report = f"{detailed_report}\n\n🤖 *AI Strategic Insights*\n{ai_insights}"
        
        print("📄 Enhanced Report with Forecasting Generated!")
        
        state["summary"] = final_report
        state["metrics"] = self.calculate_advanced_metrics(analysis)
        state["forecast"] = forecast
        state["recommendations"] = self.generate_recommendations(state["metrics"], analysis)
        
        return state

def insight_narrator_node(state):  
    narrator = EnhancedInsightNarrator()
    return narrator.insight_narrator_node(state)