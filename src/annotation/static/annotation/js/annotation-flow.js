class AnnotationFlow{
    constructor(imageId, editorId, saveButtonId,
                markCompleteButtonId, hiddenFieldNames){
        this.image = document.getElementById(imageId);

        this.editor = document.getElementById(editorId);
        this.quill = new Quill(`#${editorId}`,{
            theme: 'snow'
        });
        this.editor.style.height="96%";

        this.btnSave = document.getElementById(saveButtonId);
        this.btnMarkComplete = document.getElementById(markCompleteButtonId);
        this.hiddenFields = hiddenFieldNames.map(name => document.getElementsByName(name))
            .map(nodeList => Array.from(nodeList))
            .flat();
        this.onTextChange = this.onTextChange.bind(this);
        this.quill.on('text-change', this.onTextChange);
        
        this.setControlsEnabled(false);
        this.setControlsVisible(false);
    }

    onTextChange(delta, oldDelta, source){
        const value = JSON.stringify(this.quill.getContents());
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
        this.quill.enable(enabled);
        this.image.disabled = !enabled;
    }

    initialize(pageId){
        fetch(`api/pages/${pageId}`)
            .then(res => res.json())
            .then(data => {
                const {contents, image_path} = data;
                if (contents) {
                    const delta = JSON.parse(contents);
                    this.quill.setContents(delta.ops);
                }
                else{
                    this.quill.setText("");
                }
                this.image.src = image_path; 
                this.setControlsVisible(true);
                this.setControlsEnabled(true);
                const value = JSON.stringify(this.quill.getContents());
                this.hiddenFields.map(hf =>{
                    hf.value = value;
                });
            });
    }
}
