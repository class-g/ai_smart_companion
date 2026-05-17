import json
import os

import streamlit as st


class PageCache:
    """
    页面级缓存管理器，每个页面拥有独立的 session_state 命名空间和磁盘目录。

    - session_state 的 key 格式: {page_id}__{key}，例如 companion__messages
    - 磁盘存储路径: temp/{page_id}/，例如 temp/companion/2026-05-16_14-31-40.json

    用法:
        cache = PageCache('companion')
        cache.init({'messages': [], 'nick_name': '小甜甜'})   # 初始化默认值（幂等）
        cache.get('messages')          # 读取
        cache.set('nick_name', '新名')  # 写入
        cache.save('session_name', data)  # 持久化到磁盘
        cache.load('session_name')        # 从磁盘加载
    """

    def __init__(self, page_id: str):
        self.page_id = page_id
        self._prefix = f"{page_id}__"
        self._dir = f"temp/{page_id}"

    # ---- session_state 操作 ----

    def _key(self, key: str) -> str:
        return self._prefix + key

    def get(self, key: str, default=None):
        """获取页面作用域的 session_state 值"""
        return st.session_state.get(self._key(key), default)

    def set(self, key: str, value):
        """设置页面作用域的 session_state 值"""
        st.session_state[self._key(key)] = value

    def init(self, defaults: dict):
        """批量初始化默认值，仅当 key 不存在时才设置（幂等）"""
        for key, value in defaults.items():
            full_key = self._key(key)
            if full_key not in st.session_state:
                st.session_state[full_key] = value

    # ---- 磁盘持久化 ----

    def save(self, filename: str, data: dict):
        """保存数据到磁盘，路径为 temp/{page_id}/{filename}.json"""
        os.makedirs(self._dir, exist_ok=True)
        with open(f'{self._dir}/{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, filename: str) -> dict:
        """从磁盘加载数据"""
        with open(f'{self._dir}/{filename}.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def delete(self, filename: str):
        """从磁盘删除"""
        path = f'{self._dir}/{filename}.json'
        if os.path.exists(path):
            os.remove(path)

    def list_saved(self) -> list[str]:
        """列出磁盘上所有已保存的会话（按时间倒序）"""
        if not os.path.isdir(self._dir):
            return []
        files = [f.removesuffix('.json') for f in os.listdir(self._dir) if f.endswith('.json')]
        files.sort(reverse=True)
        return files
