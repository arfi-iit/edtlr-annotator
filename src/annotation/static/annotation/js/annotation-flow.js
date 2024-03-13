// import {AnnotationEditor} from './annotation-editor.js';

class AnnotationFlow{
    constructor(imageId, editorId, saveButtonId,
                markCompleteButtonId, hiddenFieldNames){
        this.image = document.getElementById(imageId);

        this.editor = document.getElementById(editorId);
        this.btnSave = document.getElementById(saveButtonId);
        this.btnMarkComplete = document.getElementById(markCompleteButtonId);
        this.hiddenFields = hiddenFieldNames.map(name => document.getElementsByName(name))
            .map(nodeList => Array.from(nodeList))
            .flat();
        this.onTextChange = this.onTextChange.bind(this);

        this.setControlsEnabled(false);
        this.setControlsVisible(false);

        this.mdeEditor = new AnnotationEditor(this.editor, this.onTextChange);

        window.mdeEditor = this.mdeEditor.simpleMde;
        window.codeMirror = this.mdeEditor.codeMirror;
    }

    onTextChange(value){
        this.hiddenFields.map(hf => hf.value = value);
    }

    setControlsVisible(visible){
        let controls = [
            this.btnMarkComplete,
            this.btnSave,
            this.image,
            this.editor
        ];
        controls.map(c => {
            c.style.display = visible?"inherit":"none";
        });        
    }
    
    setControlsEnabled(enabled){
        this.btnMarkComplete.disabled = !enabled;
        this.btnSave.disabled = !enabled;
        this.image.disabled = !enabled;
    }

    initialize(pageId){
        fetch(`api/pages/${pageId}`)
            .then(res => res.json())
            .then(data => {
                const {contents, image_path} = data;
                this.mdeEditor.text = contents;
                this.image.src = image_path; 
                this.setControlsVisible(true);
                this.setControlsEnabled(true);
            });
    }
}

