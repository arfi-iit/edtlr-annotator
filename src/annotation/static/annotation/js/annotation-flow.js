import { createDictmarkdownEditor } from "./dictmarkdown-editor.js";

export class AnnotationFlow {
    constructor(
        carouselId,
        editorId,
        saveButtonId,
        markCompleteButtonId,
        hiddenFieldNames,
    ) {
        this.editor = document.getElementById(editorId);
        this.btnSave = document.getElementById(saveButtonId);

        this.btnMarkComplete = document.getElementById(markCompleteButtonId);
        this.hiddenFields = hiddenFieldNames
            .map((name) => document.getElementsByName(name))
            .map((nodeList) => Array.from(nodeList))
            .flat();
        this.carousel = new PageCarousel(carouselId);

        this.onTextChange = this.onTextChange.bind(this);

        this.setControlsEnabled(false);
        this.setControlsVisible(false);

        this.dictmarkdownEditor = createDictmarkdownEditor(this.editor);
        this.dictmarkdownEditor.onTextChange(this.onTextChange);
    }

    onTextChange(value) {
        this.hiddenFields.map((hf) => (hf.value = value));
        this.setButtonsEnabled(Boolean(value));
    }

    setControlsVisible(visible) {
        let controls = [this.btnMarkComplete, this.btnSave, this.editor];
        controls.map((c) => {
            DomUtils.setElementVisible(c, visible);
        });

        this.carousel.setControlsVisible(visible);
    }

    setButtonsEnabled(enabled) {
        this.btnMarkComplete.disabled = !enabled;
        this.btnSave.disabled = !enabled;
    }

    setControlsEnabled(enabled) {
        this.setButtonsEnabled(enabled);
        this.carousel.setControlsEnabled(enabled);
    }

    initialize(entryId) {
        fetch(`api/entries/${entryId}`)
            .then((res) => {
                if (res.ok) {
                    return res.json();
                }
                console.debug(res);
                return { text: "" };
            })
            .then((data) => {
                const { text } = data;

                this.setControlsVisible(true);
                this.setControlsEnabled(true);
                this.dictmarkdownEditor.setText(text);
            });
    }
}
