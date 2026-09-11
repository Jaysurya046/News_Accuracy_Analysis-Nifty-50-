#!/usr/bin/env python3
"""
Master Pipeline Runner for Quant-Trading.

Provides a unified command-line interface to run any or all stages of the
Nifty 50 comparative analysis pipeline:
  1. generate  - Generate synthetic trade setup datasets for 10 news sources (1-year & 3-year)
  2. compare   - Compare source predicted ranges against actual Nifty High/Low
  3. prepare   - Merge datasets with ground-truth market prices
  4. train     - Train Gradient Boosting baseline models
  5. backtest  - Run comprehensive backtest metrics and source rankings
  6. visualize - Generate dashboards and cumulative analysis figures
  7. reports   - Generate detailed text reports

Usage:
  python run_pipeline.py --all
  python run_pipeline.py --stage compare
  python run_pipeline.py --stage backtest --stage visualize
"""

import argparse
import sys
import time
import subprocess
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import ensure_dirs, PROJECT_ROOT

# Ensure all directories exist
ensure_dirs()

STAGES = {
    'generate': [
        ('Generating 1-Year Datasets', sys.executable, str(PROJECT_ROOT / 'src' / 'data_generators' / 'generate_1year_nifty50_all_sources.py')),
        ('Generating 3-Year Datasets', sys.executable, str(PROJECT_ROOT / 'src' / 'data_generators' / 'generate_3year_nifty50_all_sources.py')),
    ],
    'compare': [
        ('Comparing Nifty Ranges (1Y)', sys.executable, str(PROJECT_ROOT / 'src' / 'analysis' / 'compare_nifty_ranges.py')),
        ('Comparing Both Periods (1Y & 3Y)', sys.executable, str(PROJECT_ROOT / 'src' / 'analysis' / 'compare_both_periods.py')),
        ('Summarizing Best Sources', sys.executable, str(PROJECT_ROOT / 'src' / 'analysis' / 'summarize_best_source.py')),
    ],
    'prepare': [
        ('Preparing Merged Datasets', sys.executable, str(PROJECT_ROOT / 'src' / 'analysis' / 'prepare_dataset.py')),
    ],
    'train': [
        ('Training Baseline Models', sys.executable, str(PROJECT_ROOT / 'src' / 'models' / 'train_gbm.py')),
    ],
    'backtest': [
        ('Running Predictions Backtest', sys.executable, str(PROJECT_ROOT / 'src' / 'models' / 'backtest_predictions.py')),
    ],
    'visualize': [
        ('Generating Backtest Dashboards', sys.executable, str(PROJECT_ROOT / 'src' / 'visualization' / 'visualize_backtest.py')),
        ('Plotting Source Comparisons', sys.executable, str(PROJECT_ROOT / 'src' / 'visualization' / 'plot_both_periods.py')),
        ('Plotting Best Source Counts', sys.executable, str(PROJECT_ROOT / 'src' / 'visualization' / 'plot_best_source_counts.py')),
    ],
    'reports': [
        ('Generating Text Reports', sys.executable, str(PROJECT_ROOT / 'src' / 'visualization' / 'generate_backtest_report.py')),
    ]
}

STAGE_ORDER = ['generate', 'compare', 'prepare', 'train', 'backtest', 'visualize', 'reports']

def run_step(name, *cmd):
    print(f"\n[{name}]")
    print("-" * 60)
    start_time = time.time()
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    duration = time.time() - start_time
    if result.returncode != 0:
        print(f"FAILED: {name} exited with code {result.returncode} ({duration:.2f}s)")
        return False
    print(f"SUCCESS: {name} finished in {duration:.2f}s")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Quant-Trading Pipeline Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all pipeline stages in sequence'
    )
    parser.add_argument(
        '--stage',
        action='append',
        choices=list(STAGES.keys()),
        help='Specific stage(s) to run. Can be specified multiple times.'
    )

    args = parser.parse_args()

    if not args.all and not args.stage:
        parser.print_help()
        sys.exit(0)

    stages_to_run = STAGE_ORDER if args.all else [s for s in STAGE_ORDER if s in (args.stage or [])]

    print("=" * 60)
    print("QUANT-TRADING PIPELINE EXECUTION")
    print(f"Stages: {', '.join(stages_to_run)}")
    print("=" * 60)

    total_start = time.time()
    for stage_name in stages_to_run:
        print(f"\n>>> Starting Stage: {stage_name.upper()} <<<")
        for step_info in STAGES[stage_name]:
            name = step_info[0]
            cmd = step_info[1:]
            success = run_step(name, *cmd)
            if not success:
                print(f"\nPipeline halted due to failure in stage '{stage_name}' - {name}.")
                sys.exit(1)

    total_duration = time.time() - total_start
    print("\n" + "=" * 60)
    print(f"PIPELINE COMPLETED SUCCESSFULLY in {total_duration:.2f}s")
    print("=" * 60)

if __name__ == '__main__':
    main()
