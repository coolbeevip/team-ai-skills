const skills = Array.isArray(window.SRT_SKILLS) ? window.SRT_SKILLS : [];

const translations = {
  zh: {
    pageTitle: "Skills For Real Teams · AI 团队工作流",
    pageDescription: "Skills For Real Teams：把产品定义、代码库理解、交付执行与技术债治理组织成可追溯的 AI 团队工作流。",
    skipLink: "跳到主要内容",
    skillFilters: "技能分类筛选",
    heroTitle: "让 AI 像团队一样<span class=\"title-line\">真正完成<span class=\"title-emphasis\">交付</span></span>",
    heroDescription: "从可评审 PRD 到可提交 Task，再用一个 PR 或 MR 完成交付。",
    copy: "复制",
    copied: "已复制",
    copyFailed: "复制失败",
    explore: "浏览全部技能",
    seeWorkflow: "查看工作流",
    heroConsoleAria: "技能安装",
    heroInstallLabel: "安装完整技能库",
    heroInstallDescription: "选择 Agent，再复制这一条安装命令。",
    agentPickerAria: "选择 Agent",
    skillStatLabel: "项技能",
    domainStatLabel: "个领域",
    agentStatLabel: "种 Agent",
    workflowIndex: "稳定主线",
    workflowTitle: "从想清楚<br /><span>到真正交付</span>",
    workflowDescription: "技能不是孤立菜单。每条路径都明确上游输入、阶段产物和下一位接棒者。",
    routeProduct: "产品需求",
    routeProductNote: "从规格到一个 Spec PR / MR",
    routeDebt: "技术债",
    routeDebtNote: "从证据到可提交修复",
    routeCodebase: "代码库理解",
    routeCodebaseNote: "从接手到业务说明",
    skillsIndex: "技能索引",
    skillsTitle: "按工作场景<br /><span>找到下一棒</span>",
    skillsDescription: "技能目录由仓库中的 SKILL.md 自动生成。搜索任务、产物或技能名称，快速定位下一步。",
    searchLabel: "搜索技能",
    searchPlaceholder: "搜索技能、任务或产物…",
    clearSearch: "清除",
    filterAll: "全部",
    filterConfig: "配置",
    filterProduct: "产品",
    filterCodebase: "代码库",
    filterDelivery: "交付",
    filterDebt: "技术债",
    filterWriting: "写作",
    filterArchive: "归档提炼",
    resultCount: "显示 {count} / {total} 项技能",
    groupCount: "{count} 项",
    emptyTitle: "没有匹配的技能",
    emptyDescription: "换一个关键词，或清除分类筛选。",
    resetFilters: "重置筛选",
    version: "版本",
    copySkill: "复制名称",
    copySkillAria: "复制技能名称 {name}",
    artifactIndex: "文件即状态",
    artifactTitle: "对话会消失<br /><span>产物会留下</span>",
    artifactDescription: "每一步都写入明确路径，让下一个技能、评审者或开发者知道当前状态、证据和下一步。",
    terminalFoot: "可追溯 / 可评审 / 可恢复",
    skillSummary: "{skills} 项技能 / {domains} 个领域",
    footerNote: "面向真实软件团队的文件化 AI 工作流。"
  },
  en: {
    pageTitle: "Skills For Real Teams · File-based AI team workflows",
    pageDescription: "Skills For Real Teams organizes product definition, codebase understanding, delivery execution, and technical-debt work into traceable AI team workflows.",
    skipLink: "Skip to main content",
    skillFilters: "Skill category filters",
    heroTitle: "Make AI a teammate.<span class=\"title-line\">Then <span class=\"title-emphasis\">ship.</span></span>",
    heroDescription: "Turn each reviewable PRD into commit-sized Tasks, then deliver the Spec through one PR or MR.",
    copy: "Copy",
    copied: "Copied",
    copyFailed: "Copy failed",
    explore: "Browse all skills",
    seeWorkflow: "See the workflow",
    heroConsoleAria: "Skill installation",
    heroInstallLabel: "Install the complete skill set",
    heroInstallDescription: "Choose an agent, then copy this single install command.",
    agentPickerAria: "Choose an agent",
    skillStatLabel: "skills",
    domainStatLabel: "domains",
    agentStatLabel: "agents",
    workflowIndex: "STABLE LINES",
    workflowTitle: "From clear intent<br /><span>to real delivery.</span>",
    workflowDescription: "Skills are not an isolated menu. Every route defines its upstream input, stage artifact, and next handoff.",
    routeProduct: "Product delivery",
    routeProductNote: "From specification to one Spec PR or MR",
    routeDebt: "Technical debt",
    routeDebtNote: "From evidence to commit-sized remediation",
    routeCodebase: "Codebase understanding",
    routeCodebaseNote: "From onboarding to stakeholder clarity",
    skillsIndex: "SKILL INDEX",
    skillsTitle: "Browse by the work.<br /><span>Find the next handoff.</span>",
    skillsDescription: "The index is generated from SKILL.md files in the repository. Search by task, artifact, or skill name to find the next move.",
    searchLabel: "Search skills",
    searchPlaceholder: "Search skills, tasks, or artifacts…",
    clearSearch: "Clear",
    filterAll: "All",
    filterConfig: "Config",
    filterProduct: "Product",
    filterCodebase: "Codebase",
    filterDelivery: "Delivery",
    filterDebt: "Tech debt",
    filterWriting: "Writing",
    filterArchive: "Archive",
    resultCount: "Showing {count} of {total} skills",
    groupCount: "{count} skills",
    emptyTitle: "No matching skills",
    emptyDescription: "Try another term or clear the category filter.",
    resetFilters: "Reset filters",
    version: "VERSION",
    copySkill: "Copy name",
    copySkillAria: "Copy skill name {name}",
    artifactIndex: "FILES AS STATE",
    artifactTitle: "Conversations disappear.<br /><span>Artifacts remain.</span>",
    artifactDescription: "Every step writes to an explicit path so the next skill, reviewer, or developer can see the current state, evidence, and next move.",
    terminalFoot: "TRACEABLE / REVIEWABLE / RESUMABLE",
    skillSummary: "{skills} SKILLS / {domains} DOMAINS",
    footerNote: "File-based AI workflows for real software teams."
  }
};

