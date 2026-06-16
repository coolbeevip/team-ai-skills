/**
 * Skills For Real Teams - 交互功能
 */

// ============================================
// 工具函数
// ============================================

/**
 * 防抖函数
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * 节流函数
 */
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// ============================================
// 搜索功能
// ============================================

class SearchManager {
  constructor() {
    this.searchInput = document.getElementById('skillSearch');
    this.searchClear = document.getElementById('searchClear');
    this.skillsGrid = document.getElementById('skillsGrid');
    this.skillsEmpty = document.getElementById('skillsEmpty');

    this.init();
  }

  init() {
    if (!this.searchInput) return;

    // 绑定搜索事件
    this.searchInput.addEventListener('input', debounce((e) => {
      this.handleSearch(e.target.value);
    }, 300));

    // 绑定清除事件
    if (this.searchClear) {
      this.searchClear.addEventListener('click', () => {
        this.searchInput.value = '';
        this.handleSearch('');
        this.searchInput.focus();
      });
    }
  }

  handleSearch(query) {
    const cards = this.skillsGrid?.querySelectorAll('.skill-card');
    if (!cards) return;

    const normalizedQuery = query.toLowerCase().trim();
    let visibleCount = 0;

    cards.forEach(card => {
      const name = card.dataset.name?.toLowerCase() || '';
      const description = card.dataset.description?.toLowerCase() || '';
      const category = card.dataset.category?.toLowerCase() || '';

      const isMatch = !normalizedQuery ||
        name.includes(normalizedQuery) ||
        description.includes(normalizedQuery) ||
        category.includes(normalizedQuery);

      card.style.display = isMatch ? '' : 'none';
      if (isMatch) visibleCount++;
    });

    // 显示/隐藏空状态
    if (this.skillsEmpty) {
      this.skillsEmpty.style.display = visibleCount === 0 ? 'block' : 'none';
    }

    // 高亮匹配文本
    this.highlightMatches(normalizedQuery);
  }

  highlightMatches(query) {
    const cards = this.skillsGrid?.querySelectorAll('.skill-card');
    if (!cards) return;

    cards.forEach(card => {
      const nameElement = card.querySelector('.skill-name');
      const descElement = card.querySelector('.skill-description');

      if (nameElement) {
        nameElement.innerHTML = this.highlightText(nameElement.textContent, query);
      }
      if (descElement) {
        descElement.innerHTML = this.highlightText(descElement.textContent, query);
      }
    });
  }

  highlightText(text, query) {
    if (!query) return text;

    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }
}

// ============================================
// 筛选功能
// ============================================

class FilterManager {
  constructor() {
    this.filterButtons = document.querySelectorAll('.filter-btn');
    this.skillsGrid = document.getElementById('skillsGrid');
    this.skillsEmpty = document.getElementById('skillsEmpty');
    this.activeFilter = 'all';

    this.init();
  }

  init() {
    this.filterButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        this.setFilter(btn.dataset.filter);
      });
    });
  }

  setFilter(filter) {
    this.activeFilter = filter;

    // 更新按钮状态
    this.filterButtons.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.filter === filter);
    });

    // 应用筛选
    this.applyFilter();
  }

  applyFilter() {
    const cards = this.skillsGrid?.querySelectorAll('.skill-card');
    if (!cards) return;

    let visibleCount = 0;

    cards.forEach(card => {
      const category = card.dataset.category;
      const isMatch = this.activeFilter === 'all' || category === this.activeFilter;

      card.style.display = isMatch ? '' : 'none';
      if (isMatch) visibleCount++;
    });

    // 显示/隐藏空状态
    if (this.skillsEmpty) {
      this.skillsEmpty.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }
}

// ============================================
// 视图切换
// ============================================

class ViewManager {
  constructor() {
    this.viewButtons = document.querySelectorAll('.view-btn');
    this.skillsGrid = document.getElementById('skillsGrid');
    this.currentView = 'grid';

    this.init();
  }

  init() {
    this.viewButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        this.setView(btn.dataset.view);
      });
    });
  }

  setView(view) {
    this.currentView = view;

    // 更新按钮状态
    this.viewButtons.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === view);
    });

    // 应用视图
    if (this.skillsGrid) {
      this.skillsGrid.classList.toggle('list-view', view === 'list');
    }

    // 保存偏好
    localStorage.setItem('viewPreference', view);
  }
}

// ============================================
// 动画控制
// ============================================

class AnimationManager {
  constructor() {
    this.animatedElements = new Set();
    this.init();
  }

  init() {
    // 创建观察器
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.animateElement(entry.target);
            this.observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
      }
    );

    // 观察需要动画的元素
    this.observeElements();
  }

  observeElements() {
    const elements = document.querySelectorAll(
      '.feature-card, .route-card, .example-panel, .example-row, .skill-card, .step-card'
    );

    elements.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      this.observer.observe(el);
    });
  }

  animateElement(element) {
    if (this.animatedElements.has(element)) return;

    this.animatedElements.add(element);

    // 添加动画类
    element.classList.add('animate-fade-in-up');

    // 添加延迟
    const delay = this.animatedElements.size % 4;
    element.classList.add(`delay-${delay + 1}`);
  }
}

