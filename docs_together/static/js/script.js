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

const createNewPage = () => {
  const page = document.createElement("div");
  page.classList.add("page");
  page.setAttribute("contenteditable", "true");
  writingArea.appendChild(page);
  return page;
};

const checkPageOverflow = (e) => {
  const currentPage = e.target.closest(".page");
  if (!currentPage) return;

  while (currentPage.scrollHeight > currentPage.clientHeight) {
    const pages = Array.from(writingArea.querySelectorAll(".page"));
    const currentPageIndex = pages.indexOf(currentPage);
    let nextPage = pages[currentPageIndex + 1];

    if (!nextPage) {
      nextPage = createNewPage();
    }
    
    const lastElement = currentPage.lastElementChild;
    if (lastElement) {
      nextPage.insertBefore(lastElement, nextPage.firstChild);
    } else {
      break; 
    }
  }
};

const initializer = (initialHtmlContent) => {
  highlighter(alignButtons, true);
  highlighter(spacingButtons, true);
  highlighter(formatButtons, false);
  highlighter(scriptButtons, true);

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

  const firstPage = createNewPage();

  if (initialHtmlContent) {
    firstPage.innerHTML = initialHtmlContent;
  }
  
  firstPage.focus();

  writingArea.addEventListener("input", checkPageOverflow);
  writingArea.addEventListener("paste", handlePaste);
};

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
