"""
✨ Demo script for Aura Text Editor
Explore syntax highlighting, bracket matching, and theme harmony.
"""

from dataclasses import dataclass
from typing import List, Optional
import math
import time


@dataclass
class Particle:
    """A 2D particle simulation node."""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    mass: float = 1.0

    def apply_force(self, fx: float, fy: float, dt: float) -> None:
        """Applies external force to particle using Euler integration."""
        ax = fx / self.mass
        ay = fy / self.mass
        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    @property
    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)


class ParticleField:
    """A field containing multiple interacting particles."""

    def __init__(self, count: int = 100):
        self.particles: List[Particle] = [
            Particle(x=float(i * 10), y=math.sin(i * 0.2) * 50)
            for i in range(count)
        ]
        self.is_active = True
        self.metadata = {
            "version": "1.0.0",
            "particles_count": count,
            "damping": 0.985,
        }

    def simulate(self, steps: int = 50) -> float:
        start_time = time.perf_counter()
        gravity = 9.81

        for step in range(steps):
            for p in self.particles:
                # Apply gravitational drift
                p.apply_force(fx=0.0, fy=gravity, dt=0.016)
                p.vx *= self.metadata["damping"]
                p.vy *= self.metadata["damping"]

        elapsed = time.perf_counter() - start_time
        print(f"✨ Simulation completed {steps} steps in {elapsed * 1000:.2f} ms")
        return elapsed


if __name__ == "__main__":
    field = ParticleField(count=42)
    field.simulate(steps=100)
    print("◈ Aura Editor: Aesthetic, Lightweight, Fast.")
