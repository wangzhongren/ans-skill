import importlib.util
import json
from pathlib import Path
import re
from shutil import copy2, which
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "render_architecture.py"
spec = importlib.util.spec_from_file_location("architecture_renderer", SCRIPT)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def example_project(root):
    repository = Path(__file__).resolve().parents[2]
    fixture = json.loads((repository / "scripts/tests/fixtures/architecture-example.json").read_text(encoding="utf-8"))
    source = repository / fixture["sourceProject"]
    paths = set()
    for role in fixture["roles"]:
        folder = root / "角色卡" / role["roleId"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "role-card.md").write_text("# " + role["roleId"], encoding="utf-8")
        (folder / "architecture.json").write_text(json.dumps(role, ensure_ascii=False, indent=2), encoding="utf-8")
        for collection in ("abstractions", "features", "dataFlows"):
            for item in role[collection]:
                paths.update(item.get("sourceRefs", []))
    for relative in paths:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        copy2(source / relative, destination)


def abstraction(identifier, name, layer, public=True):
    kind = "contract"
    if layer == "model":
        kind = "model"
    return {"id": identifier, "name": name, "kind": kind, "layer": layer, "public": public,
            "description": name + "的用途说明", "sourceRefs": ["src/contracts.txt"]}


def architecture(role_id, nodes):
    return {"schemaVersion": 1, "roleId": role_id, "revision": 1,
            "updatedAt": "2026-09-29", "summary": role_id + "的职责说明",
            "abstractions": nodes, "relations": [], "features": [], "dataFlows": []}


class ArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "src").mkdir()
        (self.root / "src/contracts.txt").write_text("verified test contracts", encoding="utf-8")
        self.a = architecture("a", [abstraction("a:Flow", "流程组合", "pipeline"),
                                    abstraction("a:Service", "业务操作", "service"),
                                    abstraction("a:Data", "共享数据", "model")])
        self.b = architecture("b", [abstraction("b:Store", "存取约定", "provider")])
        self.a["relations"] = [{"from": "a:Flow", "to": "a:Service", "kind": "composes"},
                               {"from": "a:Service", "to": "b:Store", "kind": "uses"}]
        self.b["relations"] = [{"from": "b:Store", "to": "a:Data", "kind": "uses-model"}]
        self.a["features"] = [{"id": "a:save", "name": "保存内容", "purpose": "保存当前内容以供后续读取。",
                               "abstractionIds": ["a:Flow", "a:Service", "b:Store"],
                               "sourceRefs": ["src/contracts.txt"]}]
        self.a["dataFlows"] = [{"id": "a:request", "featureId": "a:save", "from": "a:Service",
                                "to": "b:Store", "data": "待保存内容", "sourceRefs": ["src/contracts.txt"]}]
        self.b["dataFlows"] = [{"id": "b:result", "featureId": "a:save", "from": "b:Store",
                                "to": "a:Service", "data": "保存结果", "kind": "return"}]
        self.write_role(self.a)
        self.write_role(self.b)

    def write_role(self, value):
        folder = self.root / "role-cards" / value["roleId"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "role-card.md").write_text("# 角色 " + value["roleId"], encoding="utf-8")
        (folder / "architecture.json").write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return folder / "architecture.json"

    def page_data(self, output):
        page = output.read_text(encoding="utf-8")
        match = re.search(r'<script type="application/json" id="architecture-data">(.*?)</script>', page, re.S)
        self.assertIsNotNone(match)
        return json.loads(match.group(1))

    def test_combines_ownership_and_cross_role_function_flows(self):
        value = renderer.build(self.root)
        self.assertEqual(len(value["roles"]), 2)
        self.assertEqual({node["id"] for node in value["nodes"]},
                         {"a:Flow", "a:Service", "a:Data", "b:Store"})
        self.assertTrue(all(relation["resolved"] for relation in value["relations"]))
        self.assertTrue(all(flow["resolved"] for flow in value["dataFlows"]))
        self.assertEqual({flow["featureId"] for flow in value["dataFlows"]}, {"a:save"})
        self.assertEqual(value["issues"], [])

    def test_verified_contract_example_generates_all_three_views(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            example_project(root)
            output = root / "doc/architecture/index.html"
            result = renderer.render(root, output)
            data = self.page_data(output)
            self.assertEqual(result["roles"], 4)
            self.assertEqual(result["abstractions"], 13)
            self.assertEqual(result["features"], 4)
            self.assertEqual(result["issues"], 0)
            self.assertEqual(len(data["dataFlows"]), 4)
            self.assertTrue(all(flow["resolved"] for flow in data["dataFlows"]))

    def test_client_navigation_and_collapse_with_offline_dom(self):
        node = which("node")
        if node is None:
            self.skipTest("Node.js is needed for the in-memory DOM navigation check")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            example_project(root)
            output = root / "doc/architecture/index.html"
            renderer.render(root, output)
            helper = Path(__file__).parent / "helpers/architecture_viewer.cjs"
            result = subprocess.run([node, str(helper), str(output)],
                                    capture_output=True, text=True, check=True, timeout=15)
            report = json.loads(result.stdout)
            self.assertEqual(report["checks"], 8)
            self.assertEqual(report["views"], ["roles", "flows", "internal"])
            self.assertFalse(report["browserUsed"])

    def test_offline_html_contains_data_and_leaves_sources_unchanged(self):
        original = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        output = self.root / "doc/architecture/index.html"
        result = renderer.render(self.root, output)
        self.assertEqual(result["abstractions"], 4)
        self.assertEqual(len(self.page_data(output)["dataFlows"]), 2)
        page = output.read_text(encoding="utf-8")
        self.assertNotIn("__DATA__", page)
        self.assertNotIn("__STYLE__", page)
        self.assertNotIn("__APP__", page)
        self.assertNotRegex(page, r'<(?:script|link)[^>]+(?:src|href)=["\']https?://')
        for path, contents in original.items():
            self.assertEqual(path.read_bytes(), contents)
        self.assertEqual(set(path for path in self.root.rglob("*") if path.is_file()),
                         set(original) | {output})

    def test_untrusted_text_cannot_close_embedded_json_script(self):
        attack = "</script><script>window.architectureInjected=true</script>"
        self.a["abstractions"][0]["name"] = attack
        self.write_role(self.a)
        output = self.root / "doc/architecture/index.html"
        renderer.render(self.root, output)
        page = output.read_text(encoding="utf-8")
        self.assertEqual(page.count("</script>"), 2)
        self.assertNotIn(attack, page)
        self.assertEqual(self.page_data(output)["nodes"][0]["name"], attack)

    def test_missing_role_json_is_visible_without_invented_nodes(self):
        folder = self.root / "role-cards/c"
        folder.mkdir()
        (folder / "role-card.md").write_text("# 待补角色", encoding="utf-8")
        value = renderer.build(self.root)
        self.assertEqual(len(value["roles"]), 3)
        self.assertFalse(value["roles"][-1]["hasArchitecture"])
        self.assertFalse(any(node["roleId"] == "c" for node in value["nodes"]))
        self.assertIn("architecture.json 待补", value["issues"][0]["message"])

    def test_missing_and_private_targets_are_not_shown_as_resolved(self):
        self.a["relations"].append({"from": "a:Service", "to": "missing:Contract", "kind": "uses"})
        self.b["abstractions"][0]["public"] = False
        self.write_role(self.a)
        self.write_role(self.b)
        value = renderer.build(self.root)
        unresolved = [item for item in value["relations"] if not item["resolved"]]
        self.assertEqual(len(unresolved), 2)
        self.assertFalse(value["dataFlows"][0]["resolved"])
        self.assertTrue(any("未公开" in issue["message"] for issue in value["issues"]))
        self.assertTrue(any("待补" in issue["message"] for issue in value["issues"]))

    def test_invalid_or_duplicate_nodes_preserve_existing_page(self):
        output = self.root / "doc/architecture/index.html"
        output.parent.mkdir(parents=True)
        output.write_text("last valid graph", encoding="utf-8")
        self.a["abstractions"].append(dict(self.a["abstractions"][0]))
        self.write_role(self.a)
        with self.assertRaisesRegex(ValueError, "重复"):
            renderer.render(self.root, output)
        self.assertEqual(output.read_text(), "last valid graph")

    def test_roles_cannot_define_another_roles_nodes_or_outgoing_flows(self):
        original = json.loads(json.dumps(self.a))
        for collection, key in (("abstractions", "id"), ("relations", "from"), ("dataFlows", "from")):
            self.a = json.loads(json.dumps(original))
            self.a[collection][0][key] = "b:Store"
            self.write_role(self.a)
            with self.subTest(collection=collection), self.assertRaisesRegex(ValueError, "本角色"):
                renderer.build(self.root)

    def test_json_update_changes_generated_structure_and_version(self):
        output = self.root / "doc/architecture/index.html"
        renderer.render(self.root, output)
        self.a["revision"] = 2
        self.a["abstractions"].append(abstraction("a:Rules", "业务规则", "service", public=False))
        self.a["relations"].append({"from": "a:Service", "to": "a:Rules", "kind": "contains"})
        self.write_role(self.a)
        renderer.render(self.root, output)
        updated = self.page_data(output)
        self.assertEqual(updated["roles"][0]["revision"], 2)
        self.assertIn("a:Rules", {node["id"] for node in updated["nodes"]})

    def test_planned_abstractions_and_missing_evidence_keep_their_status(self):
        self.a["abstractions"][0]["status"] = "planned"
        self.a["abstractions"][0]["sourceRefs"] = ["src/planned-contract.ts"]
        self.write_role(self.a)
        value = renderer.build(self.root)
        self.assertEqual(value["nodes"][0]["status"], "planned")
        self.assertTrue(any("依据文件待补" in issue["message"] for issue in value["issues"]))

    def test_output_and_input_symlinks_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "linked").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "符号链接"):
                renderer.render(self.root, self.root / "linked/index.html")
            self.assertFalse((Path(outside) / "index.html").exists())
            path = self.root / "role-cards/a/architecture.json"
            content = path.read_text()
            target = Path(outside) / "architecture.json"
            target.write_text(content, encoding="utf-8")
            path.unlink()
            path.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "符号链接"):
                renderer.build(self.root)

    def test_role_directory_and_output_paths_are_explicit(self):
        (self.root / "角色卡").mkdir()
        with self.assertRaisesRegex(ValueError, "--roles"):
            renderer.build(self.root)
        self.assertEqual(len(renderer.build(self.root, "role-cards")["roles"]), 2)
        with self.assertRaisesRegex(ValueError, "相对路径"):
            renderer.render(self.root, self.root / "../outside.html", "role-cards")


if __name__ == "__main__":
    unittest.main()
