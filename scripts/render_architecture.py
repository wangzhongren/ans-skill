#!/usr/bin/env python3
"""Combine role-owned architecture JSON into an offline HTML viewer."""
import argparse
from datetime import date, datetime, timezone
import html
import json
from pathlib import Path, PureWindowsPath


LAYERS = {"interface", "pipeline", "service", "provider", "model"}
NODE_KINDS = {"concept", "contract", "model", "module"}
RELATION_KINDS = {"contains", "manages", "composes", "uses", "uses-model", "implements"}
STATUSES = {"current", "planned", "needs-review"}
ASSETS = Path(__file__).resolve().parents[1] / "assets" / "architecture-viewer"


def project_path(root, value):
    if (not isinstance(value, str) or not value.strip() or "\\" in value or "\x00" in value
            or Path(value).is_absolute() or PureWindowsPath(value).is_absolute()
            or ".." in Path(value).parts):
        raise ValueError("需要项目内的相对路径：" + str(value))
    path = root / value
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError("不能使用符号链接：" + value)
        current = current.parent
    if not path.resolve().is_relative_to(root):
        raise ValueError("路径必须位于项目内：" + value)
    return path


def required_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + " 必须有明确的文字")
    return value


def array(value, label):
    if not isinstance(value, list):
        raise ValueError(label + " 必须是数组")
    return value


def owned_id(value, role_id, label):
    identifier = required_text(value, label)
    if not identifier.startswith(role_id + ":") or identifier == role_id + ":":
        raise ValueError(label + " 必须以本角色 ID 加冒号开头：" + role_id + ":")
    return identifier


def refs(root, value):
    result = []
    for ref in array(value, "sourceRefs"):
        project_path(root, ref)
        result.append(ref)
    return result


def read_role(root, folder):
    card = project_path(root, (folder / "role-card.md").relative_to(root).as_posix())
    title = next((line[2:].strip() for line in card.read_text(encoding="utf-8").splitlines()
                  if line.startswith("# ")), folder.name)
    role = {"id": folder.name, "name": title, "summary": "", "revision": None,
            "updatedAt": None, "hasArchitecture": False, "abstractions": [],
            "relations": [], "features": [], "dataFlows": []}
    path = project_path(root, (folder / "architecture.json").relative_to(root).as_posix())
    if not path.exists():
        return role
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise ValueError(str(path.relative_to(root)) + " 需要 schemaVersion: 1")
    if value.get("roleId") != folder.name:
        raise ValueError("roleId 必须与角色目录一致：" + folder.name)
    revision = value.get("revision")
    if type(revision) is not int or revision < 1:
        raise ValueError(folder.name + " 的 revision 必须是正整数")
    updated = required_text(value.get("updatedAt"), "updatedAt")
    date.fromisoformat(updated)
    role.update(summary=required_text(value.get("summary"), "summary"), revision=revision,
                updatedAt=updated, hasArchitecture=True)
    for raw in array(value.get("abstractions"), "abstractions"):
        if not isinstance(raw, dict):
            raise ValueError("抽象节点必须是对象")
        node = dict(raw)
        node["id"] = owned_id(node.get("id"), folder.name, "抽象 ID")
        node["name"] = required_text(node.get("name"), "抽象名称")
        node["description"] = required_text(node.get("description"), "抽象说明")
        if node.get("kind") not in NODE_KINDS or node.get("layer") not in LAYERS:
            raise ValueError("抽象类型或所属层不合法：" + node["id"])
        if node["kind"] == "model" and node["layer"] != "model":
            raise ValueError("Model 数据定义必须标为 model 层：" + node["id"])
        if type(node.get("public")) is not bool:
            raise ValueError("public 必须明确写 true 或 false：" + node["id"])
        node["status"] = node.get("status", "current")
        if node["status"] not in STATUSES:
            raise ValueError("未知的抽象状态：" + node["id"])
        node["sourceRefs"] = refs(root, node.get("sourceRefs", []))
        node["roleId"] = folder.name
        role["abstractions"].append(node)
    for raw in array(value.get("relations"), "relations"):
        if not isinstance(raw, dict) or raw.get("kind") not in RELATION_KINDS:
            raise ValueError("抽象关系不合法：" + folder.name)
        relation = dict(raw)
        relation["from"] = owned_id(relation.get("from"), folder.name, "关系发起方")
        relation["to"] = required_text(relation.get("to"), "关系目标")
        relation["roleId"] = folder.name
        role["relations"].append(relation)
    for raw in array(value.get("features"), "features"):
        if not isinstance(raw, dict):
            raise ValueError("功能必须是对象")
        feature = dict(raw)
        feature["id"] = owned_id(feature.get("id"), folder.name, "功能 ID")
        feature["name"] = required_text(feature.get("name"), "功能名称")
        feature["purpose"] = required_text(feature.get("purpose"), "功能用途")
        feature["abstractionIds"] = [required_text(item, "关联抽象 ID")
                                      for item in array(feature.get("abstractionIds"), "abstractionIds")]
        feature["sourceRefs"] = refs(root, feature.get("sourceRefs", []))
        feature["roleId"] = folder.name
        role["features"].append(feature)
    for raw in array(value.get("dataFlows"), "dataFlows"):
        if not isinstance(raw, dict):
            raise ValueError("数据流必须是对象")
        flow = dict(raw)
        flow["id"] = owned_id(flow.get("id"), folder.name, "数据流 ID")
        flow["from"] = owned_id(flow.get("from"), folder.name, "数据发出方")
        for key in ("to", "featureId", "data"):
            flow[key] = required_text(flow.get(key), "数据流 " + key)
        flow["kind"] = flow.get("kind", "send")
        if flow["kind"] not in ("send", "return"):
            raise ValueError("数据流 kind 必须是 send 或 return")
        flow["condition"] = flow.get("condition", "")
        if not isinstance(flow["condition"], str):
            raise ValueError("数据流条件必须是文字")
        flow["sourceRefs"] = refs(root, flow.get("sourceRefs", []))
        flow["roleId"] = folder.name
        role["dataFlows"].append(flow)
    return role


