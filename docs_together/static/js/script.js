// ======= PODSTAWOWA KONFIGURACJA =======
let optionsButtons = document.querySelectorAll(".option-button");
let advancedOptionButton = document.querySelectorAll(".adv-option-button");
let fontName = document.getElementById("fontName");
let fontSizeRef = document.getElementById("fontSize");
let writingArea = document.getElementById("text-input");
let linkButton = document.getElementById("createLink");
let alignButtons = document.querySelectorAll(".align");
let spacingButtons = document.querySelectorAll(".spacing");
let formatButtons = document.querySelectorAll(".format");
let scriptButtons = document.querySelectorAll(".script");

let fontList = [ "Arial", "Verdana", "Times New Roman", "Garamond", "Georgia", "Courier New", "cursive" ];

const A4_HEIGHT_PX = 1122;

// ======= OBSERVER STRON =======
const observePage = (page) => {
  const observer = new MutationObserver(() => {
    if (page.classList.contains("newly-created")) return;

    const allPages = Array.from(writingArea.querySelectorAll(".page"));
    if (allPages.length === 1) return;

    const isEmpty =
      page.innerText.trim() === "" &&
      page.querySelectorAll("img, video, iframe, div").length === 0;

    if (isEmpty) {
      const currentIndex = allPages.indexOf(page);
      const previousPage = allPages[currentIndex - 1];

      const isPageActive = document.activeElement === page;

      page.remove();

      if (isPageActive && previousPage) {
        previousPage.focus();
        const range = document.createRange();
        const sel = window.getSelection();

        if (previousPage.lastChild) {
          range.selectNodeContents(previousPage);
          range.collapse(false);
        } else {
          const br = document.createElement("br");
          previousPage.appendChild(br);
          range.setStartAfter(br);
        }
        sel.removeAllRanges();
        sel.addRange(range);
      }
    }
  });

  observer.observe(page, {
    childList: true,
    characterData: true,
    subtree: true,
  });
};

// ======= TWORZENIE NOWEJ STRONY =======
const createNewPage = (initialContent = "") => {
  const page = document.createElement("div");
  page.classList.add("page", "newly-created");
  page.setAttribute("contenteditable", "true");
  page.innerHTML = initialContent || "<br>";
  writingArea.appendChild(page);

  observePage(page);
  page.focus();

  setTimeout(() => page.classList.remove("newly-created"), 50);

  return page;
};

// ======= SPRAWDZANIE PRZEPŁYWU TEKSTU =======
const checkPageOverflow = (e) => {
  const currentPage = e.target.closest(".page");
  if (!currentPage) return;

  let pages = Array.from(writingArea.querySelectorAll(".page"));
  let currentPageIndex = pages.indexOf(currentPage);

  while (currentPage.scrollHeight > currentPage.clientHeight) {
    let nextPage = pages[currentPageIndex + 1];
    if (!nextPage) {
      nextPage = createNewPage();
      pages.push(nextPage);
    }

    const children = Array.from(currentPage.childNodes);
    const lastChild = children[children.length - 1];
    if (!lastChild) break;

    nextPage.insertBefore(lastChild, nextPage.firstChild);

    const sel = window.getSelection();
    const range = document.createRange();
    range.setStartAfter(lastChild);
    range.collapse(true);
    sel.removeAllRanges();
    sel.addRange(range);

    currentPageIndex = pages.indexOf(currentPage);
  }
};

// ======= INICJALIZACJA =======
const initializer = (initialHtmlContent) => {
    highlighter(alignButtons, true);
    highlighter(spacingButtons, true);
    highlighter(formatButtons, false);
    highlighter(scriptButtons, true);

    // fonts
    fontList.forEach((value) => {
        let option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        fontName.appendChild(option);
    });

    for (let i = 1; i <= 7; i++) {
        let option = document.createElement("option");
        option.value = i;
        option.textContent = i;
        fontSizeRef.appendChild(option);
    }
    fontSizeRef.value = 3;

    writingArea.innerHTML = "";

    if (initialHtmlContent && initialHtmlContent.trim() !== "") {
      const tempDiv = document.createElement("div");
      tempDiv.innerHTML = initialHtmlContent;

      if (tempDiv.querySelector(".page")) {
        writingArea.innerHTML = initialHtmlContent;
      } else {
        createNewPage(initialHtmlContent);
      }
    } else {
      createNewPage();
    }

writingArea.querySelectorAll(".page").forEach(observePage);

    writingArea.querySelectorAll(".page").forEach(observePage);

    writingArea.addEventListener("input", checkPageOverflow);
    writingArea.addEventListener("paste", handlePaste);

    const firstPage = writingArea.querySelector(".page");
    if (firstPage) firstPage.focus();
};

