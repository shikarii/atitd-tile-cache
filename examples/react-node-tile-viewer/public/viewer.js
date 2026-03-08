import React, { useEffect, useState } from "https://esm.sh/react@18.3.1";
import { createRoot } from "https://esm.sh/react-dom@18.3.1/client";
import L from "https://esm.sh/leaflet@1.9.4";

function App() {
  const [config, setConfig] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    fetch("/api/config")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Config request failed (${response.status})`);
        }
        return response.json();
      })
      .then((data) => {
        if (!cancelled) {
          setConfig(data);
        }
      })
      .catch((fetchError) => {
        if (!cancelled) {
          setError(String(fetchError));
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!config) {
      return undefined;
    }

    const map = L.map("map", {
      center: [0, 0],
      zoom: 2,
      minZoom: 0,
      maxZoom: 6
    });

    L.tileLayer(config.tileUrlTemplate, {
      minZoom: 0,
      maxZoom: 6,
      noWrap: true,
      attribution: "(c) Desert Nomad Studios / atitd.wiki"
    }).addTo(map);

    return () => {
      map.remove();
    };
  }, [config]);

  return React.createElement(
    "main",
    { className: "app" },
    React.createElement(
      "aside",
      { className: "panel" },
      React.createElement("h1", null, "ATITD Tile Viewer"),
      error
        ? React.createElement("p", null, error)
        : React.createElement(
            "ul",
            { className: "meta" },
            React.createElement("li", null, React.createElement("strong", null, "Tale: "), config?.tale ?? "loading..."),
            React.createElement(
              "li",
              null,
              React.createElement("strong", null, "Template: "),
              React.createElement("code", null, config?.tileUrlTemplate ?? "loading...")
            )
          )
    ),
    React.createElement("section", { className: "map-wrap" }, React.createElement("div", { id: "map" }))
  );
}

const root = createRoot(document.getElementById("root"));
root.render(React.createElement(App));
