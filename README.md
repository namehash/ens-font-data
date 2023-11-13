# ENS Font Data

## Motivation

Many characters and emojis that are included in the ENSIP-15 ENS Normalization Standard are not supported by some fonts.
This repository contains a list of supported/unsupported characters and emojis grouped by default font sets on popular platforms.

## Methodology

Analysis is performed on individual Unicode codepoints and some grapheme clusters (e.g. compound emoji).
The goal is to determine whether a given codepoint or grapheme cluster is supported by a given font.

**Unicode Codepoints**\
All codepoints defined as `valid` by ENSIP-15 are checked for support. This includes special characters such as combining marks. A unicode codepoint is considered supported by a font if it is present in the *best* `cmap` table of the font. The *best* `cmap` table is determined according to [this algorithm](https://fonttools.readthedocs.io/en/latest/ttLib/tables/_c_m_a_p.html#fontTools.ttLib.tables._c_m_a_p.table__c_m_a_p.getBestCmap).

**Grapheme Clusters**\
The only multi-codepoint graphemes checked for support are the emoji sequences allowed in ENSIP-15. To check whether a grapheme cluster is supported by a font, it is programmatically rendered using the `harfbuzz` library and the result is checked for correctness (see [emoji_support.py](emoji_support.py)).

**Fonts**\
Fonts are either contained in an individual font file (`.ttf`, `.otf`) or in a font collection file (`.ttc`). Font files are processed directly and font collections are expanded into individual font files. The font files that were analyzed are not included in this repository because of their size and licensing restrictions. You may acquire them by their Unique ID from the `fonts.txt` file in the results. You can also extract them from your system using the `analyze.py` script.

## Results Format

Results are grouped by the *source font set* and then by individual *fonts* within the set. A *source font set* is a set of fonts and font collections. It usually corresponds to a set of installed fonts on a given operating system.

Each directory in the *results hierarchy* contains JSON files with the supported/unsupported codepoints and emoji. The *results hierarchy* is as follows:

```
results
├── <font_set>
│   ├── fonts.txt
│   ├── supported_chars.json
│   ├── unsupported_chars.json
│   ├── supported_emojis.json
│   ├── unsupported_emojis.json
│   ├── <font_1>
│   │   ├── supported_chars.json
│   │   ├── unsupported_chars.json
│   │   ├── supported_emojis.json
│   │   └── unsupported_emojis.json
│   └── ...
└── ...
```

The per-font results are not included in this repository because they are too large. They can be generated using the `analyze.py` script. The `fonts.txt` file contains the list of fonts that were analyzed.

Each font directory name contains the original font file/collection filename concatenated with the font unique ID, e.g. `NotoSerifCJK-Regular.ttc.1.001;GOOG;NotoSerifCJKjp-Regular;ADOBE`.

## Downstream Usage

The recommended way to use the results is to combine multiple font sets into a single set of supported/unsupported characters and emojis. This can be done using the `combine.py` script (see below). Other uses include creating a mapping from characters to fonts that support them (out of scope for this repository).

## Generating Results

The results were generated using the `analyze.py` script on multiple operating systems.

### `analyze.py`

This script analyzes the fonts installed on your system (when `--fc-list` is specified) or the fonts in the specified directory (when `--font-dir` is specified) and outputs the supported/unsupported characters and emojis to the `output` directory.

```bash
python analyze.py --fc-list <output_dir>
python analyze.py --font-dir <font_dir> <output_dir>
```

### `combine.py`

This script combines multiple sets of supported/unsupported characters and emojis into one set.

```bash
python combine.py -m all|any -o <output_dir> <input_dirs...>
```

It supports 2 modes of operation:

* `-m all` - a character or emoji is considered supported if it is supported by all specified source sets
* `-m any` - a character or emoji is considered supported if it is supported by at least one of the specified source sets

### `dump.py`

This script prints the contents of the specified JSON file.

```bash
python dump.py supported_chars.json
```

## Obtained Results

### `android11`

* OS: Android
* Version: 11
* Language: Polish
* Additional fonts: Samsung
* Method: extracted with `adb`

### `macos13`

* OS: macOS
* Version: 13.4.1 (22F82)
* Language: English (US)
* Method: `fc-list`

### `windows10`

* OS: Windows 10
* Version: TODO
* Language: English (US)
* Method: `C:\Windows\Fonts`

## Limitations

1. The set of pre-installed fonts on a given operating system is not necessarily the same as the set of fonts that are used for rendering. For example, many websites and applications bundle their own fonts.
2. The set of pre-installed fonts is subject to regional settings, software versions, user-installed fonts, etc. It is difficult to determine a set of fonts that is common to all users.

Taking the above into account, we can only provide the results for one plausible user configuration. We make the assumption that this configuration is representative of the majority of users.