// ======= MODYFIKACJA TEKSTU =======
const modifyText = (command, defaultUi, value) => {
  document.execCommand(command, defaultUi, value);
};

optionsButtons.forEach((button) => {
  button.addEventListener("click", () => {
    modifyText(button.id, false, null);
  });
});

advancedOptionButton.forEach((button) => {
  button.addEventListener("change", () => {
    modifyText(button.id, false, button.value);
  });
});

linkButton.addEventListener("click", () => {
  let userLink = prompt("Podaj adres URL:");
  if (!userLink) return;
  if (!/^https?:\/\//i.test(userLink)) {
    userLink = "http://" + userLink;
  }
  modifyText("createLink", false, userLink);
});

// ======= HIGHLIGHTER =======
const highlighter = (className, needsRemoval) => {
  className.forEach((button) => {
    button.addEventListener("click", () => {
      if (needsRemoval) {
        const alreadyActive = button.classList.contains("active");
        highlighterRemover(className);
        if (!alreadyActive) button.classList.add("active");
      } else {
        button.classList.toggle("active");
      }
    });
  });
};

const highlighterRemover = (className) => {
  className.forEach((button) => button.classList.remove("active"));
};

// ======= Wklejanie obrazków =======
const handlePaste = (e) => {
  const items = e.clipboardData?.items;
  if (!items) return;

  for (const item of items) {
    if (item.type.startsWith("image/")) {
      e.preventDefault();
      const file = item.getAsFile();
      const reader = new FileReader();

      reader.onload = function (event) {
        const img = document.createElement("img");
        img.src = event.target.result;
        img.style.maxWidth = "100%";
        img.style.borderRadius = "6px";
        img.alt = "Wklejony obraz";
        insertImageAtCursor(img);
      };
      reader.readAsDataURL(file);
    }
  }
  setTimeout(() => checkPageOverflow({ target: document.activeElement }), 50);
};

// ======= Wstawianie obrazków =======
function insertImageAtCursor(imageElement) {
  const selection = window.getSelection();
  if (!selection || !selection.rangeCount) {
    const lastPage = writingArea.querySelector('.page:last-child');
    if(lastPage) lastPage.appendChild(imageElement);
  } else {
    const range = selection.getRangeAt(0);
    range.deleteContents();
    range.insertNode(imageElement);
    range.setStartAfter(imageElement);
    range.setEndAfter(imageElement);
    selection.removeAllRanges();
    selection.addRange(range);
  }
  makeImageResizable(imageElement);
  makeImageDraggable(imageElement);
}

