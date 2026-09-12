(() => {
  "use strict";

  const storageKey = "lenovo-ai-course-state-v2";
  const readState = () => {
    try {
      return JSON.parse(localStorage.getItem(storageKey) || '{"completed":[]}');
    } catch (_error) {
      return { completed: [] };
    }
  };
  const saveState = (state) => localStorage.setItem(storageKey, JSON.stringify(state));
  const lessonShell = document.querySelector("[data-lesson]");

  const copyText = async (text, button) => {
    try {
      await navigator.clipboard.writeText(text);
      const original = button.textContent;
      button.textContent = "已复制";
      window.setTimeout(() => { button.textContent = original; }, 1500);
    } catch (_error) {
      button.textContent = "请手动选择复制";
    }
  };

  document.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const action = button.dataset.action;
    if (action === "toggle-instructor") {
      const enabled = !document.body.classList.contains("instructor-mode");
      document.body.classList.toggle("instructor-mode", enabled);
      button.setAttribute("aria-pressed", String(enabled));
      button.textContent = enabled ? "退出讲师模式" : "讲师模式";
      localStorage.setItem("lenovo-ai-instructor-mode", String(enabled));
    }
    if (action === "copy-page") {
      const source = document.querySelector("#lesson-outline");
      if (source) copyText(source.innerText.trim(), button);
    }
    if (action === "complete" && lessonShell) {
      const lesson = lessonShell.dataset.lesson;
      const state = readState();
      const completed = new Set(state.completed || []);
      completed.add(lesson);
      state.completed = [...completed].sort();
      saveState(state);
      button.classList.add("is-complete");
      button.textContent = "本课已完成";
    }
  });

  if (lessonShell) {
    const lesson = lessonShell.dataset.lesson;
    const state = readState();
    if ((state.completed || []).includes(lesson)) {
      const button = document.querySelector('[data-action="complete"]');
      if (button) {
        button.classList.add("is-complete");
        button.textContent = "本课已完成";
      }
    }
    if (localStorage.getItem("lenovo-ai-instructor-mode") === "true") {
      const button = document.querySelector('[data-action="toggle-instructor"]');
      document.body.classList.add("instructor-mode");
      if (button) {
        button.setAttribute("aria-pressed", "true");
        button.textContent = "退出讲师模式";
      }
    }
  }
})();
