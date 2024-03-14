class DomUtils {
    static setElementVisible(element, visible){
        if (visible) {
            element.classList.remove("d-none");
        }else{
            element.classList.add("d-none");
        }
    }

    static updateImageSrc(img, src){
        if (src == null || !src) {
            // Set the image to a 1x1 px white gif as suggested
            // here: https://stackoverflow.com/a/8425853/844006
            img.src = "data:image/gif;base64,R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";
        }else{
            img.src = src;
        }
    }
}
