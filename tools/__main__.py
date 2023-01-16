import argparse

from tools import run_job


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        'tool_name',
        help='Tool name',
        type=str,
    )
    # arguments to pass to tools
    arg_parser.add_argument(
        'tool_args',
        help='Tool arguments',
        type=str,
        nargs='*',
    )
    args = arg_parser.parse_args()
    if args.tool_name == 'runjob':
        run_job.main(*args.tool_args)
    else:
        raise ValueError(f'Unknown tool: {args.tool_name}')
