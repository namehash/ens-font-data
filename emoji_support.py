from uharfbuzz import Face, Font, Buffer, ot_font_set_funcs, shape


def is_emoji_supported_by_font(emoji: str, font_path: str) -> bool:
    # Load font:
    with open(font_path, 'rb') as fontfile:
        fontdata = fontfile.read()

    # Load font (has to be done for call):
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
    # Remove all (0, 0, 0, 0) positions:
    res = [pos for pos in buf.glyph_positions if not all(p == 0 for p in pos.position)]
    return len(res) == 1
