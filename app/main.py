"""Streamlit app: turn a Substack column URL into an Instagram-ready image + caption,
and update the permanent bio-link redirect. Posting to Instagram itself stays manual.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from caption import build_default_caption
from fetch import fetch_column
from history import append_post, load_history
from imagegen import build_image
from redirect import update_bio_redirect

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Column → Instagram Poster", layout="centered")
st.title("Column → Instagram Poster")

if "column" not in st.session_state:
    st.session_state.column = None

url = st.text_input("Substack column URL")

if st.button("Fetch column", disabled=not url):
    with st.spinner("Fetching and parsing column..."):
        try:
            st.session_state.column = fetch_column(url)
        except Exception as e:
            st.error(f"Couldn't fetch that URL: {e}")
            st.session_state.column = None

column = st.session_state.column

if column:
    st.subheader(column.title)
    if column.dek:
        st.caption(column.dek)
    if not column.hero_image_url:
        st.warning("No og:image found on that page — can't generate the image.")

    extra_subtitle = st.text_input("Additional subtitle text? (optional)")

    default_caption = build_default_caption(column.title, extra_subtitle)
    st.markdown("**Caption** (edit before export)")
    caption_text = st.text_area("Caption", value=default_caption, label_visibility="collapsed", height=200)

    if column.hero_image_url and st.button("Generate image"):
        with st.spinner("Building image..."):
            try:
                image = build_image(column.hero_image_url, column.title, extra_subtitle or None)
                st.session_state.generated_image = image
            except Exception as e:
                st.error(f"Couldn't build the image: {e}")

    if st.session_state.get("generated_image"):
        st.image(st.session_state.generated_image, caption="Preview (1080x1350)")

        slug = re.sub(r"[^a-z0-9]+", "-", column.title.lower()).strip("-")[:60] or "post"
        image_path = OUTPUT_DIR / f"{slug}.jpg"
        caption_path = OUTPUT_DIR / f"{slug}.txt"

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save image + caption to /output"):
                st.session_state.generated_image.save(image_path, "JPEG", quality=92)
                caption_path.write_text(caption_text)
                append_post(column.title, column.url, str(image_path), str(caption_path))
                st.success(f"Saved {image_path.name} and {caption_path.name}")

        with col2:
            st.download_button(
                "Copy caption (download .txt)",
                data=caption_text,
                file_name=caption_path.name,
                mime="text/plain",
            )

        st.divider()
        st.markdown("**Update bio link redirect**")
        st.caption("Writes this column's URL into docs/redirect.json and pushes to GitHub Pages.")
        if st.button("Update bio redirect and push"):
            with st.spinner("Committing and pushing..."):
                try:
                    output = update_bio_redirect(column.url, column.title)
                    st.success("Bio redirect updated.")
                    st.code(output or "(no output)")
                except Exception as e:
                    st.error(f"Git push failed: {e}")

with st.expander("Post history"):
    history = load_history()
    if history:
        st.table(history)
    else:
        st.write("No posts yet.")
