class AnnotationEditor {
    constructor(editorElement, onChangeCallback){
        this.editor = this.initializeEditor(editorElement);
        this.codemirror = this.editor.codemirror;
        this.codemirror.on("change", function(editor){
            const value = editor.getValue();
            onChangeCallback(value);
        });
    }

    get simpleMde(){
        return this.editor;
    }

    get codeMirror(){
        return this.codemirror;
    }

    get text(){
        return this.editor.value();
    }

    set text(val){
        this.editor.value(val);
        this.markAllSuperscripts();
        this.markAllAcronyms();
        this.markAllSpaced();
    }

    initializeEditor(editorElement){
        // Most options demonstrate the non-default behavior
        let simplemde =new SimpleMDE({
            autoDownloadFontAwesome: true,
            autofocus: true,
            element: editorElement,
            forceSync: true,
            hideIcons: ["guide", "heading"],
            indentWithTabs: false,
            insertTexts: {
                horizontalRule: ["", "\n\n-----\n\n"],
                image: ["![](http://", ")"],
                link: ["[", "](http://)"],
                table: ["", "\n\n| Column 1 | Column 2 | Column 3 |\n| -------- | -------- | -------- |\n| Text     | Text      | Text     |\n\n"],
            },
            lineWrapping: true,
            parsingConfig: {
                allowAtxHeaderWithoutSpace: true,
                strikethrough: false,
                underscoresBreakWords: true,
            },
            placeholder: "Type here...",
            previewRender: function(plainText) {
                return customMarkdownParser(plainText); // Returns HTML from a custom parser
            },
            previewRender: function(plainText, preview) { // Async method
                setTimeout(function(){
                    preview.innerHTML = customMarkdownParser(plainText);
                }, 250);

                return "Loading...";
            },
            promptURLs: true,
            renderingConfig: {
                singleLineBreaks: false,
                codeSyntaxHighlighting: true,
            },
            shortcuts: {
                drawTable: "Cmd-Alt-T",
                toggleBold: "Cmd-B",
                toggleItalic: "Cmd-I"
            },
            showIcons: ["code", "table"],
            spellChecker: false,
            status: false,
            status: ["autosave", "lines", "words", "cursor"], // Optional usage
            status: ["autosave", "lines", "words", "cursor", {
                className: "keystrokes",
                defaultValue: function(el) {
                    this.keystrokes = 0;
                    el.innerHTML = "0 Keystrokes";
                },
                onUpdate: function(el) {
                    el.innerHTML = ++this.keystrokes + " Keystrokes";
                }
            }], // Another optional usage, with a custom status bar item that counts keystrokes
            styleSelectedText: false,
            tabSize: 4,
            toolbar: [{
                name: "bold",
                action: SimpleMDE.toggleBold,
                className: "fa fa-bold",
                title: "Bold"
            },{
                name: "italic",
                action: SimpleMDE.toggleItalic,
                className: "fa fa-italic",
                title: "Italic"
            },{
                name: "superscript",
                action: AnnotationEditor.toggleSuperscript,
                className: "fa fa-superscript",
                title: "Superscript"
            },{
                name: "acronym",
                action: AnnotationEditor.toggleAcronym,
                className: "fa fa-object-ungroup",
                title: "Acronym"
            },{
                name: "spaced",
                action: AnnotationEditor.toggleSpaced,
                className: "fa fa-text-width",
                title: "Spaced"
            }],
            toolbarTips: false,
        });

        return simplemde;
    }

    markAllAcronyms(){
        const pattern = /@[^@]*@/gm;
        this.markPattern(pattern, "acronym");
    }

    markAllSuperscripts(){
        const pattern = /\^[^\^]*\^/gm;
        this.markPattern(pattern, "superscript");
    }

    markAllSpaced(){
        const pattern = /~[^~]*~/gm;
        this.markPattern(pattern, "spaced");
    }

    markPattern(pattern, className){
        const cm = this.codeMirror;
        let index = 0;
        cm.eachLine(l => {
            const matches = l.text.matchAll(pattern);
            for(const match of matches){
                const from = {line: index, ch: match.index};
                const to = {line: index, ch: match.index + match[0].length};
                cm.markText(from, to, {className: className});
            }
            index = index + 1;
        });
    }

    static toggleSpaced(editor){
        const className = "spaced";
        const marker = "~";
        AnnotationEditor.toggleMark(editor, marker, className);
    }

    static toggleAcronym(editor){
        const marker = "@";
        const className = "acronym";
        AnnotationEditor.toggleMark(editor, marker, className);
    }

    static toggleSuperscript(editor){
        const marker="^";
        const className = "superscript";
        AnnotationEditor.toggleMark(editor, marker, className);
    }

    static toggleMark(editor, marker, className){
        const cm = editor.codemirror;
        const start = cm.getCursor("start");
        const end = cm.getCursor("end");
        const mark = AnnotationEditor.getMarkAtCursor(editor, className);
        if (mark == null) {
            let initialText = cm.getSelection();
            let formattedText = marker + initialText + marker;
            cm.replaceSelection(formattedText);
            end.ch = start.ch + formattedText.length;
            cm.setSelection(start, end);
            cm.markText(start, end, {className: className});
        }else{
            const line = mark.lines[0];
            const {from, to} = line.markedSpans[0];
            const lineNumber = cm.getCursor().line;
            cm.setSelection({line: lineNumber, ch: from}, {line: lineNumber, ch: to});
            const text = cm.getSelection();
            cm.replaceSelection(text.replaceAll(marker, ""));
        }
        cm.focus();
    }

    static getMarkAtCursor(editor, markType){
        const cm = editor.codemirror;
        const marks = cm.findMarksAt(cm.getCursor());
        if (marks.length == 0) {
            return null;
        }

        const mark = marks.find(m => m.className == markType);
        if (mark) {
            return mark;
        }

        return null;
    }
}