// ============================================
// 复制功能
// ============================================

class CopyManager {
  constructor() {
    this.init();
  }

  init() {
    // 绑定所有复制按钮
    document.addEventListener('click', (e) => {
      const copyBtn = e.target.closest('[onclick*="copyCommand"], [onclick*="copySkillName"]');
      if (copyBtn) {
        e.preventDefault();
        const onclick = copyBtn.getAttribute('onclick');

        if (onclick.includes('copyCommand')) {
          this.copyCommand(copyBtn);
        } else if (onclick.includes('copySkillName')) {
          const match = onclick.match(/copySkillName\(this,\s*'([^']+)'\)/);
          if (match) {
            this.copySkillName(copyBtn, match[1]);
          }
        }
      }
    });
  }

  async copyCommand(button) {
    const codeElement = button.parentElement.querySelector('code');
    if (!codeElement) return;

    const text = codeElement.textContent;
    await this.copyToClipboard(text, button);
  }

  async copySkillName(button, name) {
    await this.copyToClipboard(name, button);
  }

  async copyToClipboard(text, button) {
    try {
      await navigator.clipboard.writeText(text);
      this.showCopyFeedback(button, true);
    } catch (err) {
      // 降级方案
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();

      try {
        document.execCommand('copy');
        this.showCopyFeedback(button, true);
      } catch (fallbackErr) {
        this.showCopyFeedback(button, false);
      }

      document.body.removeChild(textarea);
    }
  }

  showCopyFeedback(button, success) {
    const originalText = button.textContent;
    const originalBg = button.style.background;

    button.textContent = success ? '已复制' : '失败';
    button.style.background = success ? 'var(--color-success)' : 'var(--color-accent)';

    setTimeout(() => {
      button.textContent = originalText;
      button.style.background = originalBg;
    }, 2000);
  }
}

// ============================================
// 返回顶部
// ============================================

class BackToTopManager {
  constructor() {
    this.button = document.getElementById('backToTop');
    this.init();
  }

  init() {
    if (!this.button) return;

    // 监听滚动
    window.addEventListener('scroll', throttle(() => {
      this.toggleVisibility();
    }, 100));

    // 绑定点击事件
    this.button.addEventListener('click', () => {
      this.scrollToTop();
    });
  }

  toggleVisibility() {
    const isVisible = window.scrollY > 300;
    this.button.classList.toggle('visible', isVisible);
  }

  scrollToTop() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
}

// ============================================
// 导航栏滚动效果
// ============================================

class NavbarManager {
  constructor() {
    this.navbar = document.querySelector('.navbar');
    this.lastScrollY = 0;
    this.init();
  }

  init() {
    if (!this.navbar) return;

    window.addEventListener('scroll', throttle(() => {
      this.handleScroll();
    }, 100));
  }

  handleScroll() {
    const currentScrollY = window.scrollY;

    // 添加/移除滚动样式
    if (currentScrollY > 10) {
      this.navbar.classList.add('scrolled');
    } else {
      this.navbar.classList.remove('scrolled');
    }

    this.lastScrollY = currentScrollY;
  }
}

// ============================================
// 平滑滚动
// ============================================

class SmoothScrollManager {
  constructor() {
    this.init();
  }

  init() {
    // 处理锚点链接
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[href^="#"]');
      if (!link) return;

      const targetId = link.getAttribute('href');
      if (targetId === '#') return;

      const targetElement = document.querySelector(targetId);
      if (!targetElement) return;

      e.preventDefault();
      this.scrollToElement(targetElement);
    });
  }

  scrollToElement(element) {
    const navbarHeight = document.querySelector('.navbar')?.offsetHeight || 0;
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - navbarHeight - 20;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  }
}

// ============================================
// 全局函数（供 HTML onclick 使用）
// ============================================

// 为了保持向后兼容，保留全局函数
function copyCommand(button) {
  // 由 CopyManager 处理
}

function copySkillName(button, name) {
  // 由 CopyManager 处理
}

function resetFilters() {
  // 重置搜索
  const searchInput = document.getElementById('skillSearch');
  if (searchInput) {
    searchInput.value = '';
  }

  // 重置筛选
  const filterButtons = document.querySelectorAll('.filter-btn');
  filterButtons.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === 'all');
  });

  // 显示所有卡片
  const cards = document.querySelectorAll('.skill-card');
  cards.forEach(card => {
    card.style.display = '';
  });

  // 隐藏空状态
  const skillsEmpty = document.getElementById('skillsEmpty');
  if (skillsEmpty) {
    skillsEmpty.style.display = 'none';
  }
}

// ============================================
// 初始化
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  // 初始化各个管理器
  new SearchManager();
  new FilterManager();
  new ViewManager();
  new AnimationManager();
  new CopyManager();
  new BackToTopManager();
  new NavbarManager();
  new SmoothScrollManager();

  // 加载保存的视图偏好
  const savedView = localStorage.getItem('viewPreference');
  if (savedView) {
    const viewBtn = document.querySelector(`[data-view="${savedView}"]`);
    if (viewBtn) {
      viewBtn.click();
    }
  }

  console.log('Skills For Real Teams - initialized');
});
