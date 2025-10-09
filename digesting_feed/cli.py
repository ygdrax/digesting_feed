"""Simple CLI commands for managing digesting feed archives."""

import argparse
import sys

from .archive_manager import ArchiveManager
from .history_reporter import HistoryReporter


def show_stats(archive_manager: ArchiveManager) -> None:
    """Show archive statistics."""
    stats = archive_manager.get_statistics()
    print("\n📊 Archive Statistics")
    print("=" * 50)
    print(f"Total articles: {stats['total_articles']}")
    print(f"Total days: {stats['total_dates']}")
    print(f"Average articles per day: {stats['average_articles_per_day']:.1f}")
    
    if stats['date_range']['oldest'] and stats['date_range']['newest']:
        print(f"Date range: {stats['date_range']['oldest']} to {stats['date_range']['newest']}")
    
    if stats['sources']:
        print(f"Sources: {', '.join(stats['sources'])}")


def generate_report(archive_manager: ArchiveManager, days: int, output: str) -> None:
    """Generate historical report."""
    reporter = HistoryReporter(archive_manager)
    reporter.generate_html_report(days=days, output_file=output)
    print(f"Report generated: {output}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Digesting Feed Archive Management")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    subparsers.add_parser('stats', help='Show archive statistics')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate historical report')
    report_parser.add_argument('--days', type=int, default=7, help='Days to include (default: 7)')
    report_parser.add_argument('--output', default='history_report.html', help='Output file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        archive_manager = ArchiveManager()
        
        if args.command == 'stats':
            show_stats(archive_manager)
        elif args.command == 'report':
            generate_report(archive_manager, args.days, args.output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()