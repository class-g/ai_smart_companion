import streamlit as st

from utils.session import init_session_state, switch_page
from utils.image import show_gif
# from views import companion, toolbox, about, guess_word
from views import about

# ==================== 页面配置 ====================

st.set_page_config(
    page_title="CLASSG",
    page_icon="哆啦A梦3.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

init_session_state()

st.logo('哆啦A梦.gif', size='large')

# ==================== 页面注册表 ====================

PAGES = {
    # 'AI智能伴侣': {'icon': '💬', 'title': '💬 AI智能伴侣', 'module': companion},
    # 'AI汉子谜盒': {'icon': '🎯', 'title': '🎯 AI汉子谜盒', 'module': guess_word},
    # '工具箱':  {'icon': '🛠️', 'title': '🛠️ 工具箱', 'module': toolbox},
    '关于':   {'icon': 'ℹ️', 'title': 'ℹ️ 关于', 'module': about},
}

# ==================== 顶部标题栏 ====================

current = PAGES.get(st.session_state.current_page)
left_col, right_col = st.columns([5, 1])
with left_col:
    if current:
        st.title(current['title'])
with right_col:
    show_gif("哆啦A梦2.gif", width=200, border_radius=10)

# ==================== 侧边栏 ====================

with st.sidebar:
    st.subheader('📋 导航菜单')
    for page_name, page_info in PAGES.items():
        is_active = st.session_state.current_page == page_name
        st.button(
            f'{page_info["icon"]}  {page_name}',
            width='stretch',
            key=f'nav_{page_name}',
            type='primary' if is_active else 'secondary',
            on_click=switch_page,
            args=(page_name,)
        )

    st.divider()

    current = PAGES.get(st.session_state.current_page)
    if current:
        current['module'].render_sidebar()

# ==================== 主内容区 ====================

if current:
    current['module'].render_main()
