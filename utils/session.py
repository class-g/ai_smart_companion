import streamlit as st


def init_session_state():
    """初始化全局 session_state（仅页面导航等公共状态）"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = '关于'


def switch_page(page_name: str):
    """切换当前页面"""
    st.session_state.current_page = page_name
