"""Compose the default Instagram caption from column data, editable before export."""

SIGNOFF = "Meanderings by Steven Boykey Sidley - link in bio"


def build_default_caption(title: str, extra_subtitle: str, teaser: str) -> str:
    parts = [title]
    if extra_subtitle:
        parts.append(extra_subtitle)
    if teaser:
        parts.append(teaser)
    parts.append(SIGNOFF)
    return "\n\n".join(parts)
