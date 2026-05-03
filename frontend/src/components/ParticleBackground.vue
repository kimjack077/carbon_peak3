<!-- frontend/src/components/ParticleBackground.vue -->
<template>
  <div ref="container" class="particle-container"></div>
</template>

<script>
import * as THREE from 'three'

export default {
  name: 'ParticleBackground',
  data() {
    return {
      scene: null,
      camera: null,
      renderer: null,
      particles: null,
      animationId: null
    }
  },
  mounted() {
    this.initThree()
    this.animate()
  },
  beforeDestroy() {
    if (this.animationId) cancelAnimationFrame(this.animationId)
    if (this.renderer) this.renderer.dispose()
  },
  methods: {
    initThree() {
      const container = this.$refs.container
      const width = window.innerWidth
      const height = window.innerHeight

      this.scene = new THREE.Scene()
      this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
      this.camera.position.z = 50

      this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
      this.renderer.setSize(width, height)
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
      container.appendChild(this.renderer.domElement)

      // 创建粒子系统
      const particleCount = 800
      const geometry = new THREE.BufferGeometry()
      const positions = new Float32Array(particleCount * 3)
      const colors = new Float32Array(particleCount * 3)

      for (let i = 0; i < particleCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 100
        positions[i + 1] = (Math.random() - 0.5) * 100
        positions[i + 2] = (Math.random() - 0.5) * 50

        // 颜色：青色到紫色渐变
        const t = Math.random()
        colors[i] = 0.06 + t * 0.5      // R
        colors[i + 1] = 0.46 - t * 0.1  // G
        colors[i + 2] = 0.43 + t * 0.35 // B
      }

      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

      const material = new THREE.PointsMaterial({
        size: 0.8,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
      })

      this.particles = new THREE.Points(geometry, material)
      this.scene.add(this.particles)

      window.addEventListener('resize', this.handleResize)
    },
    animate() {
      this.animationId = requestAnimationFrame(this.animate)

      if (this.particles) {
        this.particles.rotation.x += 0.0003
        this.particles.rotation.y += 0.0005
      }

      this.renderer.render(this.scene, this.camera)
    },
    handleResize() {
      const width = window.innerWidth
      const height = window.innerHeight
      this.camera.aspect = width / height
      this.camera.updateProjectionMatrix()
      this.renderer.setSize(width, height)
    }
  }
}
</script>

<style scoped>
.particle-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}
</style>