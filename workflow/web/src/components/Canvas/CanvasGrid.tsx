import { useRef } from "react";

export function CanvasGrid() {
  const ref = useRef<HTMLDivElement>(null);
  return (
    <div className="canvas-wrapper">
      <div ref={ref} className="canvas-bg" />
      <div className="canvas-vignette" />
    </div>
  );
}
