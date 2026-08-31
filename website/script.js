const skills = Array.isArray(window.SRT_SKILLS) ? window.SRT_SKILLS : [];

const translations = {
  zh: {
    pageTitle: "Skills For Real Teams — AI 团队工作流",
    pageDescription: "Skills For Real Teams：把产品定义、代码库理解、交付执行与技术债治理组织成可追溯的 AI 团队工作流。",
    skipLink: "跳到主要内容",
    mainNavigation: "主导航",
    posterPreview: "产品海报预览",
    skillFilters: "技能分类筛选",
    navCapabilities: "能力",
    navWorkflow: "工作流",
    navSkills: "技能",
    navQuickstart: "开始使用",
    heroEyebrow: "FILE-BASED AI TEAM SYSTEM",
    heroTitle: "<span class=\"title-line title-line-primary\">让 AI 不只回答</span><span class=\"title-line\"><span class=\"title-segment\">让它像团队</span><span class=\"title-segment\">一样交付</span></span>",
    heroDescription: "把模糊需求变成可评审 PRD，把工程意图拆成可提交 Task，再以完整 Spec 创建一个 PR 或 MR。",
    copy: "复制",
    copied: "已复制",
    explore: "浏览全部技能",
    proofOne: "产品定义",
    proofTwo: "代码库理解",
    proofThree: "交付执行",
    proofFour: "技术债治理",
    galleryStatus: "真实工作流 · 真实产物",
    capabilityIndex: "能力图谱",
    capabilityTitle: "四条能力线<br /><span>一套交付秩序</span>",
    capabilityDescription: "每张海报对应一条真实工作流。点击海报可查看完整画面。",
    productTitle: "产品定义",
    productDescription: "从模糊输入到可评审 PRD",
    deliveryTitle: "交付执行",
    deliveryDescription: "从 PRD 到已验证的 PR / MR",
    codebaseTitle: "代码库理解",
    codebaseDescription: "把代码变成可追溯的系统知识",
    debtTitle: "技术债治理",
    debtDescription: "把维护痛点变成可提交 Task",
    workflowIndex: "稳定主线",
    workflowTitle: "不是技能菜单<br /><span>是可以接力的团队</span>",
    routeProduct: "产品需求",
    routeProductNote: "从规格到一个 Spec PR / MR",
    routeDebt: "技术债",
    routeDebtNote: "从证据到可提交修复",
    routeCodebase: "代码库理解",
    routeCodebaseNote: "从接手到业务说明",
    skillsIndex: "技能索引",
    skillsTitle: "找到此刻需要的<br /><span>团队角色</span>",
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
    emptyTitle: "没有匹配的技能",
    emptyDescription: "换一个关键词，或清除分类筛选。",
    resetFilters: "重置筛选",
    version: "版本",
    copySkill: "复制名称",
    copySkillAria: "复制技能名称 {name}",
    artifactIndex: "文件即状态",
    artifactTitle: "对话会消失<br /><span>产物会留下</span>",
    artifactDescription: "每一步都写入明确路径，让下一个 skill、人类评审者或开发者知道当前状态、证据和下一步。",
    terminalFoot: "可追溯 · 可评审 · 可恢复",
    skillSummary: "{skills} 项技能 · {domains} 个领域",
    quickstartIndex: "开始使用",
    quickstartTitle: "安装一次<br /><span>按自然语言开始</span>",
    quickstartDescription: "不需要记忆命令菜单。把目标交给 AI，它会匹配对应 skill，并把阶段产物写入项目。",
    quickstartInstallLabel: "安装技能库",
    quickstartInstallTitle: "把全部团队技能加入 Agent",
    quickstartInvokeLabel: "描述目标",
    quickstartInvokeTitle: "直接说出你要推进的工作",
    quickstartPrompt: "“请帮我细化导出筛选需求，并把规格写入 team-spec。”",
    quickstartArtifactLabel: "审阅产物",
    quickstartArtifactTitle: "沿同一个 slug 持续交接",
    footerNote: "面向真实软件团队的文件化 AI 工作流。",
    viewPoster: "查看{name}海报",
    closePoster: "关闭海报"
  },
  en: {
    pageTitle: "Skills For Real Teams — File-based AI team workflows",
    pageDescription: "Skills For Real Teams organizes product definition, codebase understanding, delivery execution, and technical-debt work into traceable AI team workflows.",
    skipLink: "Skip to main content",
    mainNavigation: "Main navigation",
    posterPreview: "Product poster preview",
    skillFilters: "Skill category filters",
    navCapabilities: "Capabilities",
    navWorkflow: "Workflow",
    navSkills: "Skills",
    navQuickstart: "Quickstart",
    heroEyebrow: "FILE-BASED AI TEAM SYSTEM",
    heroTitle: "<span class=\"title-line title-line-primary\">AI should do more than answer.</span><span class=\"title-line\">It should deliver</span><span class=\"title-line\">like a team.</span>",
    heroDescription: "Turn vague requirements into reviewable PRDs, engineering intent into commit-sized Tasks, and each complete Spec into one PR or MR.",
    copy: "Copy",
    copied: "Copied",
    explore: "Browse all skills",
    proofOne: "Product definition",
    proofTwo: "Codebase understanding",
    proofThree: "Delivery execution",
    proofFour: "Technical debt",
    galleryStatus: "REAL WORKFLOW · REAL ARTIFACTS",
    capabilityIndex: "CAPABILITY ATLAS",
    capabilityTitle: "Four capability lines.<span>One delivery system.</span>",
    capabilityDescription: "Each poster represents a real workflow. Select one to see the full image.",
    productTitle: "Product definition",
    productDescription: "From vague input to a reviewable PRD",
    deliveryTitle: "Delivery execution",
    deliveryDescription: "From PRD to a verified PR or MR",
    codebaseTitle: "Codebase understanding",
    codebaseDescription: "Turn code into traceable system knowledge",
    debtTitle: "Technical debt",
    debtDescription: "Turn maintenance pain into commit-sized Tasks",
    workflowIndex: "STABLE LINES",
    workflowTitle: "Not a skill menu.<br /><span>A team that hands work forward.</span>",
    routeProduct: "Product delivery",
    routeProductNote: "From specification to one Spec PR or MR",
    routeDebt: "Technical debt",
    routeDebtNote: "From evidence to commit-sized remediation",
    routeCodebase: "Codebase understanding",
    routeCodebaseNote: "From onboarding to stakeholder clarity",
    skillsIndex: "SKILL INDEX",
    skillsTitle: "Find the team role<br /><span>you need right now.</span>",
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
    emptyTitle: "No matching skills",
    emptyDescription: "Try another term or clear the category filter.",
    resetFilters: "Reset filters",
    version: "VERSION",
    copySkill: "Copy name",
    copySkillAria: "Copy skill name {name}",
    artifactIndex: "FILES AS STATE",
    artifactTitle: "Conversations disappear.<br /><span>Artifacts remain.</span>",
    artifactDescription: "Every step writes to an explicit path so the next skill, reviewer, or developer can see the current state, evidence, and next move.",
    terminalFoot: "TRACEABLE · REVIEWABLE · RESUMABLE",
    skillSummary: "{skills} SKILLS · {domains} DOMAINS",
    quickstartIndex: "QUICKSTART",
    quickstartTitle: "Install once.<br /><span>Start in natural language.</span>",
    quickstartDescription: "There is no command menu to memorize. Give the AI your goal; it matches the right skill and writes each stage artifact into the project.",
    quickstartInstallLabel: "INSTALL THE LIBRARY",
    quickstartInstallTitle: "Add every team skill to your agent",
    quickstartInvokeLabel: "DESCRIBE THE GOAL",
    quickstartInvokeTitle: "Say what you need to move forward",
    quickstartPrompt: "“Refine the export-filter requirement and write the specification to team-spec.”",
    quickstartArtifactLabel: "REVIEW THE ARTIFACTS",
    quickstartArtifactTitle: "Keep handing work forward under one slug",
    footerNote: "File-based AI workflows for real software teams.",
    viewPoster: "View the {name} poster",
    closePoster: "Close poster"
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
    config: "CONFIG",
    product: "PRODUCT",
    codebase: "CODEBASE",
    delivery: "DELIVERY",
    "tech-debt": "TECH DEBT",
    writing: "WRITING",
    harness: "ARCHIVE"
  }
};

