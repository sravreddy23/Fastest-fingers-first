export class UIManager {
  constructor() {
    this.canvas = document.getElementById("fxCanvas");
    this.ctx = this.canvas.getContext("2d");
    this.resize();
    window.addEventListener("resize", () => this.resize());
  }

  resize() {
    this.canvas.width = window.innerWidth * window.devicePixelRatio;
    this.canvas.height = window.innerHeight * window.devicePixelRatio;
    this.canvas.style.width = `${window.innerWidth}px`;
    this.canvas.style.height = `${window.innerHeight}px`;
    this.ctx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);
  }

  clear(dt) {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    ctx.save();
    ctx.globalAlpha = 0.38;
    for (let i = 0; i < 8; i += 1) {
      const y = ((performance.now() * 0.02 + i * 90) % (window.innerHeight + 100)) - 50;
      ctx.fillStyle = `rgba(${12 + i * 5}, ${16 + i * 4}, ${34 + i * 8}, ${0.03 + i * 0.004})`;
      ctx.fillRect(0, y, window.innerWidth, 34);
    }
    ctx.restore();
  }

  drawParticles(particles) {
    const ctx = this.ctx;
    for (const particle of particles) {
      const life = particle.life / particle.maxLife;
      if (life <= 0) continue;
      ctx.save();
      ctx.globalAlpha = life;
      const glow = ctx.createRadialGradient(particle.x, particle.y, 0, particle.x, particle.y, particle.radius * 4);
      glow.addColorStop(0, particle.color);
      glow.addColorStop(1, "transparent");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.radius * 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  }
}