// ======= RESIZE OBRAZKÓW =======
function makeImageResizable(img) {
  if (img.parentElement.classList.contains("resizable-wrapper")) return;
  const wrapper = document.createElement("div");
  wrapper.classList.add("resizable-wrapper");
  wrapper.style.position = "relative";
  wrapper.style.display = "inline-block";
  wrapper.style.verticalAlign = "bottom";
  wrapper.style.lineHeight = "0";
  img.parentNode.insertBefore(wrapper, img);
  wrapper.appendChild(img);
  const positions = ["top-left", "top-right", "bottom-left", "bottom-right"];
  const handles = [];
  positions.forEach((pos) => {
    const handle = document.createElement("div");
    handle.classList.add("resize-handle", pos);
    handle.style.display = "none";
    wrapper.appendChild(handle);
    handles.push(handle);
  });

  if (!document.getElementById("resize-style")) {
    const style = document.createElement("style");
    style.id = "resize-style";
    style.textContent = `
      .resizable-wrapper img { display: block; width: 100%; height: auto; }
      .resize-handle { width: 10px; height: 10px; background: #338cf4; border: 2px solid white; position: absolute; border-radius: 50%; cursor: pointer; z-index: 10; }
      .resize-handle.top-left { top: -6px; left: -6px; cursor: nwse-resize; }
      .resize-handle.top-right { top: -6px; right: -6px; cursor: nesw-resize; }
      .resize-handle.bottom-left { bottom: -6px; left: -6px; cursor: nesw-resize; }
      .resize-handle.bottom-right { bottom: -6px; right: -6px; cursor: nwse-resize; }
      .resizing { user-select: none; }
      .selected-img { outline: 2px solid #338cf4; border-radius: 4px; }
    `;
    document.head.appendChild(style);
  }

  let isResizing, currentHandle, startX, startY, startWidth;
  img.addEventListener("click", (e) => {
    e.stopPropagation();
    document.querySelectorAll(".resize-handle").forEach((h) => (h.style.display = "none"));
    document.querySelectorAll("img.selected-img").forEach((im) => im.classList.remove("selected-img"));
    handles.forEach((h) => (h.style.display = "block"));
    img.classList.add("selected-img");
  });
  document.addEventListener("click", (e) => {
    if (!wrapper.contains(e.target)) {
      handles.forEach((h) => (h.style.display = "none"));
      img.classList.remove("selected-img");
    }
  });
  handles.forEach((handle) => {
    handle.addEventListener("mousedown", (e) => {
      e.preventDefault(); e.stopPropagation(); isResizing = true;
      currentHandle = handle; startX = e.clientX; startY = e.clientY;
      startWidth = wrapper.offsetWidth; document.body.classList.add("resizing");
    });
  });
  document.addEventListener("mousemove", (e) => {
    if (!isResizing || !currentHandle) return;
    const dx = e.clientX - startX;
    let newWidth = startWidth;
    if (currentHandle.classList.contains("bottom-right") || currentHandle.classList.contains("top-right")) newWidth += dx;
    else newWidth -= dx;
    wrapper.style.width = Math.max(newWidth, 30) + "px";
    wrapper.style.height = "auto";
  });
  document.addEventListener("mouseup", () => {
    isResizing = false; document.body.classList.remove("resizing");
  });
}

// ======= DRAG OBRAZKÓW =======
function makeImageDraggable(img) {
  const wrapper = img.closest('.resizable-wrapper');
  if (!wrapper) return;
  wrapper.setAttribute("draggable", "true");
  wrapper.style.cursor = "grab";
  wrapper.addEventListener("dragstart", (e) => {
    e.stopPropagation(); window.draggedElement = wrapper;
    e.dataTransfer.setData("text/plain", "__image_drag__");
    e.dataTransfer.setDragImage(img, img.offsetWidth / 2, img.offsetHeight / 2);
    setTimeout(() => wrapper.classList.add("dragging-active"), 0);
  });
  wrapper.addEventListener("dragend", () => {
    wrapper.classList.remove("dragging-active"); window.draggedElement = null;
  });
}

if (!document.getElementById("drag-style")) {
  const dragStyle = document.createElement("style"); dragStyle.id = "drag-style";
  dragStyle.textContent = `.dragging-active { opacity: 0.4; }`;
  document.head.appendChild(dragStyle);
}

writingArea.addEventListener("dragover", (e) => {
  if (window.draggedElement) e.preventDefault();
});