const categoryLabels = {
  zh: {
    config: "运行时配置",
    product: "产品定义",
    codebase: "代码库理解",
    delivery: "交付执行",
    "tech-debt": "技术债治理",
    writing: "写作规范",
    harness: "归档提炼"
  },
  en: {
    config: "Runtime config",
    product: "Product definition",
    codebase: "Codebase understanding",
    delivery: "Delivery execution",
    "tech-debt": "Technical debt",
    writing: "Writing standards",
    harness: "Archive distillation"
  }
};

const categoryOrder = [
  "config",
  "product",
  "codebase",
  "delivery",
  "tech-debt",
  "writing",
  "harness"
];

let activeCategory = "all";
let activeSearch = "";
let revealObserver = null;

function observeReveals(root = document) {
  const elements = root.querySelectorAll(
    "[data-reveal]:not([data-reveal-observed])"
  );
  if (!elements.length) return;

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    elements.forEach((element) => {
      element.dataset.revealObserved = "true";
      element.dataset.revealState = "visible";
    });
    return;
  }

  if (!revealObserver) {
    revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.dataset.revealState = "visible";
          revealObserver.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8%", threshold: 0.12 }
    );
  }

  elements.forEach((element) => {
    element.dataset.revealObserved = "true";
    revealObserver.observe(element);
  });
}

function format(template, values) {
  return Object.entries(values).reduce(
    (result, [key, value]) => result.replaceAll(`{${key}}`, String(value)),
    template
  );
}

function currentLanguage() {
  return document.documentElement.dataset.language || "zh";
}

function persistLanguage(language) {
  try {
    window.localStorage.setItem("srt-language", language);
  } catch {
    // Language persistence is optional when storage is unavailable.
  }
}

async function copyText(text) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.append(textarea);
  textarea.select();
  const copied = document.execCommand("copy");
  textarea.remove();
  if (!copied) throw new Error("Copy command failed");
}

