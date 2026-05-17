import base64
from pathlib import Path

import streamlit as st


def encode_image(path: str | Path) -> str | None:
    """将图片文件编码为 base64 data URL，文件不存在返回 None"""
    p = Path(path)
    if not p.exists():
        return None
    with open(p, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    suffix = p.suffix.lstrip('.')
    mime_map = {'gif': 'image/gif', 'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'webp': 'image/webp'}
    mime = mime_map.get(suffix.lower(), 'image/png')
    return f"data:{mime};base64,{data}"


def show_gif(path: str | Path, width: int = 200, border_radius: int = 10):
    """在页面上展示 GIF 图片"""
    data_url = encode_image(path)
    if data_url:
        st.markdown(
            f'<img src="{data_url}" style="width: {width}px; border-radius: {border_radius}px;">',
            unsafe_allow_html=True
        )
    else:
        st.warning("图片未找到")


def show_image(path: str | Path, width: int = 150, border_radius: int = 20, center: bool = True):
    """在页面上展示图片"""
    data_url = encode_image(path)
    if data_url is None:
        st.warning("图片未找到")
        return
    align = 'text-align:center;' if center else ''
    st.markdown(
        f'<div style="{align}"><img src="{data_url}" style="width: {width}px; border-radius: {border_radius}px;"></div>',
        unsafe_allow_html=True
    )
