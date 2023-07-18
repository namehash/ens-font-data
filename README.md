# ens-webfont

Many characters and emojis that are included in the ENSIP-15 ENS Normalization Standard are not supported by some fonts.
This repository contains a list of supported/unsupported characters and emojis grouped by default font sets on popular platforms.

## Scripts

### `analyze.py`

This script analyzes the fonts installed on your system (when `--fc-list` is specified) or the fonts in the specified directory (when `--font-dir` is specified) and outputs the supported/unsupported characters and emojis to the `output` directory.

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

## Results

The results of the analysis are stored in the `results` directory. Each subdirectory corresponds to an operating system and contains the following files:

* `fonts.txt` - a list of font unique IDs included in this set
* `supported_chars.json` - a list of supported character codepoints
* `unsupported_chars.json` - a list of unsupported character codepoints
* `supported_emojis.json` - a list of supported emojis, each emoji is represented as a list of codepoints
* `unsupported_emojis.json` - a list of unsupported emojis, each emoji is represented as a list of codepoints
