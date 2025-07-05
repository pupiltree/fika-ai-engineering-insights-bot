# forecasting.py
# Time series forecasting for cycle time and churn prediction
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def prepare_historical_data(commit_data: List, pr_data: List) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Prepare historical data for forecasting from commit and PR data."""
    
    
    commit_records = []
    for commit in commit_data:
        if len(commit) >= 7: 
            timestamp = commit[6]  
            additions = commit[3]
            deletions = commit[4]
            churn = additions + deletions
            
            try:
                date = pd.to_datetime(timestamp).date()
                commit_records.append({
                    'date': date,
                    'churn': churn,
                    'additions': additions,
                    'deletions': deletions
                })
            except:
                continue
    
    # Convert PR data to time series
    pr_records = []
    for pr in pr_data:
        if 'created_at' in pr and 'merged_at' in pr and pr['merged_at']:
            created_at = pd.to_datetime(pr['created_at'])
            merged_at = pd.to_datetime(pr['merged_at'])
            cycle_time = (merged_at - created_at).total_seconds() / 3600  # hours
            
            pr_records.append({
                'date': merged_at.date(),
                'cycle_time': cycle_time,
                'pr_size': pr.get('additions', 0) + pr.get('deletions', 0)
            })
    
  
    if commit_records:
        commits_df = pd.DataFrame(commit_records)
        commits_df = commits_df.groupby('date').agg({
            'churn': 'sum',
            'additions': 'sum', 
            'deletions': 'sum'
        }).reset_index()
    else:
        commits_df = pd.DataFrame(columns=['date', 'churn', 'additions', 'deletions'])
    
    if pr_records:
        prs_df = pd.DataFrame(pr_records)
        prs_df = prs_df.groupby('date').agg({
            'cycle_time': 'mean',
            'pr_size': 'mean'
        }).reset_index()
    else:
        prs_df = pd.DataFrame(columns=['date', 'cycle_time', 'pr_size'])
    
    return commits_df, prs_df

def create_time_features(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    """Create time-based features for forecasting."""
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Create lag features (previous values)
    for lag in [1, 2, 3, 7]:  # 1 day, 2 days, 3 days, 1 week ago
        df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
    
    # Create rolling averages
    for window in [3, 7, 14]:  # 3-day, 1-week, 2-week averages
        df[f'{target_col}_rolling_{window}'] = df[target_col].rolling(window=window, min_periods=1).mean()
    
    # Day of week features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Trend features
    df['days_since_start'] = (df['date'] - df['date'].min()).dt.days
    
    return df

def forecast_cycle_time(pr_data: List) -> Dict:
    """Forecast next week's average cycle time."""
    try:
        commits_df, prs_df = prepare_historical_data([], pr_data)
        
        if prs_df.empty or len(prs_df) < 7:
            return {
                'forecast': 24.0,  # Default 24 hours
                'confidence': 'low',
                'reason': 'Insufficient historical data'
            }
        
        # Prepare features
        forecast_df = create_time_features(prs_df, 'cycle_time')
        forecast_df = forecast_df.dropna()
        
        if len(forecast_df) < 5:
            return {
                'forecast': 24.0,
                'confidence': 'low', 
                'reason': 'Insufficient data after feature creation'
            }
        
        # Prepare training data
        feature_cols = [col for col in forecast_df.columns if col not in ['date', 'cycle_time']]
        X = forecast_df[feature_cols].fillna(0)
        y = forecast_df['cycle_time']
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Create future dates for prediction
        last_date = forecast_df['date'].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=7, freq='D')
        
        # Prepare future features (using last known values)
        future_data = []
        for date in future_dates:
            row = {}
            for col in feature_cols:
                if 'lag' in col:
                    # Use last known value for lags
                    row[col] = y.iloc[-1] if len(y) > 0 else 24.0
                elif 'rolling' in col:
                    # Use last rolling average
                    row[col] = forecast_df[f'cycle_time_rolling_7'].iloc[-1] if len(forecast_df) > 0 else 24.0
                elif col == 'day_of_week':
                    row[col] = date.dayofweek
                elif col == 'is_weekend':
                    row[col] = 1 if date.dayofweek in [5, 6] else 0
                elif col == 'days_since_start':
                    row[col] = (date - forecast_df['date'].min()).days
                else:
                    row[col] = 0
            future_data.append(row)
        
        future_df = pd.DataFrame(future_data)
        
        # Make predictions
        predictions = model.predict(future_df)
        avg_forecast = np.mean(predictions)
        
        # Calculate confidence based on model performance
        y_pred = model.predict(X)
        mse = np.mean((y - y_pred) ** 2)
        rmse = np.sqrt(mse)
        confidence = 'high' if rmse < 5 else 'medium' if rmse < 10 else 'low'
        
        return {
            'forecast': max(0, avg_forecast),  # Ensure non-negative
            'confidence': confidence,
            'predictions': predictions.tolist(),
            'rmse': rmse,
            'trend': 'increasing' if predictions[-1] > predictions[0] else 'decreasing'
        }
        
    except Exception as e:
        logging.error(f"Error in cycle time forecasting: {e}")
        return {
            'forecast': 24.0,
            'confidence': 'low',
            'reason': f'Forecasting error: {str(e)}'
        }

