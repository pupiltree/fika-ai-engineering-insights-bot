from dataclasses import dataclass, field
from typing import List, Dict, Tuple

@dataclass
class ChartConfig:
    output_dir: str = "output"
    colors: List[str] = field(default_factory=lambda: [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"
    ])
    dora_targets: Dict[str, float] = field(default_factory=lambda: {
        "lead_time": 24,  # hours
        "deploy_frequency": 5,  # per week
        "change_failure_rate": 10,  # percent
        "mttr": 2  # hours
    })
    dora_metrics: List[str] = field(default_factory=lambda: [
        'Lead Time (hrs)',
        'Deploys (per week)',
        'Failure Rate (%)',
        'MTTR (hrs)'
    ])
    figure_size: Tuple[int, int] = (12, 8)
    pr_latency_bins: List[int] = field(default_factory=lambda: [0, 12, 24, 48, 72, 168, 336, 720])
    pr_latency_labels: List[str] = field(default_factory=lambda: ['0-12h', '12-24h', '1-2d', '2-3d', '3-7d', '7-14d', '14-30d'])
    pr_latency_colors: List[str] = field(default_factory=lambda: [
        '#2ECC71', '#58D68D', '#F39C12', '#E67E22', '#E74C3C', '#C0392B', '#8E44AD'
    ])
    # Chart-specific DPI and quality settings
    output_settings: Dict = field(default_factory=lambda: {
        "dpi": 300,
        "bbox_inches": "tight",
        "facecolor": "#fafafa",
        "edgecolor": "none",
        "pad_inches": 0.2
    })