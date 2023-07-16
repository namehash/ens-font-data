import os
import json
from argparse import ArgumentParser
import shutil


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-m', '--mode', choices=['all', 'any'], help='when to consider a character supported (all or any of the sources)', required=True)
    parser.add_argument('-o', '--output', help='output directory', required=True)
    parser.add_argument('sources', nargs='+', help='result directories to combine')
    args = parser.parse_args()

    all_supported_chars = set()
    all_unsupported_chars = set()
    all_supported_emoji = set()
    all_unsupported_emoji = set()

    for directory in args.sources:
        with open(os.path.join(directory, 'supported_chars.json'), encoding='utf-8') as f:
            supported_chars = json.load(f)

        with open(os.path.join(directory, 'unsupported_chars.json'), encoding='utf-8') as f:
            unsupported_chars = json.load(f)

        with open(os.path.join(directory, 'supported_emoji.json'), encoding='utf-8') as f:
            supported_emoji = [tuple(cps) for cps in json.load(f)]

        with open(os.path.join(directory, 'unsupported_emoji.json'), encoding='utf-8') as f:
            unsupported_emoji = [tuple(cps) for cps in json.load(f)]

        all_supported_chars.update(supported_chars)
        all_unsupported_chars.update(unsupported_chars)
        all_supported_emoji.update(supported_emoji)
        all_unsupported_emoji.update(unsupported_emoji)

    if args.mode == 'all':
        all_supported_chars -= all_unsupported_chars
        all_supported_emoji -= all_unsupported_emoji
    elif args.mode == 'any':
        all_unsupported_chars -= all_supported_chars
        all_unsupported_emoji -= all_supported_emoji

    print('supported/unsupported:')
    print(f'Characters: {len(all_supported_chars)}/{len(all_unsupported_chars)}')
    print(f'Emoji: {len(all_supported_emoji)}/{len(all_unsupported_emoji)}')

    shutil.rmtree(args.output, ignore_errors=True)
    os.makedirs(args.output)

    with open(os.path.join(args.output, 'supported_chars.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(all_supported_chars), f)

    with open(os.path.join(args.output, 'unsupported_chars.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(all_unsupported_chars), f)

    with open(os.path.join(args.output, 'supported_emoji.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(all_supported_emoji), f)

    with open(os.path.join(args.output, 'unsupported_emoji.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(all_unsupported_emoji), f)
