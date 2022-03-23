window.conceptMap = () => {
    const CANVAS_TOP_PX = 0
    const CANVAS_BOTTOM_PX = 30

    return {
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

            const context = graphRef.getContext('2d')
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
        },
    }
}
