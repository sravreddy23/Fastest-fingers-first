import { Game } from "./game.js";

export { Game };

window.addEventListener("DOMContentLoaded", () => {
  window.typingSpeedBattle = new Game();
});
