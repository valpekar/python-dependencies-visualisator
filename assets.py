"""
assets.py - Static HTML/CSS/JS snippets for the Python Dependency Visualizer CLI
Do not place logic here. Only static string templates.
"""

# --- HTML/CSS/JS Snippets ---
PYVIS_OPTIONS = '''{
  "physics": {
    "stabilization": true,
    "barnesHut": {
      "gravitationalConstant": -8000,
      "centralGravity": 0.1,
      "springLength": 250,
      "springConstant": 0.02,
      "damping": 0.3
    }
  },
  "interaction": {
    "zoomView": true,
    "zoomSpeed": 0.2,
    "hover": true
  },
  "layout": {
    "improvedLayout": true
  },
  "manipulation": true,
  "nodes": {
    "shape": "dot",
    "size": 16,
    "font": {
      "size": 16,
      "face": "Arial",
      "color": "#111",
      "bold": true
    },
    "color": {
      "background": "#C8E6C9",
      "border": "#388E3C",
      "highlight": {
        "background": "#E8F5E9",
        "border": "#388E3C"
      }
    }
  },
  "edges": {
    "arrows": { "to": { "enabled": true } },
    "color": { "color": "#666666", "highlight": "#999999" },
    "width": 2,
    "smooth": { "type": "continuous" }
  },
  "configure": { "enabled": false }
}'''

HTML_CSS = '''
<style>
@page {{ size: {width}px {height}px; margin: 0; }}
html, body {{ width: {width}px; height: {height}px; margin: 0; padding: 0; overflow: hidden; display: block; }}
#loadingBar {{ display: none !important; }}
#mynetwork {{
  width: {width}px !important;
  height: {height}px !important;
  margin: 0 auto;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
  overflow: visible !important;
}}
#mynetwork > canvas {{
  width: {width}px !important;
  height: {height}px !important;
  object-fit: contain !important;
}}
#minimalLoading {{position:absolute;top:10px;left:50%;transform:translateX(-50%);font-size:22px;color:#000;z-index:1000;}}
</style>
'''

HTML_LOADING_JS = '''
<script>
var minimalLoading = document.getElementById('minimalLoading');
if (minimalLoading) {
  minimalLoading.innerText = '0%';
  var interval = setInterval(function() {
    if (window.network && window.network.body && window.network.body.nodeIndices && window.network.body.nodeIndices.length > 0) {
      minimalLoading.innerText = '50%';
      setTimeout(function() {
        minimalLoading.innerText = '100%';
        setTimeout(function() { 
          if (minimalLoading && minimalLoading.parentNode) {
            minimalLoading.parentNode.removeChild(minimalLoading);
          }
        }, 500);
      }, 500);
      clearInterval(interval);
    }
  }, 200);
}
</script>
'''

HTML_ZOOM_JS = '''
<script>
  window.addEventListener("load", function() {
    if (window.network) {
      var pos = window.network.getViewPosition();
      window.network.moveTo({scale: 2, position: pos});
    }
  });
</script>
''' 