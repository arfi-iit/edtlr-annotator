class ValidationFlow{
    constructor(imageId, editorId, saveButtonId, markValidButtonId){
        this.image = document.getElementById(imageId);

        this.editor = document.getElementById(editorId);
        this.quill = new Quill(`#${editorId}`,{
            theme: 'snow'
        });
        this.editor.style.height="96%";

        this.btnSave = document.getElementById(saveButtonId);
        this.btnMarkValid = document.getElementById(markValidButtonId);
        this.setControlsEnabled(false);
        this.setControlsVisible(false);
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

    initialize(){
        fetch("api/ocrresults")
            .then(res => res.json())
            .then(data => {
                const {text, image_path} = data;
                this.quill.setText(text);
                this.image.src = image_path;
                this.setControlsVisible(true);
                this.setControlsEnabled(true);
            });
    }
}
