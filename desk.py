import argparse
from organizer import organizer_py, list_categories


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Organize desktop app shortcuts and executables into category folders.'
    )
    parser.add_argument(
        '-p', '--path',
        help='Desktop folder path to organize. Defaults to the current user Desktop.',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be moved without changing files.',
    )
    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='Print available app categories and exit.',
    )

    args = parser.parse_args()

    if args.list_categories:
        print('Available categories:')
        for category in list_categories():
            print(f'  - {category}')
        return

    summary = organizer_py(args.path, dry_run=args.dry_run)
    if not summary:
        print('No matching desktop app shortcuts found to organize.')
        return

    print('Desktop organization complete:')
    for category, count in sorted(summary.items()):
        print(f'  {category}: {count}')


if __name__ == '__main__':
    main()