writingArea.addEventListener("drop", (e) => {
  if (!window.draggedElement) return;
  e.preventDefault();
  const draggedWrapper = window.draggedElement;
  const dropTargetPage = e.target.closest(".page");
  if (!dropTargetPage) return;

  const range = document.caretRangeFromPoint(e.clientX, e.clientY);
  if (range) {
    range.deleteContents();
    range.insertNode(draggedWrapper);
    const selection = window.getSelection();
    range.setStartAfter(draggedWrapper);
    range.collapse(true);
    selection.removeAllRanges();
    selection.addRange(range);
  } else {
    dropTargetPage.appendChild(draggedWrapper);
  }
  window.draggedElement = null;
  setTimeout(() => {
    checkPageOverflow({ target: draggedWrapper });
  }, 50);
});
// ======= MENU KONTEKSTOWE: MINI TOOLBAR + AKCJE =======
if (writingArea) {
  const contextMenu = document.getElementById("editor-context-menu");
  const toolbarButtons = contextMenu.querySelectorAll(".ecm-tool-btn");
  const actionButtons = contextMenu.querySelectorAll(".ecm-item");
  const fontSelect = document.getElementById("ecm-fontName");

  const headingSelect = document.getElementById("ecm-heading");
  const sizeSelect = document.getElementById("ecm-fontSize");

  const globalHeadingSelect = document.getElementById("formatBlock");
  const globalFontSizeSelect = document.getElementById("fontSize");

  const globalForeInput = document.getElementById("foreColor");
  const globalBackInput = document.getElementById("backColor");

  const foreDot = contextMenu.querySelector(
    '.ecm-color-btn[data-color-type="foreColor"] .ecm-color-dot'
  );
  const backDot = contextMenu.querySelector(
    '.ecm-color-btn[data-color-type="backColor"] .ecm-color-dot'
  );

  const foreInputContext = document.getElementById("ecm-foreColor");
  const backInputContext = document.getElementById("ecm-backColor");


  let contextMenuVisible = false;
  let lastSelectionRange = null;

  function storeSelection() {
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) {
      lastSelectionRange = null;
      return;
    }
    lastSelectionRange = sel.getRangeAt(0).cloneRange();
  }

  function restoreSelection() {
    if (!lastSelectionRange) return false;
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(lastSelectionRange);
    return true;
  }

  if (fontSelect && typeof fontList !== "undefined") {
    fontList.forEach((value) => {
      const opt = document.createElement("option");
      opt.value = value;
      opt.textContent = value;
      fontSelect.appendChild(opt);
    });

    const globalFontSelect = document.getElementById("fontName");
    fontSelect.value = globalFontSelect ? globalFontSelect.value : "Arial";

    fontSelect.addEventListener("change", () => {
      const ok = restoreSelection();
      if (!ok) return;

      modifyText("fontName", false, fontSelect.value);
      if (globalFontSelect) globalFontSelect.value = fontSelect.value;
      hideContextMenu();
    });
  }

  if (headingSelect) {
    if (globalHeadingSelect) {
      headingSelect.value = globalHeadingSelect.value || "";
    }

    headingSelect.addEventListener("change", () => {
      const ok = restoreSelection();
      if (!ok) return;

      const value = headingSelect.value;
      if (value) {
        modifyText("formatBlock", false, value);
      } else {
        modifyText("formatBlock", false, "P");
      }

      if (globalHeadingSelect) {
        globalHeadingSelect.value = value;
      }

      hideContextMenu();
    });
  }

  if (sizeSelect) {
    if (globalFontSizeSelect) {
      sizeSelect.value = globalFontSizeSelect.value || "3";
    }

    sizeSelect.addEventListener("change", () => {
      const ok = restoreSelection();
      if (!ok) return;

      modifyText("fontSize", false, sizeSelect.value);

      if (globalFontSizeSelect) {
        globalFontSizeSelect.value = sizeSelect.value;
      }

      hideContextMenu();
    });
  }

  function syncDotsFromToolbar() {
    if (foreDot && globalForeInput) {
      foreDot.style.background = globalForeInput.value || "#ffffff";
    }
    if (backDot && globalBackInput) {
      backDot.style.background = globalBackInput.value || "#ffffff";
    }
  }

  function hideContextMenu() {
    if (!contextMenuVisible) return;
    contextMenu.style.display = "none";
    contextMenuVisible = false;
  }

  function showContextMenu(x, y) {
    contextMenu.style.display = "block";
    contextMenuVisible = true;

    syncDotsFromToolbar();

    const rect = contextMenu.getBoundingClientRect();
    let left = x;
    let top = y;
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    if (left + rect.width > vw - 8) left = vw - rect.width - 8;
    if (top + rect.height > vh - 8) top = vh - rect.height - 8;

    contextMenu.style.left = left + "px";
    contextMenu.style.top = top + "px";
  }

  document.addEventListener("contextmenu", (e) => {
    const page = e.target.closest(".page");

    if (!page) {
      hideContextMenu();
      return;
    }

    e.preventDefault();

    page.focus();
    storeSelection();

    showContextMenu(e.clientX, e.clientY);
  });

  document.addEventListener("click", (e) => {
    if (!contextMenu.contains(e.target)) {
      hideContextMenu();
    }
  });

  window.addEventListener("scroll", hideContextMenu);
  window.addEventListener("resize", hideContextMenu);

