import { renderPlan } from "./render";
import { drawLines } from "./lines";
import { initTooltip } from "./tooltip";
import { Node } from "./node";

interface Options {
    jsTooltips?: boolean,
    /** "light" (default), "dark", or "auto" to follow prefers-color-scheme. */
    theme?: string,
    /**
     * Smallest scale (0 to 1) to which a plan wider than its container is reduced to fit;
     * a click toggles full size. 0, the default, never scales.
     */
    fitWidth?: number
}

function showPlan(container: Element, planXml: string, options?: Options) {
    options = setDefaults(options, {
        jsTooltips: true,
        theme: "light",
        fitWidth: 0
    });

    let xmlDoc = new DOMParser().parseFromString(planXml, "text/xml");
    container.innerHTML = "";
    let root = renderPlan(xmlDoc);
    root.classList.add("qp-theme-" + options.theme);
    container.appendChild(root);
    container["xml"] = xmlDoc;
    drawLines(container);

    if (options.jsTooltips) {
        initTooltip(container);
    }
    if (options.fitWidth > 0) {
        fitToWidth(container, root, options.fitWidth);
    }
}

/**
 * Scales the plan down to the container width, never below minScale, and lets a click
 * toggle between that size and full size. CSS zoom keeps the lines and tooltips aligned.
 */
function fitToWidth(container: Element, root: HTMLElement, minScale: number) {
    container.classList.add("qp-fit");
    let scale = Math.max(minScale, Math.min(1, container.clientWidth / container.scrollWidth));
    if (!(scale < 1)) return;
    let style = <any>root.style;
    style.zoom = scale;
    root.title = "Click to toggle full size";
    root.style.cursor = "zoom-in";
    root.addEventListener("click", () => {
        let full = style.zoom != "1";
        style.zoom = full ? 1 : scale;
        root.style.cursor = full ? "zoom-out" : "zoom-in";
    });
}

/** Switches the theme of a plan already shown, e.g. when the page theme changes. */
function setTheme(container: Element, theme: string) {
    let root = container.querySelector(".qp-root");
    if (root == null) return;
    root.classList.remove("qp-theme-light", "qp-theme-dark", "qp-theme-auto");
    root.classList.add("qp-theme-" + theme);
}

function setDefaults(options: Options, defaults: Options) {
    let ret = {};
    for (let attr in defaults) {
        if (defaults.hasOwnProperty(attr)) {
            ret[attr] = defaults[attr];
        }
    }
    for (let attr in options) {
        if (options.hasOwnProperty(attr)) {
            ret[attr] = options[attr];
        }
    }
    return ret;
}

export { drawLines as drawLines, showPlan, setTheme, Node }