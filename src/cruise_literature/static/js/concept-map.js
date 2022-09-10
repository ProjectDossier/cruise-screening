window.renderPage = () => {
    const CANVAS_TOP_PX = 0
    const CANVAS_BOTTOM_PX = 30

    let zoomLevel = 1

    return {
        transform: '',

        createConcepts(divRef, items, button_class, source_taxonomy) {
            divRef.innerHTML = "&nbsp;"
            ;[...items].forEach(concept => {
                divRef.innerHTML += "<a href=\"?search_query=" + concept.text + "&source=taxonomy&source_taxonomy=" + source_taxonomy + "\" " +
                    "class=\"" + button_class + "\" " +
                    "data-currentid=\"" + concept.id + "\" " +
                    "data-childrenid=\"" + concept.children_ids +
                    "\" data-parentid=\"" + concept.parent_ids + "\">" + concept.text + "</a>"
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
                const parentIds = isDirectionTop ? node.dataset.parentid : node.dataset.childrenid

                ;[...bottomRow.children].forEach(bottomNode => {
                    const currentId = bottomNode.dataset.currentid

                    if (parentIds.split(',').includes(currentId.toString())) {
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

        renderTaxonomy(taxonomy, taxonomy_name) {
            if (!(taxonomy === undefined)) {
                // todo: take a look at $nextTick
                this.$nextTick(() => {
                    this.createConcepts(this.$refs.subParentConcepts, taxonomy.subparents, button_class = "button is-small", source_taxonomy = taxonomy_name)
                    this.createConcepts(this.$refs.parentConcepts, taxonomy.parents, button_class = "button", source_taxonomy = taxonomy_name)
                    this.createConcepts(this.$refs.coreConcept, [taxonomy.concept], button_class = "button is-link is-medium", source_taxonomy = taxonomy_name)
                    this.createConcepts(this.$refs.childrenConcepts, taxonomy.children, button_class = "button", source_taxonomy = taxonomy_name)
                    this.createConcepts(this.$refs.subChildrenConcepts, taxonomy.subchildren, button_class = "button is-small", source_taxonomy = taxonomy_name)

                    this.drawGraph(this.$refs.conceptParents, 'top')
                    this.drawGraph(this.$refs.parentsSubParents, 'top')
                    this.drawGraph(this.$refs.conceptChildren, 'bottom')
                    this.drawGraph(this.$refs.childrenSubChildren, 'bottom')


                });
            }
        },
        $nextTick(param) {

        }
    }
};