function createSkillRow(skill, language) {
  const dictionary = translations[language];
  const row = document.createElement("article");
  row.className = "skill-row";
  row.dataset.category = skill.category;

  const name = document.createElement("h3");
  name.className = "skill-name";
  name.textContent = skill.name;

  const description = document.createElement("p");
  description.className = "skill-description";
  description.textContent = skill.description[language];

  const actions = document.createElement("div");
  actions.className = "skill-actions";

  const copyButton = document.createElement("button");
  copyButton.type = "button";
  copyButton.className = "copy-skill-button";
  copyButton.textContent = dictionary.copySkill;
  copyButton.setAttribute(
    "aria-label",
    format(dictionary.copySkillAria, { name: skill.name })
  );
  copyButton.addEventListener("click", async () => {
    try {
      await copyText(skill.name);
      copyButton.textContent = translations[currentLanguage()].copied;
      window.setTimeout(() => {
        copyButton.textContent = translations[currentLanguage()].copySkill;
      }, 1400);
    } catch {
      copyButton.textContent = translations[currentLanguage()].copyFailed;
      window.setTimeout(() => {
        copyButton.textContent = translations[currentLanguage()].copySkill;
      }, 1400);
    }
  });

  actions.append(copyButton);
  row.append(name, actions, description);
  return row;
}

function createSkillGroup(category, groupSkills, language) {
  const dictionary = translations[language];
  const group = document.createElement("section");
  group.className = "skill-group";
  group.dataset.category = category;
  group.dataset.reveal = "";

  const heading = document.createElement("header");
  heading.className = "skill-group-heading";

  const title = document.createElement("h3");
  title.textContent = categoryLabels[language][category] || category;

  const count = document.createElement("span");
  count.textContent = format(dictionary.groupCount, { count: groupSkills.length });

  const list = document.createElement("div");
  list.className = "skill-list";
  list.append(...groupSkills.map((skill) => createSkillRow(skill, language)));

  heading.append(title, count);
  group.append(heading, list);
  return group;
}

function renderSkills() {
  const language = currentLanguage();
  const dictionary = translations[language];
  const normalizedSearch = activeSearch.trim().toLocaleLowerCase(language);
  const filteredSkills = skills.filter((skill) => {
    const matchesCategory =
      activeCategory === "all" || skill.category === activeCategory;
    const searchText = [
      skill.name,
      skill.description.zh,
      skill.description.en,
      ...skill.triggers
    ].join(" ").toLocaleLowerCase(language);
    return matchesCategory && searchText.includes(normalizedSearch);
  });

  const grid = document.querySelector("[data-skills-grid]");
  const empty = document.querySelector("[data-skill-empty]");
  const count = document.querySelector("[data-skill-result-count]");
  if (!grid || !empty || !count) return;

  const categories = [
    ...categoryOrder,
    ...filteredSkills
      .map((skill) => skill.category)
      .filter((category) => !categoryOrder.includes(category))
  ];
  const groups = categories
    .map((category) => ({
      category,
      groupSkills: filteredSkills.filter((skill) => skill.category === category)
    }))
    .filter(({ groupSkills }) => groupSkills.length > 0)
    .map(({ category, groupSkills }) =>
      createSkillGroup(category, groupSkills, language)
    );

  grid.replaceChildren(...groups);
  grid.hidden = filteredSkills.length === 0;
  empty.hidden = filteredSkills.length !== 0;
  count.textContent = format(dictionary.resultCount, {
    count: filteredSkills.length,
    total: skills.length
  });
  if (document.documentElement.classList.contains("motion-ready")) {
    observeReveals(grid);
  }
}

