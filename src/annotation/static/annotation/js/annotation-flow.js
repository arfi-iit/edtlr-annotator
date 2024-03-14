// import {AnnotationEditor} from './annotation-editor.js';

class AnnotationFlow{
    constructor(carouselId, editorId, saveButtonId,
                markCompleteButtonId, hiddenFieldNames){
        this.editor = document.getElementById(editorId);
        this.btnSave = document.getElementById(saveButtonId);
        this.btnMarkComplete = document.getElementById(markCompleteButtonId);
        this.hiddenFields = hiddenFieldNames.map(name => document.getElementsByName(name))
            .map(nodeList => Array.from(nodeList))
            .flat();
        this.carousel = new PageCarousel(carouselId);
        
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
            this.editor
        ];
        controls.map(c => {
            DomUtils.setElementVisible(c, visible);
        });
        
        this.carousel.setControlsVisible(visible);
    }
    
    setControlsEnabled(enabled){
        this.btnMarkComplete.disabled = !enabled;
        this.btnSave.disabled = !enabled;

        this.carousel.setControlsEnabled(enabled);
    }

    initialize(pageId){
        fetch(`api/pages/${pageId}`)
            .then(res => res.json())
            .then(data => {
                const {contents, image_path} = data;
                this.mdeEditor.text = contents;
                this.carousel.setImages({
                    previous:null,
                    current: image_path,
                    next:null
                });
                
                this.setControlsVisible(true);
                this.setControlsEnabled(true);
            });
    }
}

