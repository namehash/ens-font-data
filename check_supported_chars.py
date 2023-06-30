'''
A script used to extract supported/unsupported chars/emoji on multiple platforms.
This version works with operating systems that have the fc-list command (Linux, MacOS, etc.).
The script can be modified to work with a static list of fonts (like the Android 11 fonts).
'''

import subprocess
import re
from fontTools import ttLib
from rich.progress import track
from ens_normalize.normalization import NORMALIZATION
import json
from emoji_support import is_emoji_supported_by_font
import os
from argparse import ArgumentParser


def get_android11_fonts():
    return [os.path.join('fonts/android11-fonts', font) for font in os.listdir('fonts/android11-fonts') if re.match(r'.+\.(ttf|otf|ttc)$', font)]


def get_unix_fonts():
    font_paths = [re.match(r'^(.+\..+): ', line) for line in subprocess.getoutput('fc-list').splitlines()]
    font_paths = [match.group(1) for match in font_paths if match]
    return font_paths


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--platform', choices=['android11', 'unix'], required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    if args.platform == 'android11':
        font_paths = get_android11_fonts()
    elif args.platform == 'unix':
        font_paths = get_unix_fonts()
    else:
        raise ValueError('Unknown platform')

    supported_chars = set()

    for font_path in track(font_paths, description='Checking fonts'):
        # MacOS will fallback to /System/Library/Fonts/LastResort.otf
        if font_path.endswith('LastResort.otf'):
            continue
        fonts = []
        if font_path.endswith('.ttc'):
            for subfont in ttLib.TTCollection(font_path).fonts:
                fonts.append(subfont)
        else:
            fonts.append(ttLib.TTFont(font_path))
        
        for font in fonts:
            for table in font['cmap'].tables:
                supported_chars.update(table.cmap.keys())

    with open(os.path.join(args.output, 'supported_chars.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(supported_chars), f, ensure_ascii=True, indent=2)

    unsupported_chars = NORMALIZATION.valid - supported_chars

    with open(os.path.join(args.output, 'unsupported_chars.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(unsupported_chars), f, ensure_ascii=True, indent=2)

    supported_emoji = []
    unsupported_emoji = []

    for emoji_cps in track(NORMALIZATION.emoji, description='Checking emoji'):
        emoji = ''.join(chr(cp) for cp in emoji_cps)
        for font_path in font_paths:
            if is_emoji_supported_by_font(emoji, font_path):
                supported_emoji.append(emoji)
                break
        else:
            unsupported_emoji.append(emoji)

    with open(os.path.join(args.output, 'supported_emoji.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(supported_emoji), f, ensure_ascii=True, indent=2)

    with open(os.path.join(args.output, 'unsupported_emoji.json'), 'w', encoding='utf-8') as f:
        json.dump(sorted(unsupported_emoji), f, ensure_ascii=True, indent=2)
