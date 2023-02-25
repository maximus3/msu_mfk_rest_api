import argparse

from tools import gen_admin_models, hash_password, open_sqlalchemy, run_job


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
    elif args.tool_name == 'gen-admin-models':
        gen_admin_models.main(*args.tool_args)
    elif args.tool_name == 'sqlalchemy':
        open_sqlalchemy.main(*args.tool_args)
    elif args.tool_name == 'hash-password':
        hash_password.main(*args.tool_args)
    else:
        raise ValueError(f'Unknown tool: {args.tool_name}')
