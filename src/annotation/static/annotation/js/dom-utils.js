class DomUtils {
    static setElementVisible(element, visible){
        if (visible) {
            element.classList.remove("d-none");
        }else{
            element.classList.add("d-none");
        }
    }

    static get imageNotAvailablePath(){
        return "/static/annotation/assets/png/page-not-available.png";
    }
    
    static updateImageSrc(img, src){
        if (src == null || !src) {
            // Display page not available message.
            img.src = DomUtils.imageNotAvailablePath;
        }else{
            img.src = src;
        }
    }

    static isPageNotFoundImg(img){
        return img.src.endsWith(DomUtils.imageNotAvailablePath);
    }
}