toolbarButtons.forEach((btn) => {
  btn.addEventListener("click", (e) => {
    e.preventDefault();

    const colorType = btn.dataset.colorType;
    const command = btn.dataset.command;

    const ok = restoreSelection();
    if (!ok && writingArea) {
      const firstPage = writingArea.querySelector(".page");
      firstPage && firstPage.focus();
    }
        if (foreInputContext) {
      foreInputContext.addEventListener("change", () => {
        const ok = restoreSelection();
        if (!ok && writingArea) {
          const firstPage = writingArea.querySelector(".page");
          firstPage && firstPage.focus();
        }

        const value = foreInputContext.value;
        modifyText("foreColor", false, value);

        if (globalForeInput) {
          globalForeInput.value = value;
        }
        syncDotsFromToolbar();
      });
    }

    if (backInputContext) {
      backInputContext.addEventListener("change", () => {
        const ok = restoreSelection();
        if (!ok && writingArea) {
          const firstPage = writingArea.querySelector(".page");
          firstPage && firstPage.focus();
        }

        const value = backInputContext.value;
        modifyText("backColor", false, value);

        if (globalBackInput) {
          globalBackInput.value = value;
        }
        syncDotsFromToolbar();
      });
    }

    if (colorType) {
      if (colorType === "foreColor" && foreInputContext) {
        foreInputContext.click();
      } else if (colorType === "backColor" && backInputContext) {
        backInputContext.click();
      }
      return;
    }

    if (command) {
      modifyText(command, false, null);
      hideContextMenu();
    }
  });
});

  if (globalForeInput) {
    globalForeInput.addEventListener("input", syncDotsFromToolbar);
  }
  if (globalBackInput) {
    globalBackInput.addEventListener("input", syncDotsFromToolbar);
  }

  actionButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const action = btn.dataset.action;

      const ok = restoreSelection();
      if (!ok && writingArea) {
        const firstPage = writingArea.querySelector(".page");
        firstPage && firstPage.focus();
      }

      switch (action) {
        case "cut":
        case "copy":
          document.execCommand(action);
          break;

        case "paste":
          if (navigator.clipboard && navigator.clipboard.read) {
            navigator.clipboard.read().then((items) => {
              for (const item of items) {
                if (item.types.includes("text/html")) {
                  item.getType("text/html").then((blob) => {
                    blob.text().then((html) => {
                      document.execCommand("insertHTML", false, html);
                    });
                  });
                  return;
                }
              }
              for (const item of items) {
                if (item.types.includes("text/plain")) {
                  item.getType("text/plain").then((blob) => {
                    blob.text().then((text) => {
                      document.execCommand("insertText", false, text);
                    });
                  });
                  return;
                }
              }
            });
          } else if (navigator.clipboard && navigator.clipboard.readText) {
            navigator.clipboard.readText().then((text) => {
              if (!text) return;
              document.execCommand("insertText", false, text);
            });
          } else {
            document.execCommand("paste");
          }
          break;

        case "paste-plain":
          if (navigator.clipboard && navigator.clipboard.readText) {
            navigator.clipboard.readText().then((text) => {
              if (!text) return;
              document.execCommand("insertText", false, text);
            });
          } else {
            const tmp = document.createElement("div");
            tmp.contentEditable = "true";
            tmp.style.position = "fixed";
            tmp.style.left = "-9999px";
            document.body.appendChild(tmp);
            tmp.focus();

            const okPaste = document.execCommand("paste");
            const text = tmp.innerText;
            document.body.removeChild(tmp);

            if (!okPaste || !text) return;
            restoreSelection();
            document.execCommand("insertText", false, text);
          }
          break;

        default:
          break;
      }

      hideContextMenu();
    });
  });
}
