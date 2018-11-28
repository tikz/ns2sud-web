    // var zoom = d3.behavior.zoom()
    // .scaleExtent([1, 10])
    // .on("zoom", zoomed);

    var svg = d3.select("#graph_chart");//.call(zoom);

    var force = d3.layout.force()
    .gravity(.1)
    .distance(400)
    .charge(-5000);

    var g = svg.append("g")
    .attr("class", "everything");

    d3.json("/static/data.json", function(json) {
      force
      .nodes(json.nodes)
      .links(json.links)
      .start();


      var link = g.append("g").attr("class", "links").selectAll(".link")
      .data(json.links)
      .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return d.weight; });

      var node = g.append("g").attr("class", "nodes").selectAll(".node")
      .data(json.nodes)
      .enter().append("g")
      .attr("class", "node")
      .call(force.drag);

      node.append("circle")
      .attr("r","5");

      node.append("text")
      .attr("dx", 12)
      .attr("dy", ".35em")
      .text(function(d) { return d.name });

      force.on("tick", function() {
    // soft-center the root node
    var k = .01;
    var nodes = force.nodes();

    nodes.forEach(function(node) {
      node.y += (svg.style("height").replace("px", "")/2 - nodes[0].y) * k;
      node.x += (svg.style("width").replace("px", "")/2 - nodes[0].x) * k;
    })
    link.attr("x1", function(d) { return d.source.x; })
    .attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; })
    .attr("y2", function(d) { return d.target.y; });

    node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
  });

    });
    function zoomed() {
      g.attr("transform", "scale(" + d3.event.scale + ")");
    }