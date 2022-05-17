window.render = () => {
    const CANVAS_TOP_PX = 0
    const CANVAS_BOTTOM_PX = 30

    let zoomLevel = 1

    return {
        transform: '',

        createConcepts(divRef, items, button_class) {
            divRef.innerHTML = ""
            ;[...items].forEach(concept => {
                divRef.innerHTML += "<a href=\"?search_query=" + concept.text + "\" " +
                    "class=\"" + button_class + "\" " +
                    "data-currentid=\"" + concept.id + "\" " +
                    "data-childrenid=\"" + concept.children_ids +
                    "\" data-parentid=\"" + concept.parent_ids + "\">" + concept.text + "</a>"
            })
        },
// done <a href="{% url 'search_results' %}?search_query={{ parent.text | urlencode }}"
// done class="button"
// done data-currentid="{{ parent.id }}"
// done data-childrenid="{{ parent.children_ids }}"
// done data-parentid="{{ parent.parent_ids }}"
// data-parent="0">{{ parent.text }}</a>


        drawGraph(graphRef, direction) {
            const isDirectionTop = direction === 'top'

            const topRow = isDirectionTop ? graphRef.nextElementSibling : graphRef.previousElementSibling
            const bottomRow = isDirectionTop ? graphRef.previousElementSibling : graphRef.nextElementSibling

            graphRef.width = Math.max(topRow.clientWidth, bottomRow.clientWidth)
            graphRef.height = CANVAS_BOTTOM_PX

            const offScreenCanvas = this.createOffScreenCanvas(graphRef.width, graphRef.height)
            const context = offScreenCanvas.getContext("2d");
            context.strokeStyle = '#ababab'

            ;[...topRow.children].forEach(node => {
                const parentNodeId = parseInt(node.dataset.parent, 10)
                const parentIds = isDirectionTop ? node.dataset.parentid : node.dataset.childrenid
                console.log(parentNodeId, parentIds, bottomRow.children)

                // if (isNaN(parentIds)) return

                ;[...bottomRow.children].forEach(bottomNode => {
                    const currentId = parseInt(bottomNode.dataset.currentid, 10)
                    console.log(currentId, parentNodeId)
                    if (parentIds.split('-').includes(currentId.toString())) {
                        const bottomCenter = bottomNode.offsetLeft + bottomNode.clientWidth / 2
                        const topCenter = node.offsetLeft + node.clientWidth / 2
                        context.moveTo(topCenter, isDirectionTop ? CANVAS_BOTTOM_PX : CANVAS_TOP_PX)
                        context.lineTo(bottomCenter, isDirectionTop ? CANVAS_TOP_PX : CANVAS_BOTTOM_PX)
                        context.stroke()
                    }
                })
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

        myMethod(taxonomy) {
            this.$nextTick(() => {
                this.createConcepts(this.$refs.subParentConcepts, taxonomy.subparents, button_class = "button is-small is-warning")
                this.createConcepts(this.$refs.parentConcepts, taxonomy.parents, button_class = "button")
                this.createConcepts(this.$refs.coreConcept, [taxonomy.concept], button_class = "button is-link is-medium")
                this.createConcepts(this.$refs.childrenConcepts, taxonomy.children, button_class = "button")
                this.createConcepts(this.$refs.subChildrenConcepts, taxonomy.subchildren, button_class = "button is-small is-warning")

                this.drawGraph(this.$refs.conceptParents, 'top')
                this.drawGraph(this.$refs.parentsSubParents, 'top')
                this.drawGraph(this.$refs.conceptChildren, 'bottom')
                this.drawGraph(this.$refs.childrenSubChildren, 'bottom')


            });
        }
    }
};



window.conceptMap = (taxonomy) => {
    const CANVAS_TOP_PX = 0
    const CANVAS_BOTTOM_PX = 30

    let zoomLevel = 1

    return {
        transform: '',

        init() {
            this.createConcepts(this.$refs.childrenConcepts, taxonomy.children)
            this.createConcepts(this.$refs.parentConcepts, taxonomy.parents)

            this.drawGraph(this.$refs.conceptParents, 'top')
            this.drawGraph(this.$refs.parentsSubParents, 'top')
            this.drawGraph(this.$refs.conceptChildren, 'bottom')
            this.drawGraph(this.$refs.childrenSubChildren, 'bottom')
        },

        createConcepts(divRef, items) {

            ;[...items].forEach(concept => {
                divRef.innerHTML += "<a href=\"?search_query=" + concept.text + "\" class=\"button is-small is-warning\" >" + concept.text + "</a>"
            })
        },

        drawGraph(graphRef, direction) {
            const isDirectionTop = direction === 'top'

            const topRow = isDirectionTop ? graphRef.nextElementSibling : graphRef.previousElementSibling
            const bottomRow = isDirectionTop ? graphRef.previousElementSibling : graphRef.nextElementSibling

            graphRef.width = Math.max(topRow.clientWidth, bottomRow.clientWidth)
            graphRef.height = CANVAS_BOTTOM_PX

            const offScreenCanvas = this.createOffScreenCanvas(graphRef.width, graphRef.height)
            const context = offScreenCanvas.getContext("2d");
            context.strokeStyle = '#ababab'

            ;[...topRow.children].forEach(node => {
                const parentNodeId = parseInt(node.dataset.parent, 10)
                const parentIds = isDirectionTop ? node.dataset.parentid : node.dataset.childrenid

                if (isNaN(parentNodeId)) return

                ;[...bottomRow.children].forEach(bottomNode => {
                    const currentId = parseInt(bottomNode.dataset.currentid, 10)

                    if (parentIds.split('-').includes(currentId.toString())) {
                        const bottomCenter = bottomNode.offsetLeft + bottomNode.clientWidth / 2
                        const topCenter = node.offsetLeft + node.clientWidth / 2
                        context.moveTo(topCenter, isDirectionTop ? CANVAS_BOTTOM_PX : CANVAS_TOP_PX)
                        context.lineTo(bottomCenter, isDirectionTop ? CANVAS_TOP_PX : CANVAS_BOTTOM_PX)
                        context.stroke()
                    }
                })
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
