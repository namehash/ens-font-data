from uharfbuzz import Face, Font, Buffer, ot_font_set_funcs, shape


# from https://stackoverflow.com/a/55560968
def is_emoji_supported_by_font(emoji: str, fontdata: bytes) -> bool:
    # Load font:
    face = Face(fontdata)
    font = Font(face)
    upem = face.upem
    font.scale = (upem, upem)
    ot_font_set_funcs(font)

    # Create text buffer:
    buf = Buffer()
    buf.add_str(emoji)
    buf.guess_segment_properties()

    # Shape text:
    features = {"kern": True, "liga": True}
    shape(font, buf, features)

    infos = buf.glyph_infos
    positions = buf.glyph_positions

    # Remove all variant selectors:
    while len(infos) > 0 and infos[-1].codepoint == 3:
        infos = infos[:-1]

    # Filter empty:
    if len(infos) <= 0:
        return False

    # Remove uncombined, ending with skin tone like "👭🏿":
    lastCp = infos[-1].codepoint
    if lastCp == 1076 or lastCp == 1079 or lastCp == 1082 or lastCp == 1085 or lastCp == 1088:
        return False

    # If there is a code point 0 or 3 => Emoji not fully supported by font:
    return all(info.codepoint != 0 and info.codepoint != 3 for info in infos)
