import { assert } from "chai";
import * as QP from "../src/index";
import * as helper from "./helper";
import { plan } from "./plans";

/** A container attached to the page, so that layout (widths, zoom) is computed. */
function attached(width: number): HTMLElement {
    let container = document.createElement("div");
    container.style.width = width + "px";
    document.body.appendChild(container);
    return container;
}

function zoomOf(container: Element): string {
    return (<any>(<HTMLElement>container.querySelector(".qp-root")).style).zoom;
}

describe("Options", () => {

    describe("theme", () => {

        it("Uses the light theme by default, and the theme passed in", () => {
            assert.isNotNull(helper.showPlan(plan.KeyLookup).querySelector(".qp-root.qp-theme-light"));
            let container = document.createElement("div");
            QP.showPlan(container, plan.KeyLookup, { theme: "dark" });
            assert.isNotNull(container.querySelector(".qp-root.qp-theme-dark"));
            assert.isNull(container.querySelector(".qp-theme-light"));
        });

        it("setTheme switches the theme of a plan already shown", () => {
            let container = document.createElement("div");
            QP.showPlan(container, plan.KeyLookup, { theme: "auto" });
            QP.setTheme(container, "dark");
            let root = container.querySelector(".qp-root");
            assert.isTrue(root.classList.contains("qp-theme-dark"));
            assert.isFalse(root.classList.contains("qp-theme-auto"));
        });

        it("Gives the tooltip, which leaves the plan for the body, the theme of its plan", (done) => {
            let container = attached(2000);
            QP.showPlan(container, plan.KeyLookup, { theme: "dark" });
            let node = container.querySelector(".qp-node");
            node.dispatchEvent(new MouseEvent("mouseover"));
            setTimeout(() => {
                try {
                    let layer = document.querySelector(".qp-tt-layer");
                    assert.isNotNull(layer);
                    assert.isTrue(layer.classList.contains("qp-theme-dark"));
                    assert.isNotNull(layer.querySelector(".qp-tt"));
                    node.dispatchEvent(new MouseEvent("mouseout", { relatedTarget: document.body }));
                    assert.isNull(document.querySelector(".qp-tt-layer"));
                    done();
                } catch (e) {
                    done(e);
                } finally {
                    container.remove();
                }
            }, 700);
        });

    });

    describe("fitWidth", () => {

        // qp.css is not loaded in the tests: without it the nodes stack up and nothing is wide
        let style: HTMLStyleElement;
        beforeEach(() => {
            style = document.createElement("style");
            style.textContent = ".qp-root { display: inline-block; width: 1500px; }";
            document.head.appendChild(style);
        });
        afterEach(() => style.remove());

        it("Scales a wide plan down to its container, never below the minimum, and a click toggles full size", () => {
            let container = attached(300);
            try {
                QP.showPlan(container, plan.computeScalarPassThrough, { fitWidth: 0.6 });
                assert.equal("0.6", zoomOf(container));
                (<HTMLElement>container.querySelector(".qp-root")).click();
                assert.equal("1", zoomOf(container));
                (<HTMLElement>container.querySelector(".qp-root")).click();
                assert.equal("0.6", zoomOf(container));
            } finally {
                container.remove();
            }
        });

        it("Leaves alone a plan that fits, and any plan when the option is not set", () => {
            let wide = attached(5000);
            let narrow = attached(300);
            try {
                QP.showPlan(wide, plan.KeyLookup, { fitWidth: 0.6 });
                assert.equal("", zoomOf(wide));
                QP.showPlan(narrow, plan.computeScalarPassThrough);
                assert.equal("", zoomOf(narrow));
            } finally {
                wide.remove();
                narrow.remove();
            }
        });

    });

    describe("cost level", () => {

        it("Marks the share of the statement cost of expensive operators only", () => {
            let container = helper.showPlan(plan.KeyLookup);
            let keyLookup = helper.findNodeById(container, "5");
            assert.equal("high", keyLookup.element.querySelector(".qp-cost").getAttribute("data-cost-level"));
            let seek = helper.findNodeById(container, "3");
            let cost = seek.element.querySelector(".qp-cost");
            assert.include(cost.textContent, "0%");
            assert.isNull(cost.getAttribute("data-cost-level"));
        });

    });

});