const posterAlt = {
  zh: {
    product: "产品定义：从模糊输入到可评审 PRD",
    delivery: "交付执行：从 PRD 到已验证 PR / MR",
    codebase: "代码库理解：把代码变成可追溯的系统知识",
    "tech-debt": "技术债治理：把维护痛点变成可提交 Task"
  },
  en: {
    product: "Product definition: from vague input to a reviewable PRD",
    delivery: "Delivery execution: from PRD to a verified PR or MR",
    codebase: "Codebase understanding: turn code into traceable system knowledge",
    "tech-debt": "Technical debt: turn maintenance pain into commit-sized Tasks"
  }
};

let activeCategory = "all";
let activeSearch = "";

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

function createSkillCard(skill, language) {
  const dictionary = translations[language];
  const card = document.createElement("article");
  card.className = "skill-card";
  card.dataset.category = skill.category;

  const top = document.createElement("div");
  top.className = "skill-card-top";

  const category = document.createElement("span");
  category.className = "skill-category";
  category.textContent = categoryLabels[language][skill.category] || skill.category;
  top.append(category);

  const name = document.createElement("h3");
  name.textContent = skill.name;

  const description = document.createElement("p");
  description.className = "skill-card-description";
  description.textContent = skill.description[language];

  const foot = document.createElement("div");
  foot.className = "skill-card-foot";

  const version = document.createElement("span");
  version.className = "skill-version";
  version.textContent = `${dictionary.version} ${skill.version}`;

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
      copyButton.textContent = translations[currentLanguage()].copySkill;
    }
  });

  foot.append(version, copyButton);
  card.append(top, name, description, foot);
  return card;
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

  grid.replaceChildren(
    ...filteredSkills.map((skill) => createSkillCard(skill, language))
  );
  grid.hidden = filteredSkills.length === 0;
  empty.hidden = filteredSkills.length !== 0;
  count.textContent = format(dictionary.resultCount, {
    count: filteredSkills.length,
    total: skills.length
  });
}

