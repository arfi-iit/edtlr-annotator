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
                drawTable: "Cmd-Alt-T"
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
            }],
            toolbarTips: false,
        });
        
        return simplemde;
    }

    markAsSuperscript(from, to){
        this.codeMirror.markText(from, to, {className: "superscript"});
    }
    
    markAllSuperscripts(){
        let cm = this.codeMirror;
        const pattern = /\^.*\^/g;
        let index = 0;
        cm.eachLine(l => {
            const matches = l.text.matchAll(pattern);
            for(const match of matches){
                const from = {line: index, ch: match.index};
                const to = {line: index, ch: match.index + match[0].length};
                this.markAsSuperscript(from, to);
            }
            index = index + 1;
        });
    }
    
    static toggleSuperscript(editor){
        const marker="^";
        const className = "superscript";
        
        let cm = editor.codemirror;
        let start = cm.getCursor("start");
        let end = cm.getCursor("end");
        let mark = AnnotationEditor.getMarkAtCursor(editor, className);
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
