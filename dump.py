import json
from argparse import ArgumentParser


def load_chars(path):
    with open(path, encoding='utf-8') as f:
        return [chr(cp) for cp in json.load(f)]


def load_emoji(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('source', help='JSON file with characters/emoji to dump')
    args = parser.parse_args()

    with open(args.source, encoding='utf-8') as f:
        data = json.load(f)

    for char in data:
        print(char)
