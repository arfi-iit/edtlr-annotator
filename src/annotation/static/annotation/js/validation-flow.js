class ValidationFlow{
    constructor(imageId, editorId, saveButtonId,
                markValidButtonId, hiddenFieldNames){
        this.image = document.getElementById(imageId);

        this.editor = document.getElementById(editorId);
        this.quill = new Quill(`#${editorId}`,{
            theme: 'snow'
        });
        this.editor.style.height="96%";

        this.btnSave = document.getElementById(saveButtonId);
        this.btnMarkValid = document.getElementById(markValidButtonId);
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
            this.btnMarkValid,
            this.btnSave,
            this.image,
            this.editor
        ];
        controls.map(c => {
            c.style.display = visible?"inherit":"none";
        });        
    }
    
    setControlsEnabled(enabled){
        this.btnMarkValid.disabled = !enabled;
        this.btnSave.disabled = !enabled;
        this.quill.enable(enabled);
        this.image.disabled = !enabled;
    }

    initialize(pageId){
        fetch(`api/ocrresults/${pageId}`)
            .then(res => res.json())
            .then(data => {
                const {text, image_path} = data;
                this.quill.setText(text);
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