function updatePosterLanguage(language) {
  document.querySelectorAll("[data-poster]").forEach((image) => {
    const poster = image.dataset.poster;
    image.src = `assets/srt-brand/posters/${language}/${poster}.png`;
    image.alt = posterAlt[language][poster];
  });

  document.querySelectorAll("[data-poster-modal]").forEach((button) => {
    const poster = button.dataset.posterModal;
    button.setAttribute(
      "aria-label",
      format(translations[language].viewPoster, {
        name: categoryLabels[language][poster]
      })
    );
  });
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
  if (skillSummary) {
    skillSummary.textContent = format(dictionary.skillSummary, {
      skills: skills.length,
      domains: new Set(skills.map((skill) => skill.category)).size
    });
  }

  document.querySelectorAll("[data-language-option]").forEach((button) => {
    const active = button.dataset.languageOption === language;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });

  document
    .querySelector("[data-close-dialog]")
    ?.setAttribute("aria-label", dictionary.closePoster);

  updatePosterLanguage(language);
  renderSkills();
  if (save) persistLanguage(language);
}

document.querySelectorAll("[data-language-option]").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.languageOption));
});

document.querySelectorAll("[data-copy-command]").forEach((button) => {
  button.addEventListener("click", async () => {
    const label = button.querySelector(".copy-label, [data-i18n=\"copy\"]");
    try {
      await copyText(button.dataset.copyCommand);
      if (label) label.textContent = translations[currentLanguage()].copied;
      window.setTimeout(() => {
        if (label) label.textContent = translations[currentLanguage()].copy;
      }, 1400);
    } catch {
      if (label) label.textContent = translations[currentLanguage()].copy;
    }
  });
});

const posterDialog = document.querySelector("[data-poster-dialog]");
const dialogImage = document.querySelector("[data-dialog-image]");

document.querySelectorAll("[data-poster-modal]").forEach((button) => {
  button.addEventListener("click", () => {
    const poster = button.dataset.posterModal;
    const language = currentLanguage();
    dialogImage.src = `assets/srt-brand/posters/${language}/${poster}.png`;
    dialogImage.alt = posterAlt[language][poster];
    posterDialog.showModal();
  });
});

document
  .querySelector("[data-close-dialog]")
  ?.addEventListener("click", () => posterDialog.close());

posterDialog?.addEventListener("click", (event) => {
  if (event.target === posterDialog) posterDialog.close();
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
