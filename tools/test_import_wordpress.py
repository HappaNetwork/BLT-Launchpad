import unittest
from pathlib import Path

import yaml

from tools.import_wordpress import build_webstack


SQL = Path(__file__).parents[2] / "db_daohang_bilunton_20241218_023001_5m3WTa.sql"
OUTPUT = Path(__file__).parents[1] / "data/webstack.yml"


class ImportWordPressTests(unittest.TestCase):
    def test_build_webstack_preserves_navigation_records(self):
        data = build_webstack(SQL)
        links = [link for group in data for link in group["links"]]

        self.assertEqual(42, len(links))
        self.assertEqual(13, len(data))
        self.assertEqual(
            [
                "基金项目",
                "科研社区",
                "问卷调查",
                "文档翻译",
                "学历查询",
                "图书查询",
                "学术词典",
                "必备软件",
                "投稿选刊",
                "文献下载",
                "论文课程",
                "论文查重",
                "其他",
            ],
            [group["taxonomy"] for group in data],
        )
        self.assertIn("https://cx.cnki.net/main.html#/login", {link["url"] for link in links})
        self.assertEqual(
            ["中国知网个人查重"],
            [link["title"] for link in data[-1]["links"]],
        )
        self.assertNotIn("百度一下", {link["title"] for link in links})
        self.assertNotIn("百度汉语", {link["title"] for link in links})
        self.assertEqual(
            {
                "基金项目": "fas fa-dollar-sign",
                "问卷调查": "far fa-file-word",
                "文档翻译": "fas fa-sort-alpha-down",
                "文献下载": "fas fa-long-arrow-alt-down",
            },
            {
                group["taxonomy"]: group["icon"]
                for group in data
                if group["taxonomy"] in {"基金项目", "问卷调查", "文档翻译", "文献下载"}
            },
        )

    def test_emitted_yaml_is_valid_and_has_no_missing_logos(self):
        data = build_webstack(SQL)
        rendered = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)

        self.assertEqual(data, yaml.safe_load(rendered))
        self.assertEqual(data, yaml.safe_load(OUTPUT.read_text(encoding="utf-8")))
        self.assertNotIn("logo", rendered)
