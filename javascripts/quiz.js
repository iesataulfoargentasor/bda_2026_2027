(() => {
  const LETTERS = ["A", "B", "C", "D"];

  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function formatExplain(text) {
    return escapeHtml(text).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  }

  function renderCode(code) {
    if (!code) {
      return "";
    }
    return `<pre class="dwec-quiz__code" tabindex="0"><code>${escapeHtml(code)}</code></pre>`;
  }

  function optionId(quizId, qIndex, oIndex) {
    return `${quizId}-q${qIndex}-o${oIndex}`;
  }

  function isEachMode(data, root) {
    return data.mode === "each" || root?.dataset.check === "each";
  }

  function selectedIndex(form, qIndex) {
    const quizId = form.dataset.quizId;
    const chosen = form.querySelector(`input[name="${quizId}-q${qIndex}"]:checked`);
    return chosen ? Number(chosen.value) : null;
  }

  function scoreMessage(ok, total, unit) {
    const ratio = ok / total;
    const donde = unit || "la unidad";
    if (ok === total) {
      return "Excelente: todas correctas. Podéis pasar a las prácticas de Moodle.";
    }
    if (ratio >= 0.75) {
      return "Muy bien. Repasad solo las preguntas falladas (el enlace al apartado está al final de cada una).";
    }
    if (ratio >= 0.5) {
      return "Vais por el camino, pero conviene volver a los apartados enlazados antes de un examen.";
    }
    return `Mejor recorred de nuevo ${donde} y reintentad el test. No puntúa en Moodle: es para practicar.`;
  }

  function feedbackHtml(q, picked) {
    const letter = LETTERS[q.answer];
    const href = q.href
      ? `<p class="dwec-quiz__more"><a href="${escapeHtml(q.href)}">Repasar ${escapeHtml(q.topic)}</a></p>`
      : "";
    const correct = picked === q.answer;
    const yours =
      picked === null
        ? "<p>No habéis marcado ninguna opción.</p>"
        : correct
          ? "<p><strong>Correcta.</strong></p>"
          : `<p><strong>Incorrecta.</strong> Habéis marcado la ${LETTERS[picked]}.</p>`;
    return `${yours}<p>La respuesta correcta es la <strong>${letter}</strong>.</p><p>${formatExplain(q.explain)}</p>${href}`;
  }

  function paintQuestion(fieldset, q, picked) {
    const correct = picked === q.answer;
    fieldset.classList.toggle("dwec-quiz__question--ok", correct);
    fieldset.classList.toggle("dwec-quiz__question--ko", !correct);
    fieldset.querySelectorAll(".dwec-quiz__option").forEach((label, oIndex) => {
      label.classList.toggle("dwec-quiz__option--correct", oIndex === q.answer);
      label.classList.toggle("dwec-quiz__option--picked", oIndex === picked && !correct);
    });
    const box = fieldset.querySelector(".dwec-quiz__feedback");
    box.hidden = false;
    box.innerHTML = feedbackHtml(q, picked);
    fieldset.querySelectorAll("input[type=radio]").forEach((input) => {
      input.disabled = true;
    });
    const checkBtn = fieldset.querySelector(".dwec-quiz__check");
    if (checkBtn) {
      checkBtn.hidden = true;
    }
    return correct;
  }

  function renderForm(data, quizId, modeEach) {
    const items = data.questions
      .map((q, qIndex) => {
        const opts = q.options
          .map((opt, oIndex) => {
            const id = optionId(quizId, qIndex, oIndex);
            return `<label class="dwec-quiz__option" for="${id}">
              <input type="radio" name="${quizId}-q${qIndex}" id="${id}" value="${oIndex}">
              <span class="dwec-quiz__letter">${LETTERS[oIndex]}</span>
              <span class="dwec-quiz__option-text">${escapeHtml(opt)}</span>
            </label>`;
          })
          .join("");
        const checkBtn = modeEach
          ? `<div class="dwec-quiz__q-actions">
              <button type="button" class="md-button md-button--primary dwec-quiz__check">Comprobar respuesta</button>
            </div>`
          : "";
        return `<fieldset class="dwec-quiz__question" data-index="${qIndex}">
          <legend class="dwec-quiz__legend">
            <span class="dwec-quiz__num">${qIndex + 1} / ${data.questions.length}</span>
            <span class="dwec-quiz__topic">${escapeHtml(q.topic)}</span>
          </legend>
          <p class="dwec-quiz__prompt">${escapeHtml(q.prompt)}</p>
          ${renderCode(q.code)}
          <div class="dwec-quiz__options">${opts}</div>
          ${checkBtn}
          <div class="dwec-quiz__feedback" hidden aria-live="polite"></div>
        </fieldset>`;
      })
      .join("");

    const result = `<div class="dwec-quiz__result" hidden></div>`;
    const submit = modeEach
      ? ""
      : `<button type="submit" class="md-button md-button--primary dwec-quiz__submit">Corregir test</button>`;

    return `<form class="dwec-quiz__form" data-quiz-id="${quizId}" novalidate>
      ${modeEach ? "" : result}
      ${items}
      ${modeEach ? result : ""}
      <p class="dwec-quiz__progress" aria-live="polite"></p>
      <div class="dwec-quiz__actions">
        ${submit}
        <button type="button" class="md-button dwec-quiz__reset" hidden>Volver a intentar</button>
      </div>
    </form>`;
  }

  function updateProgress(form, total, modeEach) {
    const bar = form.querySelector(".dwec-quiz__progress");
    if (modeEach) {
      const done = form.querySelectorAll("fieldset[data-checked='1']").length;
      bar.textContent = `Comprobadas: ${done} / ${total}`;
      return;
    }
    const answered = form.querySelectorAll("input[type=radio]:checked").length;
    bar.textContent = `Respondidas: ${answered} / ${total}`;
  }

  function showTotal(form, data, ok) {
    const total = data.questions.length;
    const result = form.querySelector(".dwec-quiz__result");
    result.hidden = false;
    result.innerHTML = `<p class="dwec-quiz__score">Resultado: <strong>${ok} / ${total}</strong></p><p>${escapeHtml(scoreMessage(ok, total, data.unit))}</p>`;
  }

  function showFeedback(form, data) {
    let ok = 0;
    data.questions.forEach((q, qIndex) => {
      const fieldset = form.querySelector(`fieldset[data-index="${qIndex}"]`);
      const picked = selectedIndex(form, qIndex);
      if (paintQuestion(fieldset, q, picked)) {
        ok += 1;
      }
    });
    form.querySelector(".dwec-quiz__submit").hidden = true;
    form.querySelector(".dwec-quiz__reset").hidden = false;
    showTotal(form, data, ok);
    form.querySelector(".dwec-quiz__result").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function countOk(form) {
    return form.querySelectorAll(".dwec-quiz__question--ok").length;
  }

  function checkOne(form, data, fieldset, total) {
    if (fieldset.dataset.checked === "1") {
      return;
    }
    const qIndex = Number(fieldset.dataset.index);
    const q = data.questions[qIndex];
    const picked = selectedIndex(form, qIndex);
    const box = fieldset.querySelector(".dwec-quiz__feedback");
    if (picked === null) {
      box.hidden = false;
      box.innerHTML = "<p>Marcad una opción (A–D) antes de comprobar.</p>";
      return;
    }
    fieldset.dataset.checked = "1";
    paintQuestion(fieldset, q, picked);
    form.querySelector(".dwec-quiz__reset").hidden = false;
    updateProgress(form, total, true);
    if (form.querySelectorAll("fieldset[data-checked='1']").length === total) {
      showTotal(form, data, countOk(form));
    }
  }

  function bindForm(form, data, render, modeEach) {
    const total = data.questions.length;
    updateProgress(form, total, modeEach);
    form.addEventListener("change", () => updateProgress(form, total, modeEach));
    if (modeEach) {
      form.querySelectorAll(".dwec-quiz__question").forEach((fieldset) => {
        fieldset.querySelector(".dwec-quiz__check").addEventListener("click", () => {
          checkOne(form, data, fieldset, total);
        });
      });
    } else {
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const missing = data.questions.some((_, i) => selectedIndex(form, i) === null);
        if (missing) {
          const first = [...form.querySelectorAll("fieldset")].find((_, i) => selectedIndex(form, i) === null);
          first?.scrollIntoView({ behavior: "smooth", block: "center" });
          form.querySelector(".dwec-quiz__progress").textContent =
            `Responde las ${total} preguntas antes de corregir. Lleváis ${form.querySelectorAll("input[type=radio]:checked").length}.`;
          return;
        }
        showFeedback(form, data);
      });
    }
    form.querySelector(".dwec-quiz__reset").addEventListener("click", () => {
      render();
    });
  }

  async function mount(root) {
    if (root.dataset.ready === "1") {
      return;
    }
    const src = root.dataset.src;
    if (!src) {
      return;
    }
    root.dataset.ready = "1";
    root.innerHTML = "<p>Cargando el test…</p>";
    try {
      const url = new URL(src, window.location.href);
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(String(response.status));
      }
      const data = await response.json();
      if (!root.isConnected) {
        root.dataset.ready = "0";
        return;
      }
      const quizId = `quiz-${Math.random().toString(36).slice(2, 8)}`;
      const modeEach = isEachMode(data, root);

      const draw = () => {
        root.innerHTML = renderForm(data, quizId, modeEach);
        const form = root.querySelector("form");
        const result = form.querySelector(".dwec-quiz__result");
        result.setAttribute("tabindex", "-1");
        bindForm(form, data, draw, modeEach);
      };
      draw();
    } catch (error) {
      root.dataset.ready = "0";
      root.innerHTML = `<p>No se ha podido cargar el test. Recarga la página. (${escapeHtml(error.message)})</p>`;
    }
  }

  function init() {
    document.querySelectorAll("[data-dwec-quiz]").forEach((node) => {
      mount(node);
    });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
