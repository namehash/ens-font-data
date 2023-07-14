import os
import shutil
import subprocess
import re
from ens_normalize.normalization import NORMALIZATION
import json
from emoji_support import is_emoji_supported_by_font
from fontTools import ttLib
from argparse import ArgumentParser
from tqdm.dask import TqdmCallback
import dask.bag as db


def cps_to_chrs(cps):
    return [chr(cp) for cp in cps]


def get_supported_cps(font_path: str) -> set[int]:
    supported_cps = set()
    fonts = []
    if font_path.endswith('.ttc'):
        for subfont in ttLib.TTCollection(font_path).fonts:
            fonts.append(subfont)
    else:
        fonts.append(ttLib.TTFont(font_path))
    for font in fonts:
        supported_cps.update(font.getBestCmap().keys())
    return supported_cps


def analyze_font(font_path: str, output: str):
    font_supported_cps = get_supported_cps(font_path)
    font_unsupported_cps = NORMALIZATION.valid - font_supported_cps
    font_supported_emoji = set()
    font_unsupported_emoji = set()
    for emoji_cps in NORMALIZATION.emoji:
        emoji = ''.join(chr(cp) for cp in emoji_cps)
        if is_emoji_supported_by_font(emoji, font_path):
            font_supported_emoji.add(tuple(emoji_cps))
        else:
            font_unsupported_emoji.add(tuple(emoji_cps))

    os.makedirs(os.path.join(output, os.path.basename(font_path)), exist_ok=True)

    with open(os.path.join(output, os.path.basename(font_path), 'supported_chars.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(font_supported_cps), f)

    with open(os.path.join(output, os.path.basename(font_path), 'unsupported_chars.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(font_unsupported_cps), f)

    with open(os.path.join(output, os.path.basename(font_path), 'supported_emoji.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(font_supported_emoji), f)

    with open(os.path.join(output, os.path.basename(font_path), 'unsupported_emoji.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(font_unsupported_emoji), f)

    return font_supported_cps, font_unsupported_cps, font_supported_emoji, font_unsupported_emoji


def run():
    parser = ArgumentParser()
    parser.add_argument('--fc-list', action='store_true', help='Use fc-list to find fonts')
    parser.add_argument('--font-dir', type=str, help='Use a directory with fonts')
    parser.add_argument('output', type=str, help='Output directory')
    args = parser.parse_args()

    if args.fc_list:
        font_paths = subprocess.getoutput('fc-list').splitlines()
    elif args.font_dir:
        font_paths = []
        for root, dirs, files in os.walk(args.font_dir):
            for file in files:
                if file.endswith('.ttf') or file.endswith('.otf') or file.endswith('.ttc'):
                    font_paths.append(os.path.join(root, file))
    else:
        print('Please specify a method to find fonts')
        parser.print_help()
        exit(1)

    font_paths = [re.match(r'^(.+\.(?:ttf|otf|ttc)):', line) for line in font_paths]
    font_paths = [match.group(1) for match in font_paths if match]
    font_paths = set(font_paths)
    # MacOS will fallback to /System/Library/Fonts/LastResort.otf
    font_paths = [font_path for font_path in font_paths if not font_path.endswith('LastResort.otf')]

    print(f'Found {len(font_paths)} fonts')

    supported_cps = set()
    unsupported_cps = set()
    supported_emoji = set()
    unsupported_emoji = set()

    shutil.rmtree(args.output, ignore_errors=True)

    with TqdmCallback(desc='Analyzing fonts'):
        results = db.from_sequence(font_paths).map(analyze_font, args.output).compute()
    for font_supported_cps, font_unsupported_cps, font_supported_emoji, font_unsupported_emoji in results:
        supported_cps.update(font_supported_cps)
        unsupported_cps.update(font_unsupported_cps)
        supported_emoji.update(font_supported_emoji)
        unsupported_emoji.update(font_unsupported_emoji)

    unsupported_cps = unsupported_cps - supported_cps
    unsupported_emoji = unsupported_emoji - supported_emoji

    print('supported/unsupported:')
    print(f'Characters: {len(supported_cps)}/{len(unsupported_cps)}')
    print(f'Emoji: {len(supported_emoji)}/{len(unsupported_emoji)}')

    os.makedirs(args.output, exist_ok=True)

    with open(os.path.join(args.output, 'supported_chars.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(supported_cps), f)

    with open(os.path.join(args.output, 'unsupported_chars.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(unsupported_cps), f)

    with open(os.path.join(args.output, 'supported_emoji.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(supported_emoji), f)

    with open(os.path.join(args.output, 'unsupported_emoji.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(unsupported_emoji), f)


if __name__ == '__main__':
    run()
