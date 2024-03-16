class PageCarousel {
    constructor(elementId) {
        this.carousel = document.getElementById(elementId);

        const buttons = Array.from(this.carousel.getElementsByTagName("button"));
        this.btnPrevPage = buttons[0];
        this.btnNextPage = buttons[1];

        const images = Array.from(this.carousel.getElementsByTagName("img"));
        this.imgPreviousPage = images[0];
        this.imgCurrentPage = images[1];
        this.imgNextPage = images[2];

        this.carousel.addEventListener('slide.bs.carousel', function (eventArgs) {
            console.log(eventArgs);
            const {target, from, to} = eventArgs;
            const buttons = Array.from(target.getElementsByTagName("button"));
            const btnPrevPage = buttons[0];
            const btnNextPage = buttons[1];
            
            if (to === 0) {
                DomUtils.setElementVisible(btnPrevPage, false);
                DomUtils.setElementVisible(btnNextPage, true);                
            }
            if (to === 1) {
                const images = Array.from(target.getElementsByTagName("img"));
                DomUtils.setElementVisible(btnPrevPage,  !DomUtils.isPageNotFoundImg(images[0]));
                DomUtils.setElementVisible(btnNextPage, !DomUtils.isPageNotFoundImg(images[2]));
            }
            if (to === 2) {
                DomUtils.setElementVisible(btnPrevPage, true);
                DomUtils.setElementVisible(btnNextPage, false);
            }
        });
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
