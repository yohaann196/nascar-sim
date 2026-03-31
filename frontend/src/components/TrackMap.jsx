import { useEffect, useRef, useState } from "react";
import { API } from "../utils/api";

export default function TrackMap({ trackId, raceResult }) {
  const mapRef = useRef(null);
  const leafletMap = useRef(null);
  const [coords, setCoords] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    API.get(`/tracks/${trackId}/coords?points=200`)
      .then(setCoords)
      .catch(() => setError("Could not load track coords. Is the API running?"));
  }, [trackId]);

  useEffect(() => {
    if (!coords || !mapRef.current) return;
    if (typeof window === "undefined" || !window.L) return;

    const L = window.L;

    if (leafletMap.current) {
      leafletMap.current.remove();
    }

    const centerLat = coords.coords[0].lat;
    const centerLng = coords.coords[0].lng;

    leafletMap.current = L.map(mapRef.current).setView([centerLat, centerLng], 14);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
    }).addTo(leafletMap.current);

    // Draw track outline
    const latLngs = coords.coords.map((c) => [c.lat, c.lng]);
    L.polyline(latLngs, { color: "#e8e8e8", weight: 8, opacity: 0.9 }).addTo(leafletMap.current);
    L.polyline(latLngs, { color: "#ff6b35", weight: 3, opacity: 1.0 }).addTo(leafletMap.current);

    // Start/finish line marker
    if (latLngs.length > 0) {
      L.marker(latLngs[0], {
        icon: L.divIcon({ className: "", html: "🏁", iconSize: [24, 24] }),
      })
        .addTo(leafletMap.current)
        .bindPopup("Start / Finish");
    }

    // If race result, add car positions from final lap
    if (raceResult?.finishing_order) {
      const colors = ["#ffd700", "#c0c0c0", "#cd7f32", "#4fc3f7", "#81c784",
        "#ff8a65", "#ba68c8", "#4db6ac", "#fff176", "#ffb74d"];

      raceResult.finishing_order.slice(0, 10).forEach((car, i) => {
        const lastLap = raceResult.lap_history[raceResult.lap_history.length - 1];
        const carSnap = lastLap?.cars?.find((c) => c.number === car.number);
        if (!carSnap) return;

        const idx = Math.floor(carSnap.track_position * (coords.coords.length - 1));
        const pos = coords.coords[idx];
        if (!pos) return;

        L.circleMarker([pos.lat, pos.lng], {
          radius: 8,
          color: "#fff",
          weight: 1.5,
          fillColor: colors[i % colors.length],
          fillOpacity: 1,
        })
          .addTo(leafletMap.current)
          .bindPopup(`P${car.position} #${car.number} ${car.name}`);
      });
    }
  }, [coords, raceResult]);

  return (
    <div className="panel track-map-panel">
      <h2>Track Map</h2>
      {error && <div className="error-banner">{error}</div>}
      {!coords && !error && <div className="loading">Loading track geometry…</div>}
      <div
        ref={mapRef}
        style={{ height: 480, borderRadius: 8, background: "var(--surface)" }}
      />
      <p className="map-note">
        Colored dots = top 10 car positions after last simulated lap.
        Run a race first to see them.
      </p>
    </div>
  );
}