def forecast_churn(commit_data: List) -> Dict:
    """Forecast next week's total churn."""
    try:
        commits_df, prs_df = prepare_historical_data(commit_data, [])
        
        if commits_df.empty or len(commits_df) < 7:
            return {
                'forecast': 1000,  # Default churn
                'confidence': 'low',
                'reason': 'Insufficient historical data'
            }
        
        # Prepare features
        forecast_df = create_time_features(commits_df, 'churn')
        forecast_df = forecast_df.dropna()
        
        if len(forecast_df) < 5:
            return {
                'forecast': 1000,
                'confidence': 'low',
                'reason': 'Insufficient data after feature creation'
            }
        
        # Prepare training data
        feature_cols = [col for col in forecast_df.columns if col not in ['date', 'churn', 'additions', 'deletions']]
        X = forecast_df[feature_cols].fillna(0)
        y = forecast_df['churn']
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Create future dates for prediction
        last_date = forecast_df['date'].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=7, freq='D')
        
        # Prepare future features
        future_data = []
        for date in future_dates:
            row = {}
            for col in feature_cols:
                if 'lag' in col:
                    row[col] = y.iloc[-1] if len(y) > 0 else 1000
                elif 'rolling' in col:
                    row[col] = forecast_df[f'churn_rolling_7'].iloc[-1] if len(forecast_df) > 0 else 1000
                elif col == 'day_of_week':
                    row[col] = date.dayofweek
                elif col == 'is_weekend':
                    row[col] = 1 if date.dayofweek in [5, 6] else 0
                elif col == 'days_since_start':
                    row[col] = (date - forecast_df['date'].min()).days
                else:
                    row[col] = 0
            future_data.append(row)
        
        future_df = pd.DataFrame(future_data)
        
        # Make predictions
        predictions = model.predict(future_df)
        total_forecast = np.sum(predictions)
        
        # Calculate confidence
        y_pred = model.predict(X)
        mse = np.mean((y - y_pred) ** 2)
        rmse = np.sqrt(mse)
        confidence = 'high' if rmse < 100 else 'medium' if rmse < 500 else 'low'
        
        return {
            'forecast': max(0, total_forecast),
            'confidence': confidence,
            'daily_predictions': predictions.tolist(),
            'rmse': rmse,
            'trend': 'increasing' if predictions[-1] > predictions[0] else 'decreasing'
        }
        
    except Exception as e:
        logging.error(f"Error in churn forecasting: {e}")
        return {
            'forecast': 1000,
            'confidence': 'low',
            'reason': f'Forecasting error: {str(e)}'
        }

def generate_forecast_summary(cycle_time_forecast: Dict, churn_forecast: Dict) -> str:
    """Generate a human-readable forecast summary."""
    lines = []
    lines.append("**📊 Next Week Forecast:**")
    
    # Cycle time forecast
    ct_forecast = cycle_time_forecast['forecast']
    ct_confidence = cycle_time_forecast['confidence']
    ct_trend = cycle_time_forecast.get('trend', 'stable')
    trend_emoji = "📈" if ct_trend == 'increasing' else "📉" if ct_trend == 'decreasing' else "➡️"
    confidence_emoji = "🟢" if ct_confidence == 'high' else "🟡" if ct_confidence == 'medium' else "🔴"
    
    lines.append(f"{trend_emoji} **Cycle Time**: {ct_forecast:.1f} hours ({confidence_emoji} {ct_confidence} confidence)")
    
    # Churn forecast
    churn_forecast_val = churn_forecast['forecast']
    churn_confidence = churn_forecast['confidence']
    churn_trend = churn_forecast.get('trend', 'stable')
    trend_emoji = "📈" if churn_trend == 'increasing' else "📉" if churn_trend == 'decreasing' else "➡️"
    confidence_emoji = "🟢" if churn_confidence == 'high' else "🟡" if churn_confidence == 'medium' else "🔴"
    
    lines.append(f"{trend_emoji} **Total Churn**: {churn_forecast_val:.0f} lines ({confidence_emoji} {churn_confidence} confidence)")
    
    # Add insights
    if ct_forecast > 48:
        lines.append("⚠️ **Warning**: High cycle time forecast - consider process improvements")
    if churn_forecast_val > 5000:
        lines.append("⚠️ **Warning**: High churn forecast - monitor for potential issues")
    
    return '\n'.join(lines) 