def build(root, roles=None):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("项目目录不存在")
    if roles is None:
        existing = [root / name for name in ("角色卡", "role-cards") if (root / name).is_dir()]
        if len(existing) != 1:
            raise ValueError("请用 --roles 指定唯一的项目角色目录")
        role_directory = project_path(root, existing[0].relative_to(root).as_posix())
    else:
        role_directory = project_path(root, roles)
    registry = []
    for folder in sorted(role_directory.iterdir()):
        if folder.is_dir() and not folder.is_symlink() and (folder / "role-card.md").is_file():
            registry.append(read_role(root, folder))
    if not registry:
        raise ValueError("角色目录中没有 role-card.md")
    nodes, features, flows, relations, issues = {}, {}, {}, [], []
    for role in registry:
        if not role["hasArchitecture"]:
            issues.append({"roleId": role["id"], "message": "该角色的 architecture.json 待补"})
        for collection, target, label in ((role["abstractions"], nodes, "抽象"),
                                          (role["features"], features, "功能"),
                                          (role["dataFlows"], flows, "数据流")):
            for item in collection:
                if item["id"] in target:
                    raise ValueError(label + " ID 重复：" + item["id"])
                target[item["id"]] = item
        relations.extend(role["relations"])
    def issue(role_id, message):
        issues.append({"roleId": role_id, "message": message})
    for node in nodes.values():
        if not node["sourceRefs"]:
            issue(node["roleId"], "抽象依据待补：" + node["name"])
        for ref in node["sourceRefs"]:
            if not project_path(root, ref).is_file():
                issue(node["roleId"], "依据文件待补：" + ref)
    for relation in relations:
        source, target = nodes.get(relation["from"]), nodes.get(relation["to"])
        relation["resolved"] = source is not None and target is not None
        if not relation["resolved"]:
            issue(relation["roleId"], "抽象引用待补：" + relation["from"] + " → " + relation["to"])
        elif source["roleId"] != target["roleId"] and not target["public"] and target["layer"] != "model":
            relation["resolved"] = False
            issue(relation["roleId"], "引用了其他角色未公开的抽象：" + target["name"])
    for feature in features.values():
        for identifier in feature["abstractionIds"]:
            if identifier not in nodes:
                issue(feature["roleId"], "功能关联的抽象待补：" + identifier)
        if not feature["abstractionIds"]:
            issue(feature["roleId"], "功能关联的抽象待补：" + feature["name"])
    for flow in flows.values():
        flow["resolved"] = flow["from"] in nodes and flow["to"] in nodes and flow["featureId"] in features
        if not flow["resolved"]:
            issue(flow["roleId"], "功能或数据流接点待补：" + flow["id"])
        elif nodes[flow["from"]]["roleId"] != nodes[flow["to"]]["roleId"] and not nodes[flow["to"]]["public"]:
            flow["resolved"] = False
            issue(flow["roleId"], "数据流指向其他角色未公开的抽象：" + nodes[flow["to"]]["name"])
    return {"schemaVersion": 1, "project": root.name,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "roles": registry, "nodes": list(nodes.values()), "relations": relations,
            "features": list(features.values()), "dataFlows": list(flows.values()), "issues": issues}


def render(root, output, roles=None):
    selected_root = Path(root).expanduser().absolute()
    root = selected_root.resolve()
    output = Path(output).expanduser()
    if output.is_absolute():
        if output.is_relative_to(selected_root):
            relative = output.relative_to(selected_root).as_posix()
        elif output.is_relative_to(root):
            relative = output.relative_to(root).as_posix()
        else:
            raise ValueError("生成页面必须位于项目的已批准输出目录")
    else:
        relative = output.as_posix()
    output = project_path(root, relative)
    if output.suffix != ".html":
        raise ValueError("输出文件必须是 .html")
    value = build(root, roles)
    payload = json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    page = (ASSETS / "index.html").read_text(encoding="utf-8")
    page = page.replace("__STYLE__", (ASSETS / "style.css").read_text(encoding="utf-8"))
    page = page.replace("__APP__", (ASSETS / "app.js").read_text(encoding="utf-8"))
    page = page.replace("__PROJECT__", html.escape(value["project"]))
    page = page.replace("__DATA__", payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    return {"html": str(output), "roles": len(value["roles"]), "abstractions": len(value["nodes"]),
            "features": len(value["features"]), "issues": len(value["issues"])}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="Approved HTML output path inside the project")
    parser.add_argument("--roles", help="Project-relative role directory")
    args = parser.parse_args(argv)
    try:
        result = render(args.root, args.out, args.roles)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
