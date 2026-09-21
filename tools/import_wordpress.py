import argparse
import logging
from collections import defaultdict
from pathlib import Path

import yaml
from sqlglot import exp, parse


POST_ID, POST_TITLE, POST_STATUS, POST_TYPE = 0, 5, 7, 20
META_POST_ID, META_KEY, META_VALUE = 1, 2, 3
TERM_ID, TERM_NAME = 0, 1
TAXONOMY_ID, TAXONOMY_TERM_ID, TAXONOMY_NAME, TAXONOMY_PARENT = 0, 1, 2, 4
RELATIONSHIP_OBJECT_ID, RELATIONSHIP_TAXONOMY_ID = 0, 1
ICON_ALIASES = {
    "fa fa-usd": "fas fa-dollar-sign",
    "fa fa-file-word-o": "far fa-file-word",
    "fa fa-sort-alpha-asc": "fas fa-sort-alpha-down",
    "fa fa-long-arrow-down": "fas fa-long-arrow-alt-down",
}
EXCLUDED_TITLES = {"百度一下", "百度汉语"}


def literal_value(node):
    if isinstance(node, exp.Null):
        return None
    if isinstance(node, exp.Literal):
        return node.this
    raise ValueError(f"Unsupported SQL value: {node.sql(dialect='mysql')}")


def read_tables(sql_path: Path):
    logging.getLogger("sqlglot").setLevel(logging.ERROR)
    tables = defaultdict(list)

    for statement in parse(sql_path.read_text(encoding="utf-8"), read="mysql"):
        if not isinstance(statement, exp.Insert) or not isinstance(statement.expression, exp.Values):
            continue
        for row in statement.expression.expressions:
            tables[statement.this.name].append(tuple(literal_value(value) for value in row.expressions))

    return tables


def numeric_order(value):
    if value is None or not str(value).isdigit():
        return None
    return int(value)


def build_webstack(sql_path: Path):
    tables = read_tables(sql_path)
    meta_by_post = defaultdict(dict)
    term_meta = defaultdict(dict)

    for row in tables["wp_postmeta"]:
        meta_by_post[int(row[META_POST_ID])][row[META_KEY]] = row[META_VALUE]
    for row in tables["wp_termmeta"]:
        term_meta[int(row[META_POST_ID])][row[META_KEY]] = row[META_VALUE]

    terms = {int(row[TERM_ID]): row[TERM_NAME] for row in tables["wp_terms"]}
    taxonomies = {
        int(row[TAXONOMY_ID]): int(row[TAXONOMY_TERM_ID])
        for row in tables["wp_term_taxonomy"]
        if row[TAXONOMY_NAME] == "favorites" and int(row[TAXONOMY_PARENT]) == 0
    }
    relationships = defaultdict(list)
    for row in tables["wp_term_relationships"]:
        taxonomy_id = int(row[RELATIONSHIP_TAXONOMY_ID])
        if taxonomy_id in taxonomies:
            relationships[int(row[RELATIONSHIP_OBJECT_ID])].append(taxonomy_id)

    categories = sorted(
        taxonomies.items(),
        key=lambda item: (
            numeric_order(term_meta[item[1]].get("_term_order")) != 0,
            numeric_order(term_meta[item[1]].get("_term_order")) or 0,
            item[1],
        ),
    )
    links_by_taxonomy = defaultdict(list)

    for row in tables["wp_posts"]:
        post_id = int(row[POST_ID])
        metadata = meta_by_post[post_id]
        if (
            row[POST_TYPE] != "sites"
            or row[POST_STATUS] != "publish"
            or not metadata.get("_sites_link")
            or row[POST_TITLE] in EXCLUDED_TITLES
        ):
            continue
        if not row[POST_TITLE]:
            raise ValueError(f"Site {post_id} has no title")
        if len(relationships[post_id]) > 1:
            raise ValueError(f"Site {post_id} must belong to exactly one favorites category")
        taxonomy_id = relationships[post_id][0] if relationships[post_id] else None
        links_by_taxonomy[taxonomy_id].append(
            {
                "title": row[POST_TITLE],
                "url": metadata["_sites_link"],
                "description": metadata.get("_sites_sescribe") or "",
                "_order": numeric_order(metadata.get("_sites_order")),
                "_id": post_id,
            }
        )

    data = []
    for taxonomy_id, term_id in categories:
        links = links_by_taxonomy[taxonomy_id]
        if not links:
            raise ValueError(f"Category {terms[term_id]} has no sites")
        links.sort(key=lambda link: (link["_order"] is None, link["_order"] or 0, link["_id"]))
        icon = term_meta[term_id].get("_term_ico") or "fas fa-link"
        data.append(
            {
                "taxonomy": terms[term_id],
                "icon": ICON_ALIASES.get(icon, icon),
                "links": [{key: value for key, value in link.items() if not key.startswith("_")} for link in links],
            }
        )

    uncategorized_links = links_by_taxonomy[None]
    if uncategorized_links:
        uncategorized_links.sort(key=lambda link: (link["_order"] is None, link["_order"] or 0, link["_id"]))
        data.append(
            {
                "taxonomy": "其他",
                "icon": "fas fa-link",
                "links": [{key: value for key, value in link.items() if not key.startswith("_")} for link in uncategorized_links],
            }
        )

    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sql_path", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/webstack.yml"))
    args = parser.parse_args()
    data = build_webstack(args.sql_path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")


if __name__ == "__main__":
    main()
