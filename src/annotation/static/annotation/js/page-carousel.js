class PageCarousel {
    constructor(elementId) {
        this.carousel = document.getElementById(elementId);

        const buttons = Array.from(this.carousel.getElementsByTagName("button"));
        this.btnPrevPage = buttons[0];
        this.btnNextPage = buttons[1];

        const images = Array.from(this.carousel.getElementsByTagName("img"));

        DomUtils.setElementVisible(this.btnPrevPage, false);
        if (images.length <= 1) {
            DomUtils.setElementVisible(this.btnNextPage, false);
        }

        this.carousel.addEventListener('slide.bs.carousel', function (eventArgs) {
            const {target, from, to} = eventArgs;
            const buttons = Array.from(target.getElementsByTagName("button"));
            const btnPrevPage = buttons[0];
            const btnNextPage = buttons[1];
            const images = Array.from(target.getElementsByTagName("img"));
            
            if (to === 0) {
                DomUtils.setElementVisible(btnPrevPage, false);
                DomUtils.setElementVisible(btnNextPage, images.length > 1);                
            }else if (to === images.length - 1) {
                DomUtils.setElementVisible(btnPrevPage, images.length > 1);
                DomUtils.setElementVisible(btnNextPage, false);                
            }else{
                DomUtils.setElementVisible(btnPrevPage, to > 0 && images.length > 1);
                DomUtils.setElementVisible(btnNextPage, to < images.length -1 && images.length > 1);                
            }
        });
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

    static updateZoom(slider, imgElement) {
        const zoomLevel = slider.value;
        imgElement.classList.toggle('w-100', zoomLevel==1);
        imgElement.style.width = `${zoomLevel * 100}%`;
        imgElement.closest('.zoomable-container').classList.toggle('scrollable', zoomLevel > 1);
        
        const zoomValueElement = slider.nextElementSibling;
        zoomValueElement.textContent = `${zoomLevel}x`;
    }
}
