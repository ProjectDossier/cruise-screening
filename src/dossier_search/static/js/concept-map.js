window.conceptMap = () => {
    const CANVAS_TOP_PX = 0
    const CANVAS_BOTTOM_PX = 30

    let zoomLevel = 1

    return {
        transform: '',

        init() {
            this.drawGraph(this.$refs.conceptParents, 'top')
            this.drawGraph(this.$refs.parentsSubParents, 'top')
            this.drawGraph(this.$refs.conceptChildren, 'bottom')
            this.drawGraph(this.$refs.childrenSubChildren, 'bottom')
        },

        drawGraph(graphRef, direction) {
            const isDirectionTop = direction === 'top'

            const topRow = isDirectionTop ? graphRef.previousElementSibling : graphRef.nextElementSibling
            const bottomRow = isDirectionTop ? graphRef.nextElementSibling : graphRef.previousElementSibling

            graphRef.width = Math.max(topRow.clientWidth, bottomRow.clientWidth)
            graphRef.height = CANVAS_BOTTOM_PX

            const offScreenCanvas = this.createOffScreenCanvas(graphRef.width, graphRef.height)
            const context = offScreenCanvas.getContext("2d");
            context.strokeStyle = '#dbdbdb'
            
            ;[...topRow.children].forEach(node => {
                const parentNodeId = parseInt(node.dataset.parent, 10)
                if (isNaN(parentNodeId)) return

                const parentNode = bottomRow.children[parentNodeId]
                const bottomCenter = parentNode.offsetLeft + parentNode.clientWidth / 2
                const topCenter = node.offsetLeft + node.clientWidth / 2
                context.moveTo(topCenter, isDirectionTop ? CANVAS_TOP_PX : CANVAS_BOTTOM_PX)
                context.lineTo(bottomCenter, isDirectionTop ? CANVAS_BOTTOM_PX : CANVAS_TOP_PX)
                context.stroke()
            })

            this.copyToOnScreen(offScreenCanvas, graphRef)
        },

        createOffScreenCanvas(width, height) {
            const offScreenCanvas = document.createElement('canvas')
            offScreenCanvas.width = width
            offScreenCanvas.height = height
            return offScreenCanvas
        },

        copyToOnScreen(offScreenCanvas, onScreenCanvas) {
            const context = onScreenCanvas.getContext('2d');
            context.drawImage(offScreenCanvas, 0, 0);
        },

        zoom(event) {
            const zoomLevelPlusDelta = zoomLevel + event.deltaY / 100
            zoomLevel = Math.max(zoomLevelPlusDelta, 0.25)
            zoomLevel = Math.min(zoomLevel, 1)
            this.transform = `transform: scale(${zoomLevel})`
        },
    }
}
