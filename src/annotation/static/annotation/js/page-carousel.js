class PageCarousel {
    constructor(elementId) {
        this.carousel = document.getElementById(elementId);

        const buttons = Array.from(this.carousel.getElementsByTagName("button"));
        console.log(buttons);
        this.btnPrevPage = buttons[0];
        this.btnNextPage = buttons[1];

        const images = Array.from(this.carousel.getElementsByTagName("img"));
        console.log(images);
        this.imgPreviousPage = images[0];
        this.imgCurrentPage = images[1];
        this.imgNextPage = images[2];
    }

    setImages(images){
        const {previous, current, next} = images;
        DomUtils.updateImageSrc(this.imgPreviousPage, previous);
        this.imgCurrentPage.src = current;
        DomUtils.updateImageSrc(this.imgNextPage, next);

        DomUtils.setElementVisible(this.btnPrevPage, previous != null && previous);
        DomUtils.setElementVisible(this.btnNextPage, next != null && next);
    }

    setControlsEnabled(enabled){
        this.btnPrevPage.disabled = !enabled;
        this.btnNextPage.disabled = !enabled;
    }

    setControlsVisible(visible){
        const controls = [
            this.carousel,
        ];
        controls.map(c => {
            DomUtils.setElementVisible(c, visible);
        });
    }


}
