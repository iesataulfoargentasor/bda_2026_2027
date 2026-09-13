(() => {
  const LETTERS = ["A", "B", "C", "D"];

  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
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

  function selectedIndex(form, qIndex) {
    const chosen = form.querySelector(`input[name="q${qIndex}"]:checked`);
    return chosen ? Number(chosen.value) : null;
  }

  function scoreMessage(ok, total, unit) {
    const ratio = ok / total;
    const donde = unit || "la unidad";
    if (ok === total) {
      return "Excelente: todas correctas. Puedes pasar a las prácticas de Moodle.";
    }
    if (ratio >= 0.75) {
      return "Muy bien. Repasa solo las preguntas falladas (enlace al apartado al final de cada una).";
    }
    if (ratio >= 0.5) {
      return "Vas por el camino, pero conviene volver a los apartados enlazados antes de un examen.";
    }
    return `Mejor recorre de nuevo la ${donde} y reintenta el test. No puntúa en Moodle: es para practicar.`;
  }

  function renderForm(data, quizId) {
    const items = data.questions
      .map((q, qIndex) => {
        const opts = q.options
          .map((opt, oIndex) => {
            const id = optionId(quizId, qIndex, oIndex);
            return `<label class="dwec-quiz__option" for="${id}">
              <input type="radio" name="q${qIndex}" id="${id}" value="${oIndex}" required>
              <span class="dwec-quiz__letter">${LETTERS[oIndex]}</span>
              <span class="dwec-quiz__option-text">${escapeHtml(opt)}</span>
            </label>`;
          })
          .join("");
        return `<fieldset class="dwec-quiz__question" data-index="${qIndex}">
          <legend class="dwec-quiz__legend">
            <span class="dwec-quiz__num">${qIndex + 1} / ${data.questions.length}</span>
            <span class="dwec-quiz__topic">${escapeHtml(q.topic)}</span>
          </legend>
          <p class="dwec-quiz__prompt">${escapeHtml(q.prompt)}</p>
          ${renderCode(q.code)}
          <div class="dwec-quiz__options">${opts}</div>
          <div class="dwec-quiz__feedback" hidden></div>
        </fieldset>`;
      })
      .join("");

    return `<form class="dwec-quiz__form" novalidate>
      <div class="dwec-quiz__result" hidden></div>
      ${items}
      <p class="dwec-quiz__progress" aria-live="polite"></p>
      <div class="dwec-quiz__actions">
        <button type="submit" class="md-button md-button--primary dwec-quiz__submit">Corregir test</button>
        <button type="button" class="md-button dwec-quiz__reset" hidden>Volver a intentar</button>
      </div>
    </form>`;
  }

  function updateProgress(form, total) {
    const answered = form.querySelectorAll("input[type=radio]:checked").length;
    const bar = form.querySelector(".dwec-quiz__progress");
    bar.textContent = `Respondidas: ${answered} / ${total}`;
  }

  function showFeedback(form, data) {
    let ok = 0;
    data.questions.forEach((q, qIndex) => {
      const fieldset = form.querySelector(`fieldset[data-index="${qIndex}"]`);
      const picked = selectedIndex(form, qIndex);
      const correct = picked === q.answer;
      if (correct) {
        ok += 1;
      }
      fieldset.classList.toggle("dwec-quiz__question--ok", correct);
      fieldset.classList.toggle("dwec-quiz__question--ko", !correct);
      fieldset.querySelectorAll(".dwec-quiz__option").forEach((label, oIndex) => {
        label.classList.toggle("dwec-quiz__option--correct", oIndex === q.answer);
        label.classList.toggle("dwec-quiz__option--picked", oIndex === picked && !correct);
      });
      const box = fieldset.querySelector(".dwec-quiz__feedback");
      const letter = LETTERS[q.answer];
      const href = q.href ? `<p class="dwec-quiz__more"><a href="${escapeHtml(q.href)}">Repasar ${escapeHtml(q.topic)}</a></p>` : "";
      const yours =
        picked === null
          ? "<p>No marcaste ninguna opción.</p>"
          : correct
            ? "<p><strong>Correcta.</strong></p>"
            : `<p><strong>Incorrecta.</strong> Marcaste la ${LETTERS[picked]}.</p>`;
      box.hidden = false;
      box.innerHTML = `${yours}<p>La respuesta correcta es la <strong>${letter}</strong>.</p><p>${escapeHtml(q.explain)}</p>${href}`;
    });

    form.querySelectorAll("input[type=radio]").forEach((input) => {
      input.disabled = true;
    });
    form.querySelector(".dwec-quiz__submit").hidden = true;
    form.querySelector(".dwec-quiz__reset").hidden = false;

    const total = data.questions.length;
    const result = form.querySelector(".dwec-quiz__result");
    result.hidden = false;
    result.innerHTML = `<p class="dwec-quiz__score">Resultado: <strong>${ok} / ${total}</strong></p><p>${escapeHtml(scoreMessage(ok, total, data.unit))}</p>`;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function bindForm(form, data, render) {
    const total = data.questions.length;
    updateProgress(form, total);
    form.addEventListener("change", () => updateProgress(form, total));
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const missing = data.questions.some((_, i) => selectedIndex(form, i) === null);
      if (missing) {
        const first = [...form.querySelectorAll("fieldset")].find((fs, i) => selectedIndex(form, i) === null);
        first?.scrollIntoView({ behavior: "smooth", block: "center" });
        form.querySelector(".dwec-quiz__progress").textContent =
          `Responde las ${total} preguntas antes de corregir. Llevas ${form.querySelectorAll("input[type=radio]:checked").length}.`;
        return;
      }
      showFeedback(form, data);
    });
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

      const draw = () => {
        root.innerHTML = renderForm(data, quizId);
        const form = root.querySelector("form");
        const result = form.querySelector(".dwec-quiz__result");
        result.setAttribute("tabindex", "-1");
        bindForm(form, data, draw);
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
