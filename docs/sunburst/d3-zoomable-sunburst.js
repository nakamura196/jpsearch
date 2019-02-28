// URL: https://observablehq.com/@nakamura196/d3-zoomable-sunburst
// Title: D3 Zoomable Sunburst
// Author: Satoru Nakamura (@nakamura196)
// Version: 334
// Runtime version: 1
const m0 = {
  id: "f9e1770e0f3c730a@334",
  variables: [{
    inputs: ["md"],
    value: (function (md) {
      return (md `# D3 Zoomable Sunburst

        This variant of a [sunburst diagram](/@mbostock/d3-sunburst), a radial orientation of D3’s [hierarchical partition layout](https://github.com/d3/d3-hierarchy/blob/master/README.md#partition), shows only two layers of the [Flare visualization toolkit](https://flare.prefuse.org) package hierarchy at a time. Click a node to zoom in, or click the center to zoom out.`)
      })
    }, {
      name: "chart",
      inputs: ["partition", "data", "d3", "DOM", "width", "color", "arc", "format", "radius"],
      value: (function (partition, data, d3, DOM, width, color, arc, format, radius) {
        const root = partition(data);
        root.each(d => d.current = d);
        const svg = d3.select(DOM.svg(width, width)).style("width", "100%").style("height", "auto").style("font", "10px sans-serif");
        const g = svg.append("g").attr("transform", `translate(${width / 2},${width / 2})`);
        const path = g.append("g").selectAll("path").data(root.descendants().slice(1)).join("path").attr("fill", d => {
          while (d.depth > 1) d = d.parent;
          return color(d.data.name);
        }).attr("fill-opacity", d => arcVisible(d.current) ? (d.children ? 0.6 : 0.4) : 0).attr("d", d => arc(d.current));
        path.filter(d => d.children).style("cursor", "pointer").on("click", clicked);
        path.append("title").text(d => `${d.ancestors().map(d => d.data.name).reverse().join("/")}\n${format(d.value)}`);
        const label = g.append("g").attr("pointer-events", "none").attr("text-anchor", "middle").style("user-select", "none").selectAll("text").data(root.descendants().slice(1)).join("text").attr("dy", "0.35em").attr("fill-opacity", d => +labelVisible(d.current)).attr("transform", d => labelTransform(d.current)).text(d => d.data.name);
        const parent = g.append("circle").datum(root).attr("r", radius).attr("fill", "none").attr("pointer-events", "all").on("click", clicked);

        function clicked(p) {
          parent.datum(p.parent || root);
          root.each(d => d.target = {
            x0: Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
            x1: Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
            y0: Math.max(0, d.y0 - p.depth),
            y1: Math.max(0, d.y1 - p.depth)
          });
          const t = g.transition().duration(750);
          // Transition the data on all arcs, even the ones that aren’t visible,
          // so that if this transition is interrupted, entering arcs will start
          // the next transition from the desired position.
          path.transition(t).tween("data", d => {
            const i = d3.interpolate(d.current, d.target);
            return t => d.current = i(t);
          }).filter(function (d) {
            return +this.getAttribute("fill-opacity") || arcVisible(d.target);
          }).attr("fill-opacity", d => arcVisible(d.target) ? (d.children ? 0.6 : 0.4) : 0).attrTween("d", d => () => arc(d.current));
          label.filter(function (d) {
            return +this.getAttribute("fill-opacity") || labelVisible(d.target);
          }).transition(t).attr("fill-opacity", d => +labelVisible(d.target)).attrTween("transform", d => () => labelTransform(d.current));
        }

        function arcVisible(d) {
          return d.y1 <= 3 && d.y0 >= 1 && d.x1 > d.x0;
        }

        function labelVisible(d) {
          return d.y1 <= 3 && d.y0 >= 1 && (d.y1 - d.y0) * (d.x1 - d.x0) > 0.03;
        }

        function labelTransform(d) {
          const x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
          const y = (d.y0 + d.y1) / 2 * radius;
          return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`;
        }
        return svg.node();
      })
    }, {
      name: "data",
      inputs: ["d3"],
      value: (function (d3) {
        var arr = ['国立国会図書館', '国立科学博物館', '国立公文書館']
        var query = " SELECT DISTINCT count(?s) as ?c ?sourceInfoLabel ?sourceOrganizationLabel  ";
        query += " WHERE { ";
        query += " ?sourceInfo <http://schema.org/provider> ?sp .  ";
        query += " ?sp <http://www.w3.org/2000/01/rdf-schema#label>  ?sourceInfoLabel .    ";
        query += " ?sp <http://schema.org/sourceOrganization> ?so .     ";
        query += " ?so <http://www.w3.org/2000/01/rdf-schema#label>  ?sourceOrganizationLabel .      ";
        query += " filter ( ";
        for (var j = 0; j < arr.length; j++) {
          query += " ?sourceOrganizationLabel != '" + arr[j] + "' "
          if (j != arr.length - 1) {
            query += " && "
          }
        }
        query += " ) "
        //"?sourceOrganizationLabel != '国立国会図書館' && ?sourceOrganizationLabel != '国立科学博物館' && ?sourceOrganizationLabel != '国立公文書館')      ";
        query += " ?s <https://jpsearch.go.jp/term/property#sourceInfo> ?sourceInfo . ";
        query += " } ";
        $.ajax({
          url: "https://jpsearch.go.jp/rdf/sparql",
          type: 'GET',
          //async: false,
          data: {
            query: query,
            format: "json"
          }
        }).then(function (data) {
          var result = data.results.bindings;
          var flare = {}
          flare["name"] = "flare"
          var children = []
          flare["children"] = children
          var tmp = {}
          for (var i = 0; i < result.length; i++) {
            var obj = result[i];
            var c = obj.c.value
            var sourceInfoLabel = obj.sourceInfoLabel.value
            var sourceOrganizationLabel = obj.sourceOrganizationLabel.value
            if (!tmp[sourceOrganizationLabel]) {
              tmp[sourceOrganizationLabel] = {}
            }
            tmp[sourceOrganizationLabel][sourceInfoLabel] = c
          }
          for (var key in tmp) {
            var obj = {}
            obj["name"] = key
            var arr = []
            for (var key2 in tmp[key]) {
              var obj2 = {}
              obj2["name"] = key2
              obj2["value"] = Number(tmp[key][key2])
              arr.push(obj2)
            }
            obj["children"] = arr
            children.push(obj)
          }
          console.log(flare)
          console.log(JSON.stringify(flare))
        })
        var all = {
          "name": "flare",
          "children": [{
            "name": "国立科学博物館",
            "children": [{
              "name": "サイエンスミュージアムネット",
              "value": 8994874
            }]
          }, {
            "name": "国立国会図書館",
            "children": [{
              "name": "ADEAC：デジタルアーカイブシステム (NDLサーチ経由)",
              "value": 238584
            }, {
              "name": "NDLサーチ",
              "value": 22838268
            }, {
              "name": "国立国会図書館デジタルコレクション",
              "value": 9834160
            }]
          }, {
            "name": "大学共同利用機関法人 人間文化研究機構",
            "children": [{
              "name": "歴史人物画像データベース",
              "value": 15830
            }, {
              "name": "『日本言語地図』地図画像",
              "value": 1500
            }, {
              "name": "コーニツキー版欧州所在日本古書総合目録",
              "value": 30965
            }, {
              "name": "連歌・演能・雅楽データベース",
              "value": 244440
            }, {
              "name": "絵入源氏物語",
              "value": 227040
            }]
          }, {
            "name": "独立行政法人国立美術館",
            "children": [{
              "name": "アートコモンズ",
              "value": 45288
            }, {
              "name": "国立美術館所蔵作品総合目録",
              "value": 32696
            }]
          }, {
            "name": "文化庁・国立情報学研究所",
            "children": [{
              "name": "文化遺産オンライン",
              "value": 32703
            }]
          }, {
            "name": "NHK",
            "children": [{
              "name": "動画で見るニッポンみちしる",
              "value": 3768
            }]
          }, {
            "name": "ＮＨＫ",
            "children": [{
              "name": "動画で見るニッポンみちしる",
              "value": 3768
            }]
          }, {
            "name": "独立行政法人国立文化財機構",
            "children": [{
              "name": "国立博物館所蔵品統合検索システム",
              "value": 134054
            }]
          }, {
            "name": "国立公文書館",
            "children": [{
              "name": "国立公文書館デジタルアーカイブ",
              "value": 7147362
            }]
          }]
        }
        var part = {
          "name": "flare",
          "children": [{
            "name": "大学共同利用機関法人 人間文化研究機構",
            "children": [{
              "name": "歴史人物画像データベース",
              "value": 15830
            }, {
              "name": "『日本言語地図』地図画像",
              "value": 1500
            }, {
              "name": "コーニツキー版欧州所在日本古書総合目録",
              "value": 30965
            }, {
              "name": "連歌・演能・雅楽データベース",
              "value": 244440
            }, {
              "name": "絵入源氏物語",
              "value": 227040
            }]
          }, {
            "name": "独立行政法人国立美術館",
            "children": [{
              "name": "アートコモンズ",
              "value": 45288
            }, {
              "name": "国立美術館所蔵作品総合目録",
              "value": 32696
            }]
          }, {
            "name": "文化庁・国立情報学研究所",
            "children": [{
              "name": "文化遺産オンライン",
              "value": 32703
            }]
          }, {
            "name": "NHK",
            "children": [{
              "name": "動画で見るニッポンみちしる",
              "value": 3768
            }]
          }, {
            "name": "ＮＨＫ",
            "children": [{
              "name": "動画で見るニッポンみちしる",
              "value": 3768
            }]
          }, {
            "name": "独立行政法人国立文化財機構",
            "children": [{
              "name": "国立博物館所蔵品統合検索システム",
              "value": 134054
            }]
          }]
        }
        return (part)
      })
    }, {
      name: "partition",
      inputs: ["d3"],
      value: (function (d3) {
        return (data => {
          const root = d3.hierarchy(data).sum(d => d.value).sort((a, b) => b.value - a.value);
          return d3.partition().size([2 * Math.PI, root.height + 1])
          (root);
        })
      })
    }, {
      name: "color",
      inputs: ["d3", "data"],
      value: (function (d3, data) {
        return (d3.scaleOrdinal(d3.quantize(d3.interpolateRainbow, data.children.length + 1)))
      })
    }, {
      name: "format",
      inputs: ["d3"],
      value: (function (d3) {
        return (d3.format(",d"))
      })
    }, {
      name: "width",
      value: (function () {
        return (932)
      })
    }, {
      name: "radius",
      inputs: ["width"],
      value: (function (width) {
        return (width / 6)
      })
    }, {
      name: "arc",
      inputs: ["d3", "radius"],
      value: (function (d3, radius) {
        return (d3.arc().startAngle(d => d.x0).endAngle(d => d.x1).padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005)).padRadius(radius * 1.5).innerRadius(d => d.y0 * radius).outerRadius(d => Math.max(d.y0 * radius, d.y1 * radius - 1)))
      })
    }, {
      name: "d3",
      inputs: ["require"],
      value: (function (require) {
        return (require("d3@5"))
      })
    }]
  };
  const notebook = {
    id: "f9e1770e0f3c730a@334",
    modules: [m0]
  };
  export default notebook;
