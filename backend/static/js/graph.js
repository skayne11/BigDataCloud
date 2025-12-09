function renderGraph(data) {
    let nodes = new vis.DataSet(data.nodes);
    let edges = new vis.DataSet(data.edges);

    let container = document.getElementById("viz");
    let options = {
        nodes: {
            shape: "dot",
            size: 12,
            color: {
                background: "#66aaff",
                border: "#88bbff"
            },
            font: {
                color: "#ffffff"
            }
        },
        edges: {
            color: "#444"
        },
        physics: {
            stabilization: false,
            barnesHut: {
                avoidOverlap: 0.5
            }
        },
        interaction: {
            dragNodes: true,
            hover: true
        }
    };

    new vis.Network(container, { nodes, edges }, options);
}
