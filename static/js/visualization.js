document.addEventListener("DOMContentLoaded", function() {
    const width = 800, height = 600;

    // Djangoから渡されたデータを利用
    const data = JSON.parse(document.getElementById("graph-data").textContent);
    const relatedScores = JSON.parse(document.getElementById('related-scores').textContent);

    const svg = d3.select("#visualization").append("svg")
        .attr("width", width)
        .attr("height", height)
        .call(d3.zoom().on("zoom", (event) => {
            // zoomイベント時に全体をズーム・パン
            g.attr("transform", event.transform);
        }))
        .append("g");  // ズーム操作を適用するためにグループを追加

    // 最大関連度を計算
    const maxScore = Math.max(...Object.values(relatedScores).map(Number));

    // リンクの強さを取得する関数
    const getLinkStrength = (sourceId, targetId) => {
        const scoreKey = sourceId + ', ' + targetId;
        const scoreKey2 = targetId + ', ' + sourceId;
        const strength = relatedScores[scoreKey] || relatedScores[scoreKey2] || 0;
        return strength ? Math.max(1, strength) : 1;  // 関連度がなければ1、そうでなければその値を使う
    };

    // リンクの色を取得する関数
    const getLinkColor = (strength) => {
        if (strength > 5) return "red";
        if (strength > 2) return "orange";
        return "gray";  // デフォルトの色
    };

    // グループ要素 `g` を追加
    const g = svg.append("g");

    // リンクを描画し、太さと色を設定
    const link = g.append("g")
        .selectAll("line")
        .data(data.links)
        .enter().append("line")
        .attr("stroke-width", d => {
            const strength = getLinkStrength(d.source, d.target);
            return (strength / maxScore) * 10;  // スケーリングして太さを設定
        })
        .attr("stroke", d => getLinkColor(getLinkStrength(d.source, d.target)));  // 色を設定

    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d => d.id).distance(200))
        .force("charge", d3.forceManyBody().strength(-400))
        .force("center", d3.forceCenter(width / 2, height / 2));

    const node = g.append("g")
        .selectAll("circle")
        .data(data.nodes)
        .enter().append("circle")
        .attr("r", d => d.problem_count * 5)  // 問題数に応じて円の大きさを変更
        .attr("fill", "steelblue")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    const maxLabelLength = 10;  // ラベルとして表示する最大文字数

    const labels = g.append("g")
        .selectAll("text")
        .data(data.nodes)
        .enter().append("text")
        .attr("text-anchor", "middle")  // 中央揃え
        .attr("dy", d => d.problem_count * 5 + 15)  // 円の下に配置 (円の半径に応じて調整)
        .text(d => {
            // テキストの長さを制限し、長い場合は "..." を追加
            return d.name.length > maxLabelLength ? d.name.slice(0, maxLabelLength) + '...' : d.name;
        })
        .attr("font-size", "10px")
        .attr("fill", "black");

    node.append("title")
        .text(d => d.name);

    simulation.on("tick", () => {
        link.attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node.attr("cx", d => d.x)
            .attr("cy", d => d.y);

        labels.attr("x", d => d.x)
            .attr("y", d => d.y);
    });

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
});

