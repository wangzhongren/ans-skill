"use strict";
const architecture = JSON.parse(document.getElementById("architecture-data").textContent);
const roles = new Map(architecture.roles.map(function (role) { return [role.id, role]; }));
const nodes = new Map(architecture.nodes.map(function (node) { return [node.id, node]; }));
const features = new Map(architecture.features.map(function (feature) { return [feature.id, feature]; }));
const layerNames = {interface: "入口", pipeline: "流程组合", service: "业务能力", provider: "资源访问", model: "共享数据", common: "工具与基础框架"};
const kindNames = {contains: "组成", manages: "管理", composes: "组合", uses: "使用", "uses-model": "引用数据", implements: "实现约定"};
const state = {view: "roles", roleId: null, nodeId: null, featureId: null};
if (architecture.features.length) state.featureId = architecture.features[0].id;
const graph = document.getElementById("graph");
const details = document.getElementById("details");
const controls = document.getElementById("controls");
const svgNamespace = "http://www.w3.org/2000/svg";

function el(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}
function svgEl(tag, attributes, text) {
  const element = document.createElementNS(svgNamespace, tag);
  Object.entries(attributes || {}).forEach(function (entry) { element.setAttribute(entry[0], entry[1]); });
  if (text !== undefined) element.textContent = text;
  return element;
}
function short(text, length) {
  if (text.length > length) return text.slice(0, length - 1) + "…";
  return text;
}
function button(text, action, className) {
  const result = el("button", className || "link-button", text);
  result.type = "button";
  result.addEventListener("click", action);
  return result;
}
function row(title, description) {
  const result = el("div", "detail-row");
  result.append(el("strong", "", title), el("span", "", description));
  return result;
}
function empty(title, description) {
  const result = el("div", "empty");
  result.append(el("strong", "", title), el("p", "", description));
  graph.append(result);
}
function sourceRefs(refs) {
  if (!refs.length) return;
  details.append(el("h4", "", "核对依据"));
  refs.forEach(function (ref) { details.append(el("span", "source-ref", ref)); });
}
function openRole(roleId, nodeId) {
  state.roleId = roleId;
  state.nodeId = nodeId || null;
  state.view = "internal";
  render();
}
function openFeature(featureId) {
  state.featureId = featureId;
  state.view = "flows";
  render();
}
function roleDetail(role) {
  details.replaceChildren(el("div", "detail-kicker", "ROLE / 角色"));
  details.append(el("h3", "", role.name), el("p", "", role.summary || "架构说明待补"));
  details.append(row("当前记录", "抽象 " + role.abstractions.length + " 项 · 功能 " + role.features.length + " 项"));
  if (role.revision !== null) details.append(row("角色版本 " + role.revision, "更新于 " + role.updatedAt));
  const dependencies = architecture.relations.filter(function (relation) {
    return relation.roleId === role.id && relation.resolved && nodes.get(relation.to).roleId !== role.id;
  });
  if (dependencies.length) {
    details.append(el("h4", "", "使用其他角色的约定"));
    dependencies.forEach(function (relation) {
      const target = nodes.get(relation.to);
      details.append(button(roles.get(target.roleId).name + " · " + target.name, function () {
        openRole(target.roleId, target.id);
      }));
      details.append(el("p", "", kindNames[relation.kind]));
    });
  }
  if (role.features.length) {
    details.append(el("h4", "", "负责的功能点"));
    role.features.forEach(function (feature) {
      details.append(row(feature.name, feature.purpose));
      details.append(button("查看数据流向", function () { openFeature(feature.id); }));
    });
  }
}
function nodeDetail(node) {
  details.replaceChildren(el("div", "detail-kicker", "ABSTRACTION / 抽象"));
  details.append(el("h3", "", node.name), el("p", "", node.description));
  const chips = el("div", "chips");
  chips.append(el("span", "chip", roles.get(node.roleId).name), el("span", "chip", layerNames[node.layer]));
  if (node.public) chips.append(el("span", "chip", "公开约定"));
  if (node.status === "planned") chips.append(el("span", "chip", "计划中"));
  if (node.status === "needs-review") chips.append(el("span", "chip", "待核实"));
  details.append(chips);
  const related = architecture.features.filter(function (feature) { return feature.abstractionIds.includes(node.id); });
  if (related.length) {
    details.append(el("h4", "", "支撑的功能"));
    related.forEach(function (feature) {
      details.append(row(feature.name, feature.purpose));
      details.append(button("看数据流向", function () { openFeature(feature.id); }));
    });
  }
  const outgoing = architecture.relations.filter(function (relation) { return relation.from === node.id; });
  if (outgoing.length) {
    details.append(el("h4", "", "抽象关系"));
    outgoing.forEach(function (relation) {
      const target = nodes.get(relation.to);
      if (target && relation.resolved) {
        details.append(button(kindNames[relation.kind] + " · " + target.name, function () {
          openRole(target.roleId, target.id);
        }));
      } else {
        details.append(row("引用待补", relation.to));
      }
    });
  }
  const passing = architecture.dataFlows.filter(function (flow) {
    return flow.resolved && (flow.from === node.id || flow.to === node.id);
  });
  if (passing.length) {
    details.append(el("h4", "", "相关输入输出"));
    passing.forEach(function (flow) {
      let direction = "接收";
      if (flow.from === node.id) direction = "发出";
      details.append(row(direction + " · " + flow.data, flow.condition || features.get(flow.featureId).name));
    });
  }
  sourceRefs(node.sourceRefs);
}
function drawing(width, height) {
  const svg = svgEl("svg", {viewBox: "0 0 " + width + " " + height, role: "img", "aria-label": document.getElementById("view-title").textContent});
  const marker = svgEl("marker", {id: "arrow", viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "6", markerHeight: "6", orient: "auto-start-reverse"});
  marker.append(svgEl("path", {d: "M 0 0 L 10 5 L 0 10 z", fill: "#88a79e"}));
  const defs = svgEl("defs");
  defs.append(marker);
  svg.append(defs);
  graph.append(svg);
  return svg;
}
function positions(identifiers, edges) {
  const dependencies = new Map(identifiers.map(function (id) { return [id, []]; }));
  edges.forEach(function (edge) {
    if (edge.kind !== "return" && edge.from !== edge.to && dependencies.has(edge.from) && dependencies.has(edge.to)) {
      dependencies.get(edge.from).push(edge.to);
    }
  });
  const incoming = new Map(identifiers.map(function (id) { return [id, 0]; }));
  dependencies.forEach(function (targets) {
    targets.forEach(function (id) { incoming.set(id, incoming.get(id) + 1); });
  });
  const depths = new Map(identifiers.map(function (id) { return [id, 0]; }));
  const queue = identifiers.filter(function (id) { return incoming.get(id) === 0; });
  for (let index = 0; index < queue.length; index += 1) {
    const id = queue[index];
    dependencies.get(id).forEach(function (target) {
      depths.set(target, Math.max(depths.get(target), depths.get(id) + 1));
      incoming.set(target, incoming.get(target) - 1);
      if (incoming.get(target) === 0) queue.push(target);
    });
  }
  const maximum = Math.max(0, ...depths.values());
  const groups = new Map();
  identifiers.forEach(function (id) {
    const column = depths.get(id);
    if (!groups.has(column)) groups.set(column, []);
    groups.get(column).push(id);
  });
  const largest = Math.max(1, ...Array.from(groups.values()).map(function (group) { return group.length; }));
  const width = Math.max(840, (maximum + 1) * 400 + 100);
  const height = Math.max(350, largest * 155 + 90);
  const result = new Map();
  groups.forEach(function (group, column) {
    group.forEach(function (id, index) {
      result.set(id, {x: 180 + column * 400, y: 45 + index * 155 + (largest - group.length) * 77});
    });
  });
  return {points: result, width: width, height: height};
}
function edge(svg, from, to, label, kind) {
  if (!from || !to) return;
  const forward = to.x > from.x;
  let startX = from.x + 212;
  let endX = to.x;
  if (!forward) {
    startX = from.x;
    endX = to.x + 212;
  }
  const startY = from.y + 39;
  const endY = to.y + 39;
  const middle = (startX + endX) / 2;
  let curve = "M " + startX + " " + startY + " C " + middle + " " + startY + " " + middle + " " + endY + " " + endX + " " + endY;
  if (from.x === to.x) {
    curve = "M " + from.x + " " + startY + " C " + (from.x - 100) + " " + startY + " " + (to.x - 100) + " " + endY + " " + to.x + " " + endY;
  }
  const path = svgEl("path", {d: curve, class: "edge " + (kind || "")});
  path.append(svgEl("title", {}, label));
  svg.append(path);
  let labelX = middle;
  if (from.x === to.x) labelX = from.x - 90;
  const text = svgEl("text", {x: labelX, y: (startY + endY) / 2 - 11, "text-anchor": "middle", class: "edge-label"}, short(label, 18));
  svg.append(text);
}
function graphNode(svg, position, title, meta, badge, action) {
  const group = svgEl("g", {class: "node", transform: "translate(" + position.x + "," + position.y + ")", tabindex: "0", role: "button", "aria-label": title});
  group.append(svgEl("rect", {width: "212", height: "82", rx: "11"}));
  group.append(svgEl("circle", {cx: "17", cy: "20", r: "3", class: "accent"}));
  group.append(svgEl("text", {x: "28", y: "25", class: "title"}, short(title, 12)));
  group.append(svgEl("text", {x: "16", y: "47", class: "meta"}, short(meta, 29)));
  group.append(svgEl("rect", {x: "15", y: "57", width: "95", height: "17", rx: "4", class: "badge"}));
  group.append(svgEl("text", {x: "22", y: "69", class: "badge-text"}, badge));
  group.append(svgEl("title", {}, title + " · " + meta));
  group.addEventListener("click", action);
  group.addEventListener("keydown", function (event) {
    if (event.key === "Enter" || event.key === " ") { event.preventDefault(); action(); }
  });
  svg.append(group);
}
function legend(items) {
  const target = document.getElementById("legend");
  target.replaceChildren();
  items.forEach(function (item) { target.append(el("span", item[1], item[0])); });
}
function roleOverview() {
  document.getElementById("view-title").textContent = "角色之间，靠什么配合";
  document.getElementById("view-help").textContent = "箭头表示使用对方的约定。点击角色，展开内部抽象。";
  details.append(el("div", "detail-kicker", "START HERE / 从这里开始"), el("h3", "", "沿着抽象看系统"), el("p", "", "先选择一个角色，看它提供哪些能力、依赖谁的约定。再从功能数据流进入具体模块。"));
  const grouped = new Map();
  architecture.relations.filter(function (relation) { return relation.resolved; }).forEach(function (relation) {
    const source = nodes.get(relation.from), target = nodes.get(relation.to);
    if (source.roleId === target.roleId) return;
    const key = source.roleId + "\n" + target.roleId;
    if (!grouped.has(key)) grouped.set(key, {from: source.roleId, to: target.roleId, labels: [], kind: "model"});
    const item = grouped.get(key);
    let label = target.name;
    if (source.status === "planned" || target.status === "planned") label += "（计划中）";
    item.labels.push(label);
    if (relation.kind !== "uses-model") item.kind = "";
  });
  const edges = Array.from(grouped.values());
  const layout = positions(architecture.roles.map(function (role) { return role.id; }), edges);
  const svg = drawing(layout.width, layout.height);
  edges.forEach(function (item) { edge(svg, layout.points.get(item.from), layout.points.get(item.to), item.labels.join(" / "), item.kind); });
  architecture.roles.forEach(function (role) {
    let badge = role.abstractions.length + " 项抽象";
    if (role.abstractions.some(function (node) { return node.status === "planned"; })) badge += " · 含计划项";
    if (!role.hasArchitecture) badge = "架构待补";
    graphNode(svg, layout.points.get(role.id), role.name, role.summary || "尚未记录本角色架构", badge, function () { openRole(role.id); });
  });
  legend([["使用公开约定", ""], ["引用共享数据", "model"]]);
}
function flowOverview() {
  document.getElementById("view-title").textContent = "一个功能，数据怎样走";
  document.getElementById("view-help").textContent = "每块是角色拥有的抽象模块。点击模块，定位到内部图。";
  const select = el("select");
  select.setAttribute("aria-label", "选择功能");
  architecture.features.forEach(function (feature) {
    const option = el("option", "", feature.name);
    option.value = feature.id;
    select.append(option);
  });
  select.value = state.featureId || "";
  select.addEventListener("change", function () { state.featureId = select.value; render(); });
  controls.append(select);
  const feature = features.get(state.featureId);
  if (!feature) {
    empty("功能数据流待补", "角色尚未记录功能点。页面不会按模块名称猜测流程。");
    details.append(el("h3", "", "先记录功能用途"), el("p", "", "在负责角色的 JSON 中关联功能和抽象，再由发出数据的角色记录传递关系。"));
    legend([]);
    return;
  }
  details.append(el("div", "detail-kicker", "FEATURE / 功能"), el("h3", "", feature.name), el("p", "", feature.purpose));
  details.append(row("主要负责角色", roles.get(feature.roleId).name));
  sourceRefs(feature.sourceRefs);
  const flows = architecture.dataFlows.filter(function (flow) { return flow.featureId === feature.id && flow.resolved; });
  if (!flows.length) {
    empty("这个功能的数据流待补", "已记录用途和相关抽象，但还没有核实的数据传递关系。");
    legend([]);
    return;
  }
  const identifiers = new Set();
  flows.forEach(function (flow) { identifiers.add(flow.from); identifiers.add(flow.to); });
  const layout = positions(Array.from(identifiers), flows);
  const svg = drawing(layout.width, layout.height);
  flows.forEach(function (flow) {
    let label = flow.data;
    if (flow.condition) label += " · " + flow.condition;
    edge(svg, layout.points.get(flow.from), layout.points.get(flow.to), label, flow.kind);
  });
  identifiers.forEach(function (identifier) {
    const node = nodes.get(identifier);
    let badge = layerNames[node.layer];
    if (node.status === "planned") badge += " · 计划中";
    if (node.status === "needs-review") badge += " · 待核实";
    graphNode(svg, layout.points.get(identifier), node.name, roles.get(node.roleId).name, badge, function () { openRole(node.roleId, node.id); });
  });
  details.append(el("h4", "", "传递与条件"));
  flows.forEach(function (flow) { details.append(row(flow.data, flow.condition || "已记录的传递关系")); });
  legend([["数据传递", ""], ["结果返回", "return"]]);
}
function internalView() {
  if (!state.roleId || !roles.has(state.roleId)) {
    const recorded = architecture.roles.find(function (role) { return role.hasArchitecture; });
    if (recorded) state.roleId = recorded.id;
    else state.roleId = architecture.roles[0].id;
  }
  const role = roles.get(state.roleId);
  document.getElementById("view-title").textContent = role.name + "的抽象脉络";
  document.getElementById("view-help").textContent = "展开主干看组成，点击抽象看说明；功能点挂在对应抽象下。";
  const select = el("select");
  select.setAttribute("aria-label", "选择角色");
  architecture.roles.forEach(function (item) {
    const option = el("option", "", item.name);
    option.value = item.id;
    select.append(option);
  });
  select.value = role.id;
  select.addEventListener("change", function () { openRole(select.value); });
  controls.append(select, button("返回总览", function () { state.view = "roles"; render(); }, ""));
  document.getElementById("breadcrumb").textContent = architecture.project + " / " + role.name;
  const selected = nodes.get(state.nodeId);
  if (selected && selected.roleId === role.id) nodeDetail(selected);
  else roleDetail(role);
  if (!role.abstractions.length) {
    if (role.hasArchitecture) empty("本角色未定义业务抽象", role.summary);
    else empty("本角色的抽象图待补", "由负责角色核对公开约定、内部抽象和引用，再更新自己的 architecture.json。");
    legend([]);
    return;
  }
  const own = new Set(role.abstractions.map(function (node) { return node.id; }));
  const hierarchyKinds = new Set(["contains", "manages", "composes"]);
  const hierarchy = role.relations.filter(function (relation) {
    return relation.resolved && own.has(relation.to) && hierarchyKinds.has(relation.kind);
  });
  const incoming = new Set(hierarchy.map(function (relation) { return relation.to; }));
  let roots = role.abstractions.filter(function (node) { return !incoming.has(node.id); });
  if (!roots.length) roots = role.abstractions;
  const mindmap = el("div", "mindmap");
  const trunk = el("div", "mindmap-role");
  trunk.append(el("strong", "", role.name), el("p", "", role.summary));
  const branches = el("div", "mindmap-branches");
  mindmap.append(trunk, branches);
  function hasFocus(id, trail) {
    if (id === state.nodeId) return true;
    if (trail.has(id)) return false;
    const next = new Set(trail);
    next.add(id);
    return hierarchy.some(function (relation) { return relation.from === id && hasFocus(relation.to, next); });
  }
  function branch(node, trail, depth, relationLabel) {
    const result = el("div", "branch");
    if (trail.has(node.id)) {
      result.append(button("引用 · " + node.name, function () { nodeDetail(node); }));
      return result;
    }
    const nextTrail = new Set(trail);
    nextTrail.add(node.id);
    const children = hierarchy.filter(function (relation) { return relation.from === node.id; });
    const linkedFeatures = architecture.features.filter(function (feature) { return feature.abstractionIds.includes(node.id); });
    const references = role.relations.filter(function (relation) {
      return relation.from === node.id && !hierarchy.includes(relation);
    });
    const card = el("div", "abstract-card");
    card.dataset.nodeId = node.id;
    if (node.id === state.nodeId) card.classList.add("selected");
    const childrenContainer = el("div", "branch-children");
    const toggle = button("−", function () {
      childrenContainer.hidden = !childrenContainer.hidden;
      if (childrenContainer.hidden) toggle.textContent = "+";
      else toggle.textContent = "−";
      toggle.setAttribute("aria-expanded", String(!childrenContainer.hidden));
    }, "toggle");
    toggle.setAttribute("aria-label", "展开或收起" + node.name);
    const label = button("", function () {
      state.nodeId = node.id;
      graph.querySelectorAll(".abstract-card").forEach(function (item) {
        item.classList.toggle("selected", item.dataset.nodeId === node.id);
      });
      nodeDetail(node);
    }, "abstract-label");
    let metadata = layerNames[node.layer];
    if (node.status === "planned") metadata += " · 计划中";
    if (node.status === "needs-review") metadata += " · 待核实";
    label.append(el("strong", "", node.name), el("span", "", metadata));
    card.append(toggle, label);
    if (relationLabel) card.append(el("span", "tree-relation", relationLabel));
    result.append(card, childrenContainer);
    children.forEach(function (relation) {
      childrenContainer.append(branch(nodes.get(relation.to), nextTrail, depth + 1, kindNames[relation.kind]));
    });
    references.forEach(function (relation) {
      const target = nodes.get(relation.to);
      const leaf = el("div", "leaf leaf-reference");
      if (target && relation.resolved) {
        let name = target.name;
        if (target.roleId !== node.roleId) name = roles.get(target.roleId).name + " · " + name;
        leaf.append(button(kindNames[relation.kind] + " → " + name, function () { openRole(target.roleId, target.id); }));
      } else leaf.textContent = "引用待补 · " + relation.to;
      childrenContainer.append(leaf);
    });
    linkedFeatures.forEach(function (feature) {
      const leaf = el("div", "leaf");
      leaf.append(el("span", "", "功能 · "), button(feature.name, function () { openFeature(feature.id); }));
      childrenContainer.append(leaf);
    });
    if (!children.length && !references.length && !linkedFeatures.length) {
      childrenContainer.hidden = true;
      toggle.hidden = true;
    } else {
      childrenContainer.hidden = depth > 0 && !hasFocus(node.id, new Set());
      if (childrenContainer.hidden) toggle.textContent = "+";
      toggle.setAttribute("aria-expanded", String(!childrenContainer.hidden));
    }
    return result;
  }
  roots.forEach(function (node) { branches.append(branch(node, new Set(), 0, "")); });
  graph.append(mindmap);
  legend([]);
}
function render() {
  graph.replaceChildren();
  details.replaceChildren();
  controls.replaceChildren();
  document.getElementById("breadcrumb").textContent = "";
  document.querySelectorAll("[data-view]").forEach(function (tab) {
    tab.classList.toggle("active", tab.dataset.view === state.view);
    tab.setAttribute("aria-selected", String(tab.dataset.view === state.view));
  });
  if (state.view === "flows") flowOverview();
  else if (state.view === "internal") internalView();
  else roleOverview();
}
document.getElementById("project").textContent = architecture.project;
document.getElementById("generated").textContent = "生成于 " + new Date(architecture.generatedAt).toLocaleString("zh-CN");
[[architecture.roles.length, "角色"], [architecture.nodes.length, "抽象"], [architecture.features.length, "功能点"]].forEach(function (item) {
  const metric = el("div", "metric");
  metric.append(el("strong", "", String(item[0])), el("span", "", item[1]));
  document.getElementById("summary").append(metric);
});
document.querySelectorAll("[data-view]").forEach(function (tab) {
  tab.addEventListener("click", function () { state.view = tab.dataset.view; render(); });
});
if (architecture.issues.length) {
  const block = el("details");
  block.append(el("summary", "", architecture.issues.length + " 项信息待补或需核对"));
  const list = el("ul");
  architecture.issues.forEach(function (issue) {
    let name = issue.roleId;
    if (roles.has(issue.roleId)) name = roles.get(issue.roleId).name;
    list.append(el("li", "", name + " · " + issue.message));
  });
  block.append(list);
  document.getElementById("issues").append(block);
}
render();
