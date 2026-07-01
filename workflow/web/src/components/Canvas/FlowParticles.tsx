import { useEffect, useRef, useCallback } from "react";

interface Particle {
  el: HTMLDivElement;
  path: SVGPathElement;
  length: number;
  progress: number;
  speed: number;
  color: string;
  size: number;
}

export function FlowParticles({ paths }: { paths: SVGPathElement[] }) {
  const containerRef = useRef<HTMLDivElement>(null);

  const createParticle = useCallback((path: SVGPathElement, color: string, size: number): Particle => {
    const el = document.createElement("div");
    el.style.cssText = `position:absolute;width:${size}px;height:${size}px;border-radius:50%;background:${color};box-shadow:0 0 6px ${color};pointer-events:none;z-index:5`;
    containerRef.current?.appendChild(el);
    return { el, path, length: path.getTotalLength(), progress: Math.random(), speed: 0.003 + Math.random() * 0.004, color, size };
  }, []);

  useEffect(() => {
    if (!paths.length) return;
    const colors = ["#818CF8", "#818CF8", "#22D3EE", "#A78BFA"];
    const newParticles: Particle[] = [];
    paths.forEach((path, idx) => {
      if (!path.getTotalLength) return;
      for (let p = 0; p < 3; p++) newParticles.push(createParticle(path, colors[(idx * 3 + p) % colors.length], 3 + Math.random() * 2));
    });
    let running = true;
    const animate = () => {
      if (!running) return;
      newParticles.forEach((p) => {
        if (!p.path.isConnected) return;
        p.progress += p.speed;
        if (p.progress >= 1) p.progress = 0;
        try {
          const pt = p.path.getPointAtLength(p.progress * p.length);
          p.el.style.left = `${pt.x - p.size / 2}px`;
          p.el.style.top = `${pt.y - p.size / 2}px`;
          const trail = 1 - Math.abs(p.progress - 0.5) * 1.6;
          p.el.style.opacity = `${Math.max(0.15, trail)}`;
        } catch {}
      });
      requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
    return () => { running = false; newParticles.forEach((p) => p.el.remove()); };
  }, [paths, createParticle]);

  return <div ref={containerRef} style={{ position: "absolute", inset: 0, pointerEvents: "none", zIndex: 5 }} />;
}
