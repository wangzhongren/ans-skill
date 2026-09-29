// Test client navigation in an in-memory DOM. This does not launch or control a browser.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync(process.argv[2], "utf8");
const data = html.match(/<script type="application\/json" id="architecture-data">([\s\S]*?)<\/script>/)[1];
const app = html.match(/<script>([\s\S]*?)<\/script>/)[1];

class Element {
  constructor(tag) {
    this.tagName = tag;
    this.children = [];
    this.attributes = {};
    this.dataset = {};
    this.events = {};
    this.className = "";
    this.hidden = false;
    this.ownText = "";
  }
  get textContent() { return this.ownText + this.children.map(child => child.textContent).join(""); }
  set textContent(value) { this.ownText = String(value); this.children = []; }
  get classList() {
    const element = this;
    function values() { return new Set(element.className.split(/\s+/).filter(Boolean)); }
    return {
      add(name) { const names = values(); names.add(name); element.className = [...names].join(" "); },
      toggle(name, enabled) {
        const names = values();
        if (enabled === undefined) enabled = !names.has(name);
        if (enabled) names.add(name); else names.delete(name);
        element.className = [...names].join(" ");
      },
      contains(name) { return values().has(name); }
    };
  }
  append(...elements) {
    elements.forEach(element => { element.parentNode = this; this.children.push(element); });
  }
  replaceChildren(...elements) { this.ownText = ""; this.children = []; this.append(...elements); }
  setAttribute(name, value) {
    this.attributes[name] = String(value);
    if (name === "class") this.className = String(value);
    if (name.startsWith("data-")) this.dataset[name.slice(5)] = String(value);
  }
  getAttribute(name) { return this.attributes[name]; }
  addEventListener(type, handler) {
    if (!this.events[type]) this.events[type] = [];
    this.events[type].push(handler);
  }
  dispatch(type, extra = {}) {
    for (const handler of this.events[type] || []) handler({target: this, preventDefault() {}, ...extra});
  }
  querySelectorAll(selector) {
    function matches(element) {
      if (selector.startsWith(".")) return element.classList.contains(selector.slice(1));
      if (selector === "[data-view]") return element.dataset.view !== undefined;
      return element.tagName === selector;
    }
    const result = [];
    function walk(element) {
      for (const child of element.children) { if (matches(child)) result.push(child); walk(child); }
    }
    walk(this);
    return result;
  }
}
const root = new Element("body");
const byId = new Map();
for (const id of ["architecture-data", "project", "generated", "summary", "graph", "details",
  "controls", "view-title", "view-help", "breadcrumb", "legend", "issues"]) {
  const element = new Element("div");
  root.append(element);
  byId.set(id, element);
}
byId.get("architecture-data").textContent = data;
for (const view of ["roles", "flows", "internal"]) {
  const tab = new Element("button");
  tab.setAttribute("data-view", view);
  root.append(tab);
}
const document = {
  getElementById(id) { return byId.get(id); },
  createElement(tag) { return new Element(tag); },
  createElementNS(_namespace, tag) { return new Element(tag); },
  querySelectorAll(selector) { return root.querySelectorAll(selector); }
};
vm.runInNewContext(app, {document, console});
const graph = byId.get("graph");
function tab(view) { root.querySelectorAll("[data-view]").find(item => item.dataset.view === view).dispatch("click"); }
function clickGraphNode(name) {
  const node = graph.querySelectorAll("g").find(item => item.getAttribute("aria-label") === name);
  assert.ok(node, "Graph node exists: " + name);
  node.dispatch("click");
}
function clickButton(text) {
  const item = root.querySelectorAll("button").find(button => button.textContent === text);
  assert.ok(item, "Button exists: " + text);
  item.dispatch("click");
}
let checks = 0;
assert.match(byId.get("view-title").textContent, /角色之间/); checks++;
clickGraphNode("场景管理");
assert.match(byId.get("view-title").textContent, /场景管理的抽象脉络/); checks++;
const toggle = graph.querySelectorAll("button").find(item => item.getAttribute("aria-label") === "展开或收起场景管理约定");
const childBranch = toggle.parentNode.parentNode.children.find(item => item.classList.contains("branch-children"));
toggle.dispatch("click"); assert.equal(childBranch.hidden, true);
toggle.dispatch("click"); assert.equal(childBranch.hidden, false); checks++;
tab("flows");
let select = byId.get("controls").querySelectorAll("select")[0];
select.value = "装配:start"; select.dispatch("change");
assert.match(byId.get("details").textContent, /启动主循环/);
assert.match(graph.textContent, /固定更新与渲染回调/); checks++;
clickGraphNode("主循环约定");
assert.match(byId.get("view-title").textContent, /主循环的抽象脉络/);
assert.ok(graph.querySelectorAll(".abstract-card").some(item => item.dataset.nodeId === "主循环:GameLoop" && item.classList.contains("selected"))); checks++;
clickButton("引用数据 → 装配 · 引擎配置");
assert.match(byId.get("view-title").textContent, /装配的抽象脉络/);
assert.ok(graph.querySelectorAll(".abstract-card").some(item => item.dataset.nodeId === "装配:EngineConfig" && item.classList.contains("selected"))); checks++;
tab("flows");
select = byId.get("controls").querySelectorAll("select")[0];
select.value = "场景管理:switch"; select.dispatch("change");
assert.match(graph.textContent, /数据流待补/);
assert.equal(graph.querySelectorAll("svg").length, 0); checks++;
tab("internal");
clickButton("返回总览");
assert.match(byId.get("view-title").textContent, /角色之间/);
assert.equal(graph.querySelectorAll("g").length, 4); checks++;
console.log(JSON.stringify({checks, views: ["roles", "flows", "internal"], browserUsed: false}));
