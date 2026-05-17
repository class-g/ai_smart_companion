import streamlit as st

from utils.image import show_image


def render_sidebar():
    """渲染关于页面的侧边栏内容"""
    st.subheader('ℹ️ 信息')
    st.caption('💬 CLASSG AI v1.0.0')


def render_main():
    """渲染关于页面的主内容区"""
    st.markdown('---')

    about_col1, about_col2 = st.columns([1, 2])
    with about_col1:
        show_image("哆啦A梦3.png", width=150, border_radius=20, center=True)

    with about_col2:
        st.subheader('💬 CLASSG AI')
        st.markdown('''
        **版本：** 1.0.0

        **简介：** 基于大语言模型的智能应用，提供多种趣味 AI 互动体验，更多的可能性和快乐。

        **技术栈：** Python + Streamlit + 通义千问 (Qwen)
        ''')

    st.markdown('---')

    feat1, feat2 = st.columns(2)
    with feat1:
        st.markdown('''
        ### 💬 智能伴侣对话
        - 🎭 自定义伴侣昵称与性格
        - 📝 多会话管理
        - ⚡ 流式实时响应
        ''')
    with feat2:
        st.markdown('''
        ### 🎯 AI汉子谜盒
        - 🧩 AI 出汉字谜语，你来猜
        - 🏆 实时计分与战绩统计
        - 💡 猜错给提示，跳过可揭晓
        ''')

    st.markdown('---')
    st.caption('Built with 💡 & ☕ by CLASSG Team')