function setLanguage(language, save = true) {
  const dictionary = translations[language];
  document.documentElement.dataset.language = language;
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  document.title = dictionary.pageTitle;
  document
    .querySelector('meta[name="description"]')
    ?.setAttribute("content", dictionary.pageDescription);

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (dictionary[key]) element.textContent = dictionary[key];
  });

  document.querySelectorAll("[data-i18n-html]").forEach((element) => {
    const key = element.dataset.i18nHtml;
    if (dictionary[key]) element.innerHTML = dictionary[key];
  });

  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    const key = element.dataset.i18nAriaLabel;
    if (dictionary[key]) element.setAttribute("aria-label", dictionary[key]);
  });

  const searchInput = document.querySelector("[data-skill-search]");
  if (searchInput) searchInput.placeholder = dictionary.searchPlaceholder;

  const skillSummary = document.querySelector("[data-skill-summary]");
  const domainCount = new Set(skills.map((skill) => skill.category)).size;
  if (skillSummary) {
    skillSummary.textContent = format(dictionary.skillSummary, {
      skills: skills.length,
      domains: domainCount
    });
  }

  document.querySelectorAll("[data-skill-count]").forEach((element) => {
    element.textContent = String(skills.length);
  });
  document.querySelectorAll("[data-domain-count]").forEach((element) => {
    element.textContent = String(domainCount);
  });

  document.querySelectorAll("[data-language-option]").forEach((button) => {
    const active = button.dataset.languageOption === language;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });

  renderSkills();
  if (save) persistLanguage(language);
}

document.querySelectorAll("[data-language-option]").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.languageOption));
});

const agentButtons = document.querySelectorAll("[data-agent-command]");
const activeCommand = document.querySelector("[data-active-command]");
const activeCommandPanel = activeCommand?.closest(".active-command");

agentButtons.forEach((button) => {
  button.addEventListener("click", () => {
    agentButtons.forEach((agentButton) => {
      const active = agentButton === button;
      agentButton.classList.toggle("is-active", active);
      agentButton.setAttribute("aria-pressed", String(active));
    });
    if (!activeCommand) return;
    activeCommand.textContent = button.dataset.agentCommand;
    activeCommandPanel?.classList.remove("is-switching");
    window.requestAnimationFrame(() => {
      activeCommandPanel?.classList.add("is-switching");
    });
  });
});

document.querySelector("[data-copy-active-command]")?.addEventListener("click", async (event) => {
  const label = event.currentTarget.querySelector(".copy-label");
  const command = document.querySelector("[data-agent-command].is-active")?.dataset
    .agentCommand;
  if (!command) return;
  try {
    await copyText(command);
    if (label) label.textContent = translations[currentLanguage()].copied;
  } catch {
    if (label) label.textContent = translations[currentLanguage()].copyFailed;
  }
  window.setTimeout(() => {
    if (label) label.textContent = translations[currentLanguage()].copy;
  }, 1400);
});

const searchInput = document.querySelector("[data-skill-search]");
const searchClear = document.querySelector("[data-search-clear]");

searchInput?.addEventListener("input", (event) => {
  activeSearch = event.target.value;
  if (searchClear) searchClear.hidden = activeSearch.length === 0;
  renderSkills();
});

searchClear?.addEventListener("click", () => {
  activeSearch = "";
  searchInput.value = "";
  searchClear.hidden = true;
  searchInput.focus();
  renderSkills();
});

document.querySelectorAll("[data-category]").forEach((button) => {
  button.addEventListener("click", () => {
    activeCategory = button.dataset.category;
    document.querySelectorAll("[data-category]").forEach((filterButton) => {
      const active = filterButton === button;
      filterButton.classList.toggle("is-active", active);
      filterButton.setAttribute("aria-pressed", String(active));
    });
    renderSkills();
  });
});

document.querySelector("[data-reset-skills]")?.addEventListener("click", () => {
  activeCategory = "all";
  activeSearch = "";
  if (searchInput) searchInput.value = "";
  if (searchClear) searchClear.hidden = true;
  document.querySelectorAll("[data-category]").forEach((button) => {
    const active = button.dataset.category === "all";
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  renderSkills();
});

const queryLanguage = new URLSearchParams(window.location.search).get("lang");
let storedLanguage = null;
try {
  storedLanguage = window.localStorage.getItem("srt-language");
} catch {
  storedLanguage = null;
}
const initialLanguage = ["zh", "en"].includes(queryLanguage)
  ? queryLanguage
  : ["zh", "en"].includes(storedLanguage)
    ? storedLanguage
    : "zh";

setLanguage(initialLanguage, false);
document.documentElement.classList.add("motion-ready");
observeReveals();